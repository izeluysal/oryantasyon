"""PostgreSQL bağlantı havuzu, sorgu yardımcıları ve varsayılan veri seed'i."""
import logging
import threading
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)

MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 10
DEFAULT_ADMIN_EMAIL = "basar@ecesoft.com.tr"
DEFAULT_ADMIN_PASSWORD = "Test1234!"

_pool = None
_pool_settings = None
_pool_lock = threading.Lock()


def init_pool(settings):
    """Bağlantı ayarlarını saklar; havuz ilk kullanımda (tembel) kurulur."""
    global _pool_settings
    _pool_settings = settings


def _create_pool():
    """Ayarlardan yeni bir ThreadedConnectionPool kurar."""
    return pool.ThreadedConnectionPool(
        MIN_CONNECTIONS,
        MAX_CONNECTIONS,
        host=_pool_settings["host"],
        port=_pool_settings["port"],
        user=_pool_settings["user"],
        password=_pool_settings["password"],
        dbname=_pool_settings["database"],
        connect_timeout=5,
    )


def _acquire():
    """Havuzdan canlı bir bağlantı alır; ölü bağlantıyı atar, havuz bozuksa yeniden kurar."""
    global _pool
    with _pool_lock:
        if _pool is None:
            _pool = _create_pool()
    for attempt in range(2):
        connection = _pool.getconn()
        try:
            # Pre-ping: ölü bağlantı route'un ortasında patlamasın.
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            connection.rollback()
            return connection
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            _pool.putconn(connection, close=True)
            if attempt == 1:
                with _pool_lock:
                    _pool = None
                raise
    raise psycopg2.OperationalError("Bağlantı alınamadı")


def _release(connection):
    """Bağlantıyı havuza geri verir; kapanmış bağlantı havuza girmez."""
    if _pool is None:
        return
    _pool.putconn(connection, close=bool(connection.closed))


@contextmanager
def get_cursor(commit=True):
    """Havuzdan bağlantı alıp RealDictCursor verir; başarıda commit, hatada rollback yapar."""
    connection = _acquire()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
        if commit:
            connection.commit()
    except Exception:
        if not connection.closed:
            connection.rollback()
        raise
    finally:
        _release(connection)


def query_all(sql, params=None):
    """SELECT sorgusunun tüm satırlarını sözlük listesi olarak döndürür (boşsa boş liste)."""
    with get_cursor(commit=False) as cursor:
        cursor.execute(sql, params)
        return list(cursor.fetchall())


def query_one(sql, params=None):
    """SELECT sorgusunun ilk satırını sözlük olarak döndürür; satır yoksa None."""
    with get_cursor(commit=False) as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def execute(sql, params=None):
    """INSERT/UPDATE çalıştırır; RETURNING varsa ilk satırı, yoksa etkilenen satır sayısını döndürür."""
    with get_cursor() as cursor:
        cursor.execute(sql, params)
        if cursor.description is not None:
            return cursor.fetchone()
        return cursor.rowcount


def seed_defaults():
    """Hiç kullanıcı yoksa varsayılan platform yöneticisini oluşturur (bir kerelik)."""
    row = query_one("SELECT count(*) AS total FROM users")
    if row["total"] > 0:
        return
    execute(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'yonetici')",
        ("Platform Yöneticisi", DEFAULT_ADMIN_EMAIL, generate_password_hash(DEFAULT_ADMIN_PASSWORD)),
    )
    logger.info("Varsayılan platform yöneticisi oluşturuldu: %s", DEFAULT_ADMIN_EMAIL)
