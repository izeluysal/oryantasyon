"""Eğitim akışı: puan kuralları, sıralı kilit, izolasyon, rapor ve sertifika (gerçek veritabanıyla)."""
from _ortam import environment, make_business, make_user, new_client
from app.db import execute, query_all, query_one
from app.helpers.roles import ROLE_ADMIN, ROLE_AUDITOR, ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER

TOTAL_COINS = 4000


def _screens():
    """Tüm ekranlar sırayla, soruları (doğru indeks ve coin) ile."""
    screens = query_all(
        "SELECT training_screen_id, screen_code, timer_seconds FROM training_screens ORDER BY sort_order")
    for screen in screens:
        screen["questions"] = query_all(
            "SELECT training_question_id, correct_index, coins, jsonb_array_length(options) AS n "
            "FROM training_questions WHERE training_screen_id = %s ORDER BY sort_order",
            (screen["training_screen_id"],))
    return screens


def _answer(client, screen_id, question_id, option, token_from="/egitim"):
    """Bir soruyu yanıtlar ve JSON döndürür."""
    return client.ajax("/egitim/ekran/{}/yanit".format(screen_id), {"question_id": question_id, "option": option},
                       token_from=token_from)


def _finish_screen(client, screen):
    """Ekranı açar ve tüm soruları (ya da bilgi ekranını) doğru tamamlar."""
    assert client.get("/egitim/ekran/{}".format(screen["training_screen_id"])).status_code == 200
    if not screen["questions"]:
        return client.ajax("/egitim/ekran/{}/tamamla".format(screen["training_screen_id"]), token_from="/egitim")
    last = None
    for question in screen["questions"]:
        last = _answer(client, screen["training_screen_id"], question["training_question_id"],
                       question["correct_index"])
    return last


def _learner(app, role=ROLE_BUSINESS_USER):
    """Bir işletme ve o işletmede giriş yapmış bir öğrenen oluşturur: (istemci, kullanıcı kimliği, işletme)."""
    business_id = make_business("egitim")
    user_id, email = make_user(role, business_id)
    client = new_client(app)
    client.login(email)
    return client, user_id, business_id


def test_full_playthrough_awards_exactly_4000_coins_and_unlocks_certificate():
    """Tüm ekranlar ilk denemede doğru tamamlanınca 4000 Ece-Coin, en üst seviye, 4 rozet ve sertifika oluşur."""
    with environment() as app:
        client, user_id, _ = _learner(app)
        assert client.get("/egitim/sertifika").status_code == 302  # henüz tamamlanmadı
        for screen in _screens():
            result = _finish_screen(client, screen).get_json()
            assert result["ok"] is True
        from app.models.training import Training
        state = Training.state(user_id)
        assert state["coins"] == TOTAL_COINS and state["all_done"] is True
        assert state["level"] == "training.level.chief" and len(state["badges"]) == 4
        certificate = client.get("/egitim/sertifika")
        assert certificate.status_code == 200 and "yetkilendirme" in certificate.get_data(as_text=True)


def test_wrong_then_correct_earns_half_coins_and_breaks_first_try():
    """Korur: yanlıştan sonraki doğru yanıt yarım coin kazandırır ve ilk-deneme bayrağını düşürür."""
    with environment() as app:
        client, user_id, _ = _learner(app)
        screens = _screens()
        for earlier in screens[:2]:  # ilk ekranların soruları tek seçenekli; çok seçenekli ekrana kadar ilerle
            _finish_screen(client, earlier)
        screen = screens[2]
        question = screen["questions"][0]
        assert question["n"] > 1
        wrong = (question["correct_index"] + 1) % question["n"]
        first = _answer(client, screen["training_screen_id"], question["training_question_id"], wrong).get_json()
        assert first["correct"] is False and first["coins"] == 0
        second = _answer(client, screen["training_screen_id"], question["training_question_id"],
                         question["correct_index"]).get_json()
        assert second["correct"] is True and second["coins"] == question["coins"] // 2
        row = query_one("SELECT is_first_try, attempt_count FROM training_answers WHERE user_id = %s "
                        "AND training_question_id = %s", (user_id, question["training_question_id"]))
        assert row["is_first_try"] is False and row["attempt_count"] == 2


def test_answering_an_already_correct_question_does_not_pay_again():
    """Korur: coin istismarı. Doğru yanıtlanmış soru tekrar puan vermez."""
    with environment() as app:
        client, user_id, _ = _learner(app)
        screen = _screens()[0]
        question = screen["questions"][0]
        _answer(client, screen["training_screen_id"], question["training_question_id"], question["correct_index"])
        again = _answer(client, screen["training_screen_id"], question["training_question_id"],
                        question["correct_index"]).get_json()
        assert again["already"] is True and again["coins"] == 0
        total = query_one("SELECT sum(coins_earned) AS coins FROM training_answers WHERE user_id = %s", (user_id,))
        assert total["coins"] == question["coins"]


def test_screens_unlock_sequentially_on_the_server():
    """Korur: sıralı ilerleme. Önceki ekran bitmeden sonraki açılamaz ve yanıtlanamaz (sunucu tarafı)."""
    with environment() as app:
        client, _, _ = _learner(app)
        screens = _screens()
        second = screens[1]
        assert client.get("/egitim/ekran/{}".format(second["training_screen_id"])).status_code == 302
        question = second["questions"][0] if second["questions"] else None
        if question:
            response = _answer(client, second["training_screen_id"], question["training_question_id"],
                               question["correct_index"])
            assert response.status_code == 403
        assert client.get("/egitim/ekran/{}".format(screens[0]["training_screen_id"])).status_code == 200


def test_invalid_option_or_foreign_question_is_rejected():
    """Aralık dışı seçenek ve başka ekranın sorusu reddedilir; coin yazılmaz."""
    with environment() as app:
        client, user_id, _ = _learner(app)
        screens = _screens()
        first, other = screens[0], next(s for s in screens[1:] if s["questions"])
        question = first["questions"][0]
        assert _answer(client, first["training_screen_id"], question["training_question_id"], 99).status_code == 400
        foreign = other["questions"][0]["training_question_id"]
        assert _answer(client, first["training_screen_id"], foreign, 0).status_code == 400
        assert query_one("SELECT count(*) AS n FROM training_answers WHERE user_id = %s", (user_id,))["n"] == 0


def test_timed_screen_pays_bonus_only_when_finished_in_time():
    """Korur: zamanlı ekran. Süre dolmadan bitirene bonus; süre dolduktan sonra yarım coin ve bonus yok."""
    from app.models.training import Training
    with environment() as app:
        timed = next(s for s in _screens() if s["timer_seconds"])
        results = {}
        for label, late in (("in_time", False), ("late", True)):
            client, user_id, business_id = _learner(app)
            for screen in _screens():
                if screen["training_screen_id"] == timed["training_screen_id"]:
                    break
                _finish_screen(client, screen)
            client.get("/egitim/ekran/{}".format(timed["training_screen_id"]))
            if late:
                execute("UPDATE training_progress SET started_at = now() - interval '1 hour' "
                        "WHERE user_id = %s AND training_screen_id = %s", (user_id, timed["training_screen_id"]))
            before = Training.state(user_id)["coins"]
            _finish_screen(client, timed)
            results[label] = Training.state(user_id)["coins"] - before
        full = sum(q["coins"] for q in timed["questions"])
        assert results["in_time"] == full + 50
        assert results["late"] == sum(q["coins"] // 2 for q in timed["questions"])


def test_training_roles_and_report_isolation():
    """Eğitimi yalnızca öğrenen roller alır; rapor yalnızca kendi işletmesini gösterir; denetim okur ama alamaz."""
    with environment() as app:
        learner_a, _, business_a = _learner(app)
        learner_b, _, business_b = _learner(app)
        _, admin_email = make_user(ROLE_BUSINESS_ADMIN, business_a, name="yonetici")
        _, auditor_email = make_user(ROLE_AUDITOR, business_a, name="denetci")
        _, platform_email = make_user(ROLE_ADMIN, name="platform")
        screen = _screens()[0]
        _finish_screen(learner_a, screen)
        _finish_screen(learner_b, screen)
        assert learner_a.get("/egitim-raporu").status_code == 403
        manager = new_client(app)
        manager.login(admin_email)
        report = manager.get("/egitim-raporu/veri").get_json()
        assert report["total"] >= 1 and "__test__kullanici" in report["html"]
        emails_b = [row["email"] for row in query_all("SELECT email FROM users WHERE business_id = %s", (business_b,))]
        assert not any(email in report["html"] for email in emails_b)
        auditor = new_client(app)
        auditor.login(auditor_email)
        assert auditor.get("/egitim-raporu/veri").status_code == 200
        assert auditor.get("/egitim").status_code == 403
        platform = new_client(app)
        platform.login(platform_email)
        assert platform.get("/egitim").status_code == 403
        assert "İşletmeler menüsünden" in platform.get("/egitim-raporu").get_data(as_text=True)
        assert platform.get("/egitim-raporu/veri").status_code == 404


def test_report_counts_completed_in_progress_and_not_started():
    """Rapor sayaç kartları durumu doğru sayar: tamamlayan, devam eden, başlamayan."""
    with environment() as app:
        business_id = make_business("rapor")
        _, manager_email = make_user(ROLE_BUSINESS_ADMIN, business_id, name="mudur")
        for _ in range(2):
            make_user(ROLE_BUSINESS_USER, business_id, name="baslamayan")
        user_id, learner_email = make_user(ROLE_BUSINESS_USER, business_id, name="devam")
        learner = new_client(app)
        learner.login(learner_email)
        _finish_screen(learner, _screens()[0])
        manager = new_client(app)
        manager.login(manager_email)
        summary = manager.get("/egitim-raporu/veri").get_json()["ozet"]
        # Yönetici de öğrenen roldedir ve başlamamıştır: 2 + 1 başlamayan, 1 devam eden.
        assert summary["total"] == 4 and summary["in_progress"] == 1 and summary["not_started"] == 3
        assert summary["completed"] == 0
        filtered = manager.get("/egitim-raporu/veri?status=in_progress").get_json()
        assert filtered["total"] == 1 and "__test__devam" in filtered["html"]


def test_content_preview_is_for_managers_and_writes_nothing():
    """Eğitim içeriği önizlemesi yönetici rollerine açıktır, çalışana kapalıdır ve hiçbir kayıt yazmaz."""
    with environment() as app:
        business_id = make_business("onizleme")
        _, platform_email = make_user(ROLE_ADMIN, name="platform")
        _, manager_email = make_user(ROLE_BUSINESS_ADMIN, business_id, name="mudur")
        _, learner_email = make_user(ROLE_BUSINESS_USER, business_id, name="calisan")
        first_id = _screens()[0]["training_screen_id"]
        for email in (platform_email, manager_email):
            client = new_client(app)
            client.login(email)
            listing = client.get("/egitim-icerigi")
            assert listing.status_code == 200 and "Hassas Metroloji Yolculuğu" in listing.get_data(as_text=True)
            page = client.get("/egitim-icerigi/{}".format(first_id))
            assert page.status_code == 200 and "Evet, yolculuğa başlıyorum!" in page.get_data(as_text=True)
        learner = new_client(app)
        learner.login(learner_email)
        assert learner.get("/egitim-icerigi").status_code == 403
        assert query_one("SELECT count(*) AS n FROM training_progress WHERE business_id = %s", (business_id,))["n"] == 0


def test_every_screen_has_a_playable_video_and_poster():
    """Her ekranın videosu ve posteri sunulur; Range isteği (ileri sarma) 206 döner; sayfada <video> vardır."""
    with environment() as app:
        client, _, _ = _learner(app)
        screens = query_all("SELECT training_screen_id, video_file FROM training_screens ORDER BY sort_order")
        assert len(screens) == 24 and all(row["video_file"] for row in screens)
        for row in screens:
            video = client.get("/static/video/" + row["video_file"])
            assert video.status_code == 200 and video.mimetype == "video/mp4" and len(video.data) > 50000, row
            assert client.get("/static/video/" + row["video_file"][:-4] + ".jpg").status_code == 200
        ranged = client.get("/static/video/" + screens[0]["video_file"], headers={"Range": "bytes=0-99"})
        assert ranged.status_code == 206
        first = client.get("/egitim/ekran/{}".format(screens[0]["training_screen_id"])).get_data(as_text=True)
        assert "<video" in first and screens[0]["video_file"] in first
        assert "oryantasyon.mp4" in client.get("/egitim").get_data(as_text=True)
        assert client.get("/static/video/oryantasyon.mp4").status_code == 200


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
