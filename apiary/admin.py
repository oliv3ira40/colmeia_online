from django.contrib import admin

from .models import (
    Apiary,
    BoxModel,
    City,
    CreatorProfile,
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
        )


class OwnerRestrictedAdmin(Select2AdminMixin, admin.ModelAdmin):
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
class SpeciesAdmin(Select2AdminMixin, admin.ModelAdmin):
    list_display = ("popular_name", "scientific_name", "group")
    search_fields = ("popular_name", "scientific_name")


@admin.register(Apiary)
class ApiaryAdmin(OwnerRestrictedAdmin):
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
class HiveAdmin(OwnerRestrictedAdmin):
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
    inlines = [RevisionInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "apiary" and not request.user.is_superuser:
            kwargs["queryset"] = Apiary.objects.owned_by(request.user)
        if db_field.name == "origin_hive" and not request.user.is_superuser:
            kwargs["queryset"] = Hive.objects.owned_by(request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Revision)
class RevisionAdmin(Select2AdminMixin, admin.ModelAdmin):
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
        "review_type",
        "queen_seen",
        "temperament",
        "brood_level",
        "food_level",
        "pollen_level",
        "colony_strength",
    )
    search_fields = ("hive__identification_number", "hive__popular_name")
    inlines = [RevisionAttachmentInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "hive",
                    "review_date",
                    "review_type",
                    "queen_seen",
                    "temperament",
                    "brood_level",
                    "food_level",
                    "pollen_level",
                    "colony_strength",
                    "hive_weight",
                    "management_description",
                    "notes",
                )
            },
        ),
        (
            "Informações de colheita",
            {
                "fields": (
                    "honey_harvest_quantity",
                    "propolis_harvest_quantity",
                    "wax_harvest_quantity",
                    "pollen_harvest_quantity",
                    "harvest_notes",
                ),
                "classes": ("revision-harvest-group",),
            },
        ),
        (
            "Informações de alimentação",
            {
                "fields": (
                    "feeding_energy_type",
                    "feeding_energy_quantity",
                    "feeding_protein_type",
                    "feeding_protein_quantity",
                    "feeding_notes",
                ),
                "classes": ("revision-feeding-group",),
            },
        ),
    )

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
class RevisionAttachmentAdmin(Select2AdminMixin, admin.ModelAdmin):
    list_display = ("revision", "file")
    search_fields = ("revision__hive__identification_number",)


@admin.register(BoxModel)
class BoxModelAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(CreatorProfile)
class CreatorProfileAdmin(Select2AdminMixin, admin.ModelAdmin):
    list_display = ("name", "city", "phone", "user")
    search_fields = ("name", "phone", "city__name", "user__username")
    list_filter = ("city",)
    filter_horizontal = ("species",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("user", "city")
        if request.user.is_superuser:
            return queryset
        has_profile = CreatorProfile.objects.filter(user=request.user).exists()
        if has_profile:
            return queryset
        return queryset.filter(user=request.user)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return not CreatorProfile.objects.filter(user=request.user).exists()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.user_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return CreatorProfile.objects.filter(user=request.user).exists()
        return obj.user_id == request.user.id

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and "user" in form.base_fields:
            field = form.base_fields["user"]
            field.initial = request.user
            field.disabled = True
        return form
