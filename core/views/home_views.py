from django.shortcuts import render
from core.models import DemandeUrgente, Campagne
from django.utils import timezone


def home(request):
    demandes_recentes = DemandeUrgente.objects.filter(
        statut='active',
        delai__gte=timezone.now().date()
    ).order_by('-date_creation')[:6]

    campagnes_a_venir = Campagne.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')[:4]

    context = {
        'demandes_recentes': demandes_recentes,
        'campagnes_a_venir': campagnes_a_venir,
    }
    return render(request, 'home.html', context)