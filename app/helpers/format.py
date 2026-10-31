"""Tarih, sayı ve para biçimlendirme: dile bağlı biçimler tek yerden gelir."""
from datetime import date, datetime

from app.i18n import VARSAYILAN_DIL, current_language

BICIMLER = {
    "tr": {"tarih": "%d.%m.%Y", "tarih_saat": "%d.%m.%Y %H:%M", "ondalik": ",", "binlik": "."},
}


def _format_for(language):
    """Dilin biçim sözlüğünü döndürür; tanımsız dilde Türkçe biçim kullanılır."""
    return BICIMLER.get(language) or BICIMLER[VARSAYILAN_DIL]


def tarih(value):
    """Tarihi aktif dilin biçiminde yazar; boş değer için boş metin döner."""
    if not isinstance(value, (date, datetime)):
        return ""
    return value.strftime(_format_for(current_language())["tarih"])


def tarih_saat(value):
    """Tarih ve saati (24 saat) aktif dilin biçiminde yazar."""
    if not isinstance(value, datetime):
        return tarih(value)
    return value.strftime(_format_for(current_language())["tarih_saat"])


def sayi(value, ondalik_basamak=0):
    """Sayıyı aktif dilin binlik ve ondalık ayracıyla yazar."""
    if value is None:
        return ""
    formats = _format_for(current_language())
    text = "{:,.{}f}".format(value, ondalik_basamak)
    return text.replace(",", "\0").replace(".", formats["ondalik"]).replace("\0", formats["binlik"])
