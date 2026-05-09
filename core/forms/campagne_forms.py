from django import forms
from django.utils import timezone
from core.models import Campagne, Inscription, BLOOD_GROUPS


class CampagneForm(forms.ModelForm):
    groupes_cibles = forms.MultipleChoiceField(
        choices=BLOOD_GROUPS,
        widget=forms.CheckboxSelectMultiple,
        label="Groupes sanguins ciblés"
    )

    class Meta:
        model = Campagne
        fields = ['nom', 'date', 'lieu', 'groupes_cibles', 'capacite_totale']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("La date de la campagne ne peut pas être dans le passé.")
        return date


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['creneau_horaire']
        widgets = {
            'creneau_horaire': forms.TimeInput(attrs={'type': 'time'}),
        }