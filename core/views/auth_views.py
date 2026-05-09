from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Donneur, Hopital
from core.forms.auth_forms import (
    LoginForm, InscriptionDonneurForm, InscriptionHopitalForm,
    ProfilDonneurForm
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            if not user.is_active:
                messages.error(request, "Ce compte est désactivé.")
            else:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('login')


def inscription_donneur(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = InscriptionDonneurForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
        )
        Donneur.objects.create(
            user=user,
            groupe_sanguin=form.cleaned_data['groupe_sanguin'],
            sexe=form.cleaned_data['sexe'],
            date_naissance=form.cleaned_data['date_naissance'],
            ville=form.cleaned_data['ville'],
        )
        login(request, user)
        messages.success(request, "Compte créé avec succès. Bienvenue !")
        return redirect('dashboard_donneur')

    return render(request, 'auth/inscription_donneur.html', {'form': form})


def inscription_hopital(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = InscriptionHopitalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['nom'],
        )
        Hopital.objects.create(
            user=user,
            nom=form.cleaned_data['nom'],
            adresse=form.cleaned_data['adresse'],
            ville=form.cleaned_data['ville'],
            numero_agrement=form.cleaned_data['numero_agrement'],
        )
        messages.warning(
            request,
            "Compte créé. En attente de validation par l'administrateur."
        )
        return redirect('login')

    return render(request, 'auth/inscription_hopital.html', {'form': form})


@login_required
def modifier_profil(request):
    try:
        donneur = request.user.donneur
    except Donneur.DoesNotExist:
        messages.error(request, "Accès réservé aux donneurs.")
        return redirect('dashboard')

    form = ProfilDonneurForm(request.POST or None, instance=donneur)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # Mise à jour des champs User
        request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
        request.user.last_name = form.cleaned_data.get('last_name', request.user.last_name)
        request.user.email = form.cleaned_data.get('email', request.user.email)
        request.user.save()
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('dashboard_donneur')

    return render(request, 'auth/modifier_profil.html', {'form': form})


@login_required
def desactiver_compte(request):
    try:
        donneur = request.user.donneur
    except Donneur.DoesNotExist:
        messages.error(request, "Accès réservé aux donneurs.")
        return redirect('dashboard')

    if request.method == 'POST':
        donneur.actif = not donneur.actif
        donneur.save()
        etat = "désactivé" if not donneur.actif else "réactivé"
        messages.success(request, f"Votre compte a été {etat}.")
        return redirect('dashboard_donneur')

    return render(request, 'auth/desactiver_compte.html', {'donneur': donneur})