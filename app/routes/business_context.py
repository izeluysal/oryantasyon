"""İşletme simülasyonu: platform yöneticisinin bir işletmenin bağlamında görüntülemesi."""
from flask import Blueprint, abort, flash, redirect, request, session, url_for
from flask_login import current_user, login_required

from app.helpers.roles import ROLE_ADMIN
from app.i18n import t
from app.models.business import Business
from app.models.userslog import UsersLog

bp = Blueprint("business_context", __name__)


def _require_platform_admin():
    """Yalnızca platform yöneticisi simülasyona girebilir; sunucu tarafında zorlanır."""
    if current_user.role != ROLE_ADMIN:
        abort(403)


@bp.route("/isletme-sec", methods=["POST"])
@login_required
def select_business():
    """Seçilen işletmeyi sunucu tarafı oturuma yazar (kullanıcının gerçek business_id'si değişmez)."""
    _require_platform_admin()
    business_id = request.form.get("business_id", type=int)
    business = Business.get_by_id(business_id) if business_id else None
    if business is None or not business.is_accessible:
        flash(t("business.not_found"), "warning")
        return redirect(url_for("dashboard.index"))
    session["selected_business_id"] = business.business_id
    UsersLog.record("business_enter", user_id=current_user.user_id, business_id=business.business_id,
                    entity_type="business", entity_id=business.business_id)
    return redirect(url_for("dashboard.index"))


@bp.route("/isletme-cikis", methods=["POST"])
@login_required
def leave_business():
    """Simülasyondan çıkar; yönetici kendi platform görünümüne döner."""
    _require_platform_admin()
    left_id = session.pop("selected_business_id", None)
    if left_id:
        UsersLog.record("business_leave", user_id=current_user.user_id, business_id=left_id,
                        entity_type="business", entity_id=left_id)
    return redirect(url_for("dashboard.index"))
