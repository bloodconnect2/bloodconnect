from django.urls import path
from core.views import don_views

urlpatterns = [
    path('enregistrer/', don_views.enregistrer_don, name='enregistrer_don'),
    path('historique/', don_views.historique_dons, name='historique_dons'),
]