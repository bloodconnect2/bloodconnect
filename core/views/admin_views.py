import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from core.models import Donneur, Hopital, DemandeUrgente, Don, Campagne
from core.decorators import admin_required


@admin_required
def tableau_admin(request):
    context = {
        'total_donneurs': Donneur.objects.count(),
        'total_dons': Don.objects.filter(valide=True).count(),
        'total_hopitaux': Hopital.objects.filter(valide=True).count(),
        'hopitaux_en_attente': Hopital.objects.filter(valide=False).count(),
        'demandes_actives': DemandeUrgente.objects.filter(statut='active').count(),
    }
    return render(request, 'admin_panel/tableau.html', context)


@admin_required
def liste_hopitaux(request):
    hopitaux = Hopital.objects.select_related('user').order_by('valide', 'nom')
    return render(request, 'admin_panel/hopitaux.html', {'hopitaux': hopitaux})


@admin_required
def valider_hopital(request, pk):
    hopital = get_object_or_404(Hopital, pk=pk)

    if request.method == 'POST':
        hopital.valide = True
        hopital.save()
        messages.success(request, f"L'hôpital « {hopital.nom} » a été validé.")
        return redirect('liste_hopitaux')

    return render(request, 'admin_panel/confirmer_validation.html', {'hopital': hopital})


@admin_required
def statistiques(request):
    # Dons par groupe sanguin
    dons_par_groupe = (
        Don.objects.filter(valide=True)
        .values('donneur__groupe_sanguin')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Demandes actives par groupe sanguin
    demandes_par_groupe = (
        DemandeUrgente.objects.filter(statut='active')
        .values('groupe_sanguin')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Demandes actives par ville
    demandes_par_ville = (
        DemandeUrgente.objects.filter(statut='active')
        .values('hopital__ville')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    context = {
        'dons_par_groupe': dons_par_groupe,
        'demandes_par_groupe': demandes_par_groupe,
        'demandes_par_ville': demandes_par_ville,
    }
    return render(request, 'admin_panel/statistiques.html', context)


@admin_required
def export_donneurs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donneurs.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Nom', 'Prénom', 'Email', 'Groupe sanguin',
        'Sexe', 'Ville', 'Actif', 'Nombre de dons'
    ])

    donneurs = Donneur.objects.select_related('user').annotate(
        nb_dons=Count('dons')
    )

    for d in donneurs:
        writer.writerow([
            d.user.last_name,
            d.user.first_name,
            d.user.email,
            d.groupe_sanguin,
            d.get_sexe_display(),
            d.ville,
            'Oui' if d.actif else 'Non',
            d.nb_dons,
        ])

    return response