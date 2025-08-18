from django import forms
from django.contrib.auth.models import User
from .models import DireccionUsuario, Perfil
from django.core.exceptions import ValidationError
import re

class DireccionForm(forms.ModelForm):
    # Campo de búsqueda para autocompletado
    busqueda_direccion = forms.CharField(
        label='Buscar dirección',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Escribe tu dirección para autocompletar...',
            'autocomplete': 'off'
        })
    )
    
    # Campos de la dirección
    nombre = forms.CharField(
        label='Nombre de la dirección',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Ej: Casa, Trabajo, etc.'
        })
    )
    
    calle = forms.CharField(
        label='Calle',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Nombre de la calle'
        })
    )
    
    numero_exterior = forms.CharField(
        label='Número exterior',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Número'
        })
    )
    
    numero_interior = forms.CharField(
        label='Número interior (opcional)',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Departamento, oficina, etc.'
        })
    )
    
    colonia = forms.CharField(
        label='Colonia',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Nombre de la colonia'
        })
    )
    
    ciudad = forms.CharField(
        label='Ciudad',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Nombre de la ciudad'
        })
    )
    
    estado = forms.CharField(
        label='Estado',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Nombre del estado'
        })
    )
    
    codigo_postal = forms.CharField(
        label='Código Postal',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'CP'
        })
    )
    
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'perfil-input',
            'placeholder': 'Teléfono de contacto'
        })
    )
    
    referencias = forms.CharField(
        label='Referencias (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'perfil-textarea',
            'placeholder': 'Entre calles, puntos de referencia, etc.',
            'rows': 3
        })
    )
    
    principal = forms.BooleanField(
        label='Marcar como dirección principal',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'perfil-checkbox'})
    )

    class Meta:
        model = DireccionUsuario
        fields = [
            'nombre', 'calle', 'numero_exterior', 'numero_interior', 
            'colonia', 'ciudad', 'estado', 'codigo_postal', 
            'telefono', 'referencias', 'principal'
        ]

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que al menos los campos básicos estén completos
        campos_requeridos = ['calle', 'colonia', 'ciudad', 'estado', 'codigo_postal']
        for campo in campos_requeridos:
            if not cleaned_data.get(campo):
                raise forms.ValidationError(f'El campo "{campo}" es obligatorio.')
        
        return cleaned_data

    def save(self, user, commit=True):
        direccion_usuario = super().save(commit=False)
        direccion_usuario.user = user
        
        # Si es la primera dirección o está marcada como principal
        if direccion_usuario.principal:
            # Desmarcar otras direcciones como principales
            DireccionUsuario.objects.filter(user=user).update(principal=False)
        
        if commit:
            direccion_usuario.save()
        return direccion_usuario 

class EditarPerfilForm(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=150, required=True)
    last_name = forms.CharField(label='Apellidos', max_length=150, required=True)
    email = forms.EmailField(label='Correo electrónico', required=True)
    username = forms.CharField(label='Usuario', max_length=150, required=True)
    fecha_nacimiento = forms.DateField(label='Fecha de nacimiento', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    genero = forms.ChoiceField(label='Género', choices=[('masculino', 'Masculino'), ('femenino', 'Femenino')], required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=False, help_text='Mínimo 8 caracteres, 1 mayúscula, 1 especial')
    password_confirm = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
            if hasattr(user, 'perfil'):
                self.fields['fecha_nacimiento'].initial = user.perfil.fecha_nacimiento
                self.fields['genero'].initial = user.perfil.genero
                self.fields['telefono'].initial = user.perfil.telefono

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
            if not re.search(r'[A-Z]', password):
                raise ValidationError('Debe contener al menos una letra mayúscula.')
            if not re.search(r'[^A-Za-z0-9]', password):
                raise ValidationError('Debe contener al menos un carácter especial.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password or password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        return cleaned_data 