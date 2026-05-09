from django import forms
from django.contrib.auth.models import User
from core.models import Donneur, BLOOD_GROUPS


class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")


class InscriptionDonneurForm(forms.Form):
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    username = forms.CharField(label="Nom d'utilisateur")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    groupe_sanguin = forms.ChoiceField(choices=BLOOD_GROUPS, label="Groupe sanguin")
    sexe = forms.ChoiceField(choices=[('M', 'Homme'), ('F', 'Femme')], label="Sexe")
    date_naissance = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date de naissance"
    )
    ville = forms.CharField(label="Ville")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned


class InscriptionHopitalForm(forms.Form):
    nom = forms.CharField(label="Nom de l'hôpital")
    username = forms.CharField(label="Nom d'utilisateur")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    adresse = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Adresse")
    ville = forms.CharField(label="Ville")
    numero_agrement = forms.CharField(label="Numéro d'agrément")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_numero_agrement(self):
        agrement = self.cleaned_data['numero_agrement']
        from core.models import Hopital
        if Hopital.objects.filter(numero_agrement=agrement).exists():
            raise forms.ValidationError("Ce numéro d'agrément est déjà enregistré.")
        return agrement

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned


class ProfilDonneurForm(forms.ModelForm):
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    email = forms.EmailField(label="Email")

    class Meta:
        model = Donneur
        fields = ['groupe_sanguin', 'sexe', 'date_naissance', 'ville']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }