"""Sidebar menü verisi: tek kaynak. Etiketler metin değil çeviri anahtarıdır."""
from app.helpers.roles import ALL_ROLES, ROLE_ADMIN, ROLE_AUDITOR, ROLE_BUSINESS_ADMIN

# endpoint: url_for hedefi; roles: görebilen roller; children: 2. seviye (grup ise endpoint verilmez).
MENU_ITEMS = [
    {
        "key": "dashboard",
        "label": "menu.dashboard",
        "icon": "bi-speedometer2",
        "endpoint": "dashboard.index",
        "roles": ALL_ROLES,
    },
    {
        "key": "businesses",
        "label": "menu.businesses",
        "icon": "bi-buildings",
        "endpoint": "businesses.index",
        "roles": (ROLE_ADMIN,),
    },
    {
        "key": "deleted_report",
        "label": "menu.deleted_report",
        "icon": "bi-trash3",
        "endpoint": "deleted_report.index",
        "roles": (ROLE_ADMIN, ROLE_BUSINESS_ADMIN, ROLE_AUDITOR),
    },
    {
        "key": "settings",
        "label": "menu.settings",
        "icon": "bi-gear",
        "endpoint": "settings.index",
        "roles": (ROLE_ADMIN, ROLE_BUSINESS_ADMIN, ROLE_AUDITOR),
    },
]


def visible_menu(role):
    """Role göre süzülmüş menüyü döndürür; çocuğu kalmayan grup gösterilmez."""
    result = []
    for item in MENU_ITEMS:
        if role not in item["roles"]:
            continue
        children = [child for child in item.get("children", []) if role in child["roles"]]
        if "children" in item and not children:
            continue
        result.append(dict(item, children=children))
    return result
