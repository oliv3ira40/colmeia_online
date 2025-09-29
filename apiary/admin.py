from django.contrib import admin

from .models import Apiary, Hive, Revision, RevisionAttachment, Species


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("popular_name", "scientific_name", "group")
    search_fields = ("popular_name", "scientific_name")


@admin.register(Apiary)
class ApiaryAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "owner", "hive_count")
    search_fields = ("name", "location", "owner__username")
    list_filter = ("owner",)


class RevisionAttachmentInline(admin.TabularInline):
    model = RevisionAttachment
    extra = 0


class RevisionInline(admin.TabularInline):
    model = Revision
    extra = 0
    show_change_link = True


@admin.register(Hive)
class HiveAdmin(admin.ModelAdmin):
    list_display = (
        "identification_number",
        "popular_name",
        "species",
        "status",
        "owner",
        "apiary",
        "acquisition_date",
        "last_review_date",
    )
    list_filter = ("status", "acquisition_method", "species", "owner")
    search_fields = ("identification_number", "popular_name", "origin")
    inlines = [RevisionInline]


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ("hive", "review_date", "temperament", "queen_seen", "management_performed")
    list_filter = ("temperament", "management_performed", "queen_seen")
    search_fields = ("hive__identification_number", "hive__popular_name")
    inlines = [RevisionAttachmentInline]


@admin.register(RevisionAttachment)
class RevisionAttachmentAdmin(admin.ModelAdmin):
    list_display = ("revision", "file")
    search_fields = ("revision__hive__identification_number",)
