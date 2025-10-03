"""Admin registration for menu configuration models."""

from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import MenuConfig, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = (
        "order",
        "item_type",
        "group_label",
        "label",
        "app_label",
        "model_name",
        "url_name",
        "absolute_url",
        "permission_codename",
    )

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(MenuConfig)
class MenuConfigAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]
    list_display = ("scope", "active", "updated_at")
    list_filter = ("scope", "active")
    ordering = ("scope", "-updated_at")
    actions = ["activate"]

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.action(description=_("Ativar configuração selecionada"))
    def activate(self, request, queryset):
        for config in queryset:
            MenuConfig.objects.filter(scope=config.scope, active=True).exclude(pk=config.pk).update(active=False)
            config.active = True
            config.save(update_fields=["active", "updated_at"])
