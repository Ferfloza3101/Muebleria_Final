from django.db import models
from django.conf import settings

# categorias del blog
class CategoriaChoices(models.TextChoices):
    RECAMARA = 'recamara', 'Recámara'
    SALA = 'sala', 'Sala'
    COMEDOR = 'comedor', 'Comedor'
    BANO = 'bano', 'Baño'

# modelo de blog
class Blog(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_index=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', blank=True)
    imagen = models.ImageField(upload_to='blogs/', blank=True, null=True)
    categoria = models.CharField(max_length=30, choices=CategoriaChoices.choices, default=CategoriaChoices.RECAMARA, db_index=True)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-fecha_creacion']

# modelo de comentario
class Comentario(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.blog.titulo}"

    class Meta:
        ordering = ['-fecha']
