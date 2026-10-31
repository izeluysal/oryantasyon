"""Kişisel tercihler: tema ve sidebar durumu (AJAX uçları)."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.i18n import t

bp = Blueprint("settings", __name__, url_prefix="/ayarlar")

THEMES = ("light", "dark")
SIDEBAR_COOKIE = "sidebar_collapsed"
YEAR_SECONDS = 365 * 24 * 3600


@bp.route("/tema", methods=["POST"])
@login_required
def set_theme():
    """Tema tercihini (light/dark) kullanıcı kaydına yazar."""
    theme = request.form.get("theme", "")
    if theme not in THEMES:
        return jsonify(ok=False, message=t("error.invalid_value")), 400
    current_user.update_theme(theme)
    return jsonify(ok=True)


@bp.route("/sidebar", methods=["POST"])
@login_required
def set_sidebar():
    """Sidebar daraltma tercihini DB'ye yazar ve aynı yanıtta çerezi günceller."""
    collapsed = request.form.get("collapsed") == "1"
    current_user.update_sidebar_collapsed(collapsed)
    response = jsonify(ok=True)
    response.set_cookie(SIDEBAR_COOKIE, "1" if collapsed else "0", max_age=YEAR_SECONDS, samesite="Lax",
                        secure=bool(request.is_secure))
    return response
