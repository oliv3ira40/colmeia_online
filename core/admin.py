"""Admin registrations for the configurable admin menu."""

from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.db import DatabaseError
from django.shortcuts import redirect
from django.urls import reverse

from .admin_site import site
from .models import MenuConfig, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = (
        "order",
        "item_type",
        "section",
        "label",
        "app_label",
        "model_name",
        "url_name",
        "absolute_url",
        "permission_codename",
    )
    ordering = ("order", "id")


class _DatabaseSafeAdminMixin:
    """Mixin that prevents admin crashes when the menu tables are missing."""

    database_error_message = _(
        "As tabelas do menu personalizado ainda não foram geradas. "
        "Execute as migrations correspondentes (makemigrations/migrate)."
    )

    def _handle_database_error(self, request):
        messages.error(request, self.database_error_message)
        return redirect(reverse(f"{self.admin_site.name}:index"))

    def changelist_view(self, request, extra_context=None):  # type: ignore[override]
        try:
            return super().changelist_view(request, extra_context)
        except DatabaseError:
            return self._handle_database_error(request)

    def add_view(self, request, form_url="", extra_context=None):  # type: ignore[override]
        try:
            return super().add_view(request, form_url, extra_context)
        except DatabaseError:
            return self._handle_database_error(request)

    def change_view(self, request, object_id, form_url="", extra_context=None):  # type: ignore[override]
        try:
            return super().change_view(request, object_id, form_url, extra_context)
        except DatabaseError:
            return self._handle_database_error(request)

    def delete_view(self, request, object_id, extra_context=None):  # type: ignore[override]
        try:
            return super().delete_view(request, object_id, extra_context)
        except DatabaseError:
            return self._handle_database_error(request)


@admin.register(MenuConfig, site=site)
class MenuConfigAdmin(_DatabaseSafeAdminMixin, admin.ModelAdmin):
    list_display = ("name", "scope", "active", "include_unlisted", "updated_at")
    list_filter = ("scope", "active")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = (MenuItemInline,)

    def has_module_permission(self, request):  # type: ignore[override]
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):  # type: ignore[override]
        return request.user.is_superuser

    def has_add_permission(self, request):  # type: ignore[override]
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):  # type: ignore[override]
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):  # type: ignore[override]
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):  # type: ignore[override]
        obj.full_clean()
        super().save_model(request, obj, form, change)


@admin.register(MenuItem, site=site)
class MenuItemAdmin(_DatabaseSafeAdminMixin, admin.ModelAdmin):
    list_display = (
        "display_label",
        "config",
        "item_type",
        "order",
    )
    list_filter = ("item_type", "config__scope")
    search_fields = (
        "label",
        "app_label",
        "model_name",
        "url_name",
        "permission_codename",
    )
    ordering = ("config__name", "order", "id")
    autocomplete_fields = ("config",)

    def has_module_permission(self, request):  # type: ignore[override]
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):  # type: ignore[override]
        return request.user.is_superuser

    def has_add_permission(self, request):  # type: ignore[override]
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):  # type: ignore[override]
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):  # type: ignore[override]
        return request.user.is_superuser

    @admin.display(description=_("Rótulo"))
    def display_label(self, obj: MenuItem) -> str:
        return obj.label or obj.model_name or obj.url_name or str(obj.pk)
