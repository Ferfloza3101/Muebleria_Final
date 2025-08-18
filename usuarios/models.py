from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=10, choices=[('masculino', 'Masculino'), ('femenino', 'Femenino')], null=True, blank=True)

    def __str__(self):
        return self.user.username

class DireccionUsuario(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='direcciones')
    
    # Información básica
    nombre = models.CharField(max_length=100, help_text="Ej: Casa, Trabajo, etc.")
    telefono = models.CharField(max_length=20, blank=True)
    principal = models.BooleanField(default=False)
    
    # Componentes de la dirección
    calle = models.CharField(max_length=200)
    numero_exterior = models.CharField(max_length=20, blank=True)
    numero_interior = models.CharField(max_length=20, blank=True)
    colonia = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    pais = models.CharField(max_length=100, default='México')
    
    # Información adicional
    referencias = models.TextField(blank=True, help_text="Entre calles, puntos de referencia, etc.")
    
    # Datos de Google Places
    place_id = models.CharField(max_length=255, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dirección de Usuario"
        verbose_name_plural = "Direcciones de Usuario"
        ordering = ['-principal', '-fecha_creacion']

    def __str__(self):
        return f"{self.user.username} - {self.nombre}"

    def get_direccion_completa(self):
        """Retorna la dirección formateada completa"""
        partes = []
        if self.calle:
            calle_num = f"{self.calle}"
            if self.numero_exterior:
                calle_num += f" #{self.numero_exterior}"
            if self.numero_interior:
                calle_num += f" Int. {self.numero_interior}"
            partes.append(calle_num)
        
        if self.colonia:
            partes.append(f"Col. {self.colonia}")
        
        if self.ciudad:
            partes.append(self.ciudad)
        
        if self.estado:
            partes.append(self.estado)
        
        if self.codigo_postal:
            partes.append(f"CP {self.codigo_postal}")
        
        return ", ".join(partes)

    def get_direccion_corta(self):
        """Retorna una versión corta de la dirección"""
        return f"{self.calle} #{self.numero_exterior}, {self.colonia}, {self.ciudad}"

class MetodoPago(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metodos_pago')
    mp_customer_id = models.CharField(max_length=64, help_text='ID de customer en MercadoPago')
    mp_card_id = models.CharField(max_length=64, help_text='ID de tarjeta en MercadoPago')
    ultimos4 = models.CharField(max_length=4, help_text='Últimos 4 dígitos de la tarjeta')
    nombre_tarjeta = models.CharField(max_length=64, help_text='Nombre en la tarjeta')
    marca = models.CharField(max_length=32, help_text='Marca de la tarjeta (Visa, MasterCard, etc.)')
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['-principal', '-fecha_agregado']

    def __str__(self):
        return f"{self.user.username} - {self.marca} ****{self.ultimos4}"
