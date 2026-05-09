from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from core.models import DemandeUrgente, ReponseAppel, BLOOD_COMPATIBILITY
from core.forms.demande_forms import DemandeUrgenteForm
from core.decorators import hopital_required, donneur_required


def liste_demandes(request):
    groupe = request.GET.get('groupe', '')
    ville = request.GET.get('ville', '')

    demandes = DemandeUrgente.objects.filter(
        statut='active',
        delai__gte=timezone.now().date()
    ).order_by('delai')

    if groupe:
        demandes = demandes.filter(groupe_sanguin=groupe)
    if ville:
        demandes = demandes.filter(hopital__ville__icontains=ville)

    context = {
        'demandes': demandes,
        'groupe_filtre': groupe,
        'ville_filtre': ville,
        'groupes': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    }
    return render(request, 'demandes/liste.html', context)


def detail_demande(request, pk):
    demande = get_object_or_404(DemandeUrgente, pk=pk)
    reponses = demande.reponses.select_related('donneur__user').all()

    deja_repondu = False
    est_donneur = False

    if request.user.is_authenticated and hasattr(request.user, 'donneur'):
        est_donneur = True
        deja_repondu = ReponseAppel.objects.filter(
            demande=demande,
            donneur=request.user.donneur
        ).exists()

    context = {
        'demande': demande,
        'reponses': reponses,
        'deja_repondu': deja_repondu,
        'est_donneur': est_donneur,
    }
    return render(request, 'demandes/detail.html', context)


@hopital_required
def creer_demande(request):
    hopital = request.user.hopital
    form = DemandeUrgenteForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        demande = form.save(commit=False)
        demande.hopital = hopital
        demande.save()
        messages.success(request, "Demande urgente publiée avec succès.")
        return redirect('dashboard_hopital')

    return render(request, 'demandes/form.html', {'form': form, 'titre': 'Nouvelle demande urgente'})


@hopital_required
def modifier_demande(request, pk):
    hopital = request.user.hopital
    demande = get_object_or_404(DemandeUrgente, pk=pk, hopital=hopital)
    form = DemandeUrgenteForm(request.POST or None, instance=demande)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Demande mise à jour.")
        return redirect('dashboard_hopital')

    return render(request, 'demandes/form.html', {'form': form, 'titre': 'Modifier la demande'})


@hopital_required
def cloturer_demande(request, pk):
    hopital = request.user.hopital
    demande = get_object_or_404(DemandeUrgente, pk=pk, hopital=hopital)

    if request.method == 'POST':
        demande.statut = 'cloturee'
        demande.save()
        messages.success(request, "Demande clôturée.")
        return redirect('dashboard_hopital')

    return render(request, 'demandes/confirmer_cloture.html', {'demande': demande})


@donneur_required
def repondre_demande(request, pk):
    donneur = request.user.donneur
    demande = get_object_or_404(DemandeUrgente, pk=pk, statut='active')

    # Vérification éligibilité
    if not donneur.est_eligible():
        messages.warning(
            request,
            f"Vous n'êtes pas éligible. Prochain don possible le : {donneur.get_prochain_don()}"
        )
        return redirect('detail_demande', pk=pk)

    # Vérification compatibilité
    if demande.groupe_sanguin not in BLOOD_COMPATIBILITY.get(donneur.groupe_sanguin, []):
        messages.error(request, "Votre groupe sanguin n'est pas compatible avec cette demande.")
        return redirect('detail_demande', pk=pk)

    # Vérification doublon
    if ReponseAppel.objects.filter(demande=demande, donneur=donneur).exists():
        messages.warning(request, "Vous avez déjà répondu à cette demande.")
        return redirect('detail_demande', pk=pk)

    if request.method == 'POST':
        ReponseAppel.objects.create(
            demande=demande,
            donneur=donneur,
            statut='en_attente'
        )
        messages.success(
            request,
            "Votre réponse a été enregistrée. L'hôpital va la traiter prochainement."
        )
        return redirect('dashboard_donneur')

    return render(request, 'demandes/confirmer_reponse.html', {'demande': demande})


# ✅ Nouvelle vue : l'hôpital gère les réponses
@hopital_required
def gerer_reponses(request, pk):
    hopital = request.user.hopital
    demande = get_object_or_404(DemandeUrgente, pk=pk, hopital=hopital)
    reponses = demande.reponses.select_related('donneur__user').all()

    context = {
        'demande': demande,
        'reponses': reponses,
    }
    return render(request, 'demandes/gerer_reponses.html', context)


# ✅ Nouvelle vue : confirmer ou annuler une réponse
@hopital_required
def traiter_reponse(request, reponse_id, action):
    hopital = request.user.hopital
    reponse = get_object_or_404(
        ReponseAppel,
        pk=reponse_id,
        demande__hopital=hopital
    )
    demande = reponse.demande

    if action == 'confirmer':
        reponse.statut = 'confirme'
        reponse.save()

        # ✅ Clôturer automatiquement la demande après confirmation
        demande.statut = 'satisfaite'
        demande.save()

        # Annuler toutes les autres réponses en attente
        ReponseAppel.objects.filter(
            demande=demande,
            statut='en_attente'
        ).exclude(pk=reponse.pk).update(statut='annule')

        messages.success(
            request,
            f"Réponse de {reponse.donneur.user.get_full_name()} confirmée. La demande est maintenant clôturée."
        )
        return redirect('dashboard_hopital')

    elif action == 'annuler':
        reponse.statut = 'annule'
        reponse.save()
        messages.warning(
            request,
            f"Réponse de {reponse.donneur.user.get_full_name()} annulée."
        )
        return redirect('gerer_reponses', pk=demande.pk)

    return redirect('dashboard_hopital')