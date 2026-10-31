"""Ayarlar: sekmeli sayfa (kullanıcılar, loglar, güvenlik) ve kişisel tercihler (tema, sidebar)."""
from flask import Blueprint, Response, abort, g, jsonify, render_template, request
from flask_login import current_user, login_required

from app.helpers.excel import XLSX_MIMETYPE, excel_olustur
from app.helpers.permissions import can
from app.helpers.responses import page_count, page_number, respond
from app.helpers.roles import ROLE_ADMIN, ROLE_AUDITOR, ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER
from app.helpers.validation import validate_user_form
from app.i18n import t
from app.models.business import Business
from app.models.config import Config
from app.models.error_log import ErrorLog
from app.models.login_attempt import LoginAttempt, validate_settings
from app.models.user import User
from app.models.userslog import UsersLog

bp = Blueprint("settings", __name__, url_prefix="/ayarlar")

THEMES = ("light", "dark")
SIDEBAR_COOKIE = "sidebar_collapsed"
YEAR_SECONDS = 365 * 24 * 3600
STATUS_FILTERS = ("active", "passive")
PLATFORM_ROLES = (ROLE_ADMIN,)
BUSINESS_ROLES = (ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER, ROLE_AUDITOR)


def _scope_business_id():
    """Kullanıcı yönetiminin kapsamı: simülasyondaki/kendi işletmesi, yoksa None (platform kullanıcıları)."""
    return g.business_id


def _allowed_roles():
    """Kapsamda atanabilecek roller: platformda yalnızca yonetici, işletmede işletme rolleri."""
    return BUSINESS_ROLES if _scope_business_id() is not None else PLATFORM_ROLES


def _require(action):
    """Aksiyon yetkisini sunucuda zorlar; kapsam dışıysa 403."""
    if not can(current_user, action, _scope_business_id()):
        abort(403)


def _user_log(action, entity_id, detail):
    """Kullanıcı işlemini aktivite loguna yazar (işlemi yapan: oturumdaki kullanıcı)."""
    UsersLog.record(action, user_id=current_user.user_id, business_id=_scope_business_id(), entity_type="user",
                    entity_id=entity_id, detail=detail)


def _user_filters():
    """Kullanıcı listesi ve Excel ucunun ortak filtre okuması; geçersiz değer yok sayılır."""
    role = request.args.get("role")
    status = request.args.get("status")
    return (request.args.get("q", "").strip()[:100], role if role in _allowed_roles() else None,
            status if status in STATUS_FILTERS else None)


@bp.route("")
@login_required
def index():
    """Ayarlar sayfası: yetkiye göre sekmeler; her sekme kendi partial'ından gelir."""
    tabs = {
        "users": can(current_user, "user.view", _scope_business_id()),
        "action_logs": can(current_user, "log.view", _scope_business_id()),
        "error_logs": can(current_user, "errorlog.view"),
        "security": can(current_user, "security.manage"),
    }
    if not any(tabs.values()):
        abort(403)
    context = {"tabs": tabs, "roles": _allowed_roles(), "summary": User.summary(_scope_business_id())}
    if tabs["security"]:
        context["protection"] = Config.get("login_protection")
        context["blocks"] = LoginAttempt.active_blocks()
    can_write = can(current_user, "user.create", _scope_business_id())
    return render_template("settings/index.html", can_write=can_write,
                           can_export=can(current_user, "user.export", _scope_business_id()), **context)


@bp.route("/kullanicilar/veri")
@login_required
def users_data():
    """Filtrelenmiş kullanıcı satırları (HTML) ve sayaç özeti."""
    _require("user.view")
    query, role, status = _user_filters()
    users, total = User.list_page(_scope_business_id(), query, role, status, page_number())
    html = render_template("settings/_user_rows.html", users=users,
                           can_write=can(current_user, "user.edit", _scope_business_id()))
    return jsonify(html=html, total=total, pages=page_count(total), ozet=User.summary(_scope_business_id()))


@bp.route("/kullanicilar/excel")
@login_required
def users_export():
    """Ekrandaki filtrelerle kullanıcı listesini Excel olarak indirir."""
    _require("user.export")
    query, role, status = _user_filters()
    users, _ = User.list_page(_scope_business_id(), query, role, status, 1)
    headers = [t("user.field.full_name"), t("user.field.email"), t("user.field.phone"), t("user.field.role"),
               t("common.status"), t("user.field.last_login")]
    body = [[u.full_name, u.email, u.row["phone"] or "", t("role." + u.role),
             t("common.active") if u.is_active else t("common.passive"), u.row["last_login_at"]] for u in users]
    return Response(excel_olustur(headers, body, t("user.title")), mimetype=XLSX_MIMETYPE,
                    headers={"Content-Disposition": "attachment; filename=kullanicilar.xlsx"})


@bp.route("/kullanicilar/yeni", methods=["POST"])
@login_required
def user_create():
    """Yeni kullanıcı: business_id her zaman kapsamdan gelir, formdan alınmaz."""
    _require("user.create")
    values, error = validate_user_form(request.form, require_password=True)
    if not error and values["role"] not in _allowed_roles():
        error = "validation.role_invalid"
    if not error and User.email_taken(values["email"]):
        error = "user.error.email_taken"
    if error:
        return respond(False, t(error), "settings.index")
    user_id = User.create(_scope_business_id(), values["full_name"], values["email"], values["phone"],
                          values["role"], values["password"], values["theme"])
    if values["role"] == ROLE_BUSINESS_ADMIN:
        Business.get_by_id(_scope_business_id()).assign_admin_if_missing(user_id)
    _user_log("user_create", user_id, {"name": values["full_name"], "role": values["role"]})
    return respond(True, t("user.created"), "settings.index")


@bp.route("/kullanicilar/<int:user_id>/duzenle", methods=["POST"])
@login_required
def user_update(user_id):
    """Kullanıcıyı günceller; şifre boşsa değişmez. Kendi rolünü/durumunu değiştiremez."""
    _require("user.edit")
    target = User.get_in_scope(user_id, _scope_business_id()) or abort(404)
    values, error = validate_user_form(request.form, require_password=False)
    is_active = request.form.get("is_active") == "1"
    is_self = target.user_id == current_user.user_id
    if is_self:
        # Kendini kilitlemeyi önler: rol ve aktiflik değiştirilemez.
        values["role"], is_active = target.role, True
    if not error and values["role"] not in _allowed_roles():
        error = "validation.role_invalid"
    if not error and User.email_taken(values["email"], user_id):
        error = "user.error.email_taken"
    if not error and target.role == ROLE_ADMIN and (not is_active or values["role"] != ROLE_ADMIN) \
            and User.count_active_admins() <= 1:
        error = "user.error.last_admin"
    if error:
        return respond(False, t(error), "settings.index")
    changes = target.update_profile(values["full_name"], values["email"], values["phone"], values["role"],
                                    is_active, values["theme"], values["password"])
    _user_log("user_update", user_id, {"name": values["full_name"], "changes": changes})
    return respond(True, t("user.updated"), "settings.index")


@bp.route("/kullanicilar/<int:user_id>/sil", methods=["POST"])
@login_required
def user_delete(user_id):
    """Kullanıcıyı soft delete yapar; kendini ve son platform yöneticisini silemez (sunucuda zorlanır)."""
    _require("user.delete")
    target = User.get_in_scope(user_id, _scope_business_id()) or abort(404)
    if target.user_id == current_user.user_id:
        return respond(False, t("user.error.delete_self"), "settings.index")
    if target.role == ROLE_ADMIN and User.count_active_admins() <= 1:
        return respond(False, t("user.error.last_admin"), "settings.index")
    target.soft_delete()
    _user_log("user_delete", user_id, {"name": target.full_name,
                                       "changes": [{"column": "is_deleted", "old": False, "new": True}]})
    return respond(True, t("user.deleted"), "settings.index")


@bp.route("/loglar/islem/veri")
@login_required
def action_logs_data():
    """İşlem logları: işletme bağlamındaysa yalnızca o işletmenin, platformda tümü."""
    _require("log.view")
    rows, total = UsersLog.page(_scope_business_id(), request.args.get("q", "").strip()[:100], page_number())
    return jsonify(html=render_template("settings/_action_log_rows.html", rows=rows), total=total,
                   pages=page_count(total))


@bp.route("/loglar/hata/veri")
@login_required
def error_logs_data():
    """Hata logları: yalnızca platform yöneticisi."""
    if not can(current_user, "errorlog.view"):
        abort(403)
    rows, total = ErrorLog.page(request.args.get("q", "").strip()[:100], page_number())
    return jsonify(html=render_template("settings/_error_log_rows.html", rows=rows), total=total,
                   pages=page_count(total))


@bp.route("/guvenlik", methods=["POST"])
@login_required
def security_save():
    """Giriş koruması eşiklerini (aralık doğrulamasıyla) platform geneli olarak kaydeder."""
    if not can(current_user, "security.manage"):
        abort(403)
    try:
        values = validate_settings({
            "enabled": request.form.get("enabled") == "1",
            "max_attempts": request.form.get("max_attempts", ""),
            "block_minutes": request.form.get("block_minutes", ""),
            "window_minutes": request.form.get("window_minutes", ""),
        })
    except (ValueError, KeyError):
        return respond(False, t("security.error.range"), "settings.index")
    old = Config.get("login_protection")
    Config.set("login_protection", values)
    changes = [{"column": key, "old": old.get(key), "new": value} for key, value in values.items()
               if old.get(key) != value]
    UsersLog.record("settings_update", user_id=current_user.user_id, entity_type="login_protection",
                    detail={"changes": changes})
    return respond(True, t("security.saved"), "settings.index")


@bp.route("/guvenlik/blok-kaldir/<int:ip_block_id>", methods=["POST"])
@login_required
def security_lift_block(ip_block_id):
    """Aktif IP bloğunu süresinden önce kaldırır (kayıt silinmez, iz korunur)."""
    if not can(current_user, "security.manage"):
        abort(403)
    LoginAttempt.lift_block(ip_block_id)
    UsersLog.record("ip_block_lift", user_id=current_user.user_id, entity_type="ip_block", entity_id=ip_block_id)
    return respond(True, t("security.block_lifted"), "settings.index")


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
