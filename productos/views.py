"""
Vistas de productos
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import transaction
import unicodedata
from django.utils import timezone
import mercadopago
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.urls import reverse
from productos.services.pdf_service import PDFService
from productos.services.email_service import EmailService

from .models import Producto, Categoria, Wishlist, Carrito, ItemCarrito, BannerPromocional, Pedido, DetallePedido, ResumenPedido
from .utils import get_wishlist_ids, get_product_stock, get_cart_total_items, prepare_product_images
from .mixins import WishlistMixin, CartMixin, ProductMixin
from blog.models import Blog
from usuarios.models import DireccionUsuario
from suscripciones.forms import SuscripcionForm


# Instancias de mixins para usar en las vistas
wishlist_mixin = WishlistMixin()
cart_mixin = CartMixin()
product_mixin = ProductMixin()


def home(request):
    """
    Vista de inicio que muestra productos aleatorios en el carrusel y grid, y top productos.
    También procesa el formulario de suscripción por email.
    """
    mensaje_suscripcion = None
    mensaje_tipo = None
    if request.method == 'POST':
        form_suscripcion = SuscripcionForm(request.POST)
        if form_suscripcion.is_valid():
            form_suscripcion.save()
            mensaje_suscripcion = '¡Te has suscrito exitosamente!'
            mensaje_tipo = 'exito'
            form_suscripcion = SuscripcionForm()  # Limpiar el formulario
        else:
            mensaje_suscripcion = form_suscripcion.errors.get('email', ['Error en el formulario'])[0]
            mensaje_tipo = 'error'
    else:
        form_suscripcion = SuscripcionForm()

    # Obtener productos para el carrusel (3 productos aleatorios)
    productos_aleatorios = list(Producto.objects.filter(activo=True).order_by('?')[:3])
    
    # Preparar imágenes para cada producto del carrusel
    for producto in productos_aleatorios:
        producto.imagenes_list = prepare_product_images(producto)
    
    # Obtener productos para el grid (8 productos, excluyendo los del carrusel)
    productos_carrusel_ids = [p.id for p in productos_aleatorios]
    productos_grid = list(Producto.objects.filter(
        activo=True
    ).exclude(
        id__in=productos_carrusel_ids
    ).order_by('-ventas', '-fecha_creacion')[:8])

    # Obtener top 6 productos por ventas
    top_productos = list(Producto.objects.filter(activo=True).order_by('-ventas', '-fecha_creacion')[:6])
    if all(p.ventas == 0 for p in top_productos):
        # Si todos tienen 0 ventas, mostrar 6 aleatorios
        top_productos = list(Producto.objects.filter(activo=True).order_by('?')[:6])
    
    banner = BannerPromocional.objects.filter(
        activo=True,
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    ).order_by('-fecha_inicio').first()
    banner_productos_carrusel = banner.productos_carrusel.all() if banner else []
    
    blogs_recientes = Blog.objects.order_by('-fecha_creacion')[:2]
    
    context = {
        'productos_carrusel': productos_aleatorios,
        'productos_grid': productos_grid,
        'top_productos': top_productos,
        'banner': banner,
        'banner_productos_carrusel': banner_productos_carrusel,
        'blogs_recientes': blogs_recientes,
        'form_suscripcion': form_suscripcion,
        'mensaje_suscripcion': mensaje_suscripcion,
        'mensaje_tipo': mensaje_tipo,
    }
    return render(request, 'inicio.html', context)


def lista_productos(request, categoria_slug=None):
    """
    Vista para listar productos con filtros por categoría y búsqueda.
    """
    # Si no viene en los parámetros de URL, intentar obtenerlo de GET
    if categoria_slug is None:
        categoria_slug = request.GET.get('categoria')
    
    query = request.GET.get('q')
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    categorias = Categoria.objects.all()
    
    # Aplicar filtros
    if categoria_slug == 'ofertas':
        productos = productos.filter(oferta_activa=True)
    elif categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria)
    
    # Búsqueda por nombre y también por nombre de categoría. Si el término
    # coincide claramente con una categoría, redirigir a esa categoría.
    if query:
        def _normalize(text: str) -> str:
            if not isinstance(text, str):
                return ''
            text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
            return text.strip().lower()

        norm_q = _normalize(query)

        # Intentar detectar categoría si no se pasó categoria_slug explícito
        if not categoria_slug:
            matched_cat = None
            for cat in categorias:
                name = _normalize(cat.nombre)
                slug = _normalize(cat.slug)
                # Coincidencia directa o contenida (p.ej. "camas en general")
                if (
                    norm_q == name or
                    norm_q == slug or
                    name in norm_q or
                    norm_q in name
                ):
                    matched_cat = cat
                    break
            if matched_cat:
                return redirect('productos:lista_por_categoria', categoria_slug=matched_cat.slug)

        # Filtro OR: por nombre de producto o por nombre de categoría
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )

    # Obtener contexto de wishlist
    wishlist_context = wishlist_mixin.get_wishlist_context(request.user)

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_slug,
        'query': query,
        **wishlist_context,
    })


@login_required
def detalle_producto(request, producto_id):
    """
    Vista para mostrar el detalle completo de un producto.
    """
    producto, imagenes = product_mixin.get_product_with_images(producto_id)
    stock = get_product_stock(producto)
    
    return render(request, 'productos/detalle_producto.html', {
        'producto': producto,
        'imagenes': imagenes,
        'stock': stock,
        'mensaje': 'Detalle del producto',
    })


@login_required
def ver_carrito(request):
    """
    Vista para mostrar el carrito real del usuario.
    """
    carrito = Carrito.objects.filter(usuario=request.user).first()
    items = []
    total = 0
    if carrito:
        items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
        for item in items:
            item.subtotal = item.cantidad * item.precio_unitario
        total = sum(item.subtotal for item in items)
    return render(request, 'productos/ver_carrito.html', {
        'items': items,
        'total': total,
    })


@login_required
@require_POST
def toggle_wishlist(request, pk):
    """
    Vista AJAX para agregar/quitar productos de la wishlist.
    """
    producto = get_object_or_404(Producto, pk=pk)
    wishlist, created = Wishlist.objects.get_or_create(usuario=request.user)
    
    if producto in wishlist.productos.all():
        wishlist.productos.remove(producto)
        added = False
    else:
        wishlist.productos.add(producto)
        added = True
    
    return JsonResponse({'added': added})


@login_required
def ver_favoritos(request):
    """
    Vista para mostrar todos los productos en la wishlist del usuario.
    """
    wishlist, _ = Wishlist.objects.get_or_create(usuario=request.user)
    return render(request, 'productos/favoritos.html', {'wishlist': wishlist})


@require_GET
def wishlist_menu_ajax(request):
    """
    Vista AJAX para cargar el menú de wishlist.
    """
    if not request.user.is_authenticated:
        return HttpResponse('<div class="wishlist-empty">No tienes favoritos aún.</div>')
    
    wishlist, _ = Wishlist.objects.get_or_create(usuario=request.user)
    html = render_to_string('productos/partials/wishlist_menu.html', {'wishlist_menu': wishlist})
    return HttpResponse(html)


@login_required
@require_POST
def agregar_al_carrito(request, pk):
    """
    Vista AJAX para agregar productos al carrito.
    """
    producto = get_object_or_404(Producto, pk=pk)
    carrito = cart_mixin.get_or_create_cart(request.user)
    
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (ValueError, TypeError):
        cantidad = 1
    if cantidad < 1:
        return JsonResponse({'ok': False, 'error': 'Cantidad inválida.'}, status=400)

    stock = get_product_stock(producto)
    if cantidad > stock:
        return JsonResponse({'ok': False, 'error': f'Solo hay {stock} unidades disponibles.'}, status=400)
    
    cart_mixin.update_cart_item(carrito, producto, cantidad)
    total_items = get_cart_total_items(carrito)
    return JsonResponse({'ok': True, 'count': total_items})


@require_GET
def carrito_menu_ajax(request):
    """
    Vista AJAX para cargar el menú del carrito.
    """
    if not request.user.is_authenticated:
        return HttpResponse('<div class="cart-empty">No hay productos en el carrito.</div>')
    
    carrito = cart_mixin.get_or_create_cart(request.user)
    items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
    subtotal = sum(item.cantidad * item.precio_unitario for item in items)
    
    html = render_to_string('productos/partials/carrito_menu.html', {
        'carrito': carrito, 
        'items': items, 
        'subtotal': subtotal
    })
    return HttpResponse(html)


@login_required
@require_POST
def eliminar_del_carrito(request, pk):
    """
    Vista AJAX para eliminar productos del carrito.
    """
    producto = get_object_or_404(Producto, pk=pk)
    carrito = cart_mixin.get_or_create_cart(request.user)
    item = cart_mixin.get_cart_item(carrito, producto)
    if item:
        item.delete()
        total_items = get_cart_total_items(carrito)
        return JsonResponse({'ok': True, 'count': total_items, 'removed': True})
    else:
        return JsonResponse({'ok': False, 'error': 'Producto no está en el carrito'})


@login_required
@require_POST
def vaciar_carrito(request):
    """
    Vista AJAX para vaciar completamente el carrito.
    """
    carrito = cart_mixin.get_or_create_cart(request.user)
    ItemCarrito.objects.filter(carrito=carrito).delete()
    return JsonResponse({'ok': True, 'count': 0})


@login_required
@require_POST
def disminuir_cantidad_carrito(request, pk):
    """
    Vista AJAX para disminuir la cantidad de un producto en el carrito.
    """
    producto = get_object_or_404(Producto, pk=pk)
    carrito = cart_mixin.get_or_create_cart(request.user)
    item = cart_mixin.get_cart_item(carrito, producto)
    if item:
        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
            total_items = get_cart_total_items(carrito)
            return JsonResponse({'ok': True, 'count': total_items})
        else:
            item.delete()
            total_items = get_cart_total_items(carrito)
            return JsonResponse({'ok': True, 'count': total_items, 'removed': True})
    else:
        return JsonResponse({'ok': False, 'error': 'Producto no está en el carrito'})


# Context processor para la wishlist
def wishlist_menu_context(request):
    """
    Context processor para proporcionar datos de wishlist a todas las vistas.
    """
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(usuario=request.user)
        return {'wishlist_menu': wishlist}
    return {'wishlist_menu': None}


@require_GET
def filtrado_productos_ajax(request):
    categoria_slug = request.GET.get('categoria')
    query = request.GET.get('q')
    productos = Producto.objects.filter(activo=True)
    if categoria_slug == 'ofertas':
        productos = productos.filter(oferta_activa=True)
    elif categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria)
    if query:
        productos = productos.filter(nombre__icontains=query)
    categorias = Categoria.objects.all()
    wishlist_context = wishlist_mixin.get_wishlist_context(request.user)
    html = render_to_string('productos/partials/grid_productos.html', {
        'productos': productos,
        'wishlist_ids': wishlist_context.get('wishlist_ids', []),
    }, request=request)
    return JsonResponse({'html': html})


@login_required
def seleccionar_direccion(request):
    """seleccionar direccion de envio"""
    direcciones = request.user.direcciones.all()
    direccion_id_param = request.GET.get('direccion_id')
    try:
        direccion_seleccionada_id = int(direccion_id_param) if direccion_id_param else None
    except (TypeError, ValueError):
        direccion_seleccionada_id = None
    return render(request, 'productos/seleccionar_direccion.html', {
        'direcciones': direcciones,
        'direccion_seleccionada_id': direccion_seleccionada_id,
    })

@login_required
def agregar_direccion(request):
    """agregar direccion de envio"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        calle = request.POST.get('calle')
        numero_exterior = request.POST.get('numero_exterior', '')
        numero_interior = request.POST.get('numero_interior', '')
        colonia = request.POST.get('colonia')
        ciudad = request.POST.get('ciudad')
        estado = request.POST.get('estado')
        codigo_postal = request.POST.get('codigo_postal')
        telefono = request.POST.get('telefono', '')
        referencias = request.POST.get('referencias', '')

        nueva = DireccionUsuario.objects.create(
            user=request.user,
            nombre=nombre or '',
            calle=calle or '',
            numero_exterior=numero_exterior or '',
            numero_interior=numero_interior or '',
            colonia=colonia or '',
            ciudad=ciudad or '',
            estado=estado or '',
            codigo_postal=codigo_postal or '',
            telefono=telefono or '',
            referencias=referencias or '',
        )
        return redirect(f"{reverse('productos:seleccionar_direccion')}?direccion_id={nueva.id}")
    return render(request, 'productos/agregar_direccion.html')

@login_required
def confirmar_pedido(request):
    """
    Vista para confirmar el pedido antes de pagar.
    """
    direccion_id = request.GET.get('direccion_id')
    direccion = None
    if direccion_id:
        direccion = request.user.direcciones.filter(id=direccion_id).first()
    carrito = Carrito.objects.filter(usuario=request.user).first()
    items = []
    total = 0
    if carrito:
        items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
        for item in items:
            item.subtotal = item.cantidad * item.precio_unitario
        total = sum(item.subtotal for item in items)
    return render(request, 'productos/confirmar_pedido.html', {
        'direccion': direccion,
        'items': items,
        'total': total,
    })


@login_required
@require_POST
@csrf_exempt
def pago_mercadopago(request):
    """Genera preferencia de pago y devuelve URL"""
    import json
    from django.conf import settings as dj_settings
    data = json.loads(request.body)
    direccion_id = data.get('direccion_id')
    direccion = request.user.direcciones.filter(id=direccion_id).first()
    carrito = Carrito.objects.filter(usuario=request.user).first()
    items = []
    preference_items = []
    if carrito:
        items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
        for item in items:
            preference_items.append({
                "title": item.producto.nombre,
                "quantity": int(item.cantidad),
                "unit_price": float(item.precio_unitario),
                "currency_id": "MXN"
            })
    if not preference_items or not direccion:
        return JsonResponse({"error": "Datos incompletos para procesar el pago."}, status=400)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    base_url = request.build_absolute_uri('/').rstrip('/')
    success_url = f"{base_url}/productos/carrito/pago-exitoso/"
    failure_url = f"{base_url}/productos/carrito/pago-fallido/"
    pending_url = f"{base_url}/productos/carrito/pago-pendiente/"
    
    preference_data = {
        "items": preference_items,
        "payer": {
            "name": request.user.first_name or request.user.username,
            "email": request.user.email,
            "address": {
                "zip_code": getattr(direccion, 'codigo_postal', ''),
                "street_name": getattr(direccion, 'calle', ''),
                "street_number": getattr(direccion, 'numero_exterior', ''),
            }
        },
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url,
        },
        "external_reference": str(carrito.id),
    }
    
    print(f"URLs de redirección configuradas:")
    print(f"Success: {success_url}")
    print(f"Failure: {failure_url}")
    print(f"Pending: {pending_url}")
    
    preference_response = sdk.preference().create(preference_data)
    if "error" in preference_response["response"]:
        print("MercadoPago error:", preference_response["response"]["error"])
        return JsonResponse({"error": str(preference_response["response"]["error"]), "debug": preference_response["response"]}, status=500)
    
    url = preference_response["response"].get("init_point")
    if not url:
        print("MercadoPago response sin init_point:", preference_response["response"])
        return JsonResponse({"error": "No se pudo generar la preferencia de pago.", "debug": preference_response["response"]}, status=500)
    
    print(f"Preferencia creada exitosamente. URL: {url}")
    return JsonResponse({"url": url})


# vistas para pedidos y resúmenes

@login_required
def crear_pedido_desde_carrito(request):
    """
    Crea un pedido desde el carrito actual del usuario
    """
    try:
        carrito = Carrito.objects.filter(usuario=request.user).first()
        if not carrito:
            return JsonResponse({"error": "No hay carrito activo"}, status=400)

        items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
        if not items.exists():
            return JsonResponse({"error": "El carrito está vacío"}, status=400)

        # Obtener dirección seleccionada
        direccion_id = request.POST.get('direccion_id')
        direccion = request.user.direcciones.filter(id=direccion_id).first()
        if not direccion:
            return JsonResponse({"error": "Debe seleccionar una dirección de envío"}, status=400)

        # Verificar stock disponible antes de crear el pedido
        for item in items:
            inventario = getattr(item.producto, 'inventario', None)
            disponible = inventario.stock if inventario else 0
            if item.cantidad > disponible:
                return JsonResponse({
                    "error": f"Stock insuficiente para {item.producto.nombre}. Disponible: {disponible}"
                }, status=400)

        # Calcular total
        total = sum(item.cantidad * item.precio_unitario for item in items)

        with transaction.atomic():
            # Crear pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                direccion_envio=direccion,
                total_pedido=total,
                metodo_pago='MercadoPago',
                estado='pendiente'
            )

            # Crear detalles del pedido y descontar stock
            for item in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    subtotal=item.cantidad * item.precio_unitario
                )
                inventario = getattr(item.producto, 'inventario', None)
                if inventario:
                    inventario.stock = max(0, inventario.stock - item.cantidad)
                    inventario.save(update_fields=['stock'])
                # Actualizar ventas del producto
                item.producto.ventas = (item.producto.ventas or 0) + item.cantidad
                item.producto.save(update_fields=['ventas'])

            # Crear resumen del pedido
            resumen = ResumenPedido.objects.create(
                pedido=pedido,
                subtotal=total,
                total=total
            )

            # Limpiar carrito
            carrito.productos.clear()

        return JsonResponse({
            "success": True,
            "pedido_id": pedido.id,
            "numero_pedido": pedido.numero_pedido,
            "resumen_id": resumen.id
        })

    except Exception as e:
        print(f"Error creando pedido: {str(e)}")
        return JsonResponse({"error": "Error interno del servidor"}, status=500)

@login_required
def listar_mis_pedidos(request):
    """
    Lista todos los pedidos del usuario
    """
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    return render(request, 'productos/mis_pedidos.html', {
        'pedidos': pedidos
    })

@login_required
def detalle_pedido(request, pedido_id):
    """
    Muestra el detalle de un pedido específico
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'productos/detalle_pedido.html', {
        'pedido': pedido
    })

@login_required
def descargar_resumen_pdf(request, resumen_id):
    """
    Descarga el PDF del resumen de pedido
    """
    resumen = get_object_or_404(ResumenPedido, id=resumen_id, pedido__usuario=request.user)
    
    if resumen.archivo_pdf:
        response = HttpResponse(resumen.archivo_pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resumen_pedido_{resumen.pedido.numero_pedido}.pdf"'
        return response
    else:
        return JsonResponse({"error": "PDF no encontrado"}, status=404)

@login_required
@require_POST
def enviar_resumen_email(request):
    """
    Envía el resumen de pedido por email
    """
    try:
        data = json.loads(request.body)
        pedido_id = data.get('pedido_id')
        email_destino = data.get('email_destino')
        
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
        resumen = get_object_or_404(ResumenPedido, pedido=pedido)
        
        # Enviar email
        success = EmailService.enviar_resumen_pedido_email(resumen, email_destino)
        
        if success:
            return JsonResponse({"success": True, "message": "Resumen enviado exitosamente"})
        else:
            return JsonResponse({"error": "Error al enviar el email"}, status=500)
            
    except Exception as e:
        print(f"Error enviando resumen por email: {str(e)}")
        return JsonResponse({"error": "Error interno del servidor"}, status=500)

@login_required
def generar_pdf_frontend(request, resumen_id):
    """
    Genera la definición del PDF para el frontend
    """
    resumen = get_object_or_404(ResumenPedido, id=resumen_id, pedido__usuario=request.user)
    
    # Generar definición del PDF
    doc_definition = PDFService.generar_pdf_frontend(resumen)
    
    if doc_definition:
        return JsonResponse({
            "success": True,
            "doc_definition": doc_definition
        })
    else:
        return JsonResponse({"error": "Error generando PDF"}, status=500)

# callbacks de mercadopago

@csrf_exempt
def pago_exitoso(request):
    """
    Callback para pagos exitosos de MercadoPago
    """
    try:
        # Obtener datos del pago
        payment_id = request.GET.get('payment_id')
        external_reference = request.GET.get('external_reference')
        preference_id = request.GET.get('preference_id')
        
        print(f"Pago exitoso recibido:")
        print(f"Payment ID: {payment_id}")
        print(f"External Reference: {external_reference}")
        print(f"Preference ID: {preference_id}")
        
        # Si hay external_reference, buscar el carrito y crear pedido
        if external_reference and request.user.is_authenticated:
            try:
                carrito = Carrito.objects.get(id=external_reference, usuario=request.user)
                
                # Verificar si ya existe un pedido para este carrito
                pedido_existente = Pedido.objects.filter(
                    referencia_pago=payment_id
                ).first()
                
                if not pedido_existente:
                    # Crear pedido desde el carrito, verificando stock y descontando
                    items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
                    if items.exists():
                        # Obtener la dirección del usuario (asumimos que tiene al menos una)
                        direccion = request.user.direcciones.first()

                        # Verificar stock disponible
                        for item in items:
                            inventario = getattr(item.producto, 'inventario', None)
                            disponible = inventario.stock if inventario else 0
                            if item.cantidad > disponible:
                                print(f"Stock insuficiente para {item.producto.nombre} en pago_exitoso")
                                # No crear pedido si no hay stock suficiente
                                return render(request, 'productos/pago_exitoso.html', {
                                    'payment_id': payment_id,
                                    'error': f'Stock insuficiente para {item.producto.nombre}. Disponible: {disponible}'
                                })

                        # Calcular total
                        total = sum(item.cantidad * item.precio_unitario for item in items)

                        with transaction.atomic():
                            # Crear pedido
                            pedido = Pedido.objects.create(
                                usuario=request.user,
                                direccion_envio=direccion,
                                total_pedido=total,
                                metodo_pago='MercadoPago',
                                referencia_pago=payment_id,
                                estado_pago='aprobado',
                                estado='procesando'
                            )

                            # Crear detalles y descontar stock
                            for item in items:
                                DetallePedido.objects.create(
                                    pedido=pedido,
                                    producto=item.producto,
                                    cantidad=item.cantidad,
                                    precio_unitario=item.precio_unitario,
                                    subtotal=item.cantidad * item.precio_unitario
                                )
                                inventario = getattr(item.producto, 'inventario', None)
                                if inventario:
                                    inventario.stock = max(0, inventario.stock - item.cantidad)
                                    inventario.save(update_fields=['stock'])
                                item.producto.ventas = (item.producto.ventas or 0) + item.cantidad
                                item.producto.save(update_fields=['ventas'])

                            # Limpiar carrito
                            carrito.productos.clear()
                        
                        print(f"Pedido creado exitosamente: {pedido.numero_pedido}")
                        
                        # Enviar email de confirmación
                        try:
                            if hasattr(pedido, 'resumen'):
                                EmailService.enviar_resumen_pedido_email(pedido.resumen)
                                print(f"Email enviado para pedido {pedido.numero_pedido}")
                        except Exception as e:
                            print(f"Error enviando email: {str(e)}")
                    else:
                        print("Carrito vacío, no se puede crear pedido")
                else:
                    print(f"Pedido ya existe para payment_id: {payment_id}")
                    
            except Carrito.DoesNotExist:
                print(f"Carrito no encontrado para external_reference: {external_reference}")
        
        return render(request, 'productos/pago_exitoso.html', {
            'payment_id': payment_id,
            'pedido_creado': True
        })
        
    except Exception as e:
        print(f"Error en pago exitoso: {str(e)}")
        return render(request, 'productos/pago_exitoso.html', {
            'error': str(e)
        })

@csrf_exempt
def pago_fallido(request):
    """
    Callback para pagos fallidos de MercadoPago
    """
    payment_id = request.GET.get('payment_id')
    external_reference = request.GET.get('external_reference')
    
    print(f"Pago fallido recibido:")
    print(f"Payment ID: {payment_id}")
    print(f"External Reference: {external_reference}")
    
    return render(request, 'productos/pago_fallido.html', {
        'payment_id': payment_id
    })

@csrf_exempt
def pago_pendiente(request):
    """
    Callback para pagos pendientes de MercadoPago
    """
    payment_id = request.GET.get('payment_id')
    external_reference = request.GET.get('external_reference')
    
    print(f"Pago pendiente recibido:")
    print(f"Payment ID: {payment_id}")
    print(f"External Reference: {external_reference}")
    
    return render(request, 'productos/pago_pendiente.html', {
        'payment_id': payment_id
    })

@csrf_exempt
def webhook_mercadopago(request):
    """
    Webhook para recibir notificaciones de MercadoPago
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Webhook recibido: {data}")
            
            # Procesar la notificación según el tipo
            if data.get('type') == 'payment':
                payment_id = data.get('data', {}).get('id')
                if payment_id:
                    # Aquí puedes procesar el pago según su estado
                    print(f"Procesando pago: {payment_id}")
            
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"Error procesando webhook: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def pago_prueba(request):
    """
    Simula el pago: crea el pedido, genera PDF, envía email y vacía el carrito.
    """
    if request.method != 'POST':
        return redirect('productos:confirmar_pedido')
    try:
        direccion_id = request.POST.get('direccion_id')
        direccion = request.user.direcciones.filter(id=direccion_id).first()
        carrito = Carrito.objects.filter(usuario=request.user).first()
        if not direccion or not carrito:
            return redirect('productos:confirmar_pedido')
        items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
        if not items.exists():
            return redirect('productos:ver_carrito')
        
        # Verificar stock disponible
        for item in items:
            inventario = getattr(item.producto, 'inventario', None)
            disponible = inventario.stock if inventario else 0
            if item.cantidad > disponible:
                messages = 'Stock insuficiente para ' + item.producto.nombre
                print(messages)
                return redirect('productos:ver_carrito')

        total = sum(item.cantidad * item.precio_unitario for item in items)

        with transaction.atomic():
            # Crear pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                direccion_envio=direccion,
                total_pedido=total,
                metodo_pago='Pago de prueba',
                estado='procesando',
                estado_pago='aprobado',
            )
            for item in items:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    subtotal=item.cantidad * item.precio_unitario
                )
                inventario = getattr(item.producto, 'inventario', None)
                if inventario:
                    inventario.stock = max(0, inventario.stock - item.cantidad)
                    inventario.save(update_fields=['stock'])
                item.producto.ventas = (item.producto.ventas or 0) + item.cantidad
                item.producto.save(update_fields=['ventas'])
        # El ResumenPedido se crea por señal post_save de Pedido
        resumen = getattr(pedido, 'resumen', None)
        if resumen:
            # Generar PDF y guardar
            doc_def = PDFService.generar_resumen_pedido_pdf(resumen)
            if doc_def:
                pass
        # Vaciar carrito
        carrito.productos.clear()
        return redirect(reverse('productos:detalle_pedido', args=[pedido.id]))
    except Exception as e:
        print(f"Error en pago_prueba: {str(e)}")
        return redirect('productos:confirmar_pedido')

@login_required
@csrf_exempt
def subir_pdf_resumen(request, resumen_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        resumen = ResumenPedido.objects.get(id=resumen_id)
        pdf_file = request.FILES.get('pdf')
        if not pdf_file:
            return JsonResponse({'error': 'No se recibió el archivo PDF.'}, status=400)
        resumen.archivo_pdf.save(pdf_file.name, pdf_file, save=True)
        # Enviar email de confirmación con PDF adjunto
        EmailService.enviar_resumen_pedido_email(resumen)
        return JsonResponse({'success': True})
    except ResumenPedido.DoesNotExist:
        return JsonResponse({'error': 'Resumen no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

