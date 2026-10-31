"""Çok kiracılılık: bir işletmenin verisine başka işletmeden erişilemez."""
from _ortam import environment, make_business, make_user, new_client
from app.helpers.roles import ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER


def test_dashboard_only_counts_own_business():
    """İşletme A kullanıcısının özeti yalnızca A'nın kullanıcılarını sayar, B'ninkini katmaz."""
    with environment() as app:
        business_a, business_b = make_business("a"), make_business("b")
        _, email_a = make_user(ROLE_BUSINESS_ADMIN, business_a)
        make_user(ROLE_BUSINESS_USER, business_a)
        for _ in range(3):
            make_user(ROLE_BUSINESS_USER, business_b)
        client = new_client(app)
        assert client.login(email_a).status_code == 302
        page = client.get("/dashboard").get_data(as_text=True)
        # Kayıtlı kullanıcı sayısı 2 (A'nın); B'nin 3 kullanıcısı katılırsa 5 görünürdü.
        assert '<div class="stat-value">2</div>' in page


def test_business_user_cannot_select_other_business():
    """İşletme kullanıcısı işletme seçme ucunu kullanamaz (403) ve bağlamı değişmez."""
    with environment() as app:
        business_a, business_b = make_business("a"), make_business("b")
        _, email_a = make_user(ROLE_BUSINESS_ADMIN, business_a)
        client = new_client(app)
        client.login(email_a)
        response = client.post("/isletme-sec", {"business_id": business_b}, token_from="/dashboard")
        assert response.status_code == 403
        assert "görüntülüyorsunuz" not in client.get("/dashboard").get_data(as_text=True)


def test_inactive_business_closes_open_session():
    """İşletme pasifleştirildiğinde açık oturum bir sonraki istekte sonlandırılır."""
    from app.db import execute
    with environment() as app:
        business_id = make_business("pasif")
        _, email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        client = new_client(app)
        client.login(email)
        assert client.get("/dashboard").status_code == 200
        execute("UPDATE businesses SET is_active = FALSE WHERE business_id = %s", (business_id,))
        response = client.get("/dashboard")
        assert response.status_code == 302 and "/auth/login" in response.headers["Location"]


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
