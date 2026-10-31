"""Rol sabitleri ve rol/kapsam yardımcıları."""
ROLE_ADMIN = "yonetici"
ROLE_BUSINESS_ADMIN = "isletme_yoneticisi"
ROLE_BUSINESS_USER = "isletme_kullanicisi"
ROLE_AUDITOR = "denetim"

ALL_ROLES = (ROLE_ADMIN, ROLE_BUSINESS_ADMIN, ROLE_BUSINESS_USER, ROLE_AUDITOR)
# Rol adlarının çeviri anahtarı öneki: t(ROLE_LABEL_PREFIX + rol)
ROLE_LABEL_PREFIX = "role."
