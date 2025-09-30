"""Customização do dashboard do Django Admin para usuários não superusuários."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db.models import F, Q
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from apiary.models import Apiary, Hive, Revision


@dataclass(frozen=True)
class RevisionEntry:
    change_url: str
    hive_name: str
    hive_url: str
    species_name: str
    apiary_name: str | None
    apiary_url: str | None
    review_date_display: str
    review_time_iso: str


@dataclass(frozen=True)
class HiveEntry:
    change_url: str
    name: str
    species_name: str
    apiary_name: str | None
    apiary_url: str | None
    status_display: str
    add_revision_url: str


_original_admin_index = admin.site.index


def _format_datetime(value) -> tuple[str, str]:
    local_value = timezone.localtime(value)
    return local_value.strftime("%d/%m/%Y %H:%M"), local_value.isoformat()


def _build_recent_revisions(user) -> List[RevisionEntry]:
    revisions = (
        Revision.objects.owned_by(user)
        .select_related("hive", "hive__species", "hive__apiary")
        .order_by("-review_date")[:10]
    )
    entries: List[RevisionEntry] = []
    for revision in revisions:
        formatted_datetime, iso_datetime = _format_datetime(revision.review_date)
        hive = revision.hive
        apiary = hive.apiary
        entries.append(
            RevisionEntry(
                change_url=reverse("admin:apiary_revision_change", args=[revision.pk]),
                hive_name=str(hive),
                hive_url=reverse("admin:apiary_hive_change", args=[hive.pk]),
                species_name=hive.species.popular_name,
                # TODO: Dando erro aqui: unexpected keyword argument 'species_scientific_name'
                species_scientific_name=hive.species.scientific_name,
                apiary_name=apiary.name if apiary else None,
                apiary_url=reverse("admin:apiary_apiary_change", args=[apiary.pk]) if apiary else None,
                review_date_display=formatted_datetime,
                review_time_iso=iso_datetime,
            )
        )
    return entries


def _build_overdue_hives(user) -> List[HiveEntry]:
    now = timezone.now()
    cutoff = now - timedelta(days=7)
    hives = (
        Hive.objects.owned_by(user)
        .filter(Q(last_review_date__lt=cutoff) | Q(last_review_date__isnull=True))
        .select_related("species", "apiary")
        .order_by(F("last_review_date").asc(nulls_first=True), "identification_number")[:50]
    )
    entries: List[HiveEntry] = []
    add_revision_base_url = reverse("admin:apiary_revision_add")
    for hive in hives:
        if hive.last_review_date:
            formatted_datetime, _ = _format_datetime(hive.last_review_date)
            days_since = (now - hive.last_review_date).days
            status_display = f"Última revisão: {formatted_datetime} (há {days_since} dias)"
        else:
            status_display = "Nunca revisada"
        apiary = hive.apiary
        entries.append(
            HiveEntry(
                change_url=reverse("admin:apiary_hive_change", args=[hive.pk]),
                name=str(hive),
                species_name=hive.species.popular_name,
                apiary_name=apiary.name if apiary else None,
                apiary_url=reverse("admin:apiary_apiary_change", args=[apiary.pk]) if apiary else None,
                status_display=status_display,
                add_revision_url=f"{add_revision_base_url}?hive={hive.pk}",
            )
        )
    return entries


def _build_cards(user) -> Dict[str, Dict[str, int | str]]:
    apiaries = Apiary.objects.owned_by(user)
    hives = Hive.objects.owned_by(user)
    species_count = hives.values_list("species_id", flat=True).distinct().count()
    return {
        "apiaries": {
            "count": apiaries.count(),
            "url": reverse("admin:apiary_apiary_changelist"),
        },
        "hives": {
            "count": hives.count(),
            "url": reverse("admin:apiary_hive_changelist"),
        },
        "species": {
            "count": species_count,
            "url": reverse("admin:apiary_species_changelist"),
        },
    }


def _build_dashboard_context(user) -> Dict[str, object]:
    return {
        "cards": _build_cards(user),
        "recent_revisions": _build_recent_revisions(user),
        "overdue_hives": _build_overdue_hives(user),
        "create_revision_url": reverse("admin:apiary_revision_add"),
    }


def _custom_admin_index(self: AdminSite, request, extra_context=None):
    if request.user.is_superuser:
        return _original_admin_index(request, extra_context=extra_context)

    context = {
        **self.each_context(request),
        "title": self.index_title,
        "app_list": self.get_app_list(request),
    }
    if extra_context:
        context.update(extra_context)
    context.update(_build_dashboard_context(request.user))

    return TemplateResponse(request, "admin/custom_dashboard.html", context)


if not getattr(admin.site, "_colmeia_custom_index", False):
    admin.site.index = _custom_admin_index.__get__(admin.site, admin.sites.AdminSite)
    admin.site._colmeia_custom_index = True
