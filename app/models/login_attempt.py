"""Başarısız giriş denemeleri ve IP bloklama: login_attempts ve ip_blocks tabloları."""
import logging
import math

from app.db import execute, query_all, query_one
from app.models.config import Config

logger = logging.getLogger(__name__)

# Sebep kodları İngilizce ve ayrıştırılabilirdir (denetimde "neden reddedildi" ayırt edilebilsin).
REASON_BAD_PASSWORD = "bad_password"
REASON_UNKNOWN_EMAIL = "unknown_email"
REASON_INACTIVE_USER = "inactive_user"
REASON_INACTIVE_BUSINESS = "inactive_business"

LIMITS = {"max_attempts": (1, 100), "block_minutes": (1, 1440), "window_minutes": (1, 1440)}


def validate_settings(values):
    """Koruma ayarlarını aralık doğrulamasından geçirir; geçersizse ValueError fırlatır."""
    for name, (low, high) in LIMITS.items():
        number = int(values[name])
        if not low <= number <= high:
            raise ValueError("{} {}-{} aralığında olmalıdır".format(name, low, high))
    return {
        "enabled": bool(values.get("enabled", True)),
        "max_attempts": int(values["max_attempts"]),
        "block_minutes": int(values["block_minutes"]),
        "window_minutes": int(values["window_minutes"]),
    }


class LoginAttempt:
    """Başarısız denemeleri kaydeder, kayan pencerede sayar ve IP bloğu koyar."""

    @staticmethod
    def settings():
        """Koruma ayarlarını config'ten okur (platform geneli)."""
        return Config.get("login_protection")

    @staticmethod
    def record(ip_address, email, reason, user_agent=None):
        """Reddedilen her giriş denemesini kaydeder."""
        execute(
            "INSERT INTO login_attempts (ip_address, email, reason, user_agent) VALUES (%s, %s, %s, %s)",
            (ip_address, (email or "")[:255], reason, (user_agent or "")[:500]),
        )

    @staticmethod
    def active_block(ip_address):
        """IP'nin aktif bloğunu döndürür (blocked_until gelecekte); yoksa None."""
        return query_one(
            "SELECT ip_block_id, blocked_until, "
            "GREATEST(CEIL(EXTRACT(EPOCH FROM (blocked_until - now())) / 60), 1)::int AS minutes_left "
            "FROM ip_blocks WHERE ip_address = %s AND blocked_until > now() "
            "ORDER BY blocked_until DESC LIMIT 1",
            (ip_address,),
        )

    @staticmethod
    def active_blocks():
        """Şu an aktif olan IP bloklarını döndürür (Güvenlik sekmesi listesi)."""
        return query_all(
            "SELECT ip_block_id, ip_address, attempt_count, blocked_until FROM ip_blocks "
            "WHERE blocked_until > now() ORDER BY blocked_until DESC LIMIT 100"
        )

    @staticmethod
    def minutes_left(block):
        """Bloğun kalan süresini dakika olarak döndürür (en az 1)."""
        return max(int(math.ceil(block["minutes_left"])), 1)

    @staticmethod
    def count_recent(ip_address, window_minutes):
        """Kayan pencere içindeki başarısız deneme sayısı."""
        row = query_one(
            "SELECT count(*) AS total FROM login_attempts "
            "WHERE ip_address = %s AND created_at > now() - make_interval(mins => %s)",
            (ip_address, window_minutes),
        )
        return row["total"]

    @staticmethod
    def evaluate(ip_address):
        """Eşik aşıldıysa ve aktif blok yoksa IP'yi bloklar; yeni blok açıldıysa True döndürür."""
        protection = LoginAttempt.settings()
        if not protection.get("enabled", True):
            return False
        if LoginAttempt.active_block(ip_address):
            return False
        total = LoginAttempt.count_recent(ip_address, protection["window_minutes"])
        if total < protection["max_attempts"]:
            return False
        execute(
            "INSERT INTO ip_blocks (ip_address, blocked_until, attempt_count) "
            "VALUES (%s, now() + make_interval(mins => %s), %s)",
            (ip_address, protection["block_minutes"], total),
        )
        logger.warning("IP bloklandı: %s (%s başarısız deneme)", ip_address, total)
        return True

    @staticmethod
    def lift_block(ip_block_id):
        """Bloğu süresinden önce kaldırır: kaydı silmez, blocked_until'i şimdiye çeker."""
        execute("UPDATE ip_blocks SET blocked_until = now() WHERE ip_block_id = %s AND blocked_until > now()",
                (ip_block_id,))
