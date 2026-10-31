"""İşletmeler yönetim ekranı: yalnızca platform yöneticisi (liste, ekle, düzenle, durum, sil, Excel)."""
from flask import Blueprint, Response, abort, jsonify, render_template, request
from flask_login import current_user, login_required

from app.helpers.excel import XLSX_MIMETYPE, excel_olustur
from app.helpers.permissions import can
from app.helpers.responses import page_count, page_number, respond
from app.helpers.validation import validate_business_form
from app.i18n import t
from app.models.business import Business
from app.models.userslog import UsersLog

bp = Blueprint("businesses", __name__, url_prefix="/isletmeler")
STATUS_FILTERS = ("active", "passive")


def _require_manage():
    """İşletme yönetimi yalnızca platform yöneticisine açıktır; sunucu tarafında zorlanır."""
    if not can(current_user, "business.manage"):
        abort(403)


def _log(action, business_id, detail=None):
    """İşletme işlemini aktivite loguna yazar."""
    UsersLog.record(action, user_id=current_user.user_id, business_id=business_id, entity_type="business",
                    entity_id=business_id, detail=detail)


def _filters():
    """Liste ve Excel ucunun ortak filtre okuması; geçersiz değer yok sayılır."""
    status = request.args.get("status")
    return request.args.get("q", "").strip()[:100], status if status in STATUS_FILTERS else None


@bp.route("")
@login_required
def index():
    """İşletmeler ekranı: sayaç kartları, filtreli tablo ve ekle/düzenle modalları."""
    _require_manage()
    return render_template("businesses/index.html", summary=Business.summary())


@bp.route("/veri")
@login_required
def data():
    """Filtrelenmiş liste (HTML satırları) ve sayaç özeti; her yanıtta sayılar tazelenir."""
    _require_manage()
    query, status = _filters()
    rows, total = Business.list_page(query, status, page_number())
    html = render_template("businesses/_rows.html", rows=rows)
    return jsonify(html=html, total=total, pages=page_count(total), ozet=Business.summary())


@bp.route("/excel")
@login_required
def export():
    """Ekrandaki filtrelerle işletme listesini Excel olarak indirir."""
    _require_manage()
    query, status = _filters()
    rows, _ = Business.list_page(query, status, 1)
    headers = [t("business.field.name"), t("business.field.publish_url"), t("common.status"),
               t("business.field.users"), t("common.created_at")]
    body = [[row["business_name"], row["publish_url"],
             t("common.active") if row["is_active"] else t("common.passive"), row["user_count"], row["created_at"]]
            for row in rows]
    return Response(excel_olustur(headers, body, t("nav.businesses")), mimetype=XLSX_MIMETYPE,
                    headers={"Content-Disposition": "attachment; filename=isletmeler.xlsx"})


@bp.route("/yeni", methods=["POST"])
@login_required
def create():
    """Yeni işletme: yalnızca ad ve yayın adresi (kullanıcılar Ayarlar > Kullanıcılar'dan eklenir)."""
    _require_manage()
    values, error = validate_business_form(request.form)
    if error:
        return respond(False, t(error), "businesses.index")
    if Business.publish_url_taken(values["publish_url"]):
        return respond(False, t("business.error.publish_url_taken"), "businesses.index")
    business_id = Business.create(values["business_name"], values["publish_url"])
    _log("business_create", business_id, {"name": values["business_name"]})
    return respond(True, t("business.created"), "businesses.index")


@bp.route("/<int:business_id>/duzenle", methods=["POST"])
@login_required
def update(business_id):
    """İşletmenin adını ve yayın adresini günceller."""
    _require_manage()
    business = Business.get_by_id(business_id) or abort(404)
    values, error = validate_business_form(request.form)
    if error:
        return respond(False, t(error), "businesses.index")
    if Business.publish_url_taken(values["publish_url"], business_id):
        return respond(False, t("business.error.publish_url_taken"), "businesses.index")
    changes = business.update(values["business_name"], values["publish_url"])
    _log("business_update", business_id, {"name": values["business_name"], "changes": changes})
    return respond(True, t("business.updated"), "businesses.index")


@bp.route("/<int:business_id>/durum", methods=["POST"])
@login_required
def toggle_status(business_id):
    """İşletmeyi aktif/pasif yapar; pasif işletmenin kullanıcılarının açık oturumu sonlanır."""
    _require_manage()
    business = Business.get_by_id(business_id) or abort(404)
    new_state = not business.is_active
    business.set_active(new_state)
    _log("business_update", business_id, {"name": business.business_name,
                                          "changes": [{"column": "is_active", "old": business.is_active,
                                                       "new": new_state}]})
    return respond(True, t("business.status_changed"), "businesses.index")


@bp.route("/<int:business_id>/sil", methods=["POST"])
@login_required
def delete(business_id):
    """İşletmeyi ve kullanıcılarını soft delete yapar; birlikte silinenler log'a yazılır (geri yükleme için)."""
    _require_manage()
    business = Business.get_by_id(business_id) or abort(404)
    user_ids = business.soft_delete()
    _log("business_delete", business_id, {"name": business.business_name, "cascade_user_ids": user_ids,
                                          "changes": [{"column": "is_deleted", "old": False, "new": True}]})
    return respond(True, t("business.deleted"), "businesses.index")
