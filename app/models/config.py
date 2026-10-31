"""Çalışma zamanı ayarları: config tablosuna key/value (JSONB) erişimi."""
import copy

from psycopg2.extras import Json

from app.db import execute, query_all, query_one

# DB'de satır yoksa (ilk kurulum, kaydedilmemiş ayar) buradan okunur; UI hiçbir zaman None görmez.
DEFAULTS = {
    "login_protection": {"enabled": True, "max_attempts": 5, "block_minutes": 10, "window_minutes": 15},
    "support_contact": {"name": "", "phone": ""},
}


class Config:
    """config tablosuna ince erişim: işletme satırı, platform satırı, DEFAULTS sırasıyla okunur."""

    @staticmethod
    def get(key, default=None, business_id=None):
        """Ayarı döndürür (dict). Sıra: işletme satırı, platform satırı, DEFAULTS, default."""
        if business_id is None:
            row = query_one(
                "SELECT setting_value FROM config WHERE setting_key = %s AND business_id IS NULL",
                (key,),
            )
        else:
            row = query_one(
                "SELECT setting_value FROM config WHERE setting_key = %s "
                "AND (business_id = %s OR business_id IS NULL) ORDER BY business_id NULLS LAST LIMIT 1",
                (key, business_id),
            )
        if row:
            return row["setting_value"]
        if key in DEFAULTS:
            return copy.deepcopy(DEFAULTS[key])
        return default

    @staticmethod
    def set(key, value, business_id=None):
        """Ayarı yazar (upsert). business_id verilmezse platform satırına yazar."""
        if business_id is None:
            execute(
                "INSERT INTO config (setting_key, setting_value) VALUES (%s, %s) "
                "ON CONFLICT (setting_key) WHERE business_id IS NULL "
                "DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = now()",
                (key, Json(value)),
            )
        else:
            execute(
                "INSERT INTO config (setting_key, setting_value, business_id) VALUES (%s, %s, %s) "
                "ON CONFLICT (setting_key, business_id) WHERE business_id IS NOT NULL "
                "DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = now()",
                (key, Json(value), business_id),
            )

    @staticmethod
    def all(business_id=None):
        """DEFAULTS ile platform satırlarını, varsa işletme satırlarını birleştirip döndürür."""
        merged = copy.deepcopy(DEFAULTS)
        rows = query_all(
            "SELECT setting_key, setting_value, business_id FROM config "
            "WHERE business_id IS NULL OR business_id = %s ORDER BY business_id NULLS FIRST LIMIT 1000",
            (business_id,),
        )
        for row in rows:
            merged[row["setting_key"]] = row["setting_value"]
        return merged

    @staticmethod
    def bool(key, field, default=False, business_id=None):
        """Ayar objesindeki bir alanı boolean olarak okur ('true', '1', 'yes', 'on' kabul edilir)."""
        value = (Config.get(key, business_id=business_id) or {}).get(field, default)
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes", "on")
        return bool(value)
