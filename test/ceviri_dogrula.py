"""Çeviri dosyalarını ve koddaki t() anahtarlarını doğrular (Türkçe referans dildir)."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.i18n import DIL_BILGILERI  # noqa: E402

TRANSLATIONS = os.path.join(ROOT, "app", "translations")
PLACEHOLDER = re.compile(r"\{(\w+)\}")
LITERAL_CALL = re.compile(r"""\bt\(\s*["']([A-Za-z0-9_.]+)["']\s*[,)]""")
PREFIX_CALL = re.compile(r"""\bt\(\s*["']([A-Za-z0-9_.]+\.)["']\s*(?:~|\+)""")


def load(code):
    """Dil dosyasını okur."""
    with open(os.path.join(TRANSLATIONS, code + ".json"), encoding="utf-8") as translation_file:
        return json.load(translation_file)


def source_files():
    """Anahtar taranacak şablon, JS ve Python dosyaları."""
    for folder in ("templates", "static/js", "app"):
        for current, _, files in os.walk(os.path.join(ROOT, *folder.split("/"))):
            for name in files:
                if name.endswith((".html", ".js", ".py")):
                    yield os.path.join(current, name)


def check_languages(errors):
    """Tüm dillerin anahtar kümesini, boşluğu, çoğul ve yer tutucu tutarlılığını denetler."""
    reference = load("tr")
    for code in DIL_BILGILERI:
        data = load(code)
        if set(data) != set(reference):
            errors.append("{}: anahtar kümesi tr ile ayni degil".format(code))
        if list(data) != sorted(data):
            errors.append("{}: anahtarlar alfabetik sirali degil".format(code))
        for key, value in data.items():
            if value in ("", {}):
                errors.append("{}: bos deger: {}".format(code, key))
            ref = reference.get(key)
            if isinstance(value, dict) != isinstance(ref, dict):
                errors.append("{}: cogul/duz uyumsuzlugu: {}".format(code, key))
            elif isinstance(value, dict):
                missing = set(DIL_BILGILERI[code]["cogul"]) - set(value)
                if missing:
                    errors.append("{}: {} cogul formlari eksik: {}".format(code, key, sorted(missing)))
            elif ref is not None and set(PLACEHOLDER.findall(value)) != set(PLACEHOLDER.findall(ref)):
                errors.append("{}: yer tutucu tutarsiz: {}".format(code, key))


def check_usage(errors):
    """Kodda geçen her sabit t() anahtarının tanımlı olduğunu denetler."""
    keys = set(load("tr"))
    for path in source_files():
        with open(path, encoding="utf-8") as source:
            text = source.read()
        for match in LITERAL_CALL.finditer(text):
            if match.group(1) not in keys:
                errors.append("{}: tanimsiz anahtar: {}".format(os.path.relpath(path, ROOT), match.group(1)))
        for match in PREFIX_CALL.finditer(text):
            if not any(key.startswith(match.group(1)) for key in keys):
                errors.append("{}: onek icin anahtar yok: {}".format(os.path.relpath(path, ROOT), match.group(1)))


def main():
    """Doğrulamaları çalıştırır."""
    errors = []
    check_languages(errors)
    check_usage(errors)
    for error in errors:
        print("HATA", error)
    print("ceviri_dogrula:", "BASARISIZ" if errors else "temiz")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
