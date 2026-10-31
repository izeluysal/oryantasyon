"""Çok dillilik: dil kataloğu, t() çeviri fonksiyonu ve dil çözümleme."""
import json
import logging
import os
import time

from flask import g, has_request_context, request

logger = logging.getLogger(__name__)

DIL_BILGILERI = {
    "tr": {"ad": "Türkçe", "kisa": "TR", "bayrak": "TR", "yerel_ayar": "tr-TR", "cogul": ("one", "other")},
}
DESTEKLENEN_DILLER = tuple(DIL_BILGILERI)
VARSAYILAN_DIL = "tr"
LANGUAGE_COOKIE = "dil"

TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations")
_translations = {}
_missing_logged = {}
MISSING_LOG_INTERVAL = 60


class Anahtar:
    """Çeviri anahtarı ve parametreleri; metin alıcının dilinde sonradan üretilir."""

    def __init__(self, key, **params):
        self.key = key
        self.params = params


def cevirileri_yukle():
    """Tüm dil dosyalarını bir kez belleğe okur; bozuk dosya uygulamayı çökertmez."""
    for code in DESTEKLENEN_DILLER:
        path = os.path.join(TRANSLATIONS_DIR, code + ".json")
        try:
            with open(path, encoding="utf-8") as translation_file:
                _translations[code] = json.load(translation_file)
        except (OSError, ValueError) as error:
            logger.error("Çeviri dosyası yüklenemedi (%s): %s", code, error)
            _translations[code] = {}


def _plural_category(language, count):
    """Dilin CLDR kuralına göre çoğul kategorisini döndürür; sayı değilse 'other'."""
    if not isinstance(count, int) or isinstance(count, bool):
        return "other"
    if language in ("tr", "en"):
        return "one" if count == 1 else "other"
    return "other"


def _lookup(key, language):
    """Anahtarı aktif dilde, yoksa Türkçe'de arar; hiçbirinde yoksa None döndürür."""
    for code in (language, VARSAYILAN_DIL):
        value = _translations.get(code, {}).get(key)
        if value is not None:
            return value, code
    return None, None


def _log_missing(key):
    """Eksik anahtarı dakikada en fazla bir kez WARNING olarak loglar."""
    now = time.time()
    if now - _missing_logged.get(key, 0) >= MISSING_LOG_INTERVAL:
        _missing_logged[key] = now
        logger.warning("Eksik çeviri anahtarı: %s", key)


def current_language():
    """Aktif isteğin dilini döndürür; istek dışında varsayılan dil geçerlidir."""
    if has_request_context():
        return getattr(g, "dil", VARSAYILAN_DIL)
    return VARSAYILAN_DIL


def t(key, dil=None, **params):
    """Anahtarı çevirir. Fallback zinciri: aktif dil, Türkçe, anahtarın kendisi."""
    language = dil or current_language()
    value, found_language = _lookup(key, language)
    if value is None:
        _log_missing(key)
        return key
    if isinstance(value, dict):
        count = params.get("count")
        category = _plural_category(found_language, count)
        value = value.get(category) or value.get("other") or key
    resolved = {}
    for name, param in params.items():
        resolved[name] = t(param.key, dil=language, **param.params) if isinstance(param, Anahtar) else param
    # str.format yerine tek tek değiştirme: tanımsız yer tutucu olduğu gibi kalır, hata fırlatılmaz.
    for name, param in resolved.items():
        value = value.replace("{" + name + "}", str(param))
    return value


def resolve_anonymous_language():
    """Girişsiz istekte dil sırası: çerez, Accept-Language, varsayılan."""
    cookie_language = request.cookies.get(LANGUAGE_COOKIE)
    if cookie_language in DESTEKLENEN_DILLER:
        return cookie_language
    for part in request.headers.get("Accept-Language", "").split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code in DESTEKLENEN_DILLER:
            return code
    return VARSAYILAN_DIL
