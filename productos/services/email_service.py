from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import os

class EmailService:
    """
    Servicio para enviar emails con resumen de pedido
    """
    
    @staticmethod
    def enviar_resumen_pedido_email(resumen_pedido, email_destino=None):
        """
        Envía el resumen de pedido por email con PDF adjunto
        """
        try:
            pedido = resumen_pedido.pedido
            datos_cliente = pedido.get_datos_cliente()
            
            # Email de destino
            if not email_destino:
                email_destino = datos_cliente.get('email')
            
            if not email_destino:
                print("No se encontró email de destino")
                return False
            
            # Asunto del email
            asunto = f"Resumen de Pedido #{pedido.numero_pedido} - Mueblería OPTI"
            
            # Contenido del email
            contexto = {
                'pedido': pedido,
                'resumen': resumen_pedido,
                'datos_cliente': datos_cliente,
                'datos_envio': pedido.get_datos_envio(),
                'fecha_actual': timezone.now().strftime("%d/%m/%Y %H:%M")
            }
            
            # Renderizar template de email
            contenido_html = render_to_string('productos/emails/resumen_pedido.html', contexto)
            contenido_texto = render_to_string('productos/emails/resumen_pedido.txt', contexto)
            
            # Crear email
            email = EmailMessage(
                subject=asunto,
                body=contenido_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_destino],
                reply_to=[settings.DEFAULT_FROM_EMAIL]
            )
            
            # Configurar como HTML
            email.content_subtype = "html"
            
            # Adjuntar PDF si existe
            if resumen_pedido.archivo_pdf and os.path.exists(resumen_pedido.archivo_pdf.path):
                with open(resumen_pedido.archivo_pdf.path, 'rb') as pdf_file:
                    email.attach(
                        f"resumen_pedido_{pedido.numero_pedido}.pdf",
                        pdf_file.read(),
                        'application/pdf'
                    )
            
            # Enviar email
            email.send()
            
            # Actualizar estado del resumen
            resumen_pedido.enviado_por_email = True
            resumen_pedido.fecha_envio_email = timezone.now()
            resumen_pedido.save()
            
            print(f"Email enviado exitosamente a {email_destino}")
            return True
            
        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            return False
    
    @staticmethod
    def enviar_confirmacion_pedido_email(pedido, email_destino=None):
        """
        Envía confirmación de pedido sin PDF adjunto (para pedidos sin resumen)
        """
        try:
            datos_cliente = pedido.get_datos_cliente()
            
            # Email de destino
            if not email_destino:
                email_destino = datos_cliente.get('email')
            
            if not email_destino:
                print("No se encontró email de destino")
                return False
            
            # Asunto del email
            asunto = f"Confirmación de Pedido #{pedido.numero_pedido} - Mueblería OPTI"
            
            # Contenido del email
            contexto = {
                'pedido': pedido,
                'datos_cliente': datos_cliente,
                'datos_envio': pedido.get_datos_envio(),
                'fecha_actual': timezone.now().strftime("%d/%m/%Y %H:%M")
            }
            
            # Renderizar template de email
            contenido_html = render_to_string('productos/emails/confirmacion_pedido.html', contexto)
            contenido_texto = render_to_string('productos/emails/confirmacion_pedido.txt', contexto)
            
            # Crear email
            email = EmailMessage(
                subject=asunto,
                body=contenido_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_destino],
                reply_to=[settings.DEFAULT_FROM_EMAIL]
            )
            
            # Configurar como HTML
            email.content_subtype = "html"
            
            # Enviar email
            email.send()
            
            print(f"Email de confirmación enviado exitosamente a {email_destino}")
            return True
            
        except Exception as e:
            print(f"Error enviando email de confirmación: {str(e)}")
            return False 