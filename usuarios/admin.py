from django.contrib import admin
from .models import Perfil, DireccionUsuario

# Register your models here.

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'fecha_nacimiento', 'genero', 'telefono')
    fields = ('user', 'fecha_nacimiento', 'genero', 'telefono')

@admin.register(DireccionUsuario)
class DireccionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'nombre', 'calle', 'ciudad', 'estado', 'principal', 'fecha_creacion')
    list_filter = ('principal', 'ciudad', 'estado', 'fecha_creacion')
    search_fields = ('user__username', 'user__email', 'nombre', 'calle', 'ciudad')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'nombre', 'telefono', 'principal')
        }),
        ('Dirección', {
            'fields': ('calle', 'numero_exterior', 'numero_interior', 'colonia', 'ciudad', 'estado', 'codigo_postal', 'pais')
        }),
        ('Información Adicional', {
            'fields': ('referencias', 'place_id', 'latitud', 'longitud'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
