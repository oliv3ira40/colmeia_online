"""Customização do dashboard do Django Admin para usuários não superusuários."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.db.models import F, Q
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone

from apiary.models import (
    Apiary,
    CreatorNetworkEntry,
    Hive,
    Revision,
    RevisionAttachment,
)


@dataclass(frozen=True)
class RevisionEntry:
    change_url: str
    hive_name: str
    hive_url: str
    species_name: str
    species_scientific_name: str | None
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


@dataclass(frozen=True)
class ObservationHiveEntry:
    change_url: str
    name: str
    species_name: str
    apiary_name: str | None
    apiary_url: str | None
    status_display: str
    last_review_display: str


@dataclass(frozen=True)
class UpcomingDivisionEntry:
    change_url: str
    name: str
    species_name: str
    apiary_name: str | None
    apiary_url: str | None
    next_division_display: str
    next_division_iso: str
    is_overdue: bool


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
                species_scientific_name=hive.species.scientific_name or None,
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


def _build_observation_hives(user) -> List[ObservationHiveEntry]:
    hives = (
        Hive.objects.owned_by(user)
        .filter(status=Hive.HiveStatus.OBSERVATION)
        .select_related("species", "apiary")
        .order_by("popular_name", "identification_number")
    )
    entries: List[ObservationHiveEntry] = []
    for hive in hives:
        if hive.last_review_date:
            last_review_display, _ = _format_datetime(hive.last_review_date)
            last_review = f"Última revisão em {last_review_display}"
        else:
            last_review = "Nunca revisada"
        apiary = hive.apiary
        entries.append(
            ObservationHiveEntry(
                change_url=reverse("admin:apiary_hive_change", args=[hive.pk]),
                name=str(hive),
                species_name=hive.species.popular_name,
                apiary_name=apiary.name if apiary else None,
                apiary_url=reverse("admin:apiary_apiary_change", args=[apiary.pk]) if apiary else None,
                status_display=hive.get_status_display(),
                last_review_display=last_review,
            )
        )
    return entries


def _build_upcoming_divisions(user) -> List[UpcomingDivisionEntry]:
    today = timezone.localdate()
    hives = (
        Hive.objects.owned_by(user)
        .filter(next_division_date__isnull=False)
        .select_related("species", "apiary")
        .order_by("next_division_date", "identification_number")
    )
    entries: List[UpcomingDivisionEntry] = []
    for hive in hives:
        next_date = hive.next_division_date
        if not next_date:
            continue
        apiary = hive.apiary
        entries.append(
            UpcomingDivisionEntry(
                change_url=reverse("admin:apiary_hive_change", args=[hive.pk]),
                name=str(hive),
                species_name=hive.species.popular_name,
                apiary_name=apiary.name if apiary else None,
                apiary_url=reverse("admin:apiary_apiary_change", args=[apiary.pk]) if apiary else None,
                next_division_display=next_date.strftime("%d/%m/%Y"),
                next_division_iso=next_date.isoformat(),
                is_overdue=next_date < today,
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
        "observation_hives": _build_observation_hives(user),
        "upcoming_divisions": _build_upcoming_divisions(user),
        "create_revision_url": reverse("admin:apiary_revision_add"),
    }


def _delete_user_owned_data(user) -> None:
    attachments_qs = RevisionAttachment.objects.filter(
        revision__hive__owner=user
    )
    for attachment in attachments_qs.iterator(chunk_size=100):
        if attachment.file:
            attachment.file.delete(save=False)
        attachment.delete()

    revisions_qs = Revision.objects.filter(hive__owner=user)
    for revision in revisions_qs.iterator(chunk_size=100):
        revision.delete()

    hives_qs = Hive.objects.filter(owner=user)
    for hive in hives_qs.iterator(chunk_size=50):
        if hive.photo:
            hive.photo.delete(save=False)
        hive.delete()

    Apiary.objects.filter(owner=user).delete()
    CreatorNetworkEntry.objects.filter(user=user).delete()


@staff_member_required
def delete_personal_data_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user = request.user
        with transaction.atomic():
            _delete_user_owned_data(user)
            user.delete()
        logout(request)
        return redirect(f"{reverse('admin:login')}?deleted=1")

    context = {
        **admin.site.each_context(request),
        "title": "Excluir meus dados",
        "apiaries_count": Apiary.objects.filter(owner=request.user).count(),
        "hives_count": Hive.objects.filter(owner=request.user).count(),
        "revisions_count": Revision.objects.filter(hive__owner=request.user).count(),
        "attachments_count": RevisionAttachment.objects.filter(
            revision__hive__owner=request.user
        ).count(),
        "hive_photos_count": Hive.objects.filter(
            owner=request.user, photo__isnull=False
        ).exclude(photo="").count(),
        "has_creator_network_entry": CreatorNetworkEntry.objects.filter(user=request.user).exists(),
    }
    return TemplateResponse(request, "admin/delete_personal_data.html", context)


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


if not getattr(admin.site, "_colmeia_delete_data_url", False):
    original_get_urls = admin.site.get_urls

    def get_urls():
        urls = original_get_urls()
        custom_urls = [
            path(
                "excluir-meus-dados/",
                admin.site.admin_view(delete_personal_data_view),
                name="delete_personal_data",
            )
        ]
        return custom_urls + urls

    admin.site.get_urls = get_urls
    admin.site._colmeia_delete_data_url = True
