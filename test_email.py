import os
import django
from django.core.mail import send_mail
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'muebleria.settings')
django.setup()

print("EMAIL_HOST_USER desde decouple:", config('EMAIL_HOST_USER', default='NO ENCONTRADO'))

try:
    send_mail(
        subject='Prueba de correo Django',
        message='Este es un correo de prueba enviado desde el script test_email.py',
        from_email=None,  # Usar DEFAULT_FROM_EMAIL
        recipient_list=['ferfloza2003@gmail.com'],  # Cambiado para la prueba
        fail_silently=False,
    )
    print('Correo enviado correctamente.')
except Exception as e:
    print('Error al enviar el correo:')
    print(e) 