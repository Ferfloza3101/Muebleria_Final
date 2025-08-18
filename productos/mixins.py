"""
Mixins para la app de productos. Funciones comunes para usar en las vistas.
"""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Producto, Wishlist, Carrito, ItemCarrito
from .utils import get_wishlist_ids, get_product_stock, get_cart_total_items


class WishlistMixin:
    """
    Funciones para la wishlist.
    """
    
    def get_wishlist_context(self, user):
        """
        Devuelve un diccionario con los IDs de la wishlist del usuario.
        """
        return {'wishlist_ids': get_wishlist_ids(user)}


class CartMixin:
    """
    Funciones para el carrito.
    """
    
    def get_or_create_cart(self, user):
        """
        Devuelve el carrito del usuario o lo crea si no existe.
        """
        return Carrito.objects.get_or_create(usuario=user)[0]
    
    def get_cart_item(self, carrito, producto):
        """
        Devuelve un item del carrito o None si no existe.
        """
        try:
            return ItemCarrito.objects.get(carrito=carrito, producto=producto)
        except ItemCarrito.DoesNotExist:
            return None
    
    def update_cart_item(self, carrito, producto, cantidad):
        """
        Crea o actualiza un item en el carrito con la cantidad dada (reemplaza, no suma).
        """
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito, 
            producto=producto
        )
        item.cantidad = cantidad
        item.precio_unitario = producto.precio_actual()
        item.save()
        return item, created


class ProductMixin:
    """
    Funciones para productos.
    """
    
    def get_product_with_stock(self, producto_id):
        """
        Devuelve el producto y su stock.
        """
        producto = get_object_or_404(Producto, id=producto_id)
        stock = get_product_stock(producto)
        return producto, stock
    
    def get_product_with_images(self, producto_id):
        """
        Devuelve el producto y sus imágenes listas para mostrar.
        """
        from .utils import prepare_product_images
        producto = get_object_or_404(Producto, id=producto_id)
        imagenes = prepare_product_images(producto)
        return producto, imagenes 
