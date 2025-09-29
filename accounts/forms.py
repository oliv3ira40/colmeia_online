from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SubscriptionUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Nome de usuário",
        widget=forms.TextInput(attrs={
            "autofocus": True,
            "placeholder": "Informe um nome de usuário",
        }),
    )
    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Crie uma senha",
        }),
        help_text=UserCreationForm().fields["password1"].help_text,
    )
    password2 = forms.CharField(
        label="Confirmação de senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Repita a senha",
        }),
        help_text="Repita a mesma senha para confirmação.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
