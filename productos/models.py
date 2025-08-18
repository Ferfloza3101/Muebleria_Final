from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorias"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oferta_activa = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    imagen_principal = models.ImageField(upload_to='productos/', null=False, blank=False, default='productos/default.jpg')
    ventas = models.PositiveIntegerField(default=0, help_text='Cantidad de veces que este producto ha sido vendido')

    def __str__(self):
        return self.nombre

    def precio_actual(self):
        if self.oferta_activa and self.precio_oferta:
            return self.precio_oferta
        return self.precio

    @property
    def imagenes(self):
        return self.imagenes_producto.all()

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes_producto')
    imagen = models.ImageField(upload_to='productos/')
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'fecha_creacion']

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    stock_maximo = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"Inventario de {self.producto.nombre}"

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ItemCarrito')

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('carrito', 'producto')

class Wishlist(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, related_name='wishlists')

    def __str__(self):
        return f"Wishlist de {self.usuario.username}"

class BannerPromocional(models.Model):
    titulo = models.CharField(max_length=120)
    subtitulo = models.CharField(max_length=120, blank=True)
    texto = models.TextField(blank=True)
    imagen_lateral = models.ImageField(upload_to='banners/', blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    texto_boton = models.CharField(max_length=50, default='Comprar ahora')
    url_boton = models.URLField(blank=True, null=True)
    producto_destacado = models.ForeignKey('Producto', on_delete=models.SET_NULL, null=True, blank=True, related_name='banners_destacados')
    productos_carrusel = models.ManyToManyField('Producto', blank=True, related_name='banners_carrusel')
    activo = models.BooleanField(default=True)
    texto_descuento = models.CharField(max_length=80, default='Hasta 50% de descuento')

    class Meta:
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.titulo

    def esta_activo(self):
        import datetime
        now = datetime.datetime.now()
        return self.activo and self.fecha_inicio <= now <= self.fecha_fin

class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    numero_pedido = models.CharField(max_length=20, unique=True, blank=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Referencia a la dirección seleccionada (usando el modelo existente)
    direccion_envio = models.ForeignKey('usuarios.DireccionUsuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información de pago
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, default='MercadoPago')
    referencia_pago = models.CharField(max_length=100, blank=True)  # ID de MercadoPago
    estado_pago = models.CharField(max_length=20, default='pendiente')
    
    # Estado del pedido
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')
    notas = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.usuario.username}"

    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido único
            self.numero_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_total_detalle(self):
        """Calcula el total basado en los detalles del pedido"""
        return sum(detalle.subtotal for detalle in self.detalles.all())

    def get_datos_cliente(self):
        """Obtiene los datos del cliente desde el perfil"""
        return {
            'nombre': f"{self.usuario.first_name} {self.usuario.last_name}".strip() or self.usuario.username,
            'email': self.usuario.email,
            'telefono': getattr(self.usuario.perfil, 'telefono', '') if hasattr(self.usuario, 'perfil') else '',
        }

    def get_datos_envio(self):
        """Obtiene los datos de envío desde la dirección seleccionada"""
        if self.direccion_envio:
            return {
                'direccion_completa': self.direccion_envio.get_direccion_completa(),
                'telefono': self.direccion_envio.telefono,
                'nombre_direccion': self.direccion_envio.nombre,
            }
        return {}

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - Pedido #{self.pedido.numero_pedido}"

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

class ResumenPedido(models.Model):
    """Aqui se crearan los resumenes automaticamente"""
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='resumen')
    numero_resumen = models.CharField(max_length=20, unique=True, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Archivo PDF
    archivo_pdf = models.FileField(upload_to='resumenes_pedidos/', blank=True, null=True)
    
    # Estado de envío
    enviado_por_email = models.BooleanField(default=False)
    fecha_envio_email = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = 'Resumen de Pedido'
        verbose_name_plural = 'Resúmenes de Pedidos'

    def __str__(self):
        return f"Resumen #{self.numero_resumen} - {self.pedido.numero_pedido}"

    def save(self, *args, **kwargs):
        if not self.numero_resumen:
            # Generar número de resumen único
            self.numero_resumen = f"RES-{uuid.uuid4().hex[:8].upper()}"
        
        # Calcular totales si no están definidos
        if not self.subtotal:
            self.subtotal = self.pedido.get_total_detalle()
        if not self.total:
            self.total = self.subtotal  # Sin IVA para resumen simple
            
        super().save(*args, **kwargs)

    def get_total_formateado(self):
        """Retorna el total formateado como string"""
        return f"${self.total:,.2f}"

    def get_subtotal_formateado(self):
        """Retorna el subtotal formateado como string"""
        return f"${self.subtotal:,.2f}"

# Aqui se crearan los resumenes automaticamente

@receiver(post_save, sender=Pedido)
def crear_resumen_automaticamente(sender, instance, created, **kwargs):
    """crear resumen cuando se crea un pedido"""
    if created:
        # Solo crear resumen si no existe ya
        if not hasattr(instance, 'resumen'):
            ResumenPedido.objects.create(
                pedido=instance,
                subtotal=instance.total_pedido,
                total=instance.total_pedido
            )
            print(f"Resumen creado automáticamente para pedido {instance.numero_pedido}")

@receiver(post_save, sender=DetallePedido)
def actualizar_totales_resumen(sender, instance, created, **kwargs):
    """actualiza totales del resumen cuando se agregan detalles"""
    if created:
        pedido = instance.pedido
        if hasattr(pedido, 'resumen'):
            resumen = pedido.resumen
            resumen.subtotal = pedido.get_total_detalle()
            resumen.total = resumen.subtotal
            resumen.save()
            print(f"Totales actualizados para resumen {resumen.numero_resumen}")
