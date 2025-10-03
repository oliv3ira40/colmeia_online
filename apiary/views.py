"""Views for analytics and production dashboards."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, Iterable, List, Sequence
from urllib.parse import urlencode

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, DecimalField, Max, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from .models import Apiary, Hive, Revision


MONTH_LABELS = [
    _("Jan"),
    _("Fev"),
    _("Mar"),
    _("Abr"),
    _("Mai"),
    _("Jun"),
    _("Jul"),
    _("Ago"),
    _("Set"),
    _("Out"),
    _("Nov"),
    _("Dez"),
]


SEASON_CONTENT = {
    "summer": {
        "title": _("Verão"),
        "description": _(
            "Período de altas temperaturas e chuvas intensas. Garanta sombreamento,"
            " boa ventilação e atenção redobrada ao fornecimento de água."
        ),
        "tips": [
            _("Monitore o superaquecimento das caixas e faça manejo de ventilação."),
            _("Reforce potes de alimento para evitar fermentações."),
            _("Acompanhe possíveis enxameações após colheitas abundantes."),
        ],
    },
    "autumn": {
        "title": _("Outono"),
        "description": _(
            "Transição com redução de flores e temperaturas mais amenas."
            " Ajuste a alimentação e planeje divisões estratégicas."
        ),
        "tips": [
            _("Faça avaliações de reservas de alimento e complemente quando necessário."),
            _("Realize divisões apenas em colônias fortes."),
            _("Reforce o controle de pragas e cupins nas estruturas."),
        ],
    },
    "winter": {
        "title": _("Inverno"),
        "description": _(
            "Meses mais frios e secos. Colônias reduzem atividade externa,"
            " exigindo atenção ao isolamento e à oferta de recursos internos."
        ),
        "tips": [
            _("Evite aberturas prolongadas das caixas durante dias frios."),
            _("Planeje suplementação com alimentos energéticos e proteicos."),
            _("Proteja entradas contra ventos fortes e umidade excessiva."),
        ],
    },
    "spring": {
        "title": _("Primavera"),
        "description": _(
            "Floradas intensas impulsionam a produção. Época ideal para expansões"
            " e monitoramento de enxameação."
        ),
        "tips": [
            _("Amplie o espaço interno conforme o crescimento da colônia."),
            _("Acompanhe potes de pólen para garantir qualidade do alimento."),
            _("Planeje novas divisões e capturas diante de colmeias fortes."),
        ],
    },
}


RANK_METRICS = {
    "mel": {
        "field": "total_honey",
        "label": _("Mel (ml)"),
    },
    "propolis": {
        "field": "total_propolis",
        "label": _("Própolis (g)"),
    },
    "cera": {
        "field": "total_wax",
        "label": _("Cera (g)"),
    },
    "polen": {
        "field": "total_pollen",
        "label": _("Pólen (g)"),
    },
}


def _decimal_or_zero(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _parse_int_list(values: Iterable[str]) -> List[int]:
    integers: List[int] = []
    for value in values:
        try:
            integers.append(int(value))
        except (TypeError, ValueError):
            continue
    return integers


def _parse_status_list(values: Iterable[str]) -> List[str]:
    valid = {choice[0] for choice in Hive.HiveStatus.choices}
    statuses = []
    for value in values:
        if value in valid:
            statuses.append(value)
    return statuses


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _make_aware(dt: datetime) -> datetime:
    tz = timezone.get_current_timezone()
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, tz)
    return dt.astimezone(tz)


@dataclass
class DashboardFilters:
    """Encapsulate filter parameters shared between dashboard views."""

    period_start: datetime
    period_end: datetime
    reference_year: int
    selected_year: int | None
    start_date: date | None
    end_date: date | None
    apiary_ids: List[int]
    species_ids: List[int]
    statuses: List[str]
    rank_metric: str
    rank_limit: int
    errors: List[str]

    @classmethod
    def from_request(cls, request: HttpRequest) -> "DashboardFilters":
        today = timezone.localdate()
        selected_year = request.GET.get("ano")
        start_date = _parse_date(request.GET.get("inicio"))
        end_date = _parse_date(request.GET.get("fim"))
        errors: List[str] = []

        reference_year = today.year
        if selected_year:
            try:
                reference_year = int(selected_year)
            except (TypeError, ValueError):
                errors.append(_("Ano inválido informado. Foi utilizado o ano atual."))
                selected_year = None

        if start_date and end_date and start_date > end_date:
            errors.append(_("O intervalo inicial não pode ser maior que o final. O período foi ajustado."))
            start_date, end_date = end_date, start_date

        if start_date and end_date:
            reference_year = start_date.year
            period_start = _make_aware(datetime.combine(start_date, time.min))
            period_end = _make_aware(datetime.combine(end_date, time.max))
        else:
            year = reference_year
            period_start = _make_aware(datetime.combine(date(year, 1, 1), time.min))
            period_end = _make_aware(datetime.combine(date(year, 12, 31), time.max))
            start_date = None
            end_date = None

        rank_metric = request.GET.get("rank_metric", "mel")
        if rank_metric not in RANK_METRICS:
            errors.append(_("Métrica de ranking inválida. Foi utilizada a soma de mel."))
            rank_metric = "mel"

        rank_limit_str = request.GET.get("top")
        rank_limit = 10
        if rank_limit_str:
            try:
                rank_limit_candidate = int(rank_limit_str)
            except (TypeError, ValueError):
                errors.append(_("Valor inválido para o Top N. Utilizando 10."))
            else:
                rank_limit = max(1, min(rank_limit_candidate, 50))
        apiary_ids = _parse_int_list(request.GET.getlist("apiarios"))
        species_ids = _parse_int_list(request.GET.getlist("especies"))
        statuses = _parse_status_list(request.GET.getlist("situacoes"))

        return cls(
            period_start=period_start,
            period_end=period_end,
            reference_year=reference_year,
            selected_year=int(selected_year) if selected_year and selected_year.isdigit() else None,
            start_date=start_date,
            end_date=end_date,
            apiary_ids=apiary_ids,
            species_ids=species_ids,
            statuses=statuses,
            rank_metric=rank_metric,
            rank_limit=rank_limit,
            errors=errors,
        )

    def apply_revision_filters(self, queryset):
        qs = queryset.filter(review_date__range=(self.period_start, self.period_end))
        if self.apiary_ids:
            qs = qs.filter(hive__apiary_id__in=self.apiary_ids)
        if self.species_ids:
            qs = qs.filter(hive__species_id__in=self.species_ids)
        if self.statuses:
            qs = qs.filter(hive__status__in=self.statuses)
        return qs

    def apply_hive_filters(self, queryset):
        qs = queryset
        if self.apiary_ids:
            qs = qs.filter(apiary_id__in=self.apiary_ids)
        if self.species_ids:
            qs = qs.filter(species_id__in=self.species_ids)
        if self.statuses:
            qs = qs.filter(status__in=self.statuses)
        return qs

    def period_display(self) -> str:
        start = timezone.localtime(self.period_start)
        end = timezone.localtime(self.period_end)
        if start.date() == end.date():
            return _("{date}").format(date=start.strftime("%d/%m/%Y"))
        return _("{start} a {end}").format(
            start=start.strftime("%d/%m/%Y"),
            end=end.strftime("%d/%m/%Y"),
        )

    def month_sequence(self) -> List[tuple[int, int]]:
        if self.start_date:
            current_year = self.start_date.year
            current_month = self.start_date.month
        else:
            current_year = self.reference_year
            current_month = 1
        sequence: List[tuple[int, int]] = []
        for _ in range(12):
            sequence.append((current_year, current_month))
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
        return sequence

    def query_string(self, *, exclude: Sequence[str] | None = None, extra: Dict[str, str] | None = None) -> str:
        params: Dict[str, object] = {}
        if self.selected_year:
            params["ano"] = str(self.selected_year)
        if self.start_date:
            params["inicio"] = self.start_date.isoformat()
        if self.end_date:
            params["fim"] = self.end_date.isoformat()
        if self.apiary_ids:
            params["apiarios"] = [str(value) for value in self.apiary_ids]
        if self.species_ids:
            params["especies"] = [str(value) for value in self.species_ids]
        if self.statuses:
            params["situacoes"] = self.statuses
        params["rank_metric"] = self.rank_metric
        params["top"] = str(self.rank_limit)

        exclude = set(exclude or [])
        for key in list(params.keys()):
            if key in exclude:
                params.pop(key, None)

        if extra:
            params.update(extra)

        query_items: List[tuple[str, object]] = []
        for key, value in params.items():
            if isinstance(value, list):
                for item in value:
                    query_items.append((key, item))
            else:
                query_items.append((key, value))
        return urlencode(query_items, doseq=True)


class ProductionDashboardView(TemplateView):
    template_name = "admin/production_dashboard.html"

    @method_decorator(staff_member_required)
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def filters(self) -> DashboardFilters:
        return DashboardFilters.from_request(self.request)

    @cached_property
    def base_revisions(self):
        return Revision.objects.owned_by(self.request.user).filter(
            review_type=Revision.RevisionType.HARVEST
        )

    @cached_property
    def filtered_revisions(self):
        return self.filters.apply_revision_filters(self.base_revisions)

    def get(self, request: HttpRequest, *args, **kwargs):
        if request.GET.get("export") == "meses":
            return self._export_monthly_csv()
        return super().get(request, *args, **kwargs)

    def _export_monthly_csv(self) -> HttpResponse:
        rows = self._build_monthly_table()
        response = HttpResponse(content_type="text/csv")
        filename = f"producao-{self.filters.reference_year}.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        writer = csv.writer(response)
        writer.writerow([
            "Mês",
            "Mel (ml)",
            "Própolis (g)",
            "Cera (g)",
            "Pólen (g)",
            "# Colheitas",
        ])
        for row in rows["rows"]:
            writer.writerow(
                [
                    row["label"],
                    f"{row['honey']:.2f}",
                    f"{row['propolis']:.2f}",
                    f"{row['wax']:.2f}",
                    f"{row['pollen']:.2f}",
                    row["harvests"],
                ]
            )
        totals = rows["totals"]
        writer.writerow(
            [
                "Total",
                f"{totals['honey']:.2f}",
                f"{totals['propolis']:.2f}",
                f"{totals['wax']:.2f}",
                f"{totals['pollen']:.2f}",
                totals["harvests"],
            ]
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self.filters
        revisions = self.filtered_revisions

        cards = self._build_cards(revisions)
        monthly = self._build_monthly_table()
        chart = self._build_chart_data(monthly)
        rank = self._build_rank(revisions)
        season = self._current_season_card()
        availability = self._build_filters_availability()

        context.update(
            {
                "filters": filters,
                "filter_errors": filters.errors,
                "available_filters": availability,
                "cards": cards,
                "monthly_table": monthly,
                "chart": chart,
                "rank": rank,
                "season": season,
                "period_label": filters.period_display(),
                "rank_metrics": RANK_METRICS,
                "query_string": filters.query_string(),
                "selected_year": filters.selected_year or filters.reference_year,
            }
        )
        context.update(self._build_complementary_tables(revisions))
        return context

    def _build_filters_availability(self) -> Dict[str, List[Dict[str, object]]]:
        user = self.request.user
        hives = Hive.objects.owned_by(user)
        apiaries = (
            Apiary.objects.owned_by(user).order_by("name").values("id", "name")
        )
        species = (
            hives.order_by("species__popular_name")
            .values("species_id", "species__popular_name")
            .distinct()
        )
        statuses = [
            {"value": value, "label": label}
            for value, label in Hive.HiveStatus.choices
        ]
        years = list(self.base_revisions.datetimes("review_date", "year", order="DESC"))
        year_values = [dt.year for dt in years]
        if not year_values:
            current_year = timezone.localdate().year
            year_values = [current_year]
        return {
            "apiaries": list(apiaries),
            "species": list(species),
            "statuses": statuses,
            "years": year_values,
        }

    def _build_cards(self, revisions):
        aggregates = revisions.aggregate(
            honey=Coalesce(Sum("honey_harvest_amount"), Value(0), output_field=DecimalField()),
            propolis=Coalesce(Sum("propolis_harvest_amount"), Value(0), output_field=DecimalField()),
            wax=Coalesce(Sum("wax_harvest_amount"), Value(0), output_field=DecimalField()),
            pollen=Coalesce(Sum("pollen_harvest_amount"), Value(0), output_field=DecimalField()),
            revisions_count=Count("id"),
            last_review=Max("review_date"),
        )
        hives_qs = self.filters.apply_hive_filters(Hive.objects.owned_by(self.request.user))
        active_hives = hives_qs.exclude(status__in=[Hive.HiveStatus.DEAD, Hive.HiveStatus.LOST]).count()
        revisions_total = aggregates.get("revisions_count", 0)
        last_review_date = aggregates.get("last_review")
        last_review_display = None
        if last_review_date:
            last_review_display = timezone.localtime(last_review_date).strftime("%d/%m/%Y %H:%M")

        sixty_days_ago = timezone.now() - timedelta(days=60)
        overdue_hives = self.filters.apply_hive_filters(
            Hive.objects.owned_by(self.request.user).filter(
                Q(last_review_date__lt=sixty_days_ago) | Q(last_review_date__isnull=True)
            )
        )
        overdue_total = overdue_hives.count()
        total_filtered_hives = hives_qs.count()
        overdue_percentage = 0.0
        if total_filtered_hives:
            overdue_percentage = (overdue_total / total_filtered_hives) * 100

        return {
            "production": {
                "honey": _decimal_or_zero(aggregates.get("honey")),
                "propolis": _decimal_or_zero(aggregates.get("propolis")),
                "wax": _decimal_or_zero(aggregates.get("wax")),
                "pollen": _decimal_or_zero(aggregates.get("pollen")),
            },
            "active_hives": active_hives,
            "revision_count": revisions_total,
            "last_review": last_review_display,
            "overdue_percentage": overdue_percentage,
            "overdue_total": overdue_total,
        }

    def _build_monthly_table(self):
        month_keys = self.filters.month_sequence()
        monthly_data = (
            self.filtered_revisions.annotate(month=TruncMonth("review_date"))
            .values("month")
            .annotate(
                honey=Coalesce(Sum("honey_harvest_amount"), Value(0), output_field=DecimalField()),
                propolis=Coalesce(Sum("propolis_harvest_amount"), Value(0), output_field=DecimalField()),
                wax=Coalesce(Sum("wax_harvest_amount"), Value(0), output_field=DecimalField()),
                pollen=Coalesce(Sum("pollen_harvest_amount"), Value(0), output_field=DecimalField()),
                harvests=Count("id"),
            )
        )
        month_lookup = {
            (item["month"].year, item["month"].month): item for item in monthly_data if item["month"]
        }

        rows: List[Dict[str, object]] = []
        totals = {"honey": Decimal("0"), "propolis": Decimal("0"), "wax": Decimal("0"), "pollen": Decimal("0"), "harvests": 0}

        multiple_years = len({year for year, _ in month_keys}) > 1
        for year, month in month_keys:
            month_data = month_lookup.get((year, month), {})
            honey = _decimal_or_zero(month_data.get("honey")) if month_data else Decimal("0")
            propolis = _decimal_or_zero(month_data.get("propolis")) if month_data else Decimal("0")
            wax = _decimal_or_zero(month_data.get("wax")) if month_data else Decimal("0")
            pollen = _decimal_or_zero(month_data.get("pollen")) if month_data else Decimal("0")
            harvests = month_data.get("harvests", 0) if month_data else 0
            label = MONTH_LABELS[month - 1]
            if multiple_years:
                label = f"{label} {year}"
            rows.append(
                {
                    "month": month,
                    "label": label,
                    "honey": honey,
                    "propolis": propolis,
                    "wax": wax,
                    "pollen": pollen,
                    "harvests": harvests,
                }
            )
            totals["honey"] += honey
            totals["propolis"] += propolis
            totals["wax"] += wax
            totals["pollen"] += pollen
            totals["harvests"] += harvests

        return {"rows": rows, "totals": totals}

    def _build_chart_data(self, monthly_table):
        labels = [row["label"] for row in monthly_table["rows"]]
        return {
            "labels": labels,
            "series": {
                "honey": [float(row["honey"]) for row in monthly_table["rows"]],
                "propolis": [float(row["propolis"]) for row in monthly_table["rows"]],
                "wax": [float(row["wax"]) for row in monthly_table["rows"]],
                "pollen": [float(row["pollen"]) for row in monthly_table["rows"]],
            },
        }

    def _build_rank(self, revisions):
        metric_field = RANK_METRICS[self.filters.rank_metric]["field"]
        ranked = (
            revisions.values(
                "hive_id",
                "hive__identification_number",
                "hive__popular_name",
                "hive__species__popular_name",
                "hive__apiary__name",
            )
            .annotate(
                total_honey=Coalesce(Sum("honey_harvest_amount"), Value(0), output_field=DecimalField()),
                total_propolis=Coalesce(Sum("propolis_harvest_amount"), Value(0), output_field=DecimalField()),
                total_wax=Coalesce(Sum("wax_harvest_amount"), Value(0), output_field=DecimalField()),
                total_pollen=Coalesce(Sum("pollen_harvest_amount"), Value(0), output_field=DecimalField()),
                harvests=Count("id"),
                last_harvest=Max("review_date"),
            )
            .order_by(f"-{metric_field}", "hive__identification_number")[: self.filters.rank_limit]
        )
        items = []
        query_string = self.filters.query_string()
        for entry in ranked:
            last_harvest = entry["last_harvest"]
            last_harvest_display = _("Sem colheitas no período")
            if last_harvest:
                last_harvest_display = timezone.localtime(last_harvest).strftime("%d/%m/%Y %H:%M")
            detail_url = reverse("production-dashboard-hive-detail", args=[entry["hive_id"]])
            if query_string:
                detail_url = f"{detail_url}?{query_string}"
            items.append(
                {
                    "hive_id": entry["hive_id"],
                    "name": f"{entry['hive__identification_number']} · {entry['hive__popular_name']}",
                    "species": entry["hive__species__popular_name"],
                    "apiary": entry["hive__apiary__name"] or _("Sem meliponário"),
                    "honey": _decimal_or_zero(entry["total_honey"]),
                    "propolis": _decimal_or_zero(entry["total_propolis"]),
                    "wax": _decimal_or_zero(entry["total_wax"]),
                    "pollen": _decimal_or_zero(entry["total_pollen"]),
                    "harvests": entry["harvests"],
                    "last_harvest": last_harvest_display,
                    "detail_url": detail_url,
                }
            )
        return {
            "items": items,
            "metric": self.filters.rank_metric,
            "metric_label": RANK_METRICS[self.filters.rank_metric]["label"],
            "limit": self.filters.rank_limit,
        }

    def _current_season_card(self):
        today = timezone.localdate()
        month = today.month
        if month in (12, 1, 2):
            key = "summer"
        elif month in (3, 4, 5):
            key = "autumn"
        elif month in (6, 7, 8):
            key = "winter"
        else:
            key = "spring"
        content = SEASON_CONTENT[key]
        return {
            "title": content["title"],
            "description": content["description"],
            "tips": content["tips"],
        }

    def _build_complementary_tables(self, revisions):
        production_by_apiary = (
            revisions.values("hive__apiary__name")
            .annotate(total=Coalesce(Sum("honey_harvest_amount"), Value(0), output_field=DecimalField()))
            .order_by("-total")
        )
        production_by_species = (
            revisions.values("hive__species__popular_name")
            .annotate(total=Coalesce(Sum("honey_harvest_amount"), Value(0), output_field=DecimalField()))
            .order_by("-total")
        )
        apiary_rows = [
            {
                "name": entry["hive__apiary__name"] or _("Sem meliponário"),
                "total": _decimal_or_zero(entry["total"]),
            }
            for entry in production_by_apiary
        ]
        species_rows = [
            {
                "name": entry["hive__species__popular_name"],
                "total": _decimal_or_zero(entry["total"]),
            }
            for entry in production_by_species
        ]
        return {
            "production_by_apiary": apiary_rows,
            "production_by_species": species_rows,
        }


class HiveProductionDetailView(TemplateView):
    template_name = "admin/production_dashboard_hive_detail.html"

    @method_decorator(staff_member_required)
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.hive = self.get_hive()
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def filters(self) -> DashboardFilters:
        return DashboardFilters.from_request(self.request)

    def get_hive(self) -> Hive:
        try:
            hive = Hive.objects.select_related("species", "apiary", "owner").get(pk=self.kwargs["pk"])
        except Hive.DoesNotExist as exc:  # pragma: no cover - defensive
            raise Http404("Colmeia não encontrada") from exc
        user = self.request.user
        if not user.is_superuser and hive.owner_id != user.id:
            raise Http404("Colmeia não disponível para este usuário")
        return hive

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self.filters
        revisions_qs = filters.apply_revision_filters(
            self.hive.revisions.filter(review_type=Revision.RevisionType.HARVEST)
        ).order_by("-review_date")
        aggregates = revisions_qs.aggregate(
            honey=Coalesce(Sum("honey_harvest_amount"), Value(0), output_field=DecimalField()),
            propolis=Coalesce(Sum("propolis_harvest_amount"), Value(0), output_field=DecimalField()),
            wax=Coalesce(Sum("wax_harvest_amount"), Value(0), output_field=DecimalField()),
            pollen=Coalesce(Sum("pollen_harvest_amount"), Value(0), output_field=DecimalField()),
            harvests=Count("id"),
        )
        monthly = self._build_monthly_overview(revisions_qs)
        revisions = list(revisions_qs[:200])
        back_url = reverse("production-dashboard")
        query_string = filters.query_string(exclude=["top", "rank_metric"])
        if query_string:
            back_url = f"{back_url}?{query_string}"
        context.update(
            {
                "hive": self.hive,
                "filters": filters,
                "period_label": filters.period_display(),
                "aggregates": {k: _decimal_or_zero(v) for k, v in aggregates.items()},
                "revisions": revisions,
                "monthly": monthly,
                "back_url": back_url,
                "filter_errors": filters.errors,
                "create_revision_url": f"{reverse('admin:apiary_revision_add')}?hive={self.hive.pk}",
                "create_harvest_url": f"{reverse('admin:apiary_revision_add')}?hive={self.hive.pk}&review_type={Revision.RevisionType.HARVEST}",
            }
        )
        return context

    def _build_monthly_overview(self, revisions):
        monthly = (
            revisions.annotate(month=TruncMonth("review_date"))
            .values("month")
            .annotate(
                honey=Coalesce(Sum("honey_harvest_amount"), Value(0), output_field=DecimalField()),
                propolis=Coalesce(Sum("propolis_harvest_amount"), Value(0), output_field=DecimalField()),
                wax=Coalesce(Sum("wax_harvest_amount"), Value(0), output_field=DecimalField()),
                pollen=Coalesce(Sum("pollen_harvest_amount"), Value(0), output_field=DecimalField()),
            )
        )
        data = []
        for entry in monthly:
            month = entry["month"]
            label = month.strftime("%b/%Y") if month else ""
            data.append(
                {
                    "label": label,
                    "honey": _decimal_or_zero(entry["honey"]),
                    "propolis": _decimal_or_zero(entry["propolis"]),
                    "wax": _decimal_or_zero(entry["wax"]),
                    "pollen": _decimal_or_zero(entry["pollen"]),
                }
            )
        return data


production_dashboard = ProductionDashboardView.as_view()
hive_production_detail = HiveProductionDetailView.as_view()
