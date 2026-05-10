from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('core.urls.auth_urls')),
    path('dashboard/', include('core.urls.dashboard_urls')),
    path('demandes/', include('core.urls.demande_urls')),
    path('campagnes/', include('core.urls.campagne_urls')),
    path('dons/', include('core.urls.don_urls')),
    path('admin-panel/', include('core.urls.admin_urls')),
    path('', include('core.urls.home_urls')),

    path('auth/password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt',
         ),
         name='password_reset'),
    path('auth/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
         name='password_reset_done'),
    path('auth/password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('auth/password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
         name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)