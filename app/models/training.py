"""Eğitim: ekranlar, sorular, ilerleme ve Ece-Coin kuralları. Tüm puan kararları sunucuda verilir."""
from datetime import datetime, timezone

from app.db import PER_PAGE, get_cursor, like_pattern, query_all, query_one
from app.helpers.roles import ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER

LEARNER_ROLES = (ROLE_BUSINESS_USER, ROLE_BUSINESS_ADMIN)

# Seviye eşikleri (Ece-Coin) ve etiket anahtarları; etiketler çevirisi t() ile yapılır.
LEVELS = (
    (0, "training.level.apprentice"),
    (1001, "training.level.expert"),
    (2501, "training.level.chief"),
)

# Rozet -> koşulu oluşturan ekran kodları: hepsi ilk denemede doğru tamamlanmış olmalıdır.
BADGES = (
    ("isg", ("5.2 / 5.3",)),
    ("mass", ("2.3", "2.4", "2.5")),
    ("thermal", ("3.3", "3.5")),
    ("ethics", ("1.3", "1.4", "6.3")),
)

STATUS_FILTERS = ("completed", "in_progress", "not_started")


def level_key(coins):
    """Ece-Coin toplamına göre seviye çeviri anahtarını döndürür."""
    key = LEVELS[0][1]
    for threshold, level in LEVELS:
        if coins >= threshold:
            key = level
    return key


def earned_badges(perfect_codes):
    """İlk denemede kusursuz tamamlanan ekran kodlarından kazanılan rozet kimliklerini döndürür."""
    return [badge for badge, codes in BADGES if all(code in perfect_codes for code in codes)]


class Training:
    """Eğitim içeriği ve kullanıcı öğrenme durumu."""

    @staticmethod
    def screens():
        """Tüm ekranları sırayla döndürür; her ekranda soru sayısı vardır."""
        return query_all(
            "SELECT s.training_screen_id, s.screen_code, s.module_name, s.title, s.coins, s.bonus_coins, "
            "s.timer_seconds, s.is_critical, s.sort_order, "
            "(SELECT count(*) FROM training_questions q WHERE q.training_screen_id = s.training_screen_id) "
            "AS question_count FROM training_screens s ORDER BY s.sort_order"
        )

    @staticmethod
    def get_screen(training_screen_id):
        """Tek ekranı tüm alanlarıyla getirir; yoksa None."""
        return query_one("SELECT * FROM training_screens WHERE training_screen_id = %s", (training_screen_id,))

    @staticmethod
    def questions(training_screen_id):
        """Ekranın sorularını sırayla döndürür (doğru yanıt istemciye gönderilmez, çağıran ayıklar)."""
        return query_all(
            "SELECT training_question_id, sort_order, question_text, options, correct_index, explanation, coins "
            "FROM training_questions WHERE training_screen_id = %s ORDER BY sort_order",
            (training_screen_id,),
        )

    @staticmethod
    def total_coins():
        """Programdan kazanılabilecek toplam Ece-Coin (soru coin'leri ve zaman bonusları)."""
        return query_one(
            "SELECT (SELECT coalesce(sum(coins), 0) FROM training_questions) + "
            "coalesce(sum(bonus_coins), 0) AS total FROM training_screens"
        )["total"]

    @staticmethod
    def state(user_id):
        """Kullanıcının öğrenme durumu: tamamlanan ekranlar, coin, seviye, rozetler, ekran bazlı ayrıntı."""
        screens = Training.screens()
        progress = {row["training_screen_id"]: row for row in query_all(
            "SELECT training_screen_id, is_completed, bonus_coins, started_at, completed_at "
            "FROM training_progress WHERE user_id = %s", (user_id,))}
        answers = query_all(
            "SELECT q.training_screen_id, a.is_correct, a.is_first_try, a.coins_earned "
            "FROM training_answers a JOIN training_questions q USING (training_question_id) WHERE a.user_id = %s",
            (user_id,),
        )
        coins = sum(row["coins_earned"] for row in answers) + sum(row["bonus_coins"] for row in progress.values())
        first_try = {}
        for row in answers:
            screen_id = row["training_screen_id"]
            first_try[screen_id] = first_try.get(screen_id, 0) + int(row["is_first_try"])
        done_ids, perfect_codes = set(), set()
        for screen in screens:
            row = progress.get(screen["training_screen_id"])
            if row and row["is_completed"]:
                done_ids.add(screen["training_screen_id"])
                if first_try.get(screen["training_screen_id"], 0) == screen["question_count"]:
                    perfect_codes.add(screen["screen_code"])
        return {"screens": screens, "progress": progress, "done_ids": done_ids, "coins": coins,
                "level": level_key(coins), "badges": earned_badges(perfect_codes),
                "all_done": len(done_ids) == len(screens) and len(screens) > 0}

    @staticmethod
    def is_unlocked(state, training_screen_id):
        """Ekran açık mı: kendisinden önceki tüm ekranlar tamamlanmış olmalıdır (sıralı ilerleme)."""
        for screen in state["screens"]:
            if screen["training_screen_id"] == training_screen_id:
                return True
            if screen["training_screen_id"] not in state["done_ids"]:
                return False
        return False

    @staticmethod
    def start_screen(business_id, user_id, training_screen_id):
        """İlerleme satırını (ilk görüntüleme zamanıyla) oluşturur; varsa dokunmaz. Satırı döndürür."""
        with get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO training_progress (business_id, user_id, training_screen_id) VALUES (%s, %s, %s) "
                "ON CONFLICT (user_id, training_screen_id) DO NOTHING",
                (business_id, user_id, training_screen_id),
            )
            cursor.execute(
                "SELECT started_at, is_completed, bonus_coins, now() AS now_at FROM training_progress "
                "WHERE user_id = %s AND training_screen_id = %s",
                (user_id, training_screen_id),
            )
            return cursor.fetchone()

    @staticmethod
    def answers_of(user_id, training_screen_id):
        """Ekrandaki soruların kullanıcı yanıt durumu: {soru_id: satır}."""
        rows = query_all(
            "SELECT a.training_question_id, a.is_correct, a.attempt_count, a.coins_earned FROM training_answers a "
            "JOIN training_questions q USING (training_question_id) WHERE a.user_id = %s "
            "AND q.training_screen_id = %s",
            (user_id, training_screen_id),
        )
        return {row["training_question_id"]: row for row in rows}

    @staticmethod
    def answer(business_id, user_id, training_question_id, option_index):
        """Bir soruyu yanıtlar ve sonucu döndürür; coin kuralları burada uygulanır.

        Kurallar: ilk denemede doğru yanıt tam coin, sonraki doğru yanıt yarım coin kazandırır; süreli ekranda
        süre dolduktan sonra verilen doğru yanıt yarım coin kazandırır. Doğru yanıtlanmış soru tekrar puan vermez.
        Ekranın tüm soruları doğru olunca ekran tamamlanır; süre dolmadan bitirene zaman bonusu verilir.

        Returns:
            Sözlük: correct, coins, already, explanation, screen_completed, bonus. Soru yoksa None.
        """
        with get_cursor() as cursor:
            cursor.execute(
                "SELECT q.training_question_id, q.training_screen_id, q.correct_index, q.explanation, q.coins, "
                "jsonb_array_length(q.options) AS option_count, s.timer_seconds, s.bonus_coins "
                "FROM training_questions q JOIN training_screens s USING (training_screen_id) "
                "WHERE q.training_question_id = %s",
                (training_question_id,),
            )
            question = cursor.fetchone()
            if question is None or not 0 <= option_index < question["option_count"]:
                return None
            screen_id = question["training_screen_id"]
            cursor.execute(
                "INSERT INTO training_progress (business_id, user_id, training_screen_id) VALUES (%s, %s, %s) "
                "ON CONFLICT (user_id, training_screen_id) DO NOTHING",
                (business_id, user_id, screen_id),
            )
            cursor.execute(
                "INSERT INTO training_answers (business_id, user_id, training_question_id) VALUES (%s, %s, %s) "
                "ON CONFLICT (user_id, training_question_id) DO NOTHING",
                (business_id, user_id, training_question_id),
            )
            # Aynı soruya eşzamanlı iki yanıt çift coin yazmasın diye satır kilitlenir.
            cursor.execute(
                "SELECT training_answer_id, attempt_count, is_correct FROM training_answers "
                "WHERE user_id = %s AND training_question_id = %s FOR UPDATE",
                (user_id, training_question_id),
            )
            answer = cursor.fetchone()
            if answer["is_correct"]:
                return {"correct": True, "coins": 0, "already": True, "explanation": question["explanation"],
                        "screen_completed": False, "bonus": 0}
            cursor.execute(
                "SELECT started_at, now() AS now_at FROM training_progress "
                "WHERE user_id = %s AND training_screen_id = %s",
                (user_id, screen_id),
            )
            timing = cursor.fetchone()
            elapsed = (timing["now_at"] - timing["started_at"]).total_seconds()
            late = question["timer_seconds"] > 0 and elapsed > question["timer_seconds"]
            attempts = answer["attempt_count"] + 1
            correct = option_index == question["correct_index"]
            coins = 0
            if correct:
                full = attempts == 1 and not late
                coins = question["coins"] if full else question["coins"] // 2
            cursor.execute(
                "UPDATE training_answers SET attempt_count = %s, is_correct = %s, is_first_try = %s, "
                "coins_earned = %s, answered_at = now() WHERE training_answer_id = %s",
                (attempts, correct, correct and attempts == 1 and not late, coins, answer["training_answer_id"]),
            )
            completed, bonus = False, 0
            if correct:
                completed, bonus = Training._complete_if_finished(cursor, user_id, screen_id, question, elapsed)
            return {"correct": correct, "coins": coins, "already": False,
                    "explanation": question["explanation"] if correct else "", "screen_completed": completed,
                    "bonus": bonus}

    @staticmethod
    def _complete_if_finished(cursor, user_id, screen_id, question, elapsed):
        """Ekranın tüm soruları doğruysa ekranı tamamlar; süre dolmadan bitirene bonus verir."""
        cursor.execute(
            "SELECT count(*) AS total, count(a.training_question_id) FILTER (WHERE a.is_correct) AS correct "
            "FROM training_questions q LEFT JOIN training_answers a ON a.training_question_id = q.training_question_id "
            "AND a.user_id = %s WHERE q.training_screen_id = %s",
            (user_id, screen_id),
        )
        counts = cursor.fetchone()
        if counts["total"] != counts["correct"]:
            return False, 0
        in_time = question["timer_seconds"] > 0 and elapsed <= question["timer_seconds"]
        bonus = question["bonus_coins"] if in_time else 0
        cursor.execute(
            "UPDATE training_progress SET is_completed = TRUE, completed_at = now(), bonus_coins = %s "
            "WHERE user_id = %s AND training_screen_id = %s AND is_completed = FALSE RETURNING training_progress_id",
            (bonus, user_id, screen_id),
        )
        if cursor.fetchone() is None:
            return False, 0
        return True, bonus

    @staticmethod
    def complete_info_screen(business_id, user_id, training_screen_id):
        """Sorusuz ekranı tamamlar (yalnızca gerçekten sorusu olmayan ekranlarda); tamamlandıysa True."""
        with get_cursor() as cursor:
            cursor.execute("SELECT count(*) AS total FROM training_questions WHERE training_screen_id = %s",
                           (training_screen_id,))
            if cursor.fetchone()["total"] > 0:
                return False
            cursor.execute(
                "INSERT INTO training_progress (business_id, user_id, training_screen_id, is_completed, completed_at) "
                "VALUES (%s, %s, %s, TRUE, now()) ON CONFLICT (user_id, training_screen_id) DO UPDATE "
                "SET is_completed = TRUE, completed_at = coalesce(training_progress.completed_at, now())",
                (business_id, user_id, training_screen_id),
            )
        return True

    @staticmethod
    def remaining_seconds(screen, progress_row):
        """Süreli ekranda kalan saniye (0 = süre doldu); süresiz ekranda None."""
        if not screen["timer_seconds"]:
            return None
        started = progress_row["started_at"]
        now = progress_row["now_at"] if "now_at" in progress_row else datetime.now(timezone.utc)
        return max(int(screen["timer_seconds"] - (now - started).total_seconds()), 0)

    @staticmethod
    def report_page(business_id, query="", status=None, page=1):
        """İşletmedeki öğrenenlerin ilerleme özeti (sayfalı): (satırlar, toplam). Kullanıcı başına tek sorgu."""
        where, where_params = ["u.business_id = %s", "u.is_deleted = FALSE", "u.role = ANY(%s)"], [
            business_id, list(LEARNER_ROLES)]
        if query:
            where.append("(u.full_name ILIKE %s OR u.email ILIKE %s)")
            where_params.extend([like_pattern(query)] * 2)
        having = {
            "completed": "coalesce(p.done, 0) = t.total",
            "not_started": "coalesce(p.done, 0) = 0 AND coalesce(a.answered, 0) = 0",
            "in_progress": "coalesce(p.done, 0) < t.total AND (coalesce(p.done, 0) > 0 OR coalesce(a.answered, 0) > 0)",
        }.get(status)
        sql_where = " AND ".join(where) + (" AND " + having if having else "")
        # Parametre sırası SQL'deki sırayı izler: iki alt sorgunun işletme kimliği, WHERE, LIMIT, OFFSET.
        params = [business_id, business_id] + where_params + [PER_PAGE, (max(page, 1) - 1) * PER_PAGE]
        rows = query_all(
            "SELECT u.user_id, u.full_name, u.email, coalesce(a.coins, 0) + coalesce(p.bonus, 0) AS coins, "
            "coalesce(p.done, 0) AS done, t.total AS total, coalesce(a.answered, 0) AS answered, "
            "coalesce(a.first_try, 0) AS first_try, CASE WHEN coalesce(p.done, 0) = t.total THEN p.last_done END "
            "AS finished_at, count(*) OVER() AS total_count "
            "FROM users u CROSS JOIN (SELECT count(*) AS total FROM training_screens) t "
            "LEFT JOIN (SELECT user_id, sum(coins_earned) AS coins, count(*) AS answered, "
            "count(*) FILTER (WHERE is_first_try) AS first_try FROM training_answers WHERE business_id = %s "
            "GROUP BY user_id) a ON a.user_id = u.user_id "
            "LEFT JOIN (SELECT user_id, count(*) FILTER (WHERE is_completed) AS done, sum(bonus_coins) AS bonus, "
            "max(completed_at) AS last_done FROM training_progress WHERE business_id = %s GROUP BY user_id) p "
            "ON p.user_id = u.user_id WHERE " + sql_where
            + " ORDER BY lower(u.full_name), u.user_id LIMIT %s OFFSET %s",
            params,
        )
        return rows, (rows[0]["total_count"] if rows else 0)

    @staticmethod
    def report_summary(business_id):
        """Rapor sayaç kartları: toplam/tamamlayan/devam eden/başlamayan öğrenen sayısı."""
        return query_one(
            "WITH t AS (SELECT count(*) AS total FROM training_screens), "
            "p AS (SELECT user_id, count(*) FILTER (WHERE is_completed) AS done FROM training_progress "
            "WHERE business_id = %s GROUP BY user_id), "
            "a AS (SELECT DISTINCT user_id FROM training_answers WHERE business_id = %s) "
            "SELECT count(*) AS total, count(*) FILTER (WHERE coalesce(p.done, 0) = t.total) AS completed, "
            "count(*) FILTER (WHERE coalesce(p.done, 0) < t.total "
            "AND (coalesce(p.done, 0) > 0 OR a.user_id IS NOT NULL)) AS in_progress, "
            "count(*) FILTER (WHERE coalesce(p.done, 0) = 0 AND a.user_id IS NULL) AS not_started "
            "FROM users u CROSS JOIN t LEFT JOIN p ON p.user_id = u.user_id LEFT JOIN a ON a.user_id = u.user_id "
            "WHERE u.business_id = %s AND u.is_deleted = FALSE AND u.role = ANY(%s)",
            (business_id, business_id, business_id, list(LEARNER_ROLES)),
        )

    @staticmethod
    def perfect_codes_by_user(business_id, user_ids):
        """Verilen kullanıcıların ilk denemede kusursuz tamamladığı ekran kodları: {kullanıcı: {kod}} (tek sorgu)."""
        if not user_ids:
            return {}
        rows = query_all(
            "SELECT a.user_id, s.screen_code FROM training_answers a "
            "JOIN training_questions q USING (training_question_id) JOIN training_screens s USING (training_screen_id) "
            "JOIN training_progress p ON p.user_id = a.user_id AND p.training_screen_id = s.training_screen_id "
            "WHERE a.business_id = %s AND a.user_id = ANY(%s) AND p.is_completed "
            "GROUP BY a.user_id, s.screen_code, s.training_screen_id "
            "HAVING count(*) FILTER (WHERE a.is_first_try) = "
            "(SELECT count(*) FROM training_questions q2 WHERE q2.training_screen_id = s.training_screen_id)",
            (business_id, list(user_ids)),
        )
        result = {}
        for row in rows:
            result.setdefault(row["user_id"], set()).add(row["screen_code"])
        return result

    @staticmethod
    def hardest_screens(business_id, limit=5):
        """İlk denemede en az doğru yapılan ekranlar (içerik iyileştirme için); çalışan puanlamak için değildir."""
        return query_all(
            "SELECT s.screen_code, s.title, count(*) AS answered, "
            "round(100.0 * count(*) FILTER (WHERE a.is_first_try) / count(*)) AS rate "
            "FROM training_answers a JOIN training_questions q USING (training_question_id) "
            "JOIN training_screens s USING (training_screen_id) WHERE a.business_id = %s "
            "GROUP BY s.screen_code, s.title, s.sort_order HAVING count(*) > 0 ORDER BY rate, s.sort_order LIMIT %s",
            (business_id, limit),
        )

