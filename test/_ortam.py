"""Test ortamı: gerçek veritabanına yazar, fixture'ları `__test__` önekiyle işaretler ve yalnızca onu temizler."""
import itertools
import os
import re
import sys
from contextlib import contextmanager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from werkzeug.security import generate_password_hash  # noqa: E402

from app import create_app  # noqa: E402
from app.db import execute, get_cursor, query_one  # noqa: E402

PREFIX = "__test__"
TEST_PASSWORD = "Test-Parola-1"
# IP tabloları e-posta öneki taşımadığı için test trafiği TEST-NET-3 aralığına (RFC 5737) sabitlenir.
TEST_IP_PREFIX = "203.0.113."
_counter = itertools.count(1)
CSRF_PATTERN = re.compile(r'name="csrf_token" value="([^"]+)"')


def cleanup():
    """Önekli tüm test verisini tek bağlantı ve tek transaction içinde siler."""
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM training_answers WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE %s)",
                       (PREFIX + "%",))
        cursor.execute("DELETE FROM training_progress WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE %s)",
                       (PREFIX + "%",))
        cursor.execute("DELETE FROM userslogs WHERE user_id IN (SELECT user_id FROM users WHERE email LIKE %s)",
                       (PREFIX + "%",))
        cursor.execute("DELETE FROM userslogs WHERE business_id IN "
                       "(SELECT business_id FROM businesses WHERE business_name LIKE %s)", (PREFIX + "%",))
        cursor.execute("DELETE FROM login_attempts WHERE email LIKE %s OR ip_address LIKE %s",
                       (PREFIX + "%", TEST_IP_PREFIX + "%"))
        cursor.execute("DELETE FROM ip_blocks WHERE ip_address LIKE %s", (TEST_IP_PREFIX + "%",))
        cursor.execute("DELETE FROM error_log WHERE url LIKE %s", ("/" + PREFIX + "%",))
        cursor.execute("UPDATE businesses SET business_admin_user_id = NULL WHERE business_name LIKE %s",
                       (PREFIX + "%",))
        cursor.execute("DELETE FROM config WHERE business_id IN "
                       "(SELECT business_id FROM businesses WHERE business_name LIKE %s)", (PREFIX + "%",))
        cursor.execute("DELETE FROM users WHERE email LIKE %s", (PREFIX + "%",))
        cursor.execute("DELETE FROM businesses WHERE business_name LIKE %s", (PREFIX + "%",))


def make_business(name="isletme", active=True):
    """Önekli bir işletme oluşturur; business_id döndürür."""
    number = next(_counter)
    row = execute(
        "INSERT INTO businesses (business_name, publish_url, is_active) VALUES (%s, %s, %s) RETURNING business_id",
        ("{}{}_{}".format(PREFIX, name, number), "{}{}-{}.example.com".format(PREFIX, name, number), active),
    )
    return row["business_id"]


def make_user(role, business_id=None, name="kullanici", active=True):
    """Önekli bir kullanıcı oluşturur; (user_id, email) döndürür."""
    number = next(_counter)
    email = "{}{}{}@example.com".format(PREFIX, name, number)
    row = execute(
        "INSERT INTO users (business_id, full_name, email, password_hash, role, is_active) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING user_id",
        (business_id, PREFIX + name, email, generate_password_hash(TEST_PASSWORD), role, active),
    )
    return row["user_id"], email


class Client:
    """Gerçek CSRF doğrulamasıyla çalışan test istemcisi (CSRF devre dışı bırakılmaz)."""

    def __init__(self, app, ip):
        self.http = app.test_client()
        self.ip = ip

    def request(self, method, path, **kwargs):
        """Test IP'sini X-Forwarded-For ile vererek istek yapar."""
        headers = kwargs.pop("headers", {})
        headers["X-Forwarded-For"] = self.ip
        return getattr(self.http, method)(path, headers=headers, **kwargs)

    def get(self, path, **kwargs):
        """GET isteği."""
        return self.request("get", path, **kwargs)

    def token(self, path="/auth/login"):
        """Verilen sayfadan CSRF belirtecini okur."""
        match = CSRF_PATTERN.search(self.get(path).get_data(as_text=True))
        return match.group(1) if match else ""

    def post(self, path, data=None, token_from="/auth/login", **kwargs):
        """CSRF belirteci eklenmiş POST isteği."""
        data = dict(data or {})
        data.setdefault("csrf_token", self.token(token_from))
        return self.request("post", path, data=data, **kwargs)

    def ajax(self, path, data=None, token_from="/dashboard"):
        """AJAX (XHR) POST: CSRF belirteci başlıkla gönderilir; yanıt nesnesini döndürür (JSON: .get_json())."""
        headers = {"X-CSRFToken": self.token(token_from), "X-Requested-With": "XMLHttpRequest"}
        return self.request("post", path, data=data or {}, headers=headers)

    def login(self, email, password=TEST_PASSWORD):
        """Giriş yapar ve yanıtı döndürür."""
        return self.post("/auth/login", {"email": email, "password": password})


_ip_counter = itertools.count(10)


def new_client(app):
    """Her test için benzersiz test IP'li istemci döndürür (IP bloğu testler arasında sızmasın)."""
    return Client(app, TEST_IP_PREFIX + str(next(_ip_counter)))


@contextmanager
def environment():
    """Uygulamayı kurar, test verisini temizler; çıkışta (istisna olsa bile) tekrar temizler."""
    app = create_app()
    cleanup()
    try:
        yield app
    finally:
        cleanup()


def database_reachable():
    """Veritabanına bağlanılabiliyor mu (çalıştırıcı başlamadan önce tek mesajla bildirir)."""
    try:
        app = create_app()
        with app.app_context():
            query_one("SELECT 1 AS ok")
        return True
    except Exception as error:  # noqa: BLE001 - tek ve anlaşılır bir mesaj için tüm bağlantı hataları
        print("Veritabanina baglanilamadi:", error)
        return False
