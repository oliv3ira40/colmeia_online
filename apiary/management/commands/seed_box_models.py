from django.core.management.base import BaseCommand

from apiary.models import BoxModel

BOX_MODELS = [
    {
        "name": "INPA",
        "description": (
            "(Fernando Oliveira) – Modular vertical (ninho, sobreninho, melgueiras). "
            "É o padrão mais difundido no Brasil pela facilidade de manejo, divisão e coleta de mel. "
            "Dimensões variam por espécie (ex.: jataí, mandaçaia, uruçu etc.)."
        ),
    },
    {
        "name": "PNN",
        "description": (
            "(Paulo Nogueira-Neto) – Horizontal com “gavetas”; muito usado para jataí e mandaçaias. "
            "Facilita acessar crias, mas não é o melhor para extrair mel em grande volume."
        ),
    },
    {
        "name": "SH",
        "description": (
            "Pensada para espécies que fazem crias em “cachos” (Frieseomelitta, Leurotrigona/“lambe-olhos” etc.) "
            "e para facilitar divisões, com compartimentos horizontais e visores."
        ),
    },
    {
        "name": "Moreira (USP)",
        "description": (
            "Muito usada para Frieseomelitta varia (“marmelada”), focada em eficiência de divisão "
            "e manejo dessas espécies de crias em cachos."
        ),
    },
    {
        "name": "JCW",
        "description": (
            "Variação modular com melgueiras laterais (existe versão em “T”). "
            "Útil em cenários específicos, mas exige mais tampas/isolamentos."
        ),
    },
    {
        "name": "AF",
        "description": (
            "(Ailton Fontana) – Módulos “encaixados” num gabinete externo (tipo gaveteiro). "
            "Bom isolamento, porém construção/manutenção mais complexas e propolização pode atrapalhar."
        ),
    },
    {
        "name": "Novy",
        "description": (
            "(circular, concreto celular/argamassa) – Alta inércia térmica/acústica; "
            "pavimentos circulares com alturas adequadas aos potes de alimento. Interessante para controle térmico."
        ),
    },
    {
        "name": "Didática (com visores)",
        "description": (
            "Foco educativo/observação; pode servir para manejo leve."
        ),
    },
    {
        "name": "Cacuí (família Schwade)",
        "description": (
            "Adaptação vertical inspirada no INPA, criada na Amazônia (reservas Amanã/Mamirauá)."
        ),
    },
    {
        "name": "Kerr, Capel (horizontal/vertical), Baiano, Isis, Maria, Juliane",
        "description": (
            "Modelos menos comuns ou variações regionais com usos mais nichados."
        ),
    },
]


class Command(BaseCommand):
    help = "Carrega ou atualiza a lista padrão de modelos de caixas."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for entry in BOX_MODELS:
            obj, created_flag = BoxModel.objects.update_or_create(
                name=entry["name"],
                defaults={"description": entry["description"]},
            )
            if created_flag:
                created += 1
                action = "criado"
            else:
                updated += 1
                action = "atualizado"
            self.stdout.write(self.style.SUCCESS(f"Modelo '{obj.name}' {action}."))

        summary = (
            f"Processo concluído: {created} modelo(s) criado(s), "
            f"{updated} modelo(s) atualizado(s)."
        )
        self.stdout.write(summary)
