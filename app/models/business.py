"""İşletme (tenant) modeli: businesses tablosu."""
from app.db import PER_PAGE, get_cursor, like_pattern, query_all, query_one

BUSINESS_COLUMNS = (
    "business_id, business_name, publish_url, business_admin_user_id, is_active, is_deleted, created_at"
)


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
    def publish_url(self):
        """Yayın adresi (alt alan adı)."""
        return self.row["publish_url"]

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
    def list_page(cls, query="", status=None, page=1):
        """Aramaya ve duruma göre sayfalı işletme listesi; her satırda kullanıcı sayısı vardır: (liste, toplam)."""
        where, params = ["b.is_deleted = FALSE"], []
        if query:
            where.append("(b.business_name ILIKE %s OR b.publish_url ILIKE %s)")
            params.extend([like_pattern(query)] * 2)
        if status in ("active", "passive"):
            where.append("b.is_active = %s")
            params.append(status == "active")
        params.extend([PER_PAGE, (max(page, 1) - 1) * PER_PAGE])
        # Kullanıcı sayısı tek sorguda alınır (satır başına ayrı sorgu atılmaz).
        rows = query_all(
            "SELECT b.business_id, b.business_name, b.publish_url, b.business_admin_user_id, b.is_active, "
            "b.is_deleted, b.created_at, count(*) OVER() AS total_count, "
            "(SELECT count(*) FROM users u WHERE u.business_id = b.business_id AND u.is_deleted = FALSE) AS user_count "
            "FROM businesses b WHERE " + " AND ".join(where) + " ORDER BY lower(b.business_name) LIMIT %s OFFSET %s",
            params,
        )
        return rows, (rows[0]["total_count"] if rows else 0)

    @staticmethod
    def summary():
        """Sayaç kartları için toplam/aktif/pasif işletme sayıları."""
        row = query_one(
            "SELECT count(*) AS total, count(*) FILTER (WHERE is_active) AS active, "
            "count(*) FILTER (WHERE NOT is_active) AS passive FROM businesses WHERE is_deleted = FALSE"
        )
        return {"total": row["total"], "active": row["active"], "passive": row["passive"]}

    @staticmethod
    def count_active():
        """Silinmemiş işletme sayısı."""
        return query_one("SELECT count(*) AS total FROM businesses WHERE is_deleted = FALSE")["total"]

    @staticmethod
    def publish_url_taken(publish_url, exclude_business_id=None):
        """Yayın adresi başka bir aktif işletmede var mı?"""
        row = query_one(
            "SELECT business_id FROM businesses WHERE lower(publish_url) = lower(%s) AND is_deleted = FALSE "
            "AND business_id IS DISTINCT FROM %s",
            (publish_url, exclude_business_id),
        )
        return row is not None

    @staticmethod
    def create(business_name, publish_url):
        """Yeni işletme oluşturur ve kimliğini döndürür."""
        with get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO businesses (business_name, publish_url) VALUES (%s, %s) RETURNING business_id",
                (business_name, publish_url),
            )
            return cursor.fetchone()["business_id"]

    def update(self, business_name, publish_url):
        """Adı ve yayın adresini günceller; değişen alanları (eski/yeni) döndürür."""
        new_values = {"business_name": business_name, "publish_url": publish_url}
        changes = [
            {"column": column, "old": self.row[column], "new": value}
            for column, value in new_values.items() if self.row[column] != value
        ]
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE businesses SET business_name = %s, publish_url = %s, updated_at = now() "
                "WHERE business_id = %s",
                (business_name, publish_url, self.business_id),
            )
        return changes

    def set_active(self, is_active):
        """İşletmeyi aktif/pasif yapar."""
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE businesses SET is_active = %s, updated_at = now() WHERE business_id = %s",
                (bool(is_active), self.business_id),
            )

    def soft_delete(self):
        """İşletmeyi ve silinmemiş kullanıcılarını tek transaction'da soft delete yapar.

        Returns:
            Birlikte silinen kullanıcı kimlikleri (geri yüklemede log detail'inden okunur).
        """
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_deleted = TRUE, updated_at = now() "
                "WHERE business_id = %s AND is_deleted = FALSE RETURNING user_id",
                (self.business_id,),
            )
            user_ids = [row["user_id"] for row in cursor.fetchall()]
            cursor.execute(
                "UPDATE businesses SET is_deleted = TRUE, updated_at = now() WHERE business_id = %s",
                (self.business_id,),
            )
        return user_ids

    def assign_admin_if_missing(self, user_id):
        """İlk işletme yöneticisini birincil sorumlu yapar; zaten varsa mevcut atama korunur."""
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE businesses SET business_admin_user_id = %s WHERE business_id = %s "
                "AND business_admin_user_id IS NULL",
                (user_id, self.business_id),
            )
