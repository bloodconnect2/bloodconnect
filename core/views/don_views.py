from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from core.models import Don, Hopital
from core.forms.don_forms import DonForm
from core.decorators import donneur_required
from datetime import timedelta


@donneur_required
def enregistrer_don(request):
    donneur = request.user.donneur
    today = timezone.now().date()

    # Bloquer si compte désactivé
    if not donneur.actif:
        messages.error(request, "Votre compte donneur est désactivé. Réactivez-le pour enregistrer un don.")
        return redirect('dashboard_donneur')

    # Bloquer si non éligible
    if not donneur.est_eligible():
        prochain = donneur.get_prochain_don()
        messages.error(
            request,
            f"Vous ne pouvez pas enregistrer un don avant le {prochain}. "
            f"Délai minimum : {donneur.get_delai_don()} jours."
        )
        return redirect('historique_dons')

    form = DonForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        date_don = form.cleaned_data['date_don']

        # Contrôle : seule la date d'aujourd'hui est acceptée
        if date_don != today:
            form.add_error('date_don', f"Seule la date d'aujourd'hui ({today}) est acceptée.")
            return render(request, 'dons/enregistrer.html', {
                'form': form,
                'donneur': donneur,
                'today': today,
            })

        # Contrôle : respect du délai entre deux dons
        dernier_don = donneur.dons.filter(valide=True).order_by('-date_don').first()
        if dernier_don:
            date_minimale = dernier_don.date_don + timedelta(days=donneur.get_delai_don())
            if date_don < date_minimale:
                form.add_error('date_don', f"Délai non respecté. Prochain don autorisé : {date_minimale}.")
                return render(request, 'dons/enregistrer.html', {
                    'form': form,
                    'donneur': donneur,
                    'today': today,
                })

        don = form.save(commit=False)
        don.donneur = donneur
        don.save()
        messages.success(request, "Don enregistré avec succès.")
        return redirect('historique_dons')

    return render(request, 'dons/enregistrer.html', {
        'form': form,
        'donneur': donneur,
        'today': today,
        'prochain_don': donneur.get_prochain_don(),
    })
@donneur_required
def historique_dons(request):
    donneur = request.user.donneur
    dons = donneur.dons.all().order_by('-date_don')

    return render(request, 'dons/historique.html', {
        'dons': dons
    })    