"""Custom AdminSite implementation with configurable menu."""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass

from django.contrib.admin import AdminSite
from django.core.exceptions import PermissionDenied
from django.urls import NoReverseMatch, reverse
from django.utils.text import slugify

from .models import MenuConfig, MenuItem

logger = logging.getLogger(__name__)


@dataclass
class _MenuEntry:
    app_key: str
    app_label: str
    app_name: str
    model_dict: dict[str, object]


class ColmeiaAdminSite(AdminSite):
    """Admin site that keeps the default behaviour with a configurable menu."""

    def get_app_list(self, request):
        base_app_list = super().get_app_list(request)
        user = getattr(request, "user", None)
        if not user or user.is_anonymous or user.is_superuser:
            return base_app_list

        try:
            config = (
                MenuConfig.objects.prefetch_related("items")
                .filter(scope=MenuConfig.Scope.NON_SUPERUSER, active=True)
                .order_by("-updated_at")
                .first()
            )
        except Exception:  # pragma: no cover - defensive fallback
            logger.exception("Unable to load menu configuration; falling back to default menu.")
            return base_app_list

        if not config:
            return base_app_list

        builder = _MenuBuilder(self, request, config)
        try:
            app_list = builder.build()
        except Exception:  # pragma: no cover - defensive fallback
            logger.exception("Error while building custom admin menu; falling back to default menu.")
            return base_app_list

        if not app_list:
            return base_app_list
        return app_list


class _MenuBuilder:
    """Helper responsible for converting MenuConfig entries to admin app_list."""

    def __init__(self, site: ColmeiaAdminSite, request, config: MenuConfig) -> None:
        self.site = site
        self.request = request
        self.config = config

    def build(self) -> list[dict[str, object]]:
        items = self.config.items.all().order_by("order", "id")
        grouped: OrderedDict[str, dict[str, object]] = OrderedDict()
        for item in items:
            entry = self._build_entry(item)
            if entry is None:
                continue
            app_dict = grouped.setdefault(
                entry.app_key,
                {
                    "app_label": entry.app_label,
                    "name": entry.app_name,
                    "app_url": "#",
                    "has_module_perms": True,
                    "models": [],
                },
            )
            app_dict["models"].append(entry.model_dict)

        return list(grouped.values())

    # === Builders ===
    def _build_entry(self, item: MenuItem) -> _MenuEntry | None:
        if item.item_type == MenuItem.ItemType.MODEL:
            return self._build_model_entry(item)
        if item.item_type == MenuItem.ItemType.URL:
            return self._build_link_entry(item)
        return None

    def _build_model_entry(self, item: MenuItem) -> _MenuEntry | None:
        model = item.get_model()
        if model is None:
            return None
        if model not in self.site._registry:
            return None

        model_admin = self.site._registry[model]
        perms = model_admin.get_model_perms(self.request)
        if not any(perms.values()):
            return None

        model_meta = model._meta
        label = item.label or model_meta.verbose_name_plural.title()
        changelist_url = self._reverse_or_none(
            f"admin:{model_meta.app_label}_{model_meta.model_name}_changelist"
        )
        if changelist_url is None:
            return None
        add_url = None
        if perms.get("add"):
            add_url = self._reverse_or_none(
                f"admin:{model_meta.app_label}_{model_meta.model_name}_add"
            )

        app_config = model_meta.app_config
        group_name = item.group_label.strip() if item.group_label else app_config.verbose_name
        app_key = slugify(group_name) or app_config.label
        model_dict = {
            "name": label,
            "object_name": model_meta.object_name,
            "perms": perms,
            "admin_url": changelist_url,
            "add_url": add_url,
            "view_only": not perms.get("change", False),
        }
        return _MenuEntry(
            app_key=app_key,
            app_label=app_config.label,
            app_name=group_name,
            model_dict=model_dict,
        )

    def _build_link_entry(self, item: MenuItem) -> _MenuEntry | None:
        permission_codename = item.permission_codename.strip()
        if permission_codename and not self.request.user.has_perm(permission_codename):
            return None

        url = None
        if item.url_name:
            url = self._reverse_or_none(item.url_name)
        if not url and item.absolute_url:
            url = item.absolute_url
        if not url:
            return None

        label = item.label or item.url_name or item.absolute_url
        group_name = item.group_label.strip() if item.group_label else "Links"
        app_key = slugify(group_name) or "links"
        model_dict = {
            "name": label,
            "object_name": "CustomLink",
            "perms": {"add": False, "change": False, "delete": False, "view": True},
            "admin_url": url,
            "view_only": True,
        }
        return _MenuEntry(
            app_key=app_key,
            app_label=app_key,
            app_name=group_name,
            model_dict=model_dict,
        )

    # === Helpers ===
    def _reverse_or_none(self, name: str) -> str | None:
        try:
            return reverse(name)
        except NoReverseMatch:
            return None
        except PermissionDenied:
            return None
