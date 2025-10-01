import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apiary.models import City


class Command(BaseCommand):
    help = "Carrega ou atualiza a lista de cidades brasileiras."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file_path",
            default=str(Path(settings.BASE_DIR) / "docs" / "estados-cidades.json"),
            help="Caminho para o arquivo JSON contendo estados e cidades.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])

        if not file_path.exists():
            raise CommandError(f"Arquivo não encontrado: {file_path}")

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Não foi possível ler o JSON: {exc}") from exc

        states = data.get("estados")
        if not isinstance(states, list):
            raise CommandError("Estrutura inválida: o arquivo deve conter a chave 'estados' com uma lista.")

        created = 0
        updated = 0

        for state in states:
            uf = state.get("sigla")
            cities = state.get("cidades")

            if not uf or not isinstance(uf, str):
                self.stderr.write(self.style.WARNING("UF inválida encontrada; registro ignorado."))
                continue

            if not isinstance(cities, list):
                self.stderr.write(
                    self.style.WARNING(f"Lista de cidades inválida para a UF {uf!r}; registro ignorado.")
                )
                continue

            uf = uf.strip().upper()

            for city_name in cities:
                if not isinstance(city_name, str):
                    self.stderr.write(
                        self.style.WARNING(f"Cidade inválida na UF {uf!r}; valor ignorado: {city_name!r}.")
                    )
                    continue

                formatted_name = f"{city_name.strip()} - {uf}"
                obj, created_flag = City.objects.update_or_create(name=formatted_name)

                if created_flag:
                    created += 1
                    action = "criada"
                else:
                    updated += 1
                    action = "atualizada"

                self.stdout.write(self.style.SUCCESS(f"Cidade '{obj.name}' {action}."))

        summary = (
            f"Importação concluída: {created} cidade(s) criada(s), "
            f"{updated} cidade(s) atualizada(s)."
        )
        self.stdout.write(summary)
