"""Custom ``AdminSite`` with configurable menu for non-superusers."""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import Iterable, cast

from django.apps import apps
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db import DatabaseError
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst, slugify

from .models import MenuConfig, MenuItem

logger = logging.getLogger(__name__)


class ControlledAdminSite(AdminSite):
    """Admin site that exposes a curated menu for non-superusers."""

    menu_scope = MenuConfig.MenuScope.NON_SUPERUSER

    def get_app_list(self, request):  # type: ignore[override]
        default_app_list = super().get_app_list(request)
        if request.user.is_superuser:
            return default_app_list

        try:
            config = (
                MenuConfig.objects.filter(scope=self.menu_scope, active=True)
                .prefetch_related("items")
                .order_by("-updated_at")
                .first()
            )
        except DatabaseError:
            logger.debug("MenuConfig table unavailable, returning default admin menu.")
            return default_app_list

        if config is None:
            return default_app_list

        items = list(config.items.all())
        if not items:
            return default_app_list

        builder = _MenuBuilder(self, request, default_app_list)
        custom_menu = builder.build(items, include_unlisted=config.include_unlisted)
        if custom_menu is None:
            return default_app_list
        return custom_menu


@dataclass
class _MenuGroup:
    key: str
    name: str
    app_label: str
    app_url: str | None
    models: list[dict]


class _MenuBuilder:
    """Utility responsible for building the admin ``app_list`` structure."""

    def __init__(self, admin_site: AdminSite, request, default_app_list: Iterable[dict]):
        self.admin_site = admin_site
        self.request = request
        self.default_app_list = list(default_app_list)
        self.groups: "OrderedDict[str, _MenuGroup]" = OrderedDict()
        self.included_models: set[tuple[str, str]] = set()

    # Public API ---------------------------------------------------------
    def build(
        self,
        menu_items: Iterable[MenuItem],
        *,
        include_unlisted: bool,
    ) -> list[dict] | None:
        for item in menu_items:
            try:
                if item.item_type == MenuItem.ItemType.MODEL:
                    self._add_model_item(item)
                elif item.item_type == MenuItem.ItemType.URL:
                    self._add_link_item(item)
            except Exception:  # pragma: no cover - defensive guard
                logger.exception("Erro ao montar item de menu %s", item.pk)

        if not self.groups:
            return None

        if include_unlisted:
            self._append_unlisted_entries()

        return [self._serialize_group(group) for group in self.groups.values()]

    # Internal helpers --------------------------------------------------
    def _add_model_item(self, item: MenuItem) -> None:
        if not item.app_label or not item.model_name:
            return

        try:
            model = apps.get_model(item.app_label, item.model_name)
        except LookupError:
            logger.warning(
                "Modelo %s.%s não encontrado para o menu", item.app_label, item.model_name
            )
            return

        model_admin = self.admin_site._registry.get(model)
        if model_admin is None:
            logger.debug(
                "Modelo %s não está registrado no admin, ignorando", model.__name__
            )
            return

        if not model_admin.has_module_permission(self.request):
            return

        perms = model_admin.get_model_perms(self.request)
        if not any(perms.values()):
            return

        info = (model_admin.opts.app_label, model_admin.opts.model_name)
        label = item.label or capfirst(model_admin.opts.verbose_name_plural)
        model_dict = {
            "name": label,
            "object_name": model_admin.opts.object_name,
            "perms": perms,
        }

        if perms.get("view") or perms.get("change"):
            try:
                model_dict["admin_url"] = reverse(
                    f"{self.admin_site.name}:{info[0]}_{info[1]}_changelist",
                )
            except NoReverseMatch:
                logger.debug(
                    "URL do changelist não encontrada para %s.%s", info[0], info[1]
                )

        if perms.get("add"):
            try:
                model_dict["add_url"] = reverse(
                    f"{self.admin_site.name}:{info[0]}_{info[1]}_add",
                )
            except NoReverseMatch:
                logger.debug(
                    "URL de criação não encontrada para %s.%s", info[0], info[1]
                )

        model_dict["view_only"] = not perms.get("change")

        group = self._resolve_group(item, model_admin)
        group.models.append(model_dict)
        self.included_models.add(info)

    def _add_link_item(self, item: MenuItem) -> None:
        url = None
        if item.url_name:
            try:
                url = reverse(item.url_name)
            except NoReverseMatch:
                logger.info("URL nomeada %s não encontrada", item.url_name)
        if url is None and item.absolute_url:
            url = item.absolute_url
        if url is None:
            return

        if item.permission_codename:
            permission_codename = item.permission_codename.strip()
            if permission_codename and not self.request.user.has_perm(permission_codename):
                return

        label = item.label or item.url_name or item.absolute_url
        perms = {"add": False, "change": False, "delete": False, "view": True}
        model_dict = {
            "name": label,
            "object_name": label,
            "perms": perms,
            "admin_url": url,
            "view_only": True,
        }

        group = self._resolve_group(item, None)
        group.models.append(model_dict)

    def _resolve_group(self, item: MenuItem, model_admin) -> _MenuGroup:
        if item.section:
            display_name = item.section
            group_key = f"section::{slugify(item.section) or 'section'}"
            app_label = slugify(item.section) or "section"
            app_url: str | None = None
        elif model_admin is not None:
            app_config = model_admin.opts.app_config
            display_name = capfirst(app_config.verbose_name)
            group_key = f"app::{app_config.label}" if app_config else f"app::{item.app_label}"
            app_label = app_config.label if app_config else item.app_label
            try:
                app_url = reverse(
                    f"{self.admin_site.name}:app_list",
                    kwargs={"app_label": app_label},
                )
            except NoReverseMatch:
                app_url = None
        else:
            display_name = "Links"
            group_key = "section::links"
            app_label = "links"
            app_url = None

        group = self.groups.get(group_key)
        if group is None:
            group = _MenuGroup(
                key=group_key,
                name=display_name,
                app_label=app_label,
                app_url=app_url,
                models=[],
            )
            self.groups[group_key] = group
        return group

    def _append_unlisted_entries(self) -> None:
        for app_entry in self.default_app_list:
            app_label = app_entry.get("app_label")
            if not app_label:
                continue
            group_key = f"app::{app_label}"
            group = self.groups.get(group_key)
            if group is None:
                group = _MenuGroup(
                    key=group_key,
                    name=app_entry.get("name", capfirst(app_label)),
                    app_label=app_label,
                    app_url=app_entry.get("app_url"),
                    models=[],
                )
                self.groups[group_key] = group

            for model_dict in app_entry.get("models", []):
                object_name = model_dict.get("object_name")
                if not object_name:
                    continue
                identifier = (app_label, object_name.lower())
                if identifier in self.included_models:
                    continue
                group.models.append(model_dict)

    @staticmethod
    def _serialize_group(group: _MenuGroup) -> dict:
        app_url = group.app_url or "#"
        return {
            "name": group.name,
            "app_label": group.app_label,
            "app_url": app_url,
            "models": group.models,
        }


site = cast(ControlledAdminSite, admin.site)
