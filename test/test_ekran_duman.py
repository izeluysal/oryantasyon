"""Duman testi: ekranlar hata vermeden açılır."""
from _ortam import environment, make_business, make_user, new_client
from app.helpers.roles import ALL_ROLES, ROLE_ADMIN


def test_login_page_and_static_assets_open():
    """Giriş ekranı ve yerel (CDN'siz) vendor dosyaları açılır; sayfada CDN adresi bulunmaz."""
    with environment() as app:
        client = new_client(app)
        page = client.get("/auth/login")
        html = page.get_data(as_text=True)
        assert page.status_code == 200
        assert "cdn." not in html and "googleapis" not in html
        for asset in ("/static/vendor/bootstrap/css/bootstrap.min.css", "/static/vendor/roboto/roboto-latin.woff2",
                      "/static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff2", "/static/css/style.css",
                      "/static/favicon.ico"):
            assert client.get(asset).status_code == 200, asset


def test_dashboard_opens_for_every_role():
    """Dashboard her rol için açılır ve sürüm numarası sidebar'da görünür."""
    with environment() as app:
        business_id = make_business("duman")
        version = app.config["APP_VERSION"]
        for role in ALL_ROLES:
            _, email = make_user(role, None if role == ROLE_ADMIN else business_id)
            client = new_client(app)
            client.login(email)
            response = client.get("/dashboard")
            assert response.status_code == 200, role
            assert "v" + version in response.get_data(as_text=True)


def test_error_pages_do_not_expose_internals():
    """404 sayfası bağımsız şablonla döner ve teknik ayrıntı içermez."""
    with environment() as app:
        response = new_client(app).get("/__test__/olmayan-sayfa")
        html = response.get_data(as_text=True)
        assert response.status_code == 404
        assert "Sayfa bulunamadı" in html and "Traceback" not in html


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
