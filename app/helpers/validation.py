"""Form girdisi doğrulama: sunucu tarafında zorunlu; hata anahtarı döner (çeviri çağıranda yapılır)."""
import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PUBLISH_URL_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}$", re.IGNORECASE)
MIN_PASSWORD_LENGTH = 8
MAX_NAME_LENGTH = 255
MAX_PHONE_LENGTH = 50


def clean_text(value, max_length):
    """Metni kırpar ve uzunluk sınırına getirir."""
    return (value or "").strip()[:max_length]


def validate_user_form(form, require_password):
    """Kullanıcı formunu doğrular.

    Returns:
        (değerler, hata_anahtarı) ikilisi; hata yoksa hata_anahtarı None'dır.
    """
    values = {
        "full_name": clean_text(form.get("full_name"), MAX_NAME_LENGTH),
        "email": clean_text(form.get("email"), MAX_NAME_LENGTH).lower(),
        "phone": clean_text(form.get("phone"), MAX_PHONE_LENGTH),
        "role": form.get("role", ""),
        "password": form.get("password", ""),
        "theme": form.get("theme", "light"),
    }
    if not values["full_name"]:
        return values, "validation.full_name_required"
    if not EMAIL_PATTERN.match(values["email"]):
        return values, "validation.email_invalid"
    if values["theme"] not in ("light", "dark"):
        return values, "validation.theme_invalid"
    password = values["password"]
    if (require_password or password) and len(password) < MIN_PASSWORD_LENGTH:
        return values, "validation.password_short"
    return values, None


def validate_business_form(form):
    """İşletme formunu doğrular: (değerler, hata_anahtarı)."""
    values = {
        "business_name": clean_text(form.get("business_name"), MAX_NAME_LENGTH),
        "publish_url": clean_text(form.get("publish_url"), MAX_NAME_LENGTH).lower(),
    }
    if not values["business_name"]:
        return values, "validation.business_name_required"
    if not PUBLISH_URL_PATTERN.match(values["publish_url"]):
        return values, "validation.publish_url_invalid"
    return values, None
