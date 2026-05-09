from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.models import Donneur, Hopital, DemandeUrgente, Campagne, Don


def get_role(user):
    if user.is_superuser:
        return 'admin'
    if hasattr(user, 'donneur'):
        return 'donneur'
    if hasattr(user, 'hopital'):
        return 'hopital'
    return None


@login_required
def dashboard_redirect(request):
    role = get_role(request.user)
    if role == 'admin':
        return redirect('tableau_admin')
    elif role == 'donneur':
        return redirect('dashboard_donneur')
    elif role == 'hopital':
        return redirect('dashboard_hopital')
    return redirect('login')


@login_required
def dashboard_donneur(request):
    try:
        donneur = request.user.donneur
    except Donneur.DoesNotExist:
        return redirect('dashboard')

    # Groupes compatibles avec le donneur
    groupes_compatibles = donneur.get_groupes_compatibles()

    # Demandes urgentes compatibles et actives
    demandes = DemandeUrgente.objects.filter(
        groupe_sanguin__in=groupes_compatibles,
        statut='active',
        delai__gte=timezone.now().date()
    ).order_by('delai')

    # Campagnes à venir ciblant le groupe du donneur
    campagnes = Campagne.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')
    campagnes_compatibles = [
        c for c in campagnes
        if donneur.groupe_sanguin in c.groupes_cibles
    ]

    # Derniers dons
    derniers_dons = donneur.dons.filter(valide=True).order_by('-date_don')[:5]

    context = {
        'donneur': donneur,
        'eligible': donneur.est_eligible(),
        'prochain_don': donneur.get_prochain_don(),
        'demandes': demandes,
        'campagnes': campagnes_compatibles,
        'derniers_dons': derniers_dons,
    }
    return render(request, 'dashboard/donneur.html', context)


@login_required
def dashboard_hopital(request):
    try:
        hopital = request.user.hopital
    except Hopital.DoesNotExist:
        return redirect('dashboard')

    if not hopital.valide:
        return render(request, 'dashboard/hopital_en_attente.html')

    demandes_actives = hopital.demandes.filter(statut='active').order_by('-date_creation')
    campagnes = hopital.campagnes.filter(date__gte=timezone.now().date()).order_by('date')
    total_dons = hopital.dons_recus.count()

    context = {
        'hopital': hopital,
        'demandes_actives': demandes_actives,
        'campagnes': campagnes,
        'total_dons': total_dons,
    }
    return render(request, 'dashboard/hopital.html', context)