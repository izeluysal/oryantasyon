"""Rol ayrıcalıkları ve merkezi yetki (can) kararları; hem engellenen hem meşru akış test edilir."""
from _ortam import environment, make_business, make_user, new_client
from app.db import query_one
from app.helpers.roles import ROLE_ADMIN, ROLE_AUDITOR, ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER


def test_admin_can_enter_and_leave_business():
    """Yönetici işletmeye girince banner görünür, çıkınca kaybolur (meşru akış çalışır)."""
    with environment() as app:
        business_id = make_business("sim")
        _, email = make_user(ROLE_ADMIN)
        client = new_client(app)
        client.login(email)
        response = client.post("/isletme-sec", {"business_id": business_id}, token_from="/dashboard")
        assert response.status_code == 302
        assert "görüntülüyorsunuz" in client.get("/dashboard").get_data(as_text=True)
        client.post("/isletme-cikis", token_from="/dashboard")
        assert "görüntülüyorsunuz" not in client.get("/dashboard").get_data(as_text=True)


def test_non_admin_roles_are_blocked_from_business_select():
    """İşletme yöneticisi ve denetim rolü simülasyon uçlarına giremez (sunucu tarafı 403)."""
    with environment() as app:
        business_id = make_business("yetki")
        for role in (ROLE_BUSINESS_ADMIN, ROLE_AUDITOR):
            _, email = make_user(role, business_id)
            client = new_client(app)
            client.login(email)
            assert client.post("/isletme-sec", {"business_id": business_id}, token_from="/dashboard").status_code == 403
            assert client.post("/isletme-cikis", token_from="/dashboard").status_code == 403


def test_anonymous_is_redirected_to_login():
    """Girişsiz istek korumalı sayfalarda giriş ekranına yönlenir."""
    with environment() as app:
        client = new_client(app)
        for path in ("/dashboard", "/ayarlar", "/isletmeler", "/silinme-raporu"):
            response = client.get(path)
            assert response.status_code == 302 and "/auth/login" in response.headers["Location"], path


def test_business_admin_cannot_use_platform_screens():
    """İşletme yöneticisi İşletmeler, Güvenlik ve Hata Logları uçlarına giremez (menüden gizlemek yetmez)."""
    with environment() as app:
        business_id = make_business("yetki")
        _, email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        client = new_client(app)
        client.login(email)
        assert client.get("/isletmeler").status_code == 403
        assert client.get("/isletmeler/veri").status_code == 403
        new_business = {"business_name": "X", "publish_url": "x.example.com"}
        assert client.ajax("/isletmeler/yeni", new_business).status_code == 403
        assert client.get("/ayarlar/loglar/hata/veri").status_code == 403
        assert client.ajax("/ayarlar/guvenlik", {"max_attempts": "1", "block_minutes": "1", "window_minutes": "1"}
                           ).status_code == 403


def test_auditor_is_read_only_and_business_user_has_no_access():
    """Denetim kullanıcıları görür ama yazamaz; işletme kullanıcısı (ince yetki yok) ayarlara giremez."""
    with environment() as app:
        business_id = make_business("denetim")
        _, auditor = make_user(ROLE_AUDITOR, business_id)
        _, plain = make_user(ROLE_BUSINESS_USER, business_id)
        client = new_client(app)
        client.login(auditor)
        assert client.get("/ayarlar").status_code == 200
        assert client.get("/ayarlar/kullanicilar/veri").status_code == 200
        form = {"full_name": "X", "email": "__test__x@example.com", "role": ROLE_BUSINESS_USER, "theme": "light",
                "password": "uzunparola1"}
        assert client.ajax("/ayarlar/kullanicilar/yeni", form).status_code == 403
        assert client.ajax("/ayarlar/kullanicilar/1/sil").status_code == 403
        other = new_client(app)
        other.login(plain)
        assert other.get("/ayarlar").status_code == 403
        assert other.get("/silinme-raporu").status_code == 403


def test_business_admin_can_manage_own_users():
    """Meşru akış: işletme yöneticisi kendi işletmesinde kullanıcı ekler, düzenler, siler."""
    with environment() as app:
        business_id = make_business("meşru")
        _, email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        client = new_client(app)
        client.login(email)
        form = {"full_name": "__test__ekle", "email": "__test__ekle@example.com", "role": ROLE_BUSINESS_USER,
                "theme": "light", "password": "uzunparola1"}
        assert client.ajax("/ayarlar/kullanicilar/yeni", form).get_json()["ok"] is True
        user_id = query_one("SELECT user_id FROM users WHERE email = %s", ("__test__ekle@example.com",))["user_id"]
        form["full_name"] = "__test__degisti"
        form["is_active"] = "1"
        assert client.ajax("/ayarlar/kullanicilar/{}/duzenle".format(user_id), form).get_json()["ok"] is True
        assert client.ajax("/ayarlar/kullanicilar/{}/sil".format(user_id)).get_json()["ok"] is True
        row = query_one("SELECT full_name, is_deleted FROM users WHERE user_id = %s", (user_id,))
        assert row["full_name"] == "__test__degisti" and row["is_deleted"] is True


def test_business_admin_cannot_create_platform_admin():
    """İşletme bağlamında yönetici rolü atanamaz (rol yükseltme engeli)."""
    with environment() as app:
        business_id = make_business("yukselt")
        _, email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        client = new_client(app)
        client.login(email)
        form = {"full_name": "__test__yon", "email": "__test__yon@example.com", "role": ROLE_ADMIN, "theme": "light",
                "password": "uzunparola1"}
        assert client.ajax("/ayarlar/kullanicilar/yeni", form).status_code == 400
        assert query_one("SELECT user_id FROM users WHERE email = %s", ("__test__yon@example.com",)) is None


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
