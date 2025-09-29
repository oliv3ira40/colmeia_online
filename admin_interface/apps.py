"""AppConfig proxying to the bundled admin interface implementation."""

from pathlib import Path

from admin_interface_unfold.apps import AdminInterfaceConfig as BaseAdminInterfaceConfig


class AdminInterfaceConfig(BaseAdminInterfaceConfig):
    """Ensure Django discovers the local static and template assets."""

    path = str(Path(__file__).resolve().parent)
