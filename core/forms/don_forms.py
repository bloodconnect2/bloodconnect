from django import forms
from core.models import Don, Hopital


class DonForm(forms.ModelForm):
    class Meta:
        model = Don
        fields = ['hopital', 'date_don', 'notes']
        widgets = {
            'date_don': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hopital'].queryset = Hopital.objects.filter(valide=True)