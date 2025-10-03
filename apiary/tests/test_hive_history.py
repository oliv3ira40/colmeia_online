from __future__ import annotations

from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apiary.models import Apiary, Hive, QuickObservation, Revision, Species


class HiveHistoryViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="historian",
            password="testpass123",
            email="historian@example.com",
            is_staff=True,
        )
        self.client.force_login(self.user)
        self.species = Species.objects.create(
            group=Species.SpeciesGroup.STINGLESS,
            scientific_name="Melipona quadrifasciata",
            popular_name="Mandaçaia",
        )
        self.apiary = Apiary.objects.create(name="Apiário Central", owner=self.user)
        self.hive = Hive.objects.create(
            owner=self.user,
            popular_name="Colmeia 01",
            species=self.species,
            apiary=self.apiary,
            acquisition_method=Hive.AcquisitionMethod.DIVISION,
        )
        other_user = User.objects.create_user(
            username="other",
            password="pass456",
            email="other@example.com",
            is_staff=True,
        )
        other_species = Species.objects.create(
            group=Species.SpeciesGroup.STINGLESS,
            scientific_name="Melipona scutellaris",
            popular_name="Uruçu",
        )
        other_apiary = Apiary.objects.create(name="Apiário Vizinho", owner=other_user)
        self.other_hive = Hive.objects.create(
            owner=other_user,
            popular_name="Colmeia 99",
            species=other_species,
            apiary=other_apiary,
            acquisition_method=Hive.AcquisitionMethod.CAPTURE,
        )

    def test_page_loads_without_hive(self):
        response = self.client.get(reverse("hive-history"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["selected_hive"])
        self.assertIsNone(response.context["timeline_page"])
        self.assertIn(self.hive, response.context["available_hives"])

    def test_timeline_merges_revision_and_observation(self):
        revision_date = timezone.now() - timedelta(days=2)
        Revision.objects.create(
            hive=self.hive,
            review_date=revision_date,
            review_type=Revision.RevisionType.HARVEST,
            honey_harvest_amount=Decimal("1000"),
            energetic_food_amount=Decimal("200"),
            management_description="Inspeção geral.",
        )
        QuickObservation.objects.create(
            hive=self.hive,
            date=timezone.localdate(),
            notes="Observação rápida do dia.",
        )
        url = reverse("hive-history") + f"?hive={self.hive.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        page = response.context["timeline_page"]
        self.assertIsNotNone(page)
        self.assertEqual(len(page.object_list), 2)
        types = {item["type"] for item in page.object_list}
        self.assertEqual(types, {"revision", "observation"})
        summary = response.context["summary"]
        self.assertEqual(summary["produced"]["honey"], Decimal("1000"))
        self.assertEqual(summary["consumed"]["energetic"], Decimal("200"))

    def test_user_cannot_access_foreign_hive(self):
        url = reverse("hive-history") + f"?hive={self.other_hive.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
