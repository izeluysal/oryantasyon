"""Giriş ve çıkış: e-posta + şifre, beni hatırla, başarısız giriş kaydı ve IP bloklama."""
import logging

import psycopg2
from flask import Blueprint, flash, g, make_response, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.i18n import t
from app.models.business import Business
from app.models.login_attempt import (
    REASON_BAD_PASSWORD,
    REASON_INACTIVE_BUSINESS,
    REASON_INACTIVE_USER,
    REASON_UNKNOWN_EMAIL,
    LoginAttempt,
)
from app.models.user import User
from app.models.userslog import UsersLog

logger = logging.getLogger(__name__)
bp = Blueprint("auth", __name__, url_prefix="/auth")

SIDEBAR_COOKIE = "sidebar_collapsed"


def _safe_next(target):
    """Yönlendirme hedefi yalnızca aynı sitenin göreli yoluysa kabul edilir."""
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return None


def _record_failure(ip_address, email, reason):
    """Reddedilen girişi kaydeder ve eşik aşıldıysa bloklar. Hata giriş akışını düşürmez."""
    try:
        LoginAttempt.record(ip_address, email, reason, request.headers.get("User-Agent"))
        if LoginAttempt.evaluate(ip_address):
            UsersLog.record("ip_block", entity_type="ip_block", detail={"ip_address": ip_address})
    except psycopg2.Error as error:
        # Loglama hatası giriş ekranını 500'e düşürmemeli.
        logger.error("Başarısız giriş kaydedilemedi: %s", error)


def _blocked_response(block):
    """Aktif blok varken 429 ve kalan süreyi gösteren giriş sayfası döndürür."""
    minutes = LoginAttempt.minutes_left(block)
    return render_template("auth/login.html", error=t("auth.blocked", count=minutes), email=""), 429


def _reject(email, reason, ip_address):
    """Reddi kaydeder; kullanıcıya hesabın varlığını sızdırmayan tek bir mesaj gösterir."""
    _record_failure(ip_address, email, reason)
    block = LoginAttempt.active_block(ip_address)
    if block:
        return _blocked_response(block)
    return render_template("auth/login.html", error=t("auth.invalid_credentials"), email=email), 401


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Giriş ekranı: yalnızca e-posta, şifre ve 'beni hatırla'."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "GET":
        return render_template("auth/login.html", error=None, email="")

    ip_address = request.remote_addr
    email = request.form.get("email", "").strip()[:255]
    password = request.form.get("password", "")
    # Blok kontrolü şifre doğrulamasından ÖNCE yapılır: bloklu IP'ye deneme hakkı verilmez.
    block = LoginAttempt.active_block(ip_address)
    if block:
        return _blocked_response(block)

    user = User.get_by_email(email) if email else None
    if user is None:
        return _reject(email, REASON_UNKNOWN_EMAIL, ip_address)
    if not user.is_active:
        return _reject(email, REASON_INACTIVE_USER, ip_address)
    if not user.check_password(password):
        return _reject(email, REASON_BAD_PASSWORD, ip_address)
    if user.business_id is not None:
        business = Business.get_by_id(user.business_id)
        if business is None or not business.is_accessible:
            return _reject(email, REASON_INACTIVE_BUSINESS, ip_address)

    session.clear()
    login_user(user, remember=request.form.get("remember") == "1")
    user.touch_login()
    UsersLog.record("login", user_id=user.user_id, business_id=user.business_id, entity_type="user",
                    entity_id=user.user_id)
    response = make_response(redirect(_safe_next(request.args.get("next")) or url_for("dashboard.index")))
    response.set_cookie(SIDEBAR_COOKIE, "1" if user.sidebar_collapsed else "0", max_age=365 * 24 * 3600,
                        samesite="Lax", secure=bool(request.is_secure))
    return response


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Çıkış yalnızca POST ile yapılır (CSRF korumalı); bağlantıya tıklatarak oturum kapatılamaz."""
    UsersLog.record("logout", user_id=current_user.user_id, business_id=g.get("business_id"),
                    entity_type="user", entity_id=current_user.user_id)
    logout_user()
    session.clear()
    flash(t("auth.logged_out"), "success")
    return redirect(url_for("auth.login"))
