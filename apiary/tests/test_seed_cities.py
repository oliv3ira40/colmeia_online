import json
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from apiary.models import City


class SeedCitiesCommandTests(TestCase):
    def setUp(self):
        file_path = Path(settings.BASE_DIR) / "docs" / "estados-cidades.json"
        with file_path.open(encoding="utf-8") as handler:
            raw_data = json.load(handler)

        expected = []
        for entry in raw_data:
            state_code = entry["sigla"]
            for city_name in entry["cidades"]:
                expected.append(f"{city_name} - {state_code}")

        self.expected_names = expected

    def test_seed_cities_populates_all_entries(self):
        call_command("seed_cities")
        self.assertEqual(City.objects.count(), len(self.expected_names))

        call_command("seed_cities")
        self.assertEqual(City.objects.count(), len(self.expected_names))

        for name in self.expected_names:
            self.assertTrue(City.objects.filter(name=name).exists())
