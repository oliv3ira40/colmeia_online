from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Configurações principais"

    def ready(self) -> None:
        # Importações tardias para evitar problemas de inicialização circular.
        from . import admin  # noqa: F401  # registra os modelos auxiliares
        from .admin_dashboard import apply_admin_customizations
        from .admin_site import site

        apply_admin_customizations(site)
