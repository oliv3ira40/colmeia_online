from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from PIL import UnidentifiedImageError


def generate_hive_identifier() -> str:
    """Generate a unique identifier for a hive."""
    prefix = "COL"
    while True:
        identifier = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
        if not Hive.objects.filter(identification_number=identifier).exists():
            return identifier


from .utils.images import convert_image_to_webp


def _convert_image_field_to_webp(field_file, *, field_name: str) -> None:
    file_obj = getattr(field_file, "file", None)
    if not file_obj or not isinstance(file_obj, UploadedFile):
        return

    original_name = getattr(file_obj, "name", field_file.name)
    try:
        converted = convert_image_to_webp(file_obj, original_name=original_name)
    except UnidentifiedImageError as exc:
        raise ValidationError({field_name: "Envie uma imagem válida."}) from exc

    field_file.save(converted.name, converted, save=False)


class Species(models.Model):
    class SpeciesGroup(models.TextChoices):
        APIS_MELLIFERA = "apis_mellifera", "Apis mellifera"
        STINGLESS = "sem_ferrao", "Sem ferrão"

    BRAZILIAN_STATES = [
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    ]

    group = models.CharField(
        "Grupo",
        max_length=20,
        choices=SpeciesGroup.choices,
    )
    scientific_name = models.CharField("Nome científico", max_length=255)
    popular_name = models.CharField("Nome popular", max_length=255)
    characteristics = models.TextField("Características", blank=True)
    states = models.JSONField(
        "UFs",
        default=list,
        blank=True,
        help_text="Lista das UFs onde a espécie é encontrada",
    )
    default_temperament = models.CharField(
        "Temperamento padrão",
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Espécies"
        ordering = ["popular_name", "scientific_name"]

    def __str__(self) -> str:
        return f"{self.popular_name} ({self.scientific_name})"

    def clean(self) -> None:
        """Ensure that only valid states are stored."""
        super().clean()
        if self.states:
            if not isinstance(self.states, list):
                raise ValidationError({"states": "Informe as UFs como uma lista."})
            invalid_states = [state for state in self.states if state not in dict(self.BRAZILIAN_STATES)]
            if invalid_states:
                raise ValidationError({
                    "states": "Estados inválidos informados: {}".format(
                        ", ".join(sorted(set(invalid_states)))
                    )
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ApiaryQuerySet(models.QuerySet):
    def owned_by(self, user) -> "ApiaryQuerySet":
        if user.is_superuser:
            return self
        return self.filter(owner=user)


class Apiary(models.Model):
    name = models.CharField("Nome", max_length=255)
    location = models.CharField("Localização (cidade/estado)", max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="apiaries",
        verbose_name="Responsável/Proprietário",
    )
    hive_count = models.PositiveIntegerField(
        "Qtd. de colmeias vinculadas", default=0, editable=False
    )
    notes = models.TextField("Observações", blank=True)

    objects = ApiaryQuerySet.as_manager()

    class Meta:
        verbose_name = "Meliponário/Apiário"
        verbose_name_plural = "Meliponários/Apiários"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def update_hive_count(self) -> None:
        total = self.hives.count()
        Apiary.objects.filter(pk=self.pk).update(hive_count=total)
        self.hive_count = total

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class HiveQuerySet(models.QuerySet):
    def owned_by(self, user) -> "HiveQuerySet":
        if user.is_superuser:
            return self
        return self.filter(owner=user)


class BoxModel(models.Model):
    name = models.CharField("Nome", max_length=255, unique=True)
    description = models.TextField("Descrição", blank=True)

    class Meta:
        verbose_name = "Modelo de caixa"
        verbose_name_plural = "Modelos de caixas"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField("Nome", max_length=255, unique=True)

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Hive(models.Model):
    class AcquisitionMethod(models.TextChoices):
        PURCHASE = "compra", "Compra"
        TRADE = "troca", "Troca"
        DIVISION = "divisao", "Divisão"
        CAPTURE = "captura", "Captura"
        DONATION = "doacao", "Doação"

    class HiveStatus(models.TextChoices):
        PRODUCTIVE = "producao", "Em produção"
        OBSERVATION = "observacao", "Em observação"
        ORPHAN = "orfa", "Órfã"
        DEAD = "morta", "Morta"
        DONATED = "doadavendida", "Doada/Vendida"
        LOST = "perdida", "Perdida"

    identification_number = models.CharField(
        "N. de identificação",
        max_length=20,
        unique=True,
        editable=False,
        default=generate_hive_identifier,
    )
    acquisition_method = models.CharField(
        "Método de aquisição",
        max_length=20,
        choices=AcquisitionMethod.choices,
    )
    origin = models.CharField("Origem da colmeia", max_length=255, blank=True)
    acquisition_date = models.DateField(
        "No caso de compra, qual a data de aquisição"
    )
    transfer_date = models.DateField(
        "Data de transferência para a caixa",
        null=True,
        blank=True,
        help_text="Informe quando a colmeia capturada foi transferida para a caixa.",
    )
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name="hives",
        verbose_name="Espécie",
    )
    popular_name = models.CharField("Nome popular", max_length=255)
    status = models.CharField(
        "Situação",
        max_length=20,
        choices=HiveStatus.choices,
        default=HiveStatus.PRODUCTIVE,
    )
    next_division_date = models.DateField(
        "Data da próxima divisão",
        null=True,
        blank=True,
        help_text="Data planejada para a próxima divisão da colmeia.",
    )
    apiary = models.ForeignKey(
        Apiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hives",
        verbose_name="Meliponário/Apiário",
    )
    origin_hive = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_hives",
        verbose_name="Colmeia de origem",
        help_text="No caso de divisão, selecione a colmeia de origem.",
    )
    box_model = models.ForeignKey(
        BoxModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hives",
        verbose_name="Modelo de caixa",
    )
    last_review_date = models.DateTimeField(
        "Data da última revisão", null=True, blank=True, editable=False
    )
    notes = models.TextField("Observações", blank=True)
    position = models.CharField(
        "Posição no meliponário", max_length=255, blank=True
    )
    photo = models.ImageField(
        "Foto da colmeia", upload_to="hive_photos/", blank=True, null=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hives",
        verbose_name="Proprietário",
    )

    objects = HiveQuerySet.as_manager()

    class Meta:
        verbose_name = "Colmeia"
        verbose_name_plural = "Colmeias"
        ordering = ["-acquisition_date", "identification_number"]

    def __str__(self) -> str:
        return f"{self.identification_number} - {self.popular_name}"

    def clean(self) -> None:
        super().clean()
        errors = {}

        if self.apiary_id and self.owner_id:
            apiary_owner_id = self.apiary.owner_id if self.apiary else None
            if apiary_owner_id != self.owner_id:
                errors["apiary"] = (
                    "A colmeia só pode ser vinculada a meliponários/apiários do mesmo usuário."
                )

        if self.acquisition_method == Hive.AcquisitionMethod.CAPTURE:
            if not self.transfer_date:
                errors["transfer_date"] = (
                    "Informe a data de transferência quando a colmeia é capturada."
                )
        elif self.transfer_date:
            errors["transfer_date"] = (
                "A data de transferência só deve ser preenchida quando a colmeia é capturada."
            )

        if self.acquisition_method == Hive.AcquisitionMethod.DIVISION:
            if not self.origin_hive:
                errors["origin_hive"] = (
                    "Informe a colmeia de origem quando o método de aquisição for divisão."
                )
            elif self.origin_hive_id == self.pk:
                errors["origin_hive"] = "A colmeia de origem não pode ser a própria colmeia."
            elif (
                self.origin_hive
                and self.owner_id
                and self.origin_hive.owner_id != self.owner_id
            ):
                errors["origin_hive"] = (
                    "Escolha uma colmeia de origem pertencente ao mesmo usuário."
                )
        elif self.origin_hive:
            errors["origin_hive"] = (
                "A colmeia de origem só deve ser preenchida quando o método for divisão."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        previous_apiary_id = None
        if self.pk:
            previous_apiary_id = (
                Hive.objects.filter(pk=self.pk)
                .values_list("apiary_id", flat=True)
                .first()
            )
        self.full_clean()
        if self.photo:
            _convert_image_field_to_webp(self.photo, field_name="photo")
        super().save(*args, **kwargs)
        if previous_apiary_id and previous_apiary_id != self.apiary_id:
            previous_apiary = Apiary.objects.filter(pk=previous_apiary_id).first()
            if previous_apiary:
                previous_apiary.update_hive_count()
        if self.apiary_id and self.apiary:
            self.apiary.update_hive_count()

    def delete(self, *args, **kwargs):
        apiary_id = self.apiary_id
        super().delete(*args, **kwargs)
        if apiary_id:
            apiary = Apiary.objects.filter(pk=apiary_id).first()
            if apiary:
                apiary.update_hive_count()


class RevisionQuerySet(models.QuerySet):
    def owned_by(self, user) -> "RevisionQuerySet":
        if user.is_superuser:
            return self
        return self.filter(hive__owner=user)


class Revision(models.Model):
    class ReviewType(models.TextChoices):
        ROUTINE = "rotina", "Revisão de rotina"
        DIVISION = "divisao", "Divisão"
        TREATMENT = "tratamento", "Tratamento"
        FEEDING = "alimentacao", "Alimentação"
        HARVEST = "colheita", "Colheita"

    class TemperamentChoices(models.TextChoices):
        VERY_CALM = "muito_mansa", "Muito mansa"
        CALM = "mansa", "Mansa"
        MEDIUM = "media", "Média"
        SKITTISH = "arisca", "Arisca"
        AGGRESSIVE = "agressiva", "Agressiva"

    class FeedingEnergyType(models.TextChoices):
        SYRUP = "xarope", "Xarope"
        APIS_HONEY = "mel_apis", "Mel de Apis"
        ASF_HONEY = "mel_asf", "Mel de ASF"

    class FeedingProteinType(models.TextChoices):
        POLLEN_BOMB = "bombom_polen", "Bombom de Pólen"
        SOY_BOMB = "bombom_soja", "Bombom Soja"
        POLLEN_PASTE = "pasta_polen", "Pasta de Pólen"
        SOY_PASTE = "pasta_soja", "Pasta de Soja"

    class BroodLevel(models.TextChoices):
        NONE = "nenhuma", "Nenhuma"
        LOW = "pouca", "Pouca"
        MODERATE = "moderada", "Moderada"
        ABUNDANT = "abundante", "Abundante"

    class ResourceLevel(models.TextChoices):
        NONE = "nenhum", "Nenhum"
        LOW = "pouco", "Pouco"
        MODERATE = "moderado", "Moderado"
        ABUNDANT = "abundante", "Abundante"

    class ColonyStrength(models.TextChoices):
        WEAK = "fraca", "Fraca"
        MEDIUM = "media", "Média"
        STRONG = "forte", "Forte"

    hive = models.ForeignKey(
        Hive,
        on_delete=models.CASCADE,
        related_name="revisions",
        verbose_name="Colmeia",
    )
    review_date = models.DateTimeField("Data da revisão")
    review_type = models.CharField(
        "Tipo de revisão",
        max_length=20,
        choices=ReviewType.choices,
        default=ReviewType.ROUTINE,
    )
    queen_seen = models.BooleanField("Rainha vista", default=False)
    brood_level = models.CharField(
        "Cria",
        max_length=20,
        choices=BroodLevel.choices,
        blank=True,
    )
    food_level = models.CharField(
        "Alimento/Reservas",
        max_length=20,
        choices=ResourceLevel.choices,
        blank=True,
    )
    pollen_level = models.CharField(
        "Pólen",
        max_length=20,
        choices=ResourceLevel.choices,
        blank=True,
    )
    colony_strength = models.CharField(
        "Força da colônia",
        max_length=20,
        choices=ColonyStrength.choices,
        blank=True,
    )
    temperament = models.CharField(
        "Temperamento",
        max_length=20,
        choices=TemperamentChoices.choices,
        blank=True,
    )
    hive_weight = models.DecimalField(
        "Peso da colmeia",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    notes = models.TextField("Observações", blank=True)
    management_description = models.TextField(
        "Descreva manejo(s) realizado(s)",
        blank=True,
    )
    honey_harvest_quantity = models.DecimalField(
        "Quantidade de mel colhida (ml)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    propolis_harvest_quantity = models.DecimalField(
        "Quantidade de própolis colhida (g)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    wax_harvest_quantity = models.DecimalField(
        "Quantidade de cera colhida (g)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    pollen_harvest_quantity = models.DecimalField(
        "Quantidade de pólen colhida (g)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    harvest_notes = models.TextField(
        "Observações específicas sobre a colheita",
        blank=True,
    )
    feeding_energy_type = models.CharField(
        "Tipo de alimento energético fornecido",
        max_length=20,
        choices=FeedingEnergyType.choices,
        blank=True,
    )
    feeding_energy_quantity = models.DecimalField(
        "Quantidade de alimento energético fornecido (ml ou g)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    feeding_protein_type = models.CharField(
        "Tipo de alimento proteico fornecido",
        max_length=20,
        choices=FeedingProteinType.choices,
        blank=True,
    )
    feeding_protein_quantity = models.DecimalField(
        "Quantidade de suplemento proteico fornecido (g)",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    feeding_notes = models.TextField(
        "Observações específicas sobre a alimentação",
        blank=True,
    )

    objects = RevisionQuerySet.as_manager()

    class Meta:
        verbose_name = "Revisão"
        verbose_name_plural = "Revisões"
        ordering = ["-review_date"]

    def __str__(self) -> str:
        return f"Revisão em {self.review_date:%d/%m/%Y} - {self.hive}"

    def clean(self) -> None:
        super().clean()
        errors = {}

        harvest_fields = [
            "honey_harvest_quantity",
            "propolis_harvest_quantity",
            "wax_harvest_quantity",
            "pollen_harvest_quantity",
            "harvest_notes",
        ]

        feeding_fields = [
            "feeding_energy_type",
            "feeding_energy_quantity",
            "feeding_protein_type",
            "feeding_protein_quantity",
            "feeding_notes",
        ]

        if self.review_type != Revision.ReviewType.HARVEST:
            for field_name in harvest_fields:
                value = getattr(self, field_name)
                if value not in (None, ""):
                    errors[field_name] = (
                        "Essas informações são exibidas apenas quando o tipo de revisão é Colheita."
                    )

        if self.review_type != Revision.ReviewType.FEEDING:
            for field_name in feeding_fields:
                value = getattr(self, field_name)
                if value not in (None, ""):
                    errors[field_name] = (
                        "Essas informações são exibidas apenas quando o tipo de revisão é Alimentação."
                    )

        if (
            self.review_type == Revision.ReviewType.FEEDING
            and self.feeding_energy_quantity
            and not self.feeding_energy_type
        ):
            errors["feeding_energy_type"] = (
                "Informe o tipo do alimento energético para registrar a quantidade."
            )

        if (
            self.review_type == Revision.ReviewType.FEEDING
            and self.feeding_protein_quantity
            and not self.feeding_protein_type
        ):
            errors["feeding_protein_type"] = (
                "Informe o tipo do alimento proteico para registrar a quantidade."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        Hive.objects.filter(pk=self.hive_id).update(last_review_date=self.review_date)

    def delete(self, *args, **kwargs):
        hive_id = self.hive_id
        super().delete(*args, **kwargs)
        latest_review = Revision.objects.filter(hive_id=hive_id).order_by("-review_date").first()
        Hive.objects.filter(pk=hive_id).update(
            last_review_date=latest_review.review_date if latest_review else None
        )


class CreatorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="creator_profile",
        verbose_name="Usuário",
    )
    name = models.CharField("Nome do criador", max_length=255)
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="creator_profiles",
        verbose_name="Localização (cidade/estado)",
    )
    species = models.ManyToManyField(
        Species,
        related_name="creator_profiles",
        verbose_name="Espécies criadas",
        blank=True,
    )
    phone = models.CharField("Telefone (WhatsApp)", max_length=20)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Criador inscrito"
        verbose_name_plural = "Criadores inscritos"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RevisionAttachment(models.Model):
    revision = models.ForeignKey(
        Revision,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Revisão",
    )
    file = models.ImageField("Imagem", upload_to="revision_attachments/")

    class Meta:
        verbose_name = "Anexo da Revisão"
        verbose_name_plural = "Anexos da Revisão"

    def __str__(self) -> str:
        return f"Anexo da revisão {self.revision_id}"

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.file:
            _convert_image_field_to_webp(self.file, field_name="file")
        return super().save(*args, **kwargs)
