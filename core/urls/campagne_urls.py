from django.urls import path
from core.views import campagne_views

urlpatterns = [
    path('', campagne_views.liste_campagnes, name='liste_campagnes'),
    path('creer/', campagne_views.creer_campagne, name='creer_campagne'),
    path('<int:pk>/', campagne_views.detail_campagne, name='detail_campagne'),
    path('<int:pk>/inscrire/', campagne_views.inscrire_campagne, name='inscrire_campagne'),
]