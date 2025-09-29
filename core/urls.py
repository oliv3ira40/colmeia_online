from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from core import admin_dashboard  # noqa: F401  # Importa para aplicar o dashboard customizado

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path(
        "sobre-o-sistema/",
        TemplateView.as_view(template_name="system_overview.html"),
        name="system_overview",
    ),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    