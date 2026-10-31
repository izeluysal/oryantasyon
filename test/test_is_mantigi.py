"""Hesaplamaların ve kuralların doğru sonuç üretmesi (biçimleme, çeviri, Excel, koruma ayarları)."""
from datetime import date, datetime

from _ortam import environment
from app import i18n
from app.helpers.excel import excel_olustur, neutralize
from app.helpers.format import sayi, tarih, tarih_saat
from app.models.login_attempt import validate_settings


def test_number_and_date_formats_follow_turkish_rules():
    """Sayı Türkçe ayraçlarla (1.234,50), tarih gg.aa.yyyy, saat 24 saat biçiminde yazılır."""
    with environment() as app:
        with app.test_request_context("/"):
            assert sayi(1234567) == "1.234.567"
            assert sayi(1234.5, ondalik_basamak=2) == "1.234,50"
            assert tarih(date(2026, 8, 31)) == "31.08.2026"
            assert tarih_saat(datetime(2026, 8, 31, 14, 30)) == "31.08.2026 14:30"
            assert tarih(None) == ""


def test_translation_fallback_placeholders_and_plurals():
    """Fallback anahtarın kendisine düşer; yer tutucu doldurulur; tanımsız yer tutucu olduğu gibi kalır."""
    with environment() as app:
        with app.test_request_context("/"):
            assert i18n.t("olmayan.anahtar") == "olmayan.anahtar"
            assert i18n.t("deleted.restored", name="Ayşe") == "Ayşe geri yüklendi."
            assert "{name}" in i18n.t("deleted.restored")
            assert "5 dakika" in i18n.t("auth.blocked", count=5)


def test_excel_neutralizes_formulas_and_keeps_real_types():
    """Formül gibi başlayan metne tek tırnak eklenir; sayı ve tarih gerçek tipte yazılır."""
    from io import BytesIO

    from openpyxl import load_workbook

    assert neutralize("=1+1") == "'=1+1" and neutralize("+cmd") == "'+cmd" and neutralize("@x") == "'@x"
    assert neutralize("normal") == "normal" and neutralize("a\x00b") == "ab"
    data = excel_olustur(["=baslik", "sayi", "tarih"], [["=HYPERLINK(1)", 42, date(2026, 8, 31)]])
    sheet = load_workbook(BytesIO(data)).active
    assert sheet["A1"].value == "'=baslik" and sheet["A2"].value == "'=HYPERLINK(1)"
    assert sheet["B2"].value == 42 and isinstance(sheet["C2"].value, datetime)


def test_login_protection_settings_are_range_validated():
    """Sıfır/negatif deneme sınırı korumayı sessizce kapatırdı; aralık dışı değer reddedilir."""
    ok = validate_settings({"enabled": True, "max_attempts": "5", "block_minutes": "10", "window_minutes": "15"})
    assert ok == {"enabled": True, "max_attempts": 5, "block_minutes": 10, "window_minutes": 15}
    for bad in ({"max_attempts": "0"}, {"max_attempts": "101"}, {"block_minutes": "1441"}, {"window_minutes": "-1"}):
        values = {"enabled": True, "max_attempts": "5", "block_minutes": "10", "window_minutes": "15"}
        values.update(bad)
        try:
            validate_settings(values)
        except ValueError:
            continue
        raise AssertionError("aralık dışı değer kabul edildi: {}".format(bad))


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("gecti:", name)
