from django.contrib import admin

from .forms import ColmeiaForm, RevisaoForm
from .models import (
    Apiary,
    BoxModel,
    City,
    CreatorNetworkEntry,
    Hive,
    Revision,
    RevisionAttachment,
    Species,
)


class Select2AdminMixin:
    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
            )
        }
        js = (
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.full.min.js",
            "apiary/js/hive_species_filter.js",
            "apiary/js/conditional-fields.js"
        )


class BaseAdmin(Select2AdminMixin, admin.ModelAdmin):
    class Media(Select2AdminMixin.Media):
        pass
        # js = ("apiary/js/conditional-fields.js",)


class BaseInline(admin.TabularInline):
    class Media:
        pass
        # js = ("apiary/js/conditional-fields.js",)


class OwnerRestrictedAdmin(BaseAdmin):
    owner_field_name = "owner"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(**{self.owner_field_name: request.user})

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if request.user.is_superuser:
            return tuple(list_display)
        return tuple(
            field for field in list_display if field != self.owner_field_name
        )

    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request))
        if request.user.is_superuser:
            return tuple(list_filter)
        return tuple(
            item
            for item in list_filter
            if item != self.owner_field_name
        )

    def get_exclude(self, request, obj=None):
        exclude = list(super().get_exclude(request, obj) or [])
        if not request.user.is_superuser and self.owner_field_name not in exclude:
            exclude.append(self.owner_field_name)
        return tuple(exclude)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            setattr(obj, self.owner_field_name, request.user)
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and self.owner_field_name in form.base_fields:
            field = form.base_fields[self.owner_field_name]
            if obj is not None:
                field.initial = getattr(obj, self.owner_field_name)
            else:
                field.initial = request.user
            field.disabled = True
        return form


@admin.register(Species)
class SpeciesAdmin(BaseAdmin):
    list_display = ("popular_name", "scientific_name", "group")
    search_fields = ("popular_name", "scientific_name")


@admin.register(BoxModel)
class BoxModelAdmin(BaseAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


@admin.register(City)
class CityAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Apiary)
class ApiaryAdmin(OwnerRestrictedAdmin):
    list_display = ("name", "city", "owner", "hive_count")
    search_fields = ("name", "city__name", "owner__username")
    list_filter = ("owner", "city")


class RevisionAttachmentInline(BaseInline):
    model = RevisionAttachment
    extra = 0


@admin.register(Hive)
class ColmeiaAdmin(OwnerRestrictedAdmin):
    list_display = (
        "identification_number",
        "popular_name",
        "species",
        "status",
        "next_division_date",
        "owner",
        "apiary",
        "acquisition_date",
        "last_review_date",
    )
    list_filter = (
        "status",
        "acquisition_method",
        "species",
        "owner",
    )
    search_fields = ("identification_number", "popular_name", "origin")
    form = ColmeiaForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "apiary" and not request.user.is_superuser:
            kwargs["queryset"] = Apiary.objects.owned_by(request.user)
        if db_field.name == "origin_hive" and not request.user.is_superuser:
            kwargs["queryset"] = Hive.objects.owned_by(request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Revision)
class RevisaoAdmin(BaseAdmin):
    list_display = (
        "hive",
        "review_date",
        "review_type",
        "queen_seen",
        "temperament",
        "brood_level",
        "food_level",
        "pollen_level",
        "colony_strength",
    )
    list_filter = (
        "queen_seen",
        "review_type",
        "temperament",
        "brood_level",
        "food_level",
        "pollen_level",
        "colony_strength",
    )
    search_fields = ("hive__identification_number", "hive__popular_name")
    inlines = [RevisionAttachmentInline]
    form = RevisaoForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(hive__owner=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hive" and not request.user.is_superuser:
            kwargs["queryset"] = Hive.objects.owned_by(request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(RevisionAttachment)
class RevisionAttachmentAdmin(BaseAdmin):
    list_display = ("revision", "file")
    search_fields = ("revision__hive__identification_number",)


@admin.register(CreatorNetworkEntry)
class CreatorNetworkEntryAdmin(OwnerRestrictedAdmin):
    owner_field_name = "user"
    list_display = ("name", "city", "phone", "is_opt_in")
    list_filter = ("is_opt_in",)
    search_fields = ("name", "phone", "city__name", "user__username")
    filter_horizontal = ("species",)
