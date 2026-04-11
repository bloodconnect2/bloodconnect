from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('core.urls.auth_urls')),
    path('dashboard/', include('core.urls.dashboard_urls')),
    path('demandes/', include('core.urls.demande_urls')),
    path('campagnes/', include('core.urls.campagne_urls')),
    path('dons/', include('core.urls.don_urls')),
    path('admin-panel/', include('core.urls.admin_urls')),
    path('', include('core.urls.home_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)