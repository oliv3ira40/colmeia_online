from __future__ import annotations

from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delete_data_entry_url"] = reverse("privacy-delete-entry")
        context["admin_login_url"] = reverse("admin:login")
        return context


class DeleteDataRedirectView(View):
    def get(self, request, *args, **kwargs):
        target_url = reverse("admin:delete_personal_data")
        if request.user.is_authenticated:
            return redirect(target_url)

        login_url = reverse("admin:login")
        query = urlencode({"next": target_url})
        return redirect(f"{login_url}?{query}")
