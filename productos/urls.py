from django.urls import path
from . import views

app_name = 'productos'

# rutas de productos
urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('filtrar/', views.filtrado_productos_ajax, name='filtrado_productos_ajax'),
    path('categoria/<slug:categoria_slug>/', views.lista_productos, name='lista_por_categoria'),
    path('<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/seleccionar-direccion/', views.seleccionar_direccion, name='seleccionar_direccion'),
    path('carrito/agregar-direccion/', views.agregar_direccion, name='agregar_direccion'),
    path('carrito/confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('favoritos/', views.ver_favoritos, name='ver_favoritos'),
    path('wishlist/menu/', views.wishlist_menu_ajax, name='wishlist_menu_ajax'),
    path('carrito/add/<int:pk>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/menu/', views.carrito_menu_ajax, name='carrito_menu_ajax'),
    path('carrito/remove/<int:pk>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/clear/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/decrease/<int:pk>/', views.disminuir_cantidad_carrito, name='disminuir_cantidad_carrito'),
    path('carrito/pago-mercadopago/', views.pago_mercadopago, name='pago_mercadopago'),
    path('carrito/pago-prueba/', views.pago_prueba, name='pago_prueba'),
    
    # urls de pedidos y resúmenes
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/crear/', views.crear_pedido_desde_carrito, name='crear_pedido'),
    path('resumen/<int:resumen_id>/pdf/', views.descargar_resumen_pdf, name='descargar_resumen_pdf'),
    path('resumen/<int:resumen_id>/generar/', views.generar_pdf_frontend, name='generar_pdf_frontend'),
    path('enviar-resumen-email/', views.enviar_resumen_email, name='enviar_resumen_email'),
    path('resumen/<int:resumen_id>/subir_pdf/', views.subir_pdf_resumen, name='subir_pdf_resumen'),
    
    # callbacks de mercadopago
    path('carrito/pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('carrito/pago-fallido/', views.pago_fallido, name='pago_fallido'),
    path('carrito/pago-pendiente/', views.pago_pendiente, name='pago_pendiente'),
    path('webhook-mercadopago/', views.webhook_mercadopago, name='webhook_mercadopago'),
]
