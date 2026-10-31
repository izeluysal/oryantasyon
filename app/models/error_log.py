"""Uygulama hataları: error_log tablosu ve veritabanı kesintisi için dosya-önce günlüğü."""
import json
import logging
import os
import time
from datetime import datetime

import psycopg2

from app.db import PER_PAGE, execute, like_pattern, query_all
from app.paths import LOGS_DIR

logger = logging.getLogger(__name__)

SUPPRESS_SECONDS = 60
_recent = {}


class ErrorLog:
    """error_log tablosuna hata yazar; bağlantı hatası önce diske yazılır."""

    @staticmethod
    def record(error_code, url, reason, ip_address=None, user_id=None):
        """Hatayı tabloya yazar. Tabloya yazılamazsa dosyaya düşer, asla isteği düşürmez."""
        try:
            execute(
                "INSERT INTO error_log (error_code, url, reason, ip_address, user_id) VALUES (%s, %s, %s, %s, %s)",
                (str(error_code), (url or "")[:500], str(reason)[:4000], ip_address, user_id),
            )
        except psycopg2.Error as error:
            logger.error("error_log tablosuna yazılamadı: %s", error)
            ErrorLog.write_to_file(error_code, url, reason, ip_address, user_id)

    @staticmethod
    def page(query="", page=1):
        """Hata kayıtlarını sayfalı döndürür: (satırlar, toplam). Yalnızca platform yöneticisine açıktır."""
        where, params = "", []
        if query:
            where = "WHERE e.error_code ILIKE %s OR e.url ILIKE %s OR e.reason ILIKE %s "
            params.extend([like_pattern(query)] * 3)
        params.extend([PER_PAGE, (max(page, 1) - 1) * PER_PAGE])
        rows = query_all(
            "SELECT e.error_log_id, e.error_code, e.url, e.reason, e.ip_address, e.occurrence_count, e.created_at, "
            "count(*) OVER() AS total_count FROM error_log e " + where
            + "ORDER BY e.created_at DESC, e.error_log_id DESC LIMIT %s OFFSET %s",
            params,
        )
        return rows, (rows[0]["total_count"] if rows else 0)

    @staticmethod
    def write_to_file(error_code, url, reason, ip_address=None, user_id=None):
        """Hatayı GG-AA-YYYY.log dosyasına tek satırlık JSON olarak ekler (aynı hata 60 sn bastırılır)."""
        signature = (str(error_code), url, str(reason))
        now = time.time()
        if now - _recent.get(signature, 0) < SUPPRESS_SECONDS:
            return
        _recent[signature] = now
        entry = {
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "error_code": str(error_code),
            "url": url,
            "reason": str(reason)[:1000],
            "ip_address": ip_address,
            "user_id": user_id,
        }
        path = os.path.join(LOGS_DIR, datetime.now().strftime("%d-%m-%Y") + ".log")
        try:
            os.makedirs(LOGS_DIR, exist_ok=True)
            with open(path, "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as error:
            # Disk hatası hata sayfasının önüne geçmemeli; yalnızca bildirilir.
            logger.error("Bağlantı hatası dosyaya yazılamadı: %s", error)
