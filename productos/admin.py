from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages
from .models import Producto, Categoria, Inventario, Carrito, ItemCarrito, ImagenProducto, Wishlist, BannerPromocional, Pedido, DetallePedido, ResumenPedido
from .services.pdf_service import PDFService
from .services.email_service import EmailService

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'precio_oferta', 'oferta_activa', 'activo', 'ventas')
    list_filter = ('categoria', 'oferta_activa', 'activo')
    search_fields = ('nombre', 'descripcion')
    inlines = [ImagenProductoInline]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'stock', 'stock_minimo', 'stock_maximo')
    list_filter = ('stock_minimo', 'stock_maximo')
    search_fields = ('producto__nombre',)

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'productos_en_carrito')
    search_fields = ('usuario__username',)
    def productos_en_carrito(self, obj):
        items = ItemCarrito.objects.filter(carrito=obj).select_related('producto')
        if not items:
            return '(Vacío)'
        return ', '.join([f"{item.producto.nombre} (x{item.cantidad})" for item in items])
    productos_en_carrito.short_description = 'Productos en carrito'

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('carrito', 'producto', 'cantidad', 'precio_unitario')
    list_filter = ('carrito',)
    search_fields = ('producto__nombre', 'carrito__usuario__username')

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'orden', 'fecha_creacion')
    list_filter = ('producto',)
    search_fields = ('producto__nombre',)
    ordering = ('producto', 'orden', 'fecha_creacion')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'productos_count')
    search_fields = ('usuario__username', 'productos__nombre')
    filter_horizontal = ('productos',)
    def productos_count(self, obj):
        return obj.productos.count()
    productos_count.short_description = 'N° de productos'

@admin.register(BannerPromocional)
class BannerPromocionalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'activo')
    list_filter = ('activo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'subtitulo', 'texto')
    filter_horizontal = ('productos_carrusel',)

# ============================================================================
# ADMIN PARA PEDIDOS Y RESÚMENES
# ============================================================================

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'usuario', 'fecha_pedido', 'total_pedido', 'estado', 'metodo_pago')
    list_filter = ('estado', 'metodo_pago', 'fecha_pedido')
    search_fields = ('numero_pedido', 'usuario__username', 'usuario__email')
    readonly_fields = ('numero_pedido', 'fecha_pedido', 'fecha_actualizacion')
    inlines = [DetallePedidoInline]
    ordering = ('-fecha_pedido',)
    actions = ['generar_pdf_manual', 'enviar_email_manual']
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'fecha_pedido', 'fecha_actualizacion', 'estado')
        }),
        ('Información de Pago', {
            'fields': ('total_pedido', 'metodo_pago', 'referencia_pago', 'estado_pago')
        }),
        ('Dirección de Envío', {
            'fields': ('direccion_envio',),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'direccion_envio')
    
    def generar_pdf_manual(self, request, queryset):
        """Genera PDF manualmente para los pedidos seleccionados"""
        for pedido in queryset:
            if hasattr(pedido, 'resumen'):
                try:
                    # Generar definición del PDF
                    doc_definition = PDFService.generar_resumen_pedido_pdf(pedido.resumen)
                    if doc_definition:
                        messages.success(request, f'PDF generado para pedido {pedido.numero_pedido}')
                    else:
                        messages.error(request, f'Error generando PDF para pedido {pedido.numero_pedido}')
                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
            else:
                messages.warning(request, f'No hay resumen para pedido {pedido.numero_pedido}')
    
    generar_pdf_manual.short_description = "Generar PDF manualmente"
    
    def enviar_email_manual(self, request, queryset):
        """Envía email manualmente para los pedidos seleccionados"""
        for pedido in queryset:
            if hasattr(pedido, 'resumen'):
                try:
                    success = EmailService.enviar_resumen_pedido_email(pedido.resumen)
                    if success:
                        messages.success(request, f'Email enviado para pedido {pedido.numero_pedido}')
                    else:
                        messages.error(request, f'Error enviando email para pedido {pedido.numero_pedido}')
                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
            else:
                messages.warning(request, f'No hay resumen para pedido {pedido.numero_pedido}')
    
    enviar_email_manual.short_description = "Enviar email manualmente"

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__estado', 'producto__categoria')
    search_fields = ('pedido__numero_pedido', 'producto__nombre')
    readonly_fields = ('subtotal',)
    ordering = ('-pedido__fecha_pedido',)

@admin.register(ResumenPedido)
class ResumenPedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_resumen', 'pedido', 'fecha_emision', 'total', 'enviado_por_email')
    list_filter = ('enviado_por_email', 'fecha_emision')
    search_fields = ('numero_resumen', 'pedido__numero_pedido')
    readonly_fields = ('numero_resumen', 'fecha_emision', 'subtotal', 'total')
    ordering = ('-fecha_emision',)
    actions = ['generar_pdf_manual', 'enviar_email_manual']
    
    fieldsets = (
        ('Información del Resumen', {
            'fields': ('numero_resumen', 'pedido', 'fecha_emision')
        }),
        ('Totales', {
            'fields': ('subtotal', 'total')
        }),
        ('Archivo PDF', {
            'fields': ('archivo_pdf',)
        }),
        ('Estado de Envío', {
            'fields': ('enviado_por_email', 'fecha_envio_email')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pedido')
    
    def generar_pdf_manual(self, request, queryset):
        """Genera PDF manualmente para los resúmenes seleccionados"""
        for resumen in queryset:
            try:
                # Generar definición del PDF
                doc_definition = PDFService.generar_resumen_pedido_pdf(resumen)
                if doc_definition:
                    messages.success(request, f'PDF generado para resumen {resumen.numero_resumen}')
                else:
                    messages.error(request, f'Error generando PDF para resumen {resumen.numero_resumen}')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    generar_pdf_manual.short_description = "Generar PDF manualmente"
    
    def enviar_email_manual(self, request, queryset):
        """Envía email manualmente para los resúmenes seleccionados"""
        for resumen in queryset:
            try:
                success = EmailService.enviar_resumen_pedido_email(resumen)
                if success:
                    messages.success(request, f'Email enviado para resumen {resumen.numero_resumen}')
                else:
                    messages.error(request, f'Error enviando email para resumen {resumen.numero_resumen}')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    enviar_email_manual.short_description = "Enviar email manualmente"
