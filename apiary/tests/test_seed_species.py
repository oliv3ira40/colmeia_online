import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.conf import settings
from django.test import TestCase

from apiary.models import Species


settings.MIGRATION_MODULES = {
    **getattr(settings, "MIGRATION_MODULES", {}),
    "apiary": None,
}


class SeedSpeciesCommandTests(TestCase):
    def setUp(self):
        super().setUp()
        self.temp_file = tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False)
        self.addCleanup(self._cleanup_temp_file)

    def _cleanup_temp_file(self):
        self.temp_file.close()
        try:
            Path(self.temp_file.name).unlink(missing_ok=True)
        except TypeError:
            Path(self.temp_file.name).unlink()

    def _write_payload(self, payload):
        self.temp_file.seek(0)
        self.temp_file.truncate()
        json.dump(payload, self.temp_file, ensure_ascii=False)
        self.temp_file.flush()

    def test_seed_species_persists_characteristics_and_group(self):
        payload = [
            {
                "nome_popular": "Abelha Teste",
                "nome_cientifico": "Testus mellis",
                "grupo": "sem_ferrao",
                "ufs": ["sp", "rj"],
                "caracteristicas": "Espécie dócil utilizada em testes.",
            },
            {
                "nome_popular": "Abelha Europeia",
                "nome_cientifico": "Apis mellifera test",
                "grupo": "apis_mellifera",
                "ufs": ["mg"],
                "caracteristicas": "Possui ferrão ativo e alta produtividade.",
            },
        ]
        self._write_payload(payload)

        call_command("seed_species", file=self.temp_file.name)

        stingless = Species.objects.get(scientific_name="Testus mellis")
        self.assertEqual(stingless.popular_name, "Abelha Teste")
        self.assertEqual(stingless.group, Species.SpeciesGroup.STINGLESS)
        self.assertEqual(stingless.states, ["SP", "RJ"])
        self.assertEqual(
            stingless.characteristics,
            "Espécie dócil utilizada em testes.",
        )

        apis = Species.objects.get(scientific_name="Apis mellifera test")
        self.assertEqual(apis.group, Species.SpeciesGroup.APIS_MELLIFERA)
        self.assertEqual(apis.states, ["MG"])
        self.assertEqual(
            apis.characteristics,
            "Possui ferrão ativo e alta produtividade.",
        )

    def test_seed_species_updates_existing_species(self):
        initial_payload = [
            {
                "nome_popular": "Abelha Inicial",
                "nome_cientifico": "Testus update",
                "grupo": "sem_ferrao",
                "ufs": ["sp"],
                "caracteristicas": "Descrição inicial.",
            }
        ]
        self._write_payload(initial_payload)
        call_command("seed_species", file=self.temp_file.name)

        updated_payload = [
            {
                "nome_popular": "Abelha Atualizada",
                "nome_cientifico": "Testus update",
                "grupo": "apis_mellifera",
                "ufs": ["rs"],
                "caracteristicas": "Descrição atualizada.",
            }
        ]
        self._write_payload(updated_payload)
        call_command("seed_species", file=self.temp_file.name)

        species = Species.objects.get(scientific_name="Testus update")
        self.assertEqual(species.popular_name, "Abelha Atualizada")
        self.assertEqual(species.group, Species.SpeciesGroup.APIS_MELLIFERA)
        self.assertEqual(species.states, ["RS"])
        self.assertEqual(species.characteristics, "Descrição atualizada.")
