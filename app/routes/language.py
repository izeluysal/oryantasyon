"""Dil seçimi: girişsiz ekranlarda yalnızca çerezi yazar, kullanıcı kaydına dokunmaz."""
from flask import Blueprint, abort, redirect, request

from app.i18n import DESTEKLENEN_DILLER, LANGUAGE_COOKIE

bp = Blueprint("language", __name__)
YEAR_SECONDS = 365 * 24 * 3600


def _safe_path(target):
    """Yönlendirme yalnızca aynı sitenin göreli yoluysa kabul edilir (açık yönlendirme engeli)."""
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return "/"


@bp.route("/dil/<code>")
def set_language(code):
    """Seçilen dili çereze yazıp önceki sayfaya döner."""
    if code not in DESTEKLENEN_DILLER:
        abort(404)
    response = redirect(_safe_path(request.args.get("next")))
    response.set_cookie(LANGUAGE_COOKIE, code, max_age=YEAR_SECONDS, samesite="Lax", secure=bool(request.is_secure))
    return response
