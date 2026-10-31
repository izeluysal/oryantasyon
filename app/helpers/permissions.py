"""Merkezi yetki kontrolü: tek `can()` fonksiyonu, önce izolasyon sonra rol kuralları."""
from flask import g

from app.helpers.roles import ROLE_ADMIN, ROLE_AUDITOR, ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER

# Aksiyon -> (yazma mı, işletme yöneticisine açık mı). Denetim yalnızca okuma aksiyonlarına erişir.
ACTIONS = {
    "business.manage": (True, False),
    "user.view": (False, True),
    "user.create": (True, True),
    "user.edit": (True, True),
    "user.delete": (True, True),
    "user.export": (False, True),
    "log.view": (False, True),
    "errorlog.view": (False, False),
    "security.manage": (True, False),
    "deleted.view": (False, True),
    "deleted.restore": (True, True),
}


def effective_business_id():
    """İsteğin bağlamındaki işletme: işletme kullanıcısında kendi işletmesi, yöneticide seçili simülasyon."""
    return getattr(g, "business_id", None)


def can(user, action, resource_business_id=None):
    """Kullanıcının aksiyonu yapıp yapamayacağını döndürür.

    Sıra: yonetici her zaman izinli; diğer roller için önce izolasyon (kaynağın işletmesi kullanıcının
    bağlamındaki işletmeyle eşleşmeli), sonra rol bazlı kural. Denetim rolü hiçbir yazma aksiyonu yapamaz.
    """
    if not user.is_authenticated or action not in ACTIONS:
        return False
    if user.role == ROLE_ADMIN:
        return True
    is_write, business_admin_allowed = ACTIONS[action]
    if resource_business_id is not None and resource_business_id != user.business_id:
        return False
    if resource_business_id is None and action.startswith(("user.", "deleted.")):
        # İşletme kullanıcısı için işletmesiz (platform) kaynak yoktur.
        return False
    if user.role == ROLE_AUDITOR:
        return not is_write and business_admin_allowed
    if user.role == ROLE_BUSINESS_ADMIN:
        return business_admin_allowed
    if user.role == ROLE_BUSINESS_USER:
        return False
    return False
