from django import forms
from .models import Suscriptor

class SuscripcionForm(forms.ModelForm):
    class Meta:
        model = Suscriptor
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ingresa tu correo electrónico',
                'class': 'suscripcion-input',
                'autocomplete': 'off',
            }),
        }
        labels = {
            'email': '',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Suscriptor.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está suscrito.')
        return email
 