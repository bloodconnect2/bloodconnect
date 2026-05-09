from django.urls import path
from core.views import home_views

urlpatterns = [
    path('', home_views.home, name='home'),
]