from django.core.management.base import BaseCommand

from apiary.models import BoxModel

BOX_MODELS = [
    (
        "INPA",
        "(Fernando Oliveira) – Modular vertical (ninho, sobreninho, melgueiras). É o padrão mais difundido no Brasil pela facilidade de manejo, divisão e coleta de mel. Dimensões variam por espécie (ex.: jataí, mandaçaia, uruçu etc.).",
    ),
    (
        "PNN",
        "(Paulo Nogueira-Neto) – Horizontal com “gavetas”; muito usado para jataí e mandaçaias. Facilita acessar crias, mas não é o melhor para extrair mel em grande volume.",
    ),
    (
        "SH",
        "Pensada para espécies que fazem crias em “cachos” (Frieseomelitta, Leurotrigona/“lambe-olhos” etc.) e para facilitar divisões, com compartimentos horizontais e visores.",
    ),
    (
        "Moreira (USP)",
        "Muito usada para Frieseomelitta varia (“marmelada”), focada em eficiência de divisão e manejo dessas espécies de crias em cachos.",
    ),
    (
        "JCW",
        "Variação modular com melgueiras laterais (existe versão em “T”). Útil em cenários específicos, mas exige mais tampas/isolamentos.",
    ),
    (
        "AF",
        "(Ailton Fontana) – Módulos “encaixados” num gabinete externo (tipo gaveteiro). Bom isolamento, porém construção/manutenção mais complexas e propolização pode atrapalhar.",
    ),
    (
        "Novy",
        "(circular, concreto celular/argamassa) – Alta inércia térmica/acústica; pavimentos circulares com alturas adequadas aos potes de alimento. Interessante para controle térmico.",
    ),
    (
        "Didática (com visores)",
        "Foco educativo/observação; pode servir para manejo leve.",
    ),
    (
        "Cacuí (família Schwade)",
        "Adaptação vertical inspirada no INPA, criada na Amazônia (reservas Amanã/Mamirauá).",
    ),
    (
        "Kerr",
        "Modelo menos comum inspirado nos estudos de Warwick Kerr, com variações regionais de uso.",
    ),
    (
        "Capel",
        "Modelo que possui versões horizontal e vertical, utilizado em nichos específicos e adaptações regionais.",
    ),
    (
        "Baiano",
        "Variação regional focada em facilidade de construção e materiais simples.",
    ),
    (
        "Isis",
        "Modelo empregado por criadores que buscam modularidade intermediária e bom isolamento.",
    ),
    (
        "Maria",
        "Projeto voltado para pequenos espaços, priorizando visualização da postura e organização interna.",
    ),
    (
        "Juliane",
        "Modelo colaborativo desenvolvido por criadores da região Sul, com foco em divisões rápidas.",
    ),
]


class Command(BaseCommand):
    help = "Cria ou atualiza a lista padrão de modelos de caixas."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for name, description in BOX_MODELS:
            obj, was_created = BoxModel.objects.update_or_create(
                name=name,
                defaults={"description": description},
            )
            if was_created:
                created += 1
                action = "criado"
            else:
                updated += 1
                action = "atualizado"
            self.stdout.write(self.style.SUCCESS(f"Modelo '{obj.name}' {action} com sucesso."))

        summary = f"Seed concluída: {created} criado(s), {updated} atualizado(s)."
        self.stdout.write(summary)
