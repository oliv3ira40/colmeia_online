"""Models for configuring the Django admin menu."""

from __future__ import annotations

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class MenuConfig(models.Model):
    """Stores menu configurations that can be enabled per scope."""

    class Scope(models.TextChoices):
        NON_SUPERUSER = "non_superuser", _("Usuários sem superusuário")

    scope = models.CharField(
        max_length=32,
        choices=Scope.choices,
        default=Scope.NON_SUPERUSER,
        verbose_name=_("escopo"),
        help_text=_("Usuários aos quais essa configuração deve ser aplicada."),
    )
    active = models.BooleanField(
        default=False,
        verbose_name=_("ativa"),
        help_text=_("Marque para tornar essa configuração a vigente para o escopo."),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("criada em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("atualizada em"))

    class Meta:
        verbose_name = _("configuração de menu")
        verbose_name_plural = _("configurações de menu")
        constraints = [
            models.UniqueConstraint(
                fields=["scope"],
                condition=Q(active=True),
                name="unique_active_menu_per_scope",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - human readable only
        status = _("ativa") if self.active else _("inativa")
        return f"{self.get_scope_display()} ({status})"


class MenuItem(models.Model):
    """Defines individual menu entries for non-superuser dashboards."""

    class ItemType(models.TextChoices):
        MODEL = "model", _("Modelo do admin")
        URL = "url", _("Link personalizado")

    config = models.ForeignKey(
        MenuConfig,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("configuração"),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("ordem"),
        help_text=_("Menor valor aparece primeiro."),
    )
    item_type = models.CharField(
        max_length=12,
        choices=ItemType.choices,
        verbose_name=_("tipo de item"),
    )
    group_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("grupo"),
        help_text=_("Nome da seção a exibir no menu. Deixe vazio para usar o padrão."),
    )
    label = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("rótulo"),
        help_text=_("Texto mostrado no menu. Para modelos vazios usamos o nome plural."),
    )
    app_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("app label"),
        help_text=_("Necessário para itens de modelo. Ex.: apiary."),
    )
    model_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("nome do modelo"),
        help_text=_("Necessário para itens de modelo. Ex.: Hive."),
    )
    url_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("nome da URL"),
        help_text=_("Nome da URL para usar com reverse()."),
    )
    absolute_url = models.URLField(
        blank=True,
        verbose_name=_("URL absoluta"),
        help_text=_("Usada como fallback quando o nome da URL não estiver disponível."),
    )
    permission_codename = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("permissão extra"),
        help_text=_("Opcional. Ex.: apiary.view_hive. Apenas usuários com essa permissão verão o item."),
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("item de menu")
        verbose_name_plural = _("itens de menu")
        constraints = [
            models.CheckConstraint(
                check=Q(item_type="model", app_label__gt="", model_name__gt="")
                | Q(item_type="url"),
                name="menuitem_model_requires_target",
            ),
            models.CheckConstraint(
                check=Q(item_type="url", url_name__gt="")
                | Q(item_type="url", absolute_url__gt="")
                | Q(item_type="model"),
                name="menuitem_url_requires_destination",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - human readable only
        base_label = self.label or self.app_label or self.url_name or "item"
        return f"{self.get_item_type_display()} - {base_label}"

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.item_type == self.ItemType.MODEL:
            if not self.app_label or not self.model_name:
                errors["app_label"] = _("Informe app label e nome do modelo para itens de modelo.")
        elif self.item_type == self.ItemType.URL:
            if not self.url_name and not self.absolute_url:
                errors["url_name"] = _("Informe o nome da URL ou uma URL absoluta.")
        if errors:
            raise ValidationError(errors)

    def get_model(self):
        if self.item_type != self.ItemType.MODEL:
            return None
        if not self.app_label or not self.model_name:
            return None
        try:
            return apps.get_model(self.app_label, self.model_name)
        except (LookupError, ValueError):
            return None
