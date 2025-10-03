from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Hive, Revision


class RevisaoForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        # All conditional fields remain optional on the backend.
        return cleaned_data


class ColmeiaForm(forms.ModelForm):
    class Meta:
        model = Hive
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acquisition_date"].required = False
        self.fields["transfer_box_date"].required = False
        self.fields["origin_hive"].required = False

        photo_field = self.fields.get("photo")
        if photo_field is not None:
            attrs = photo_field.widget.attrs
            attrs["data-image-preview"] = "true"
            attrs["data-preview-label"] = str(_("Prévia"))
            attrs["data-preview-open-label"] = str(_("Abrir em nova aba"))

            initial_url = ""
            photo_instance = getattr(self.instance, "photo", None)
            if photo_instance:
                try:
                    initial_url = photo_instance.url
                except ValueError:
                    initial_url = ""
            attrs["data-initial-preview-url"] = initial_url

    def clean(self):
        cleaned_data = super().clean()
        acquisition_method = cleaned_data.get("acquisition_method")
        acquisition_date = cleaned_data.get("acquisition_date")
        origin_hive = cleaned_data.get("origin_hive")
        transfer_box_date = cleaned_data.get("transfer_box_date")

        errors = {}

        if acquisition_method == Hive.AcquisitionMethod.PURCHASE:
            if not acquisition_date:
                errors["acquisition_date"] = [
                    "Informe a data de aquisição para colmeias adquiridas por compra."
                ]
        if acquisition_method == Hive.AcquisitionMethod.DIVISION:
            if not origin_hive:
                errors["origin_hive"] = [
                    "Informe a colmeia de origem para colmeias adquiridas por divisão."
                ]
        if acquisition_method == Hive.AcquisitionMethod.CAPTURE:
            if not transfer_box_date:
                errors["transfer_box_date"] = [
                    "Informe a data de transferência para colmeias capturadas."
                ]

        if errors:
            raise ValidationError(errors)

        return cleaned_data
