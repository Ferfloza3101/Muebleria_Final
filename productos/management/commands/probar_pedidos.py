from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from productos.models import Producto, Carrito, ItemCarrito, Pedido, DetallePedido, ResumenPedido
from productos.services.pdf_service import PDFService
from productos.services.email_service import EmailService
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crea un pedido de prueba, genera PDF y envía email.'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No hay usuario superusuario.'))
            return
        
        # Crear producto de prueba
        producto, _ = Producto.objects.get_or_create(
            nombre='Producto Test',
            defaults={'precio': Decimal('123.45')}
        )
        
        # Crear carrito
        carrito, _ = Carrito.objects.get_or_create(usuario=user)
        # Eliminar cualquier item previo de ese producto en el carrito
        ItemCarrito.objects.filter(carrito=carrito, producto=producto).delete()
        ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=2, precio_unitario=producto.precio)
        
        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=user,
            direccion_envio=None,
            total_pedido=Decimal('246.90'),
            metodo_pago='Prueba',
            estado='pendiente'
        )
        DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=2,
            precio_unitario=producto.precio,
            subtotal=Decimal('246.90')
        )
        
        # Buscar el resumen creado automáticamente
        resumen = getattr(pedido, 'resumen', None)
        if not resumen:
            self.stdout.write(self.style.ERROR('No se creó el resumen automáticamente.'))
            return
        
        # Generar PDF
        PDFService.generar_resumen_pedido_pdf(resumen)
        self.stdout.write(self.style.SUCCESS(f'PDF generado para resumen {resumen.numero_resumen}'))
        
        # Enviar email
        EmailService.enviar_resumen_pedido_email(resumen)
        self.stdout.write(self.style.SUCCESS(f'Email enviado para resumen {resumen.numero_resumen}'))
        
        self.stdout.write(self.style.SUCCESS('¡Prueba completada!'))