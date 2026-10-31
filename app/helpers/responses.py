"""AJAX/normal istek yanıtları: XHR'a JSON, doğrudan form gönderimine flash + redirect."""
import math

from flask import flash, jsonify, redirect, request, url_for

from app.db import PER_PAGE


def wants_json():
    """İstek XHR/JSON mu?"""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json


def respond(ok, message, fallback_endpoint, status=None, **extra):
    """İşlem sonucunu istek türüne göre döndürür (varsayılan: AJAX JSON, yedek: flash + redirect)."""
    if wants_json():
        return jsonify(ok=ok, message=message, **extra), status or (200 if ok else 400)
    flash(message, "success" if ok else "danger")
    return redirect(url_for(fallback_endpoint))


def page_number():
    """Sorgu parametresinden sayfa numarasını (en az 1) okur."""
    return max(request.args.get("page", 1, type=int) or 1, 1)


def page_count(total):
    """Toplam kayıttan sayfa sayısını hesaplar (en az 1)."""
    return max(int(math.ceil(total / PER_PAGE)), 1)
