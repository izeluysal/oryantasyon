"""Tek seferlik araç: eski statik programın içeriğinden eğitim tohum SQL'ini (03) ve ses dosyalarını üretir.

Kullanım:
    python test/export_training_content.py

Çıktı: md/oryantasyon/03_training_content.sql ve static/audio/*.mp3. İçerik kaynağı test/legacy_program/content.js'tir.
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY = os.path.join(ROOT, "test", "legacy_program")
OUTPUT = os.path.join(ROOT, "md", "oryantasyon", "03_training_content.sql")
AUDIO_DIR = os.path.join(ROOT, "static", "audio")


def literal(text):
    """Metni PostgreSQL dolar-tırnaklı string olarak yazar (kesme işareti kaçırma sorunu olmaz)."""
    assert "$q$" not in text
    return "$q$" + text + "$q$"


def jsonb(value):
    """Değeri jsonb sabiti olarak yazar."""
    return literal(json.dumps(value, ensure_ascii=False)) + "::jsonb"


def main():
    """content.js'i okuyup SQL ve ses dosyalarını üretir."""
    with open(os.path.join(LEGACY, "content.js"), encoding="utf-8") as content_file:
        text = content_file.read()
    data = json.loads(text[text.index("{"):text.rindex("}") + 1])
    os.makedirs(AUDIO_DIR, exist_ok=True)
    lines = [
        "-- Eğitim içeriği tohumu (test/export_training_content.py ile üretilmiştir). Tekrar çalıştırılabilir:",
        "-- ekranlar screen_code, sorular (ekran, sıra) ile güncellenir; öğrenme kayıtlarına dokunulmaz.",
        "BEGIN;",
    ]
    total = 0
    for order, screen in enumerate(data["screens"], start=1):
        audio = "s{:02d}.mp3".format(order - 1)
        shutil.copyfile(os.path.join(LEGACY, "audio", audio), os.path.join(AUDIO_DIR, audio))
        total += screen["coins"]
        lines.append(
            "INSERT INTO training_screens (screen_code, module_name, title, bullets, note, table_data, voice_text, "
            "audio_file, coins, bonus_coins, timer_seconds, is_critical, sort_order) VALUES ({}, {}, {}, {}, {}, {}, "
            "{}, {}, {}, {}, {}, {}, {}) ON CONFLICT (screen_code) DO UPDATE SET "
            "module_name = EXCLUDED.module_name, title = EXCLUDED.title, bullets = EXCLUDED.bullets, "
            "note = EXCLUDED.note, table_data = EXCLUDED.table_data, voice_text = EXCLUDED.voice_text, "
            "audio_file = EXCLUDED.audio_file, coins = EXCLUDED.coins, bonus_coins = EXCLUDED.bonus_coins, "
            "timer_seconds = EXCLUDED.timer_seconds, is_critical = EXCLUDED.is_critical, "
            "sort_order = EXCLUDED.sort_order;".format(
                literal(screen["no"]), literal(screen["module"]), literal(screen["title"]),
                jsonb(screen["bullets"]), literal(screen["note"]),
                jsonb(screen["table"]) if screen["table"] else "NULL", literal(screen["voice"]), literal(audio),
                screen["coins"], screen["bonus"], screen["timer"], str(screen["critical"]).upper(), order))
        for position, item in enumerate(screen["items"], start=1):
            lines.append(
                "INSERT INTO training_questions (training_screen_id, sort_order, question_text, options, "
                "correct_index, explanation, coins) VALUES ((SELECT training_screen_id FROM training_screens "
                "WHERE screen_code = {}), {}, {}, {}, {}, {}, {}) ON CONFLICT (training_screen_id, sort_order) "
                "DO UPDATE SET question_text = EXCLUDED.question_text, options = EXCLUDED.options, "
                "correct_index = EXCLUDED.correct_index, explanation = EXCLUDED.explanation, "
                "coins = EXCLUDED.coins;".format(
                    literal(screen["no"]), position, literal(item["q"]), jsonb(item["opts"]), item["c"],
                    literal(item["why"]), item["coin"]))
    lines.append("COMMIT;")
    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as output_file:
        output_file.write("\n".join(lines) + "\n")
    print("ekran:", len(data["screens"]), "toplam coin:", total, "->", os.path.relpath(OUTPUT, ROOT))


if __name__ == "__main__":
    main()
