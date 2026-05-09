from django.urls import path
from core.views import auth_views

urlpatterns = [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('inscription/donneur/', auth_views.inscription_donneur, name='inscription_donneur'),
    path('inscription/hopital/', auth_views.inscription_hopital, name='inscription_hopital'),
    path('profil/', auth_views.modifier_profil, name='modifier_profil'),
    path('desactiver/', auth_views.desactiver_compte, name='desactiver_compte'),
]