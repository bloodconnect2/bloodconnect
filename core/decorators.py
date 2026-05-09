from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def donneur_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'donneur'):
            messages.error(request, "Accès réservé aux donneurs.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def hopital_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'hopital'):
            messages.error(request, "Accès réservé aux hôpitaux.")
            return redirect('dashboard')
        hopital = request.user.hopital
        if not hopital.valide:
            messages.warning(request, "Votre compte est en attente de validation.")
            return redirect('dashboard_hopital')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper