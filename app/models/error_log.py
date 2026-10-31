"""Uygulama hataları: error_log tablosu ve veritabanı kesintisi için dosya-önce günlüğü."""
import json
import logging
import os
import time
from datetime import datetime

import psycopg2

from app.db import execute
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
