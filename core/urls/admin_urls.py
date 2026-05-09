from django.urls import path
from core.views import admin_views

urlpatterns = [
    path('', admin_views.tableau_admin, name='tableau_admin'),
    path('hopitaux/', admin_views.liste_hopitaux, name='liste_hopitaux'),
    path('hopitaux/<int:pk>/valider/', admin_views.valider_hopital, name='valider_hopital'),
    path('donneurs/export/', admin_views.export_donneurs_csv, name='export_donneurs_csv'),
    path('statistiques/', admin_views.statistiques, name='statistiques'),
]