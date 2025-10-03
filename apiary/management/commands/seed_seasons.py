from django.core.management.base import BaseCommand

from apiary.models import Season

SEASONS = [
    {
        "name": "Outono",
        "start_month": 3,
        "start_day": 20,
        "end_month": 6,
        "end_day": 20,
    },
    {
        "name": "Inverno",
        "start_month": 6,
        "start_day": 20,
        "end_month": 9,
        "end_day": 22,
    },
    {
        "name": "Primavera",
        "start_month": 9,
        "start_day": 22,
        "end_month": 12,
        "end_day": 21,
    },
    {
        "name": "Verão",
        "start_month": 12,
        "start_day": 21,
        "end_month": 3,
        "end_day": 20,
    },
]


class Command(BaseCommand):
    help = "Carrega ou atualiza a lista de estações do ano."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for data in SEASONS:
            obj, created_flag = Season.objects.update_or_create(
                name=data["name"],
                defaults={
                    "start_month": data["start_month"],
                    "start_day": data["start_day"],
                    "end_month": data["end_month"],
                    "end_day": data["end_day"],
                },
            )
            if created_flag:
                created += 1
                action = "criada"
            else:
                updated += 1
                action = "atualizada"
            self.stdout.write(self.style.SUCCESS(f"Estação '{obj.name}' {action}."))

        summary = (
            f"Processo concluído: {created} estação(ões) criada(s), "
            f"{updated} estação(ões) atualizada(s)."
        )
        self.stdout.write(summary)
