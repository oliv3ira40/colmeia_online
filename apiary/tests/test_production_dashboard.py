from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apiary.models import Apiary, Hive, Revision, Species

class ProductionDashboardViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="manager",
            password="testpass123",
            is_staff=True,
            email="manager@example.com",
        )
        self.client.force_login(self.user)
        self.species = Species.objects.create(
            group=Species.SpeciesGroup.STINGLESS,
            scientific_name="Melipona quadrifasciata",
            popular_name="Mandaçaia",
        )
        self.apiary = Apiary.objects.create(name="Sítio Flor do Mel", owner=self.user)
        self.hive = Hive.objects.create(
            owner=self.user,
            popular_name="Colmeia A",
            species=self.species,
            apiary=self.apiary,
            acquisition_method=Hive.AcquisitionMethod.DIVISION,
        )
        aware_date = timezone.now()
        Revision.objects.create(
            hive=self.hive,
            review_date=aware_date,
            review_type=Revision.RevisionType.HARVEST,
            honey_harvest_amount=Decimal("1200"),
            propolis_harvest_amount=Decimal("250"),
            wax_harvest_amount=Decimal("180"),
            pollen_harvest_amount=Decimal("90"),
        )
        other_user = User.objects.create_user(
            username="visitor",
            password="pass456",
            is_staff=True,
            email="visitor@example.com",
        )
        other_species = Species.objects.create(
            group=Species.SpeciesGroup.STINGLESS,
            scientific_name="Melipona scutellaris",
            popular_name="Uruçu",
        )
        other_apiary = Apiary.objects.create(name="Apiário Vizinho", owner=other_user)
        other_hive = Hive.objects.create(
            owner=other_user,
            popular_name="Colmeia B",
            species=other_species,
            apiary=other_apiary,
            acquisition_method=Hive.AcquisitionMethod.CAPTURE,
        )
        Revision.objects.create(
            hive=other_hive,
            review_date=aware_date,
            review_type=Revision.RevisionType.HARVEST,
            honey_harvest_amount=Decimal("500"),
        )

    def test_dashboard_context_contains_expected_blocks(self):
        response = self.client.get(reverse("production-dashboard"))
        self.assertEqual(response.status_code, 200)
        monthly_table = response.context["monthly_table"]
        self.assertEqual(len(monthly_table["rows"]), 12)
        cards = response.context["cards"]
        self.assertEqual(cards["revision_count"], 1)
        rank = response.context["rank"]
        self.assertEqual(len(rank["items"]), 1)
        self.assertIn("season", response.context)

    def test_csv_export_returns_file(self):
        url = reverse("production-dashboard") + "?export=meses"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("producao", response["Content-Disposition"])

    def test_hive_detail_view_requires_ownership(self):
        detail_url = reverse("production-dashboard-hive-detail", args=[self.hive.pk])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context["hive"], self.hive)
        self.assertGreater(context["aggregates"]["honey"], 0)

    def test_dashboard_filters_do_not_show_other_user_data(self):
        response = self.client.get(reverse("production-dashboard"))
        chart_data = response.context["chart"]
        self.assertGreater(sum(chart_data["series"]["honey"]), 0)
        # The honey total should match only the logged user's revision (1200)
        total_honey = response.context["monthly_table"]["totals"]["honey"]
        self.assertEqual(total_honey, Decimal("1200"))
