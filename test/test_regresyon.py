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


def _log_id(action, entity_id):
    """Verilen işlem ve kayıt için en son log kimliğini döndürür."""
    from app.db import query_one
    return query_one("SELECT max(userslog_id) AS id FROM userslogs WHERE action = %s AND entity_id = %s",
                     (action, entity_id))["id"]


def test_user_delete_is_soft_and_can_be_restored_from_deleted_report():
    """Korur: fiziksel DELETE yasağı ve geri alma ekranı. Silinen kullanıcı satırı durur, rapordan geri gelir."""
    from app.db import query_one
    with environment() as app:
        business_id = make_business("geri")
        _, admin_email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        victim_id, victim_email = make_user(ROLE_BUSINESS_ADMIN, business_id, name="kurban")
        client = new_client(app)
        client.login(admin_email)
        assert client.ajax("/ayarlar/kullanicilar/{}/sil".format(victim_id)).get_json()["ok"] is True
        assert query_one("SELECT is_deleted FROM users WHERE user_id = %s", (victim_id,))["is_deleted"] is True
        assert victim_email not in client.get("/ayarlar/kullanicilar/veri").get_json()["html"]
        log_id = _log_id("user_delete", victim_id)
        assert "__test__kurban" in client.get("/silinme-raporu/veri").get_json()["html"]
        detail = client.get("/silinme-raporu/{}/detay".format(log_id)).get_json()
        assert detail["changes"] == [{"column": "is_deleted", "old": False, "new": True}]
        assert client.ajax("/silinme-raporu/{}/geri-yukle".format(log_id), token_from="/silinme-raporu"
                           ).get_json()["ok"] is True
        assert query_one("SELECT is_deleted FROM users WHERE user_id = %s", (victim_id,))["is_deleted"] is False


def test_restore_is_refused_when_email_was_taken_meanwhile():
    """Korur: benzersizlik çakışması. Silinen kaydın e-postası başkasına geçtiyse geri yükleme reddedilir."""
    from app.db import query_one
    with environment() as app:
        business_id = make_business("cakisma")
        _, admin_email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        victim_id, victim_email = make_user(ROLE_BUSINESS_ADMIN, business_id, name="eski")
        client = new_client(app)
        client.login(admin_email)
        client.ajax("/ayarlar/kullanicilar/{}/sil".format(victim_id))
        form = {"full_name": "__test__yeni", "email": victim_email, "role": ROLE_BUSINESS_ADMIN, "theme": "light",
                "password": "uzunparola1"}
        assert client.ajax("/ayarlar/kullanicilar/yeni", form).get_json()["ok"] is True
        response = client.ajax("/silinme-raporu/{}/geri-yukle".format(_log_id("user_delete", victim_id)),
                               token_from="/silinme-raporu")
        assert response.status_code == 400 and "başka bir aktif kayıtta" in response.get_json()["message"]
        assert query_one("SELECT is_deleted FROM users WHERE user_id = %s", (victim_id,))["is_deleted"] is True


def test_user_cannot_delete_self_or_last_platform_admin():
    """Korur: kendini ve son yöneticiyi silip sistemi kilitleme."""
    from app.db import execute
    with environment() as app:
        user_id, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login(email)
        assert client.ajax("/ayarlar/kullanicilar/{}/sil".format(user_id)).status_code == 400
        # Seed kullanıcısı da aktif yönetici olduğu için, "son yönetici" kuralı tüm yöneticiler pasifken denenir.
        other_id, _ = make_user(ROLE_ADMIN, name="ikinci")
        execute("UPDATE users SET is_active = FALSE WHERE role = 'yonetici' AND user_id NOT IN (%s, %s)",
                (user_id, other_id))
        try:
            execute("UPDATE users SET is_active = FALSE WHERE user_id = %s", (other_id,))
            response = client.ajax("/ayarlar/kullanicilar/{}/sil".format(user_id))
            assert response.status_code == 400
        finally:
            execute("UPDATE users SET is_active = TRUE WHERE role = 'yonetici' AND email NOT LIKE %s", ("__test__%",))


def test_business_delete_cascades_users_and_restore_brings_them_back():
    """Korur: işletme silinince kullanıcıları da soft delete olur; geri yüklemede onlar da döner (log detail)."""
    from app.db import query_one
    with environment() as app:
        business_id = make_business("zincir")
        user_id, _ = make_user(ROLE_BUSINESS_ADMIN, business_id)
        _, admin_email = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login(admin_email)
        assert client.ajax("/isletmeler/{}/sil".format(business_id)).get_json()["ok"] is True
        assert query_one("SELECT is_deleted FROM users WHERE user_id = %s", (user_id,))["is_deleted"] is True
        log_id = _log_id("business_delete", business_id)
        assert client.ajax("/silinme-raporu/{}/geri-yukle".format(log_id), token_from="/silinme-raporu"
                           ).get_json()["ok"] is True
        business_row = query_one("SELECT is_deleted FROM businesses WHERE business_id = %s", (business_id,))
        assert business_row["is_deleted"] is False
        assert query_one("SELECT is_deleted FROM users WHERE user_id = %s", (user_id,))["is_deleted"] is False


def test_state_changing_posts_require_csrf_token():
    """Korur: CSRF. Belirteçsiz POST hiçbir kayıt oluşturmaz (AJAX'a JSON 400 döner)."""
    from app.db import query_one
    with environment() as app:
        _, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login(email)
        response = client.request("post", "/isletmeler/yeni", data={"business_name": "__test__csrf",
                                                                     "publish_url": "csrf.example.com"},
                                  headers={"X-Requested-With": "XMLHttpRequest"})
        assert response.status_code == 400 and response.get_json()["ok"] is False
        assert query_one("SELECT 1 AS found FROM businesses WHERE business_name = %s", ("__test__csrf",)) is None


def test_business_publish_url_must_be_unique_and_valid():
    """Korur: yinelenen yayın adresi ve geçersiz adres reddedilir."""
    with environment() as app:
        _, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login(email)
        good = {"business_name": "__test__a", "publish_url": "test-same.example.com"}
        assert client.ajax("/isletmeler/yeni", good).get_json()["ok"] is True
        duplicate = client.ajax("/isletmeler/yeni", dict(good, business_name="__test__b"))
        assert duplicate.status_code == 400
        invalid = client.ajax("/isletmeler/yeni", {"business_name": "__test__c", "publish_url": "bosluk var"})
        assert invalid.status_code == 400


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
