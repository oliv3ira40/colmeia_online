from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from core import admin_dashboard  # noqa: F401  # Importa para aplicar o dashboard customizado
from core.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    