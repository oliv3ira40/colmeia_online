from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

admin.site.unregister(User)
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    def group_name(self, obj):
        return obj.groups.first()
    group_name.short_description = _('Grupo')

    list_display = ('is_active', 'first_name', 'last_name', 'username', 'email', 'is_staff', 'is_superuser', 'group_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    list_editable = ('is_active',)
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('is_active', 'first_name')
    list_display_links = ('first_name', 'last_name')

    fieldsets = (
        (
            _("Login"), {
                "classes": ["tab"],
                "fields": ("username", "password")
            }
        ),
        (
            _("Personal info"), {
                "classes": ["tab"],
                "fields": ("first_name", "last_name", "email"),
            }
        ),
        (
            _("Permissions"), {
                "classes": ["tab"],
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
            }
        ),
        (
            _("Important dates"), {
                "classes": ["tab"],
                "fields": ("last_login", "date_joined")
            }
        ),
    )
