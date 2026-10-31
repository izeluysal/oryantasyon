"""Silinme Raporu: silme/güncelleme logları, ayrıntı penceresi ve geri yükleme."""
from flask import Blueprint, abort, g, jsonify, render_template, request
from flask_login import current_user, login_required

from app.helpers.permissions import can
from app.helpers.responses import page_count, page_number, respond
from app.helpers.roles import ROLE_ADMIN
from app.i18n import t
from app.models.restore import ENTITY_MAP, RestoreError, apply_restore
from app.models.userslog import UsersLog

bp = Blueprint("deleted_report", __name__, url_prefix="/silinme-raporu")


def _scope_business_id():
    """Raporun kapsamı: işletme bağlamı varsa o işletme; platform görünümünde (yonetici) tümü."""
    return g.business_id


def _require_view():
    """Raporu görme yetkisini sunucuda zorlar."""
    if not can(current_user, "deleted.view", _scope_business_id()):
        abort(403)


@bp.route("")
@login_required
def index():
    """Silinme Raporu ekranı."""
    _require_view()
    can_restore = can(current_user, "deleted.restore", _scope_business_id())
    return render_template("deleted_report/index.html", can_restore=can_restore)


@bp.route("/veri")
@login_required
def data():
    """Silinme/güncelleme kayıtları (HTML satırları)."""
    _require_view()
    rows, total = UsersLog.deleted_page(_scope_business_id(), request.args.get("q", "").strip()[:100],
                                        page_number())
    html = render_template("deleted_report/_rows.html", rows=rows, detail_of=UsersLog.parse_detail,
                           restorable=ENTITY_MAP,
                           can_restore=can(current_user, "deleted.restore", _scope_business_id()))
    return jsonify(html=html, total=total, pages=page_count(total))


@bp.route("/<int:userslog_id>/detay")
@login_required
def detail(userslog_id):
    """İşlemin kolon / eski değer / yeni değer ayrıntısı; görüntüleyenin kapsamıyla sınırlıdır."""
    _require_view()
    log_row = UsersLog.get(userslog_id) or abort(404)
    if current_user.role != ROLE_ADMIN and log_row["business_id"] != current_user.business_id:
        abort(404)
    info = UsersLog.parse_detail(log_row["detail"])
    return jsonify(ok=True, name=info.get("name", ""), changes=info.get("changes", []))


@bp.route("/<int:userslog_id>/geri-yukle", methods=["POST"])
@login_required
def restore(userslog_id):
    """Silinmiş kaydı geri yükler: log, izolasyon, işlem türü, kayıt türü, durum ve benzersizlik doğrulanır."""
    log_row = UsersLog.get(userslog_id) or abort(404)
    # İzolasyon: URL'den gelen log kimliğine güvenilmez; log'un işletmesi kullanıcının kapsamında olmalı.
    # business_id'si NULL olan platform kayıtlarını yalnızca ana kullanıcı geri yükleyebilir.
    if not can(current_user, "deleted.restore", log_row["business_id"]):
        abort(404)
    try:
        name = apply_restore(log_row)
    except RestoreError as error:
        return respond(False, t(str(error)), "deleted_report.index")
    UsersLog.record(log_row["entity_type"] + "_restore", user_id=current_user.user_id,
                    business_id=log_row["business_id"], entity_type=log_row["entity_type"],
                    entity_id=log_row["entity_id"], detail={"name": name, "source_log_id": userslog_id})
    return respond(True, t("deleted.restored", name=name), "deleted_report.index")
