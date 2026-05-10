from django import forms
from django.utils import timezone
from core.models import DemandeUrgente

class DemandeUrgenteForm(forms.ModelForm):
    class Meta:
        model = DemandeUrgente
        fields = ['groupe_sanguin', 'quantite', 'delai', 'description']
        widgets = {
            'delai': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_delai(self):
        delai = self.cleaned_data.get('delai')
        if delai and delai < timezone.now().date():
            raise forms.ValidationError(
                f"La date limite ne peut pas être dans le passé. Date minimale : {timezone.now().date()}"
            )
        return delai