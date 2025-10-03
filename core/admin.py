"""Admin registrations for the configurable admin menu."""

from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

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


@admin.register(MenuConfig, site=site)
class MenuConfigAdmin(admin.ModelAdmin):
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
class MenuItemAdmin(admin.ModelAdmin):
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
