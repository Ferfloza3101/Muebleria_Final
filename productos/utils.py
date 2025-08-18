"""
Utilidades comunes para la aplicación de productos.
Contiene funciones auxiliares que se utilizan en múltiples vistas.
"""

from .models import Wishlist, Carrito, ItemCarrito
from django.db.models import Sum


def get_wishlist_ids(user):
    """
    Obtiene los IDs de productos en la wishlist del usuario.
    
    Args:
        user: Usuario autenticado
        
    Returns:
        list: Lista de IDs de productos en la wishlist
    """
    if user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(usuario=user)
        return list(wishlist.productos.values_list('id', flat=True))
    return []


def get_product_stock(producto):
    """
    Obtiene el stock disponible de un producto.
    
    Args:
        producto: Instancia del modelo Producto
        
    Returns:
        int: Cantidad de stock disponible
    """
    return producto.inventario.stock if hasattr(producto, 'inventario') else 0


def get_cart_total_items(carrito):
    """total de items en el carrito"""
    return ItemCarrito.objects.filter(carrito=carrito).aggregate(total=Sum('cantidad'))['total'] or 0


def prepare_product_images(producto):
    """prepara imagenes del producto"""
    imagenes_secundarias = list(producto.imagenes)
    imagenes = []
    if producto.imagen_principal:
        imagenes.append({'imagen': producto.imagen_principal})
    for img in imagenes_secundarias:
        if not producto.imagen_principal or img.imagen.url != producto.imagen_principal.url:
            imagenes.append({'imagen': img.imagen})
    return imagenes 
















