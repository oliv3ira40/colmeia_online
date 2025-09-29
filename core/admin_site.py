from __future__ import annotations

from datetime import timedelta

from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.db.models import F, Q
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from apiary.models import Apiary, Hive, Revision


class CustomAdminSite(AdminSite):
    site_header = "ComeiasOnline"
    site_title = "ComeiasOnline"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        if request.user.is_active and request.user.is_superuser:
            return super().index(request, extra_context)

        available_apps = self.get_app_list(request)

        context = {
            **self.each_context(request),
            "title": self.index_title,
            "available_apps": available_apps,
            "app_list": available_apps,
        }
        context.update(self.get_dashboard_context(request))

        if extra_context:
            context.update(extra_context)

        request.current_app = self.name
        return TemplateResponse(request, "admin/custom_index.html", context)

    def get_dashboard_context(self, request):
        user = request.user
        now = timezone.localtime(timezone.now())
        threshold = now - timedelta(days=7)

        apiaries_qs = Apiary.objects.owned_by(user)
        hives_qs = Hive.objects.owned_by(user)

        apiary_count = apiaries_qs.count()
        hive_count = hives_qs.count()
        species_count = hives_qs.values("species_id").distinct().count()

        recent_revisions_qs = (
            Revision.objects.owned_by(user)
            .select_related("hive__species", "hive__apiary")
            .order_by("-review_date")[:10]
        )

        recent_revisions = [
            {
                "instance": revision,
                "change_url": reverse(
                    "admin:apiary_revision_change", args=[revision.pk]
                ),
                "hive_url": reverse("admin:apiary_hive_change", args=[revision.hive_id]),
                "species": revision.hive.species,
                "apiary": revision.hive.apiary,
                "review_date": timezone.localtime(revision.review_date),
            }
            for revision in recent_revisions_qs
        ]

        overdue_qs = (
            hives_qs.filter(
                Q(last_review_date__lt=threshold) | Q(last_review_date__isnull=True)
            )
            .select_related("species", "apiary")
            .order_by(F("last_review_date").asc(nulls_first=True))
        )

        overdue_hives = []
        for hive in overdue_qs[:50]:
            last_review = (
                timezone.localtime(hive.last_review_date)
                if hive.last_review_date
                else None
            )
            overdue_hives.append(
                {
                    "instance": hive,
                    "change_url": reverse("admin:apiary_hive_change", args=[hive.pk]),
                    "species": hive.species,
                    "apiary": hive.apiary,
                    "last_review": last_review,
                    "add_revision_url": f"{reverse('admin:apiary_revision_add')}?hive={hive.pk}",
                }
            )

        return {
            "dashboard_now": now,
            "overdue_threshold": threshold,
            "apiary_count": apiary_count,
            "hive_count": hive_count,
            "species_count": species_count,
            "recent_revisions": recent_revisions,
            "overdue_hives": overdue_hives,
            "new_revision_url": reverse("admin:apiary_revision_add"),
        }


admin_site = CustomAdminSite(name="admin")

User = get_user_model()
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
