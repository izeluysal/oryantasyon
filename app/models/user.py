"""Kullanıcı modeli: users tablosu, oturum anahtarı ve tema/sidebar tercihleri."""
import hashlib
import hmac

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app.db import execute, query_all, query_one
from app.helpers.roles import ROLE_ADMIN

# Kolon listesi tek yerde: SELECT * kullanılmaz, password_hash dışarı sızmasın diye açıkça seçilir.
USER_COLUMNS = (
    "user_id, business_id, full_name, email, phone, password_hash, role, theme, language, "
    "sidebar_collapsed, last_login_at, is_active, is_deleted, created_at"
)


class User(UserMixin):
    """users tablosundaki bir satırı Flask-Login kullanıcısı olarak sarar."""

    def __init__(self, row):
        self.row = row

    @property
    def user_id(self):
        """Kullanıcının birincil anahtarı."""
        return self.row["user_id"]

    @property
    def business_id(self):
        """Kullanıcının sabitlendiği işletme; ana kullanıcıda (yonetici) None."""
        return self.row["business_id"]

    @property
    def full_name(self):
        """Ad soyad."""
        return self.row["full_name"]

    @property
    def email(self):
        """E-posta adresi."""
        return self.row["email"]

    @property
    def role(self):
        """Rol anahtarı (bkz. app.helpers.roles)."""
        return self.row["role"]

    @property
    def theme(self):
        """Tema tercihi: light veya dark."""
        return self.row["theme"]

    @property
    def language(self):
        """Arayüz dili tercihi."""
        return self.row["language"]

    @property
    def sidebar_collapsed(self):
        """Sidebar'ın daraltılmış olup olmadığı."""
        return self.row["sidebar_collapsed"]

    @property
    def is_active(self):
        """Pasif kullanıcı giriş yapamaz (UserMixin.is_active'i ezer)."""
        return bool(self.row["is_active"]) and not self.row["is_deleted"]

    @property
    def is_platform_admin(self):
        """Ana (platform) kullanıcı mı?"""
        return self.role == ROLE_ADMIN

    @property
    def initials(self):
        """Avatar için ad soyadın baş harfleri."""
        parts = [part for part in self.full_name.split() if part]
        return "".join(part[0].upper() for part in parts[:2]) or "?"

    def session_key(self):
        """Şifreye bağlı oturum anahtarı: şifre değişince açık oturumlar geçersizleşir."""
        raw = "{}:{}".format(self.user_id, self.row["password_hash"])
        secret = current_app.config["SECRET_KEY"].encode("utf-8")
        return hmac.new(secret, raw.encode("utf-8"), hashlib.sha256).hexdigest()[:32]

    def get_id(self):
        """Oturuma yazılan kimlik: kullanıcı numarası ve oturum anahtarı."""
        return "{}:{}".format(self.user_id, self.session_key())

    def check_password(self, password):
        """Düz şifreyi saklanan hash ile karşılaştırır."""
        return check_password_hash(self.row["password_hash"], password)

    @classmethod
    def get_by_id(cls, user_id):
        """Silinmemiş kullanıcıyı kimliğiyle getirir; yoksa None."""
        row = query_one(
            "SELECT " + USER_COLUMNS + " FROM users WHERE user_id = %s AND is_deleted = FALSE",
            (user_id,),
        )
        return cls(row) if row else None

    @classmethod
    def get_by_session_id(cls, session_id):
        """Oturum kimliğini ('id:anahtar') doğrular; anahtar uyuşmazsa None döner."""
        user_part, _, key = str(session_id).partition(":")
        if not user_part.isdigit():
            return None
        user = cls.get_by_id(int(user_part))
        if user is None or not hmac.compare_digest(user.session_key(), key):
            return None
        return user

    @classmethod
    def get_by_email(cls, email):
        """Silinmemiş kullanıcıyı e-postasıyla (büyük/küçük harf duyarsız) getirir; yoksa None."""
        row = query_one(
            "SELECT " + USER_COLUMNS + " FROM users WHERE lower(email) = lower(%s) AND is_deleted = FALSE",
            (email,),
        )
        return cls(row) if row else None

    @classmethod
    def list_active_admins(cls):
        """Aktif platform yöneticilerini döndürür (güvenlik bildirimleri için)."""
        rows = query_all(
            "SELECT " + USER_COLUMNS + " FROM users WHERE role = %s AND is_active = TRUE AND is_deleted = FALSE "
            "ORDER BY user_id LIMIT 100",
            (ROLE_ADMIN,),
        )
        return [cls(row) for row in rows]

    @classmethod
    def count_active(cls, business_id=None):
        """Silinmemiş kullanıcı sayısı; business_id verilirse yalnızca o işletmeninki."""
        if business_id is None:
            row = query_one("SELECT count(*) AS total FROM users WHERE is_deleted = FALSE")
        else:
            row = query_one(
                "SELECT count(*) AS total FROM users WHERE is_deleted = FALSE AND business_id = %s",
                (business_id,),
            )
        return row["total"]

    def touch_login(self):
        """Son giriş zamanını şimdiye çeker."""
        execute("UPDATE users SET last_login_at = now() WHERE user_id = %s", (self.user_id,))

    def update_theme(self, theme):
        """Tema tercihini (light/dark) kalıcı olarak kaydeder."""
        execute("UPDATE users SET theme = %s, updated_at = now() WHERE user_id = %s", (theme, self.user_id))

    def update_sidebar_collapsed(self, collapsed):
        """Sidebar daraltma tercihini kalıcı olarak kaydeder."""
        execute(
            "UPDATE users SET sidebar_collapsed = %s, updated_at = now() WHERE user_id = %s",
            (bool(collapsed), self.user_id),
        )
