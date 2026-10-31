"""Aktivite logu: userslogs tablosuna kayıt (yalnızca-ekleme) ve sayfalı sorgulama."""
import json
import logging

import psycopg2
from flask import has_request_context, request

from app.db import PER_PAGE, execute, like_pattern, query_all, query_one

logger = logging.getLogger(__name__)

LOG_SELECT = (
    "SELECT l.userslog_id, l.user_id, l.business_id, l.action, l.entity_type, l.entity_id, l.detail, l.ip_address, "
    "l.created_at, u.full_name AS actor_name, b.business_name, count(*) OVER() AS total_count "
    "FROM userslogs l LEFT JOIN users u ON u.user_id = l.user_id "
    "LEFT JOIN businesses b ON b.business_id = l.business_id "
)


class UsersLog:
    """userslogs tablosuna önemli işlemleri yazar ve okur."""

    @staticmethod
    def record(action, user_id=None, business_id=None, entity_type=None, entity_id=None, detail=None):
        """İşlemi loglar. Log hatası asıl akışı düşürmez; yalnızca loglanır."""
        ip_address = request.remote_addr if has_request_context() else None
        if detail is not None and not isinstance(detail, str):
            detail = json.dumps(detail, ensure_ascii=False, default=str)
        try:
            execute(
                "INSERT INTO userslogs (user_id, business_id, action, entity_type, entity_id, detail, ip_address) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user_id, business_id, action, entity_type, entity_id, detail, ip_address),
            )
        except psycopg2.Error as error:
            logger.error("Aktivite logu yazılamadı (%s): %s", action, error)

    @staticmethod
    def page(business_id, query="", page=1):
        """İşlem loglarını sayfalı döndürür; business_id None ise tüm kayıtlar (yalnızca platform yöneticisi)."""
        where, params = [], []
        if business_id is not None:
            where.append("l.business_id = %s")
            params.append(business_id)
        if query:
            where.append("(l.action ILIKE %s OR u.full_name ILIKE %s OR l.entity_type ILIKE %s)")
            params.extend([like_pattern(query)] * 3)
        params.extend([PER_PAGE, (max(page, 1) - 1) * PER_PAGE])
        rows = query_all(
            LOG_SELECT + ("WHERE " + " AND ".join(where) + " " if where else "")
            + "ORDER BY l.created_at DESC, l.userslog_id DESC LIMIT %s OFFSET %s",
            params,
        )
        return rows, (rows[0]["total_count"] if rows else 0)

    @staticmethod
    def deleted_page(business_id, query="", page=1):
        """Silinme Raporu kaynağı: adı _delete veya _update ile biten işlemler (en yeni üstte)."""
        where = ["(l.action LIKE '%%\\_delete' OR l.action LIKE '%%\\_update')"]
        params = []
        if business_id is not None:
            where.append("l.business_id = %s")
            params.append(business_id)
        if query:
            where.append("(l.action ILIKE %s OR l.entity_type ILIKE %s OR l.detail ILIKE %s)")
            params.extend([like_pattern(query)] * 3)
        params.extend([PER_PAGE, (max(page, 1) - 1) * PER_PAGE])
        rows = query_all(
            LOG_SELECT + "WHERE " + " AND ".join(where)
            + " ORDER BY l.created_at DESC, l.userslog_id DESC LIMIT %s OFFSET %s",
            params,
        )
        return rows, (rows[0]["total_count"] if rows else 0)

    @staticmethod
    def get(userslog_id):
        """Tek log satırını getirir; yoksa None."""
        return query_one(
            "SELECT userslog_id, user_id, business_id, action, entity_type, entity_id, detail, created_at "
            "FROM userslogs WHERE userslog_id = %s",
            (userslog_id,),
        )

    @staticmethod
    def parse_detail(detail):
        """Log detail alanını sözlüğe çevirir; bozuk veya boşsa boş sözlük döner."""
        try:
            value = json.loads(detail) if detail else {}
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}
