from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import SubscriptionUserCreationForm


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = SubscriptionUserCreationForm
    success_url = reverse_lazy("admin:login")

    def form_valid(self, form: UserCreationForm):
        # 1) cria usuário já como staff (membro da equipe)
        user = form.save(commit=False)
        user.is_staff = True
        user.save()

        group = Group.objects.filter(pk=1, name="Assinante").first()
        if not group:
            group, _ = Group.objects.get_or_create(name="Assinante")
        user.groups.add(group)
        messages.success(
            self.request,
            "Cadastro realizado com sucesso! Você já pode acessar com suas credenciais.",
        )
        return super().form_valid(form)
