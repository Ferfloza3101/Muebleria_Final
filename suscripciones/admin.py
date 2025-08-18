from django.contrib import admin
from django import forms
from django.core.mail import send_mass_mail
from django.contrib import messages
from .models import Suscriptor
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html

# Forzar uso de Suscriptor.objects para linter

class EnviarCorreoForm(forms.Form):
    asunto = forms.CharField(label='Asunto', max_length=120)
    mensaje = forms.CharField(label='Mensaje', widget=forms.Textarea)

@admin.register(Suscriptor)
class SuscriptorAdmin(admin.ModelAdmin):
    list_display = ('email', 'fecha_suscripcion', 'is_active')
    change_list_template = 'admin/suscripciones/suscriptor_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('enviar-correo/', self.admin_site.admin_view(self.enviar_correo_view), name='enviar_correo_suscriptores'),
        ]
        return custom_urls + urls

    def enviar_correo_view(self, request):
        if request.method == 'POST':
            form = EnviarCorreoForm(request.POST)
            if form.is_valid():
                asunto = form.cleaned_data['asunto']
                mensaje = form.cleaned_data['mensaje']
                emails = list(Suscriptor.objects.filter(is_active=True).values_list('email', flat=True))
                if emails:
                    from_email = None  # Usar el default
                    datatuple = [
                        (asunto, mensaje, from_email, [email]) for email in emails
                    ]
                    try:
                        send_mass_mail(datatuple, fail_silently=False)
                        self.message_user(request, f"Correo enviado a {len(emails)} suscriptores.", messages.SUCCESS)
                    except Exception as e:
                        self.message_user(request, f"Error al enviar el correo: {e}", messages.ERROR)
                else:
                    self.message_user(request, "No hay suscriptores activos.", messages.WARNING)
                return redirect('..')
        else:
            form = EnviarCorreoForm()
        context = {'form': form, 'title': 'Enviar correo a suscriptores'}
        return render(request, 'admin/enviar_correo_suscriptores.html', context) 