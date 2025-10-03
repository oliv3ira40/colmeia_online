"""Custom AdminConfig to wire the controlled admin site as default."""

from django.contrib.admin.apps import AdminConfig


class ControlledAdminConfig(AdminConfig):
    default_site = "core.admin_site.ControlledAdminSite"
