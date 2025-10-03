from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig as DjangoAdminConfig


class AdminMenuConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "admin_menu"
    verbose_name = "Menu personalizado do admin"


class ColmeiaAdminConfig(DjangoAdminConfig):
    default = False
    default_site = "admin_menu.sites.ColmeiaAdminSite"
