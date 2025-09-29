import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apiary.models import Species


def _normalize_states(states):
    if not states:
        return []
    if not isinstance(states, (list, tuple)):
        raise ValueError("O campo 'ufs' deve ser uma lista de siglas de estados.")
    cleaned_states = []
    for state in states:
        if not isinstance(state, str):
            raise ValueError("Cada UF deve ser uma string.")
        cleaned_states.append(state.strip().upper())
    return cleaned_states


class Command(BaseCommand):
    help = "Carrega ou atualiza espécies a partir de um arquivo JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file_path",
            default=str(Path(settings.BASE_DIR) / "docs" / "especies.json"),
            help="Caminho para o arquivo JSON com os dados das espécies.",
        )
        parser.add_argument(
            "--group",
            dest="default_group",
            default=Species.SpeciesGroup.STINGLESS,
            choices=[choice[0] for choice in Species.SpeciesGroup.choices],
            help="Grupo padrão a ser atribuído às espécies importadas.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])
        default_group = options["default_group"]

        if not file_path.exists():
            raise CommandError(f"Arquivo não encontrado: {file_path}")

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Não foi possível ler o JSON: {exc}") from exc

        if not isinstance(data, list):
            raise CommandError("O arquivo JSON deve conter uma lista de espécies.")

        created_count = 0
        updated_count = 0

        for index, entry in enumerate(data, start=1):
            scientific_name = (entry.get("nome_cientifica") or "").strip()
            if not scientific_name:
                self.stderr.write(
                    self.style.WARNING(
                        f"Registro #{index} ignorado: 'nome_cientifica' é obrigatório."
                    )
                )
                continue

            popular_name = (entry.get("nome_popular") or "").strip()
            if not popular_name:
                popular_name = scientific_name

            try:
                states = _normalize_states(entry.get("ufs"))
            except ValueError as exc:
                self.stderr.write(
                    self.style.WARNING(
                        f"Registro '{scientific_name}' ignorado: {exc}"
                    )
                )
                continue

            characteristics = (entry.get("caracteristicas") or "").strip()
            default_temperament = entry.get("temperamento_padrao")
            if isinstance(default_temperament, str):
                default_temperament = default_temperament.strip() or None

            defaults = {
                "group": default_group,
                "popular_name": popular_name,
                "states": states,
                "characteristics": characteristics,
                "default_temperament": default_temperament,
            }

            species, created = Species.objects.update_or_create(
                scientific_name=scientific_name,
                defaults=defaults,
            )

            if created:
                created_count += 1
                action = "criada"
            else:
                updated_count += 1
                action = "atualizada"

            self.stdout.write(
                self.style.SUCCESS(
                    f"Espécie '{species.scientific_name}' {action} com sucesso."
                )
            )

        summary_message = (
            f"Importação concluída: {created_count} criada(s), "
            f"{updated_count} atualizada(s)."
        )
        self.stdout.write(summary_message)
