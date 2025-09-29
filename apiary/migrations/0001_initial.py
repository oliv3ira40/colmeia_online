# Generated manually because automated migrations are unavailable in the execution environment.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import apiary.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Species",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("group", models.CharField(choices=[("apis_mellifera", "Apis mellifera"), ("sem_ferrao", "Sem ferrão")], max_length=20)),
                ("scientific_name", models.CharField(max_length=255)),
                ("popular_name", models.CharField(max_length=255)),
                ("characteristics", models.TextField(blank=True)),
                (
                    "states",
                    models.JSONField(blank=True, default=list, help_text="Lista das UFs onde a espécie é encontrada"),
                ),
                ("default_temperament", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "ordering": ["popular_name", "scientific_name"],
                "verbose_name_plural": "Espécies",
            },
        ),
        migrations.CreateModel(
            name="Apiary",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("location", models.CharField(max_length=255)),
                ("hive_count", models.PositiveIntegerField(default=0, editable=False)),
                ("notes", models.TextField(blank=True)),
                (
                    "owner",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="apiaries", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "Meliponário/Apiário",
                "verbose_name_plural": "Meliponários/Apiários",
            },
        ),
        migrations.CreateModel(
            name="Hive",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "identification_number",
                    models.CharField(default=apiary.models.generate_hive_identifier, editable=False, max_length=20, unique=True),
                ),
                ("acquisition_method", models.CharField(choices=[("compra", "Compra"), ("troca", "Troca"), ("divisao", "Divisão"), ("captura", "Captura"), ("doacao", "Doação")], max_length=20)),
                ("origin", models.CharField(blank=True, max_length=255)),
                ("acquisition_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("producao", "Em produção"),
                            ("observacao", "Em observação"),
                            ("orfa", "Órfã"),
                            ("morta", "Morta"),
                            ("doadavendida", "Doada/Vendida"),
                            ("perdida", "Perdida"),
                        ],
                        default="producao",
                        max_length=20,
                    ),
                ),
                ("last_review_date", models.DateTimeField(blank=True, editable=False, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "apiary",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hives",
                        to="apiary.apiary",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="hives", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "species",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hives", to="apiary.species"),
                ),
                (
                    "popular_name",
                    models.CharField(max_length=255),
                ),
            ],
            options={
                "ordering": ["-acquisition_date", "identification_number"],
                "verbose_name": "Colmeia",
                "verbose_name_plural": "Colmeias",
            },
        ),
        migrations.CreateModel(
            name="Revision",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("review_date", models.DateTimeField()),
                ("queen_seen", models.BooleanField(default=False)),
                (
                    "brood_level",
                    models.CharField(
                        choices=[
                            ("nenhuma", "Nenhuma"),
                            ("pouca", "Pouca"),
                            ("moderada", "Moderada"),
                            ("abundante", "Abundante"),
                        ],
                        max_length=20,
                        verbose_name="Cria",
                    ),
                ),
                (
                    "food_level",
                    models.CharField(
                        choices=[
                            ("nenhum", "Nenhum"),
                            ("pouco", "Pouco"),
                            ("moderado", "Moderado"),
                            ("abundante", "Abundante"),
                        ],
                        max_length=20,
                        verbose_name="Alimento/Reservas",
                    ),
                ),
                (
                    "pollen_level",
                    models.CharField(
                        choices=[
                            ("nenhum", "Nenhum"),
                            ("pouco", "Pouco"),
                            ("moderado", "Moderado"),
                            ("abundante", "Abundante"),
                        ],
                        max_length=20,
                        verbose_name="Pólen",
                    ),
                ),
                (
                    "colony_strength",
                    models.CharField(
                        choices=[
                            ("fraca", "Fraca"),
                            ("media", "Média"),
                            ("forte", "Forte"),
                        ],
                        max_length=20,
                        verbose_name="Força da colônia",
                    ),
                ),
                (
                    "temperament",
                    models.CharField(
                        choices=[
                            ("muito_mansa", "Muito mansa"),
                            ("mansa", "Mansa"),
                            ("media", "Média"),
                            ("arisca", "Arisca"),
                            ("agressiva", "Agressiva"),
                        ],
                        max_length=20,
                    ),
                ),
                ("hive_weight", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("notes", models.TextField(blank=True)),
                (
                    "management_description",
                    models.TextField(blank=True, verbose_name="Descreva manejo(s) realizado(s)"),
                ),
                (
                    "hive",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revisions", to="apiary.hive"),
                ),
            ],
            options={
                "ordering": ["-review_date"],
                "verbose_name": "Revisão",
                "verbose_name_plural": "Revisões",
            },
        ),
        migrations.CreateModel(
            name="RevisionAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="revision_attachments/")),
                (
                    "revision",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="apiary.revision"),
                ),
            ],
            options={
                "verbose_name": "Anexo da Revisão",
                "verbose_name_plural": "Anexos da Revisão",
            },
        ),
    ]
