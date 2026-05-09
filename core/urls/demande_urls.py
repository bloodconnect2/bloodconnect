from django.urls import path
from core.views import demande_views

urlpatterns = [
    path('', demande_views.liste_demandes, name='liste_demandes'),
    path('creer/', demande_views.creer_demande, name='creer_demande'),
    path('<int:pk>/', demande_views.detail_demande, name='detail_demande'),
    path('<int:pk>/modifier/', demande_views.modifier_demande, name='modifier_demande'),
    path('<int:pk>/cloturer/', demande_views.cloturer_demande, name='cloturer_demande'),
    path('<int:pk>/repondre/', demande_views.repondre_demande, name='repondre_demande'),
    path('<int:pk>/reponses/', demande_views.gerer_reponses, name='gerer_reponses'),
    path('reponse/<int:reponse_id>/<str:action>/', demande_views.traiter_reponse, name='traiter_reponse'),
]