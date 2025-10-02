from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from core import admin_dashboard  # noqa: F401  # Importa para aplicar o dashboard customizado
from apiary.views import hive_production_detail, production_dashboard

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path(
        "admin/dashboard/producao/",
        production_dashboard,
        name="production-dashboard",
    ),
    path(
        "admin/dashboard/producao/colmeias/<int:pk>/",
        hive_production_detail,
        name="production-dashboard-hive-detail",
    ),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    