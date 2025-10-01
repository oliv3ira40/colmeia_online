from django.views.generic import TemplateView

from apiary.models import CreatorProfile


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_profile = None
        if user.is_authenticated:
            user_profile = (
                CreatorProfile.objects.select_related("city")
                .prefetch_related("species")
                .filter(user=user)
                .first()
            )

        can_view_entries = bool(user_profile)
        if user.is_superuser:
            can_view_entries = True

        entries_queryset = (
            CreatorProfile.objects.select_related("city")
            .prefetch_related("species")
            .order_by("name")
        )
        entries = list(entries_queryset) if can_view_entries else []
        context.update(
            {
                "creator_entries": entries,
                "can_view_creator_entries": can_view_entries,
                "user_creator_profile": user_profile,
                "total_creator_entries": len(entries),
            }
        )
        return context
