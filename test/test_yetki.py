"""Rol ayrıcalıkları: işletme simülasyonu yalnızca platform yöneticisine açıktır."""
from _ortam import environment, make_business, make_user, new_client
from app.helpers.roles import ROLE_ADMIN, ROLE_AUDITOR, ROLE_BUSINESS_ADMIN


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
    """Girişsiz istek korumalı sayfada giriş ekranına yönlenir."""
    with environment() as app:
        response = new_client(app).get("/dashboard")
        assert response.status_code == 302 and "/auth/login" in response.headers["Location"]


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
