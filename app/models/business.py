"""İşletme (tenant) modeli: businesses tablosu."""
from app.db import query_all, query_one

BUSINESS_COLUMNS = "business_id, business_name, publish_url, business_admin_user_id, is_active, is_deleted, created_at"


class Business:
    """businesses tablosundaki bir satırı sarar."""

    def __init__(self, row):
        self.row = row

    @property
    def business_id(self):
        """İşletmenin birincil anahtarı."""
        return self.row["business_id"]

    @property
    def business_name(self):
        """İşletme adı."""
        return self.row["business_name"]

    @property
    def is_active(self):
        """Pasif işletmenin kullanıcıları giriş yapamaz."""
        return bool(self.row["is_active"])

    @property
    def is_accessible(self):
        """İşletmeye erişim açık mı: aktif ve silinmemiş."""
        return bool(self.row["is_active"]) and not self.row["is_deleted"]

    @classmethod
    def get_by_id(cls, business_id):
        """Silinmemiş işletmeyi getirir; yoksa None."""
        row = query_one(
            "SELECT " + BUSINESS_COLUMNS + " FROM businesses WHERE business_id = %s AND is_deleted = FALSE",
            (business_id,),
        )
        return cls(row) if row else None

    @classmethod
    def list_selectable(cls):
        """Simülasyon için seçilebilir (aktif, silinmemiş) işletmeleri döndürür."""
        rows = query_all(
            "SELECT " + BUSINESS_COLUMNS + " FROM businesses WHERE is_active = TRUE AND is_deleted = FALSE "
            "ORDER BY lower(business_name) LIMIT 500",
        )
        return [cls(row) for row in rows]

    @classmethod
    def count_active(cls):
        """Silinmemiş işletme sayısı."""
        return query_one("SELECT count(*) AS total FROM businesses WHERE is_deleted = FALSE")["total"]
