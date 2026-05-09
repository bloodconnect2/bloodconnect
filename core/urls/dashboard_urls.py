from django.urls import path
from core.views import dashboard_views

urlpatterns = [
    path('', dashboard_views.dashboard_redirect, name='dashboard'),
    path('donneur/', dashboard_views.dashboard_donneur, name='dashboard_donneur'),
    path('hopital/', dashboard_views.dashboard_hopital, name='dashboard_hopital'),
]