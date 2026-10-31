"""Merkezi yetki kontrolü: tek `can()` fonksiyonu, önce izolasyon sonra rol kuralları."""
from flask import g

from app.helpers.roles import ROLE_AUDITOR, ROLE_ADMIN, ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER

READERS = (ROLE_BUSINESS_ADMIN, ROLE_AUDITOR)
WRITERS = (ROLE_BUSINESS_ADMIN,)

# Aksiyon -> roller (yonetici ayrıca değerlendirilir), kapsam şartı ve yalnızca-öğrenen bayrağı.
# scoped: kaynağın işletmesi verilmek zorundadır; learner_only: platform yöneticisine de kapalıdır
# (eğitimi almak, kullanıcının kendi işletmesine bağlı öğrenme kaydıdır).
ACTIONS = {
    "business.manage": {"roles": (), "scoped": False},
    "user.view": {"roles": READERS, "scoped": True},
    "user.create": {"roles": WRITERS, "scoped": True},
    "user.edit": {"roles": WRITERS, "scoped": True},
    "user.delete": {"roles": WRITERS, "scoped": True},
    "user.export": {"roles": READERS, "scoped": True},
    "log.view": {"roles": READERS, "scoped": True},
    "errorlog.view": {"roles": (), "scoped": False},
    "security.manage": {"roles": (), "scoped": False},
    "deleted.view": {"roles": READERS, "scoped": True},
    "deleted.restore": {"roles": WRITERS, "scoped": True},
    "training.take": {"roles": (ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER), "scoped": True, "learner_only": True},
    "training.report": {"roles": READERS, "scoped": True},
}


def effective_business_id():
    """İsteğin bağlamındaki işletme: işletme kullanıcısında kendi işletmesi, yöneticide seçili simülasyon."""
    return getattr(g, "business_id", None)


def can(user, action, resource_business_id=None):
    """Kullanıcının aksiyonu yapıp yapamayacağını döndürür.

    Sıra: yonetici her zaman izinli (yalnızca-öğrenen aksiyonlar hariç); diğer roller için önce izolasyon
    (kaynağın işletmesi kullanıcının işletmesiyle eşleşmeli), sonra rol kuralı. Denetim rolü hiçbir yazma
    aksiyonunu yapamaz: yazma aksiyonlarının rol listesinde yoktur.
    """
    spec = ACTIONS.get(action)
    if spec is None or not user.is_authenticated:
        return False
    if user.role == ROLE_ADMIN:
        return not spec.get("learner_only", False)
    if user.business_id is None or user.role not in spec["roles"]:
        return False
    if spec["scoped"] and resource_business_id is None:
        return False
    return resource_business_id is None or resource_business_id == user.business_id
