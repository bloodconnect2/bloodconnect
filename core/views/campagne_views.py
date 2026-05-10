from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from core.models import Campagne, Inscription
from core.forms.campagne_forms import CampagneForm, InscriptionForm
from core.decorators import hopital_required, donneur_required
from django.core.paginator import Paginator


def liste_campagnes(request):
    campagnes = Campagne.objects.filter(
        date__gte=timezone.now().date()
    ).select_related('hopital').order_by('date')

    paginator = Paginator(campagnes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'campagnes/liste.html', {
        'campagnes': page_obj,
        'page_obj': page_obj,
    })


def detail_campagne(request, pk):
    campagne = get_object_or_404(Campagne, pk=pk)
    inscriptions = campagne.inscriptions.select_related('donneur__user').all()

    deja_inscrit = False
    est_donneur = False

    if request.user.is_authenticated and hasattr(request.user, 'donneur'):
        est_donneur = True
        deja_inscrit = Inscription.objects.filter(
            campagne=campagne,
            donneur=request.user.donneur
        ).exists()

    context = {
        'campagne': campagne,
        'inscriptions': inscriptions,
        'places_restantes': campagne.places_restantes(),
        'deja_inscrit': deja_inscrit,
        'est_donneur': est_donneur,
    }
    return render(request, 'campagnes/detail.html', context)


@hopital_required
def creer_campagne(request):
    hopital = request.user.hopital
    form = CampagneForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        campagne = form.save(commit=False)
        campagne.hopital = hopital
        campagne.save()
        messages.success(request, "Campagne créée avec succès.")
        return redirect('dashboard_hopital')

    return render(request, 'campagnes/form.html', {'form': form})


@donneur_required
def inscrire_campagne(request, pk):
    donneur = request.user.donneur
    campagne = get_object_or_404(Campagne, pk=pk)

    # Vérification places disponibles
    if campagne.places_restantes() <= 0:
        messages.error(request, "Cette campagne est complète.")
        return redirect('detail_campagne', pk=pk)

    # Vérification doublon
    if Inscription.objects.filter(campagne=campagne, donneur=donneur).exists():
        messages.warning(request, "Vous êtes déjà inscrit à cette campagne.")
        return redirect('detail_campagne', pk=pk)

    # Vérification compatibilité groupe sanguin
    if campagne.groupes_cibles and donneur.groupe_sanguin not in campagne.groupes_cibles:
        messages.error(request, "Votre groupe sanguin n'est pas ciblé par cette campagne.")
        return redirect('detail_campagne', pk=pk)

    form = InscriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        inscription = form.save(commit=False)
        inscription.campagne = campagne
        inscription.donneur = donneur
        inscription.save()
        messages.success(request, "Inscription confirmée !")
        return redirect('dashboard_donneur')

    return render(request, 'campagnes/inscrire.html', {'form': form, 'campagne': campagne})