"""Zamanlanmış görevler: günlük aktarımı (dosya yalnızca commit sonrası silinir), retention ve arşiv."""
import csv
import json
import os
import tempfile
from datetime import date, timedelta

from _ortam import environment
from app import scheduler
from app.db import execute, query_all, query_one


def _write_log(directory, day, lines):
    """GG-AA-YYYY.log dosyası yazar ve yolunu döndürür."""
    path = os.path.join(directory, day.strftime("%d-%m-%Y") + ".log")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return path


def _entry(url, when="2026-01-05T10:00:00+03:00"):
    """Geçerli bir günlük satırı."""
    return json.dumps({"created_at": when, "error_code": "503", "url": url, "reason": "OperationalError: x",
                       "ip_address": "203.0.113.5", "user_id": None})


def test_connection_log_import_keeps_original_timestamps_and_deletes_file_after_commit():
    """Korur: created_at dosyadaki orijinal zamandır; dosya commit sonrası silinir, bugünküne dokunulmaz."""
    with environment():
        with tempfile.TemporaryDirectory() as directory:
            yesterday = date.today() - timedelta(days=1)
            old = _write_log(directory, yesterday, [_entry("/__test__a"), _entry("/__test__b"), "bozuk satir"])
            today = _write_log(directory, date.today(), [_entry("/__test__c")])
            summary = scheduler.import_connection_error_logs(directory)
            assert summary["files"] == 1 and summary["rows"] == 2
            assert not os.path.exists(old) and os.path.exists(today)
            row = query_one("SELECT created_at FROM error_log WHERE url = %s", ("/__test__a",))
            assert row["created_at"].year == 2026 and row["created_at"].month == 1 and row["created_at"].day == 5
            assert query_one("SELECT 1 AS found FROM error_log WHERE url = %s", ("/__test__c",)) is None


def test_connection_log_without_valid_lines_is_renamed_not_deleted():
    """Korur: tek kopya hataların sessizce silinmemesi. Geçerli satırı olmayan dosya .bozuk olarak saklanır."""
    with environment():
        with tempfile.TemporaryDirectory() as directory:
            path = _write_log(directory, date.today() - timedelta(days=2), ["yarim yazilmis {", "baska bozuk"])
            scheduler.import_connection_error_logs(directory)
            assert not os.path.exists(path) and os.path.exists(path + ".bozuk")


def test_failed_import_keeps_the_file():
    """Korur: aktarım başarısızsa dosya silinmez (veritabanı hâlâ erişilemezken dosyayı silmek hataları yok eder)."""
    with environment():
        with tempfile.TemporaryDirectory() as directory:
            # error_code kolonu 10 karakterle sınırlı: tablo kısıtı ihlali aktarımı başarısız kılar.
            bad = json.dumps({"created_at": "2026-01-05T10:00:00+03:00", "error_code": "x" * 50, "url": "/__test__z"})
            path = _write_log(directory, date.today() - timedelta(days=1), [bad])
            summary = scheduler.import_connection_error_logs(directory)
            assert summary["failed"] == 1 and os.path.exists(path)
            assert query_one("SELECT 1 AS found FROM error_log WHERE url = %s", ("/__test__z",)) is None


def test_login_attempt_retention_removes_only_old_rows():
    """30 günden eski denemeler silinir, yeniler kalır (yalnızca test e-postalarıyla sınırlandırılarak çağrılır)."""
    with environment():
        execute("INSERT INTO login_attempts (ip_address, email, reason, created_at) VALUES "
                "('203.0.113.50', '__test__eski@example.com', 'bad_password', now() - interval '40 days'), "
                "('203.0.113.50', '__test__yeni@example.com', 'bad_password', now() - interval '1 day')")
        deleted = scheduler.purge_login_attempts(email_like="__test__%")
        remaining = [row["email"] for row in query_all(
            "SELECT email FROM login_attempts WHERE email LIKE '__test__%'")]
        assert deleted == 1 and remaining == ["__test__yeni@example.com"]


def test_userslogs_archive_writes_csv_then_removes_old_rows():
    """2 yıldan eski loglar tarih ve tablo adı içeren CSV'ye yazılır, ardından tablodan kaldırılır; yenisi kalır."""
    with environment():
        execute("INSERT INTO userslogs (action, created_at) VALUES "
                "('__test__eski', now() - interval '3 years'), ('__test__yeni', now() - interval '1 day')")
        with tempfile.TemporaryDirectory() as directory:
            count = scheduler.archive_userslogs(directory, action_like="__test__%")
            name = "userslogs_{}.csv".format(date.today().isoformat())
            with open(os.path.join(directory, name), encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
        assert count == 1 and len(rows) == 1 and "__test__eski" in rows[0]
        left = [row["action"] for row in query_all("SELECT action FROM userslogs WHERE action LIKE '__test__%'")]
        assert left == ["__test__yeni"]


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
