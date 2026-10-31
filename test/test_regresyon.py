"""Geçmişte bulunan veya standartla korunan davranışların geri dönmemesi."""
from _ortam import TEST_PASSWORD, environment, make_business, make_user, new_client
from app.db import execute
from app.helpers.roles import ROLE_ADMIN, ROLE_BUSINESS_ADMIN
from app.models.config import Config


def test_login_message_does_not_leak_account_existence():
    """Korur: hesap sayımı (account enumeration). Bilinmeyen e-posta ve yanlış şifre AYNI mesajı vermeli."""
    with environment() as app:
        _, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        wrong_password = client.login(email, "yanlis").get_data(as_text=True)
        unknown = client.login("__test__yok@example.com", "yanlis").get_data(as_text=True)
        assert "E-posta veya şifre hatalı." in wrong_password
        assert "E-posta veya şifre hatalı." in unknown


def test_ip_is_blocked_after_threshold_and_block_precedes_password_check():
    """Korur: kaba kuvvet. Eşik aşılınca 429; blok varken DOĞRU şifre bile kabul edilmez."""
    with environment() as app:
        _, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        limit = Config.get("login_protection")["max_attempts"]
        for _ in range(limit):
            client.login(email, "yanlis")
        response = client.login(email, TEST_PASSWORD)
        assert response.status_code == 429
        assert "dakika sonra tekrar" in response.get_data(as_text=True)


def test_logout_requires_post_with_csrf():
    """Korur: bağlantıya tıklatarak oturum kapattırma. GET 405, belirteçsiz POST reddedilir."""
    with environment() as app:
        _, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login(email)
        assert client.get("/auth/logout").status_code == 405
        response = client.request("post", "/auth/logout", data={})
        assert response.status_code == 302 and client.get("/dashboard").status_code == 200


def test_password_change_invalidates_open_session():
    """Korur: çalınmış oturum. Şifre değişince açık oturum geçersizleşmeli (oturum anahtarı şifreye bağlı)."""
    from werkzeug.security import generate_password_hash
    with environment() as app:
        user_id, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login(email)
        assert client.get("/dashboard").status_code == 200
        execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (generate_password_hash("yeni"), user_id))
        response = client.get("/dashboard")
        assert response.status_code == 302 and "/auth/login" in response.headers["Location"]


def test_theme_and_sidebar_preferences_are_persisted():
    """Korur: tercihlerin DB'de tutulması (cookie yalnızca önbellek). Tema ve sidebar kalıcı yazılır."""
    from app.db import query_one
    with environment() as app:
        business_id = make_business("tema")
        user_id, email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        client = new_client(app)
        client.login(email)
        token = client.token("/dashboard")
        headers = {"X-CSRFToken": token, "X-Requested-With": "XMLHttpRequest"}
        theme_response = client.request("post", "/ayarlar/tema", data={"theme": "dark"}, headers=dict(headers))
        sidebar_response = client.request("post", "/ayarlar/sidebar", data={"collapsed": "1"}, headers=dict(headers))
        assert theme_response.status_code == 200 and sidebar_response.status_code == 200
        row = query_one("SELECT theme, sidebar_collapsed FROM users WHERE user_id = %s", (user_id,))
        assert row["theme"] == "dark" and row["sidebar_collapsed"] is True
        page = client.get("/dashboard").get_data(as_text=True)
        assert 'data-theme="dark"' in page and "sidebar-collapsed" in page
        invalid = client.request("post", "/ayarlar/tema", data={"theme": "hacker"}, headers=dict(headers))
        assert invalid.status_code == 400


def test_failed_logins_are_recorded_for_every_rejection_branch():
    """Korur: girişin reddedildiği HER dal loglanmalı (yalnızca şifre hatası değil)."""
    from app.db import query_all
    with environment() as app:
        business_id = make_business("kapali", active=False)
        _, inactive_user = make_user(ROLE_BUSINESS_ADMIN, business_id)
        _, passive_user = make_user(ROLE_ADMIN, active=False)
        _, active_user = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login("__test__yok@example.com")
        client.login(passive_user)
        client.login(active_user, "yanlis")
        client.login(inactive_user)
        reasons = {row["reason"] for row in query_all(
            "SELECT reason FROM login_attempts WHERE ip_address = %s", (client.ip,))}
        assert reasons == {"unknown_email", "inactive_user", "bad_password", "inactive_business"}


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
