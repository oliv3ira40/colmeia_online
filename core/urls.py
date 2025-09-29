from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from core.views import home
from core.admin_site import admin_site

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin_site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    