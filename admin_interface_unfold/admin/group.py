from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin

admin.site.unregister(Group)
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    def count_permissions(self, obj):
        return obj.permissions.count()
    count_permissions.short_description = _('Permissions')

    def count_users(self, obj):
        return obj.user_set.count()
    count_users.short_description = _('Usuários')
    list_display = ('name', 'count_users', 'count_permissions')
