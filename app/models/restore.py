"""Silinme Raporu geri yükleme: log satırından kaydı doğrulayıp geri getirir."""
from psycopg2 import sql

from app.db import get_cursor
from app.models.userslog import UsersLog

# Geri yüklenebilir kayıt türleri tek haritada tanımlıdır; tablo adı hiçbir zaman istekten veya log'dan üretilmez.
ENTITY_MAP = {
    "user": {"table": "users", "pk": "user_id", "name": "full_name", "unique": "email"},
    "business": {"table": "businesses", "pk": "business_id", "name": "business_name", "unique": "publish_url"},
}


class RestoreError(Exception):
    """Geri yükleme reddedildi; message bir çeviri anahtarıdır."""


def _table(entity):
    """Haritadaki tablo ve kolon adlarını güvenli tanımlayıcı olarak döndürür."""
    return (sql.Identifier(entity["table"]), sql.Identifier(entity["pk"]), sql.Identifier(entity["name"]),
            sql.Identifier(entity["unique"]))


def apply_restore(log_row):
    """Silme log'unun işaret ettiği kaydı geri yükler; adını döndürür.

    Sıra: işlem silme mi, tür haritada mı, kayıt hâlâ silinmiş mi, benzersizlik çakışması var mı.
    İzolasyon (log'un işletmesi kullanıcının erişebildiği kapsamda mı) çağıran route'ta yapılır.
    """
    if not log_row["action"].endswith("_delete"):
        raise RestoreError("deleted.error.not_delete")
    entity = ENTITY_MAP.get(log_row["entity_type"])
    if entity is None:
        raise RestoreError("deleted.error.unsupported")
    table, pk, name, unique = _table(entity)
    with get_cursor() as cursor:
        cursor.execute(
            sql.SQL("SELECT {name} AS record_name, {unique} AS unique_value, is_deleted FROM {table} WHERE {pk} = %s")
            .format(name=name, unique=unique, table=table, pk=pk),
            (log_row["entity_id"],),
        )
        record = cursor.fetchone()
        if record is None:
            raise RestoreError("deleted.error.missing")
        if not record["is_deleted"]:
            raise RestoreError("deleted.error.already_active")
        cursor.execute(
            sql.SQL("SELECT {pk} AS conflict_id FROM {table} WHERE lower({unique}::text) = lower(%s) "
                    "AND is_deleted = FALSE AND {pk} <> %s").format(pk=pk, table=table, unique=unique),
            (record["unique_value"], log_row["entity_id"]),
        )
        if cursor.fetchone():
            raise RestoreError("deleted.error.conflict")
        cursor.execute(
            sql.SQL("UPDATE {table} SET is_deleted = FALSE, updated_at = now() WHERE {pk} = %s")
            .format(table=table, pk=pk),
            (log_row["entity_id"],),
        )
        if log_row["entity_type"] == "business":
            _restore_cascaded_users(cursor, UsersLog.parse_detail(log_row["detail"]).get("cascade_user_ids", []))
    return record["record_name"]


def _restore_cascaded_users(cursor, user_ids):
    """İşletmeyle birlikte silinen kullanıcıları geri getirir; e-postası başkasına geçmiş olanlar atlanır."""
    for user_id in user_ids:
        cursor.execute(
            "UPDATE users SET is_deleted = FALSE, updated_at = now() WHERE user_id = %s AND is_deleted = TRUE "
            "AND NOT EXISTS (SELECT 1 FROM users other WHERE lower(other.email) = lower(users.email) "
            "AND other.is_deleted = FALSE AND other.user_id <> users.user_id)",
            (user_id,),
        )
