"""Çok kiracılılık: bir işletmenin verisine başka işletmeden erişilemez."""
from _ortam import environment, make_business, make_user, new_client
from app.db import execute, query_one
from app.helpers.roles import ROLE_ADMIN, ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER
from app.models.userslog import UsersLog


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
    with environment() as app:
        business_id = make_business("pasif")
        _, email = make_user(ROLE_BUSINESS_ADMIN, business_id)
        client = new_client(app)
        client.login(email)
        assert client.get("/dashboard").status_code == 200
        execute("UPDATE businesses SET is_active = FALSE WHERE business_id = %s", (business_id,))
        response = client.get("/dashboard")
        assert response.status_code == 302 and "/auth/login" in response.headers["Location"]


def test_user_list_is_limited_to_own_business():
    """Kullanıcı listesi ucu başka işletmenin kullanıcısını döndürmez (sorgu seviyesi izolasyon)."""
    with environment() as app:
        business_a, business_b = make_business("a"), make_business("b")
        _, email_a = make_user(ROLE_BUSINESS_ADMIN, business_a, name="aaa")
        _, email_b = make_user(ROLE_BUSINESS_USER, business_b, name="bbb")
        client = new_client(app)
        client.login(email_a)
        data = client.get("/ayarlar/kullanicilar/veri").get_json()
        assert email_a in data["html"] and email_b not in data["html"]
        assert data["total"] == 1 and data["ozet"]["total"] == 1


def test_cannot_edit_or_delete_user_of_other_business():
    """Başka işletmenin kullanıcısı düzenlenemez/silinemez; varlığı sızdırılmaz (404) ve kayıt değişmez."""
    with environment() as app:
        business_a, business_b = make_business("a"), make_business("b")
        _, email_a = make_user(ROLE_BUSINESS_ADMIN, business_a)
        victim_id, victim_email = make_user(ROLE_BUSINESS_USER, business_b)
        client = new_client(app)
        client.login(email_a)
        form = {"full_name": "Ele Gecirilmis", "email": victim_email, "role": ROLE_BUSINESS_USER, "theme": "light"}
        assert client.ajax("/ayarlar/kullanicilar/{}/duzenle".format(victim_id), form).status_code == 404
        assert client.ajax("/ayarlar/kullanicilar/{}/sil".format(victim_id)).status_code == 404
        row = query_one("SELECT full_name, is_deleted FROM users WHERE user_id = %s", (victim_id,))
        assert row["full_name"].startswith("__test__") and row["is_deleted"] is False


def test_new_user_always_belongs_to_own_business_even_if_form_says_otherwise():
    """business_id formdan alınmaz: forma başka işletme kimliği eklense de kullanıcı kendi işletmesine yazılır."""
    with environment() as app:
        business_a, business_b = make_business("a"), make_business("b")
        _, email_a = make_user(ROLE_BUSINESS_ADMIN, business_a)
        client = new_client(app)
        client.login(email_a)
        form = {"full_name": "__test__yeni", "email": "__test__yeni@example.com", "role": ROLE_BUSINESS_USER,
                "theme": "light", "password": "uzunparola1", "business_id": business_b}
        assert client.ajax("/ayarlar/kullanicilar/yeni", form).get_json()["ok"] is True
        row = query_one("SELECT business_id FROM users WHERE email = %s", ("__test__yeni@example.com",))
        assert row["business_id"] == business_a


def test_deleted_report_is_scoped_and_restore_of_other_business_is_blocked():
    """Silinme raporu yalnızca kendi işletmesini gösterir; başka işletmenin log'u geri yüklenemez (404)."""
    with environment() as app:
        business_a, business_b = make_business("a"), make_business("b")
        _, email_a = make_user(ROLE_BUSINESS_ADMIN, business_a)
        victim_id, _ = make_user(ROLE_BUSINESS_USER, business_b, name="kurban")
        execute("UPDATE users SET is_deleted = TRUE WHERE user_id = %s", (victim_id,))
        UsersLog.record("user_delete", business_id=business_b, entity_type="user", entity_id=victim_id,
                        detail={"name": "Kurban", "changes": []})
        log_id = query_one("SELECT max(userslog_id) AS id FROM userslogs WHERE business_id = %s", (business_b,))["id"]
        client = new_client(app)
        client.login(email_a)
        assert "Kurban" not in client.get("/silinme-raporu/veri").get_json()["html"]
        assert client.get("/silinme-raporu/{}/detay".format(log_id)).status_code == 404
        restore = client.ajax("/silinme-raporu/{}/geri-yukle".format(log_id), token_from="/silinme-raporu")
        assert restore.status_code == 404
        assert query_one("SELECT is_deleted FROM users WHERE user_id = %s", (victim_id,))["is_deleted"] is True


def test_platform_admin_in_business_context_manages_only_that_business():
    """Yönetici işletmeye girince liste yalnızca o işletmeyi, girmeden yalnızca platform kullanıcılarını gösterir."""
    with environment() as app:
        business_a, business_b = make_business("a"), make_business("b")
        _, email_admin = make_user(ROLE_ADMIN, name="yon")
        _, email_a = make_user(ROLE_BUSINESS_USER, business_a, name="aaa")
        _, email_b = make_user(ROLE_BUSINESS_USER, business_b, name="bbb")
        client = new_client(app)
        client.login(email_admin)
        platform = client.get("/ayarlar/kullanicilar/veri").get_json()["html"]
        assert email_admin in platform and email_a not in platform and email_b not in platform
        client.post("/isletme-sec", {"business_id": business_a}, token_from="/dashboard")
        inside = client.get("/ayarlar/kullanicilar/veri").get_json()["html"]
        assert email_a in inside and email_b not in inside and email_admin not in inside


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
