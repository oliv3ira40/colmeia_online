from django.core.management import call_command
from django.test import TestCase

from apiary.management.commands.seed_box_models import BOX_MODELS
from apiary.models import BoxModel


class SeedBoxModelsCommandTests(TestCase):
    def test_seed_box_models_is_idempotent(self):
        self.assertEqual(BoxModel.objects.count(), 0)

        call_command("seed_box_models")
        self.assertEqual(BoxModel.objects.count(), len(BOX_MODELS))

        call_command("seed_box_models")
        self.assertEqual(BoxModel.objects.count(), len(BOX_MODELS))

        for name, description in BOX_MODELS:
            stored = BoxModel.objects.get(name=name)
            self.assertEqual(stored.description, description)
