"""Aktivite logu: userslogs tablosuna kayıt (yalnızca-ekleme)."""
import json
import logging

import psycopg2
from flask import has_request_context, request

from app.db import execute

logger = logging.getLogger(__name__)


class UsersLog:
    """userslogs tablosuna önemli işlemleri yazar."""

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
