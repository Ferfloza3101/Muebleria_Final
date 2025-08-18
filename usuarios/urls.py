from django.urls import path
from . import views

app_name = 'usuarios'

# rutas de usuarios
urlpatterns = [
    path('', views.perfil, name='perfil'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    # URLs para direcciones
    path('direcciones/', views.direcciones_lista, name='direcciones_lista'),
    path('direcciones/agregar/', views.direccion_agregar, name='direccion_agregar'),
    path('direcciones/<int:direccion_id>/eliminar/', views.direccion_eliminar, name='direccion_eliminar'),
    path('direcciones/<int:direccion_id>/principal/', views.direccion_principal, name='direccion_principal'),
    path('pedidos/fragment/', views.pedidos_fragment, name='pedidos_fragment'),
]
