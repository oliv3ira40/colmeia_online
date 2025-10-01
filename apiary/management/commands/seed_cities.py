import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apiary.models import City


class Command(BaseCommand):
    help = "Carrega cidades brasileiras no formato 'Cidade - UF'."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file_path",
            default=str(Path(settings.BASE_DIR) / "docs" / "estados-cidades.json"),
            help="Caminho para o arquivo JSON com estados e cidades.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])

        if not file_path.exists():
            raise CommandError(f"Arquivo não encontrado: {file_path}")

        try:
            raw_data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Não foi possível ler o JSON: {exc}") from exc

        if not isinstance(raw_data, list):
            raise CommandError("O arquivo precisa conter uma lista de estados.")

        created = 0
        updated = 0

        for state_entry in raw_data:
            state_code = (state_entry.get("sigla") or "").strip().upper()
            cities = state_entry.get("cidades") or []

            if not state_code:
                self.stderr.write(
                    self.style.WARNING("Registro de estado ignorado: campo 'sigla' obrigatório.")
                )
                continue

            if not isinstance(cities, list):
                self.stderr.write(
                    self.style.WARNING(
                        f"Estado {state_code}: campo 'cidades' deve ser uma lista de nomes."
                    )
                )
                continue

            for city_name in cities:
                if not isinstance(city_name, str):
                    self.stderr.write(
                        self.style.WARNING(
                            f"Estado {state_code}: cidade ignorada porque não é uma string."
                        )
                    )
                    continue

                formatted_name = f"{city_name.strip()} - {state_code}"
                city, was_created = City.objects.update_or_create(name=formatted_name)

                if was_created:
                    created += 1
                    action = "criada"
                else:
                    updated += 1
                    action = "atualizada"

                self.stdout.write(
                    self.style.SUCCESS(f"Cidade '{city.name}' {action} com sucesso.")
                )

        summary = f"Seed concluída: {created} criada(s), {updated} atualizada(s)."
        self.stdout.write(summary)
