"""Uygulama fabrikası: yapılandırma, eklentiler, blueprint kayıtları ve hata yakalayıcılar."""
import json
import logging
import os
import secrets
from datetime import timedelta

import psycopg2
from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, logout_user
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from app import db
from app.helpers import format as formatting
from app.helpers.roles import ROLE_ADMIN
from app.i18n import (
    DIL_BILGILERI,
    LANGUAGE_COOKIE,
    VARSAYILAN_DIL,
    cevirileri_yukle,
    resolve_anonymous_language,
    t,
)
from app.menu import visible_menu
from app.models.business import Business
from app.models.error_log import ErrorLog
from app.models.user import User
from app.paths import CONFIG_PATH, FILES_DIR, IMAGES_DIR, VERSION_PATH

logger = logging.getLogger(__name__)

SECRET_PLACEHOLDERS = ("", "your-secret-key")
CSRF_TIME_LIMIT_SECONDS = 8 * 60 * 60
REMEMBER_DAYS = 30
SIDEBAR_COOKIE = "sidebar_collapsed"
DB_ERRORS = (psycopg2.OperationalError, psycopg2.InterfaceError)

login_manager = LoginManager()
csrf = CSRFProtect()


def _load_config():
    """config.json'u okur; secret_key boş veya placeholder ise üretip dosyaya geri yazar."""
    with open(CONFIG_PATH, encoding="utf-8") as config_file:
        config = json.load(config_file)
    flask_settings = config.setdefault("flask", {})
    if flask_settings.get("secret_key", "") in SECRET_PLACEHOLDERS:
        flask_settings["secret_key"] = secrets.token_hex(32)
        with open(CONFIG_PATH, "w", encoding="utf-8", newline="\n") as config_file:
            json.dump(config, config_file, indent=2)
            config_file.write("\n")
        logger.info("Flask secret_key üretildi ve config.json'a yazıldı")
    return config


def _read_version():
    """version.txt içindeki sürüm numarasını bir kez okur."""
    try:
        with open(VERSION_PATH, encoding="utf-8") as version_file:
            return version_file.read().strip()
    except OSError:
        return "?"


def _is_ajax():
    """İstek AJAX mı (JSON hata yanıtı verilmeli mi)?"""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json


def _safe_referrer():
    """Yalnızca aynı host'a ait önceki sayfayı döndürür (açık yönlendirmeyi önler)."""
    referrer = request.referrer or ""
    return referrer if referrer.startswith(request.host_url) else None


def create_app():
    """Flask uygulamasını kurar ve döndürür."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = _load_config()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    secure = config.get("container", {}).get("publish_address", "").startswith("https")
    app.config.update(
        SECRET_KEY=config["flask"]["secret_key"],
        WTF_CSRF_TIME_LIMIT=CSRF_TIME_LIMIT_SECONDS,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=secure,
        REMEMBER_COOKIE_DURATION=timedelta(days=REMEMBER_DAYS),
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_SECURE=secure,
        APP_VERSION=_read_version(),
        COOKIE_SECURE=secure,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    )
    for directory in (FILES_DIR, IMAGES_DIR):
        os.makedirs(directory, exist_ok=True)

    db.init_pool(config["postgres"])
    cevirileri_yukle()
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.user_loader(User.get_by_session_id)

    _register_blueprints(app)
    _register_context(app)
    _register_error_handlers(app)
    _seed(app)
    return app


def _register_blueprints(app):
    """Tüm route blueprint'lerini kaydeder."""
    from app.routes import auth, business_context, businesses, dashboard, deleted_report, language, settings

    for module in (auth, dashboard, settings, business_context, language, businesses, deleted_report):
        app.register_blueprint(module.bp)


def _seed(app):
    """Varsayılan veriyi oluşturur; veritabanı kapalıysa çökmeden ilk isteği bekler."""
    try:
        db.seed_defaults()
    except DB_ERRORS as error:
        logger.error("Açılışta veritabanına bağlanılamadı, ilk istekte yeniden denenecek: %s", error)


def _register_context(app):
    """Her istek için dil, işletme bağlamı, şablon değişkenleri ve filtreleri tanımlar."""
    app.jinja_env.globals["t"] = t
    app.jinja_env.filters.update(
        tarih=formatting.tarih,
        tarih_saat=formatting.tarih_saat,
        sayi=formatting.sayi,
    )

    @app.before_request
    def load_request_context():
        """Dili ve işletme bağlamını çözer; erişimi kapanan işletmenin kullanıcısını çıkarır."""
        g.dil = resolve_anonymous_language()
        g.business = None
        g.business_id = None
        g.sidebar_collapsed = request.cookies.get(SIDEBAR_COOKIE) == "1"
        if request.endpoint == "static" or not current_user.is_authenticated:
            return None
        g.dil = current_user.language
        if SIDEBAR_COOKIE not in request.cookies:
            g.sidebar_collapsed = bool(current_user.sidebar_collapsed)
        if current_user.business_id is not None:
            business = Business.get_by_id(current_user.business_id)
            if business is None or not business.is_accessible:
                logout_user()
                session.clear()
                flash(t("auth.business_closed"), "warning")
                return redirect(url_for("auth.login"))
            g.business, g.business_id = business, business.business_id
        elif session.get("selected_business_id"):
            # Session'daki seçim her istekte yeniden doğrulanır; süresiz güvenilmez.
            business = Business.get_by_id(session["selected_business_id"])
            if business is None or not business.is_accessible:
                session.pop("selected_business_id", None)
            else:
                g.business, g.business_id = business, business.business_id
        return None

    @app.context_processor
    def inject_template_context():
        """Şablonlara sürüm, dil bilgisi, menü ve seçilebilir işletmeleri geçirir."""
        language = getattr(g, "dil", VARSAYILAN_DIL)
        context = {
            "app_version": app.config["APP_VERSION"],
            "aktif_dil": language,
            "yerel_ayar": DIL_BILGILERI[language]["yerel_ayar"],
            "diller": DIL_BILGILERI,
            "business": getattr(g, "business", None),
            "sidebar_collapsed": getattr(g, "sidebar_collapsed", False),
            "menu_items": [],
            "selectable_businesses": [],
        }
        try:
            if current_user.is_authenticated and request.endpoint != "static":
                context["menu_items"] = visible_menu(current_user.role)
                if current_user.role == ROLE_ADMIN:
                    context["selectable_businesses"] = Business.list_selectable()
        except DB_ERRORS:
            # DB kesintisinde hata sayfası da render edilebilmeli; menü verisi olmadan devam edilir.
            logger.warning("Şablon bağlamı veritabanına erişilemediği için eksik kuruldu")
        return context

    @app.after_request
    def set_language_cookie(response):
        """Dil çerezini (önbellek) yazar; doğruluk kaynağı veritabanıdır."""
        language = getattr(g, "dil", None)
        if language and request.cookies.get(LANGUAGE_COOKIE) != language and request.endpoint != "static":
            response.set_cookie(LANGUAGE_COOKIE, language, max_age=365 * 24 * 3600, samesite="Lax",
                                secure=app.config["COOKIE_SECURE"])
        return response


def _register_error_handlers(app):
    """Merkezi hata yakalayıcılar: DB kesintisi, CSRF, 403, 404, 500."""

    @app.errorhandler(psycopg2.OperationalError)
    @app.errorhandler(psycopg2.InterfaceError)
    def handle_db_down(error):
        """Veritabanına erişilemediğinde bağımsız 503 sayfası gösterir; hata önce dosyaya yazılır."""
        logger.error("Veritabanı bağlantı hatası: %s", error)
        ErrorLog.write_to_file(503, request.path, "{}: {}".format(type(error).__name__, error), request.remote_addr)
        return render_template("errors/db_down.html"), 503

    @app.errorhandler(CSRFError)
    def handle_csrf(error):
        """Süresi dolmuş/eksik CSRF belirtecinde kullanıcı dostu yanıt verir."""
        message = t("error.csrf")
        if _is_ajax():
            return jsonify(ok=False, message=message), 400
        flash(message, "warning")
        target = _safe_referrer()
        if target:
            return redirect(target)
        return redirect(url_for("auth.login") if not current_user.is_authenticated else url_for("dashboard.index"))

    @app.errorhandler(403)
    def handle_forbidden(error):
        """Yetkisiz erişim."""
        if _is_ajax():
            return jsonify(ok=False, message=t("error.403.message")), 403
        return render_template("errors/error.html", code=403), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        """Bulunamayan sayfa."""
        if _is_ajax():
            return jsonify(ok=False, message=t("error.404.message")), 404
        return render_template("errors/error.html", code=404), 404

    @app.errorhandler(500)
    def handle_server_error(error):
        """Beklenmeyen hata: error_log'a yazılır, kullanıcıya teknik ayrıntı gösterilmez."""
        reason = repr(getattr(error, "original_exception", error))
        user_id = current_user.user_id if current_user.is_authenticated else None
        ErrorLog.record(500, request.path, reason, request.remote_addr, user_id)
        if _is_ajax():
            return jsonify(ok=False, message=t("error.500.message")), 500
        return render_template("errors/error.html", code=500), 500
