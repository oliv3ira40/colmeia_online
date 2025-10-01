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
    def _resolve_group(self, raw_group, scientific_name):
        default_group = Species.SpeciesGroup.STINGLESS

        if raw_group is None or (isinstance(raw_group, str) and not raw_group.strip()):
            return default_group

        normalized_group = str(raw_group).strip().lower()
        valid_groups = {choice[0] for choice in Species.SpeciesGroup.choices}

        if normalized_group in valid_groups:
            return normalized_group

        self.stderr.write(
            self.style.WARNING(
                "Registro '%s': grupo '%s' inválido. Usando grupo padrão '%s'."
                % (scientific_name, raw_group, default_group)
            )
        )
        return default_group

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])

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
            scientific_name = (entry.get("nome_cientifico") or "").strip()
            if not scientific_name:
                self.stderr.write(
                    self.style.WARNING(
                        f"Registro #{index} ignorado: 'nome_cientifico' é obrigatório."
                    )
                )
                continue

            popular_name = (entry.get("nome_popular") or "").strip()
            if not popular_name:
                popular_name = scientific_name

            group_value = entry.get("grupo")
            group = self._resolve_group(group_value, scientific_name)

            try:
                states = _normalize_states(entry.get("ufs"))
            except ValueError as exc:
                self.stderr.write(
                    self.style.WARNING(
                        f"Registro '{scientific_name}' ignorado: {exc}"
                    )
                )
                continue

            raw_characteristics = entry.get("caracteristicas")
            if raw_characteristics is None:
                characteristics = ""
            else:
                characteristics = str(raw_characteristics).strip()
            default_temperament = entry.get("temperamento_padrao")
            if isinstance(default_temperament, str):
                default_temperament = default_temperament.strip() or None

            defaults = {
                "group": group,
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
