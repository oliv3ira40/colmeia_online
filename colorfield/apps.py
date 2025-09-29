"""AppConfig stub matching the expected third-party package."""

from pathlib import Path

from django.apps import AppConfig


class ColorfieldConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "colorfield"
    path = str(Path(__file__).resolve().parent)
