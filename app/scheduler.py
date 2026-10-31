"""Zamanlanmış görevler: bağlantı hatası günlüğünün aktarımı, giriş denemesi retention'ı, aylık log arşivi."""
import csv
import glob
import json
import logging
import os
import re
import time
from datetime import date, datetime

import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
from psycopg2.extras import execute_values

from app.db import get_cursor
from app.models.userslog import UsersLog
from app.paths import LOGS_DIR

logger = logging.getLogger(__name__)

BATCH_SIZE = 500
LOGIN_ATTEMPT_RETENTION_DAYS = 30
USERSLOGS_RETENTION_YEARS = 2
STALE_FILE_DAYS = 7
FILE_NAME_PATTERN = re.compile(r"^(\d{2})-(\d{2})-(\d{4})\.log$")
# Birden fazla gunicorn worker'ı aynı görevleri iki kez çalıştırmasın diye tek worker kilidi alır.
SCHEDULER_LOCK_KEY = 872341
_lock_connection = None


def _parse_line(line):
    """Günlük satırını (tek satırlık JSON) sözlüğe çevirir; bozuksa None döner."""
    try:
        entry = json.loads(line)
        datetime.fromisoformat(entry["created_at"])
        return entry if isinstance(entry, dict) and entry.get("error_code") else None
    except (ValueError, KeyError, TypeError):
        return None


def import_connection_error_logs(logs_dir=LOGS_DIR):
    """Bugüne ait olmayan GG-AA-YYYY.log dosyalarını error_log tablosuna aktarır.

    Silme sırası kritiktir: dosya yalnızca aktarım commit edildikten sonra silinir; aktarım başarısızsa
    dosya (hataların tek kopyası olduğu için) korunur. Geçerli satırı olmayan dosya .bozuk olarak saklanır.

    Returns:
        Aktarım özeti sözlüğü: files, rows, failed.
    """
    summary = {"files": 0, "rows": 0, "failed": 0}
    today = date.today()
    for path in sorted(glob.glob(os.path.join(logs_dir, "*.log"))):
        match = FILE_NAME_PATTERN.match(os.path.basename(path))
        if not match:
            continue
        file_date = date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        if file_date >= today:
            continue  # bugünün dosyası hâlâ yazılıyor olabilir
        age_days = (today - file_date).days
        try:
            with open(path, encoding="utf-8") as log_file:
                lines = [line.strip() for line in log_file if line.strip()]
            entries = [entry for entry in map(_parse_line, lines) if entry]
            if len(entries) != len(lines):
                logger.warning("Bozuk satırlar atlandı: %s (%s satır)", path, len(lines) - len(entries))
            if not entries:
                os.replace(path, path + ".bozuk")
                continue
            with get_cursor() as cursor:
                for start in range(0, len(entries), BATCH_SIZE):
                    batch = entries[start:start + BATCH_SIZE]
                    execute_values(
                        cursor,
                        "INSERT INTO error_log (created_at, error_code, url, reason, ip_address, user_id) VALUES %s",
                        [(e["created_at"], e["error_code"], e.get("url"), e.get("reason"), e.get("ip_address"),
                          None) for e in batch],
                    )
            # Commit get_cursor çıkışında yapıldı; ancak buradan sonra dosya silinir.
            os.remove(path)
            summary["files"] += 1
            summary["rows"] += len(entries)
        except (psycopg2.Error, OSError) as error:
            summary["failed"] += 1
            logger.error("Hata günlüğü aktarılamadı, dosya korunuyor (%s): %s", path, error)
            if age_days > STALE_FILE_DAYS:
                logger.critical("Aktarılamayan günlük %s günden eski: veritabanı kapalı olabilir", age_days)
    if summary["files"] or summary["failed"]:
        UsersLog.record("error_log_import", entity_type="error_log", detail=summary)
    return summary


def purge_login_attempts(retention_days=LOGIN_ATTEMPT_RETENTION_DAYS, email_like=None):
    """Retention süresinden eski başarısız giriş denemelerini siler (yalnızca-ekleme tablosu, retention'a tabidir)."""
    with get_cursor() as cursor:
        cursor.execute(
            "DELETE FROM login_attempts WHERE created_at < now() - make_interval(days => %s) "
            "AND (%s::text IS NULL OR email LIKE %s::text)",
            (retention_days, email_like, email_like),
        )
        return cursor.rowcount


def archive_userslogs(out_dir=LOGS_DIR, years=USERSLOGS_RETENTION_YEARS, action_like=None):
    """2 yıldan eski aktivite loglarını userslogs_YYYY-MM-DD.csv dosyasına aktarıp tablodan kaldırır.

    Dosya diske yazılıp kapatıldıktan sonra aynı kayıtlar silinir; yazma başarısızsa hiçbir kayıt silinmez.

    Returns:
        Arşivlenen satır sayısı.
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "userslogs_{}.csv".format(date.today().isoformat()))
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT userslog_id, user_id, business_id, action, entity_type, entity_id, detail, ip_address, "
            "created_at FROM userslogs WHERE created_at < now() - make_interval(years => %s) "
            "AND (%s::text IS NULL OR action LIKE %s::text) ORDER BY userslog_id LIMIT %s",
            (years, action_like, action_like, BATCH_SIZE * 100),
        )
        rows = cursor.fetchall()
        if not rows:
            return 0
        with open(path, "a", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            for row in rows:
                writer.writerow(list(row.values()))
        cursor.execute("DELETE FROM userslogs WHERE userslog_id = ANY(%s)", ([row["userslog_id"] for row in rows],))
    return len(rows)


def _acquire_lock():
    """Tek worker'ın zamanlayıcıyı çalıştırması için advisory kilidi almaya çalışır."""
    global _lock_connection
    from app.db import _pool_settings
    connection = psycopg2.connect(
        host=_pool_settings["host"], port=_pool_settings["port"], user=_pool_settings["user"],
        password=_pool_settings["password"], dbname=_pool_settings["database"], connect_timeout=5)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(%s)", (SCHEDULER_LOCK_KEY,))
        acquired = cursor.fetchone()[0]
    if not acquired:
        connection.close()
        return False
    _lock_connection = connection  # bağlantı açık kaldığı sürece kilit tutulur
    return True


def start(app):
    """Zamanlayıcıyı başlatır; DB kapalıysa veya kilit başka worker'daysa sessizce başlamaz."""
    try:
        if not _acquire_lock():
            return None
    except psycopg2.Error as error:
        logger.error("Zamanlayıcı başlatılamadı (veritabanı yok): %s", error)
        return None
    scheduler = BackgroundScheduler(timezone="Europe/Istanbul")
    options = {"max_instances": 1, "coalesce": True, "misfire_grace_time": 3600}
    scheduler.add_job(import_connection_error_logs, "cron", hour=0, minute=5, id="import_error_logs", **options)
    scheduler.add_job(purge_login_attempts, "cron", hour=3, minute=30, id="purge_login_attempts", **options)
    scheduler.add_job(archive_userslogs, "cron", day=1, hour=3, minute=0, id="archive_userslogs", **options)
    scheduler.start()
    logger.info("Zamanlanmış görevler başlatıldı (%s)", time.strftime("%H:%M:%S"))
    return scheduler
