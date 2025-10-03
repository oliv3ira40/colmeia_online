"""Core models used to configure the Django admin menu."""

from __future__ import annotations

from typing import Iterable

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class MenuConfig(models.Model):
    """Stores menu configuration metadata for the Django admin site."""

    class MenuScope(models.TextChoices):
        NON_SUPERUSER = "non_superuser", _("Usuários sem privilégio de superusuário")

    name = models.CharField(
        "nome",
        max_length=100,
        unique=True,
        help_text=_("Identificador amigável exibido na lista do admin."),
    )
    scope = models.CharField(
        "escopo",
        max_length=32,
        choices=MenuScope.choices,
        default=MenuScope.NON_SUPERUSER,
    )
    active = models.BooleanField(
        "ativo",
        default=False,
        help_text=_("Apenas uma configuração pode estar ativa por escopo."),
    )
    include_unlisted = models.BooleanField(
        "incluir itens não configurados",
        default=False,
        help_text=_(
            "Quando habilitado, itens padrão do admin não listados abaixo são "
            "acrescentados ao final do menu."
        ),
    )
    updated_at = models.DateTimeField(
        "atualizado em",
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Configuração de menu")
        verbose_name_plural = _("Configurações de menu")
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.get_scope_display()})"

    def clean(self) -> None:
        super().clean()
        if not self.active:
            return
        existing = (
            MenuConfig.objects.filter(scope=self.scope, active=True)
            .exclude(pk=self.pk)
            .exists()
        )
        if existing:
            raise ValidationError(
                {
                    "active": _(
                        "Já existe uma configuração ativa para este escopo. "
                        "Desative-a antes de ativar outra."
                    )
                }
            )


class MenuItem(models.Model):
    """Defines an individual entry inside a ``MenuConfig``."""

    class ItemType(models.TextChoices):
        MODEL = "model", _("Modelo do Django")
        URL = "url", _("Link personalizado")

    config = models.ForeignKey(
        MenuConfig,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("configuração"),
    )
    order = models.PositiveIntegerField(
        "ordem",
        default=0,
        help_text=_("Itens são exibidos de acordo com este valor crescente."),
    )
    item_type = models.CharField(
        "tipo",
        max_length=20,
        choices=ItemType.choices,
    )
    section = models.CharField(
        "seção",
        max_length=100,
        blank=True,
        help_text=_(
            "Nome do agrupamento exibido na barra lateral. "
            "Em branco usa o nome do aplicativo." 
        ),
    )
    app_label = models.CharField(
        "app_label",
        max_length=100,
        blank=True,
        help_text=_("Formato: app_label do modelo (ex.: apiary)."),
    )
    model_name = models.CharField(
        "modelo",
        max_length=100,
        blank=True,
        help_text=_("Nome do modelo registrado no admin (ex.: Hive)."),
    )
    url_name = models.CharField(
        "nome da URL",
        max_length=200,
        blank=True,
        help_text=_("Nome completo da URL para ``reverse`` (ex.: dashboard:index)."),
    )
    absolute_url = models.URLField(
        "URL absoluta",
        blank=True,
        help_text=_("Usada quando ``nome da URL`` não está disponível."),
    )
    label = models.CharField(
        "rótulo",
        max_length=120,
        blank=True,
        help_text=_("Texto exibido no menu. Em branco usa o nome padrão."),
    )
    permission_codename = models.CharField(
        "permissão necessária",
        max_length=150,
        blank=True,
        help_text=_(
            "Opcional: informe no formato ``app_label.codename`` para limitar a "
            "exibição do item." 
        ),
    )

    class Meta:
        verbose_name = _("Item de menu")
        verbose_name_plural = _("Itens de menu")
        ordering = ("order", "id")

    def __str__(self) -> str:
        base = self.label or self.model_name or self.url_name or "Item"
        return f"{self.get_item_type_display()}: {base}"

    def clean(self) -> None:
        super().clean()
        errors: dict[str, Iterable[str]] = {}
        if self.item_type == self.ItemType.MODEL:
            if not self.app_label:
                errors.setdefault("app_label", []).append(_("Informe o app_label."))
            if not self.model_name:
                errors.setdefault("model_name", []).append(_("Informe o modelo."))
        elif self.item_type == self.ItemType.URL:
            if not self.url_name and not self.absolute_url:
                errors.setdefault("url_name", []).append(
                    _("Informe um nome de URL ou uma URL absoluta.")
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.app_label:
            self.app_label = self.app_label.strip()
        if self.model_name:
            self.model_name = self.model_name.strip()
        if self.url_name:
            self.url_name = self.url_name.strip()
        if self.label:
            self.label = self.label.strip()
        if self.section:
            self.section = self.section.strip()
        if self.permission_codename:
            self.permission_codename = self.permission_codename.strip()
        super().save(*args, **kwargs)


