import os
import base64
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
import json

class PDFService:
    """
    Servicio para generar PDFs de resumen de pedido usando pdfmake
    """
    
    @staticmethod
    def generar_resumen_pedido_pdf(resumen_pedido):
        """
        Genera un PDF de resumen de pedido usando pdfmake
        """
        try:
            pedido = resumen_pedido.pedido
            datos_cliente = pedido.get_datos_cliente()
            datos_envio = pedido.get_datos_envio()
            
            # Definición del documento PDF
            doc_definition = {
                'pageSize': 'A4',
                'pageMargins': [40, 60, 40, 60],
                'header': {
                    'text': 'RESUMEN DE PEDIDO',
                    'alignment': 'center',
                    'margin': [0, 20, 0, 0],
                    'fontSize': 18,
                    'bold': True
                },
                'footer': {
                    'text': f'Generado el {timezone.now().strftime("%d/%m/%Y %H:%M")}',
                    'alignment': 'center',
                    'margin': [0, 0, 0, 20],
                    'fontSize': 8,
                    'color': '#666666'
                },
                'content': [
                    # Información del pedido
                    {
                        'text': f'Pedido #{pedido.numero_pedido}',
                        'fontSize': 16,
                        'bold': True,
                        'margin': [0, 0, 0, 10]
                    },
                    {
                        'text': f'Fecha: {pedido.fecha_pedido.strftime("%d/%m/%Y %H:%M")}',
                        'fontSize': 10,
                        'margin': [0, 0, 0, 20]
                    },
                    
                    # Información del cliente
                    {
                        'text': 'DATOS DEL CLIENTE',
                        'fontSize': 12,
                        'bold': True,
                        'margin': [0, 20, 0, 10]
                    },
                    {
                        'text': [
                            {'text': 'Nombre: ', 'bold': True},
                            datos_cliente.get('nombre', 'No especificado')
                        ],
                        'fontSize': 10,
                        'margin': [0, 0, 0, 5]
                    },
                    {
                        'text': [
                            {'text': 'Email: ', 'bold': True},
                            datos_cliente.get('email', 'No especificado')
                        ],
                        'fontSize': 10,
                        'margin': [0, 0, 0, 5]
                    },
                    {
                        'text': [
                            {'text': 'Teléfono: ', 'bold': True},
                            datos_cliente.get('telefono', 'No especificado')
                        ],
                        'fontSize': 10,
                        'margin': [0, 0, 0, 20]
                    },
                    
                    # Información de envío
                    {
                        'text': 'DIRECCIÓN DE ENVÍO',
                        'fontSize': 12,
                        'bold': True,
                        'margin': [0, 20, 0, 10]
                    },
                    {
                        'text': [
                            {'text': 'Dirección: ', 'bold': True},
                            datos_envio.get('direccion_completa', 'No especificada')
                        ],
                        'fontSize': 10,
                        'margin': [0, 0, 0, 5]
                    },
                    {
                        'text': [
                            {'text': 'Teléfono: ', 'bold': True},
                            datos_envio.get('telefono', 'No especificado')
                        ],
                        'fontSize': 10,
                        'margin': [0, 0, 0, 20]
                    },
                    
                    # Productos
                    {
                        'text': 'PRODUCTOS',
                        'fontSize': 12,
                        'bold': True,
                        'margin': [0, 20, 0, 10]
                    },
                    # Tabla de productos
                    {
                        'table': {
                            'headerRows': 1,
                            'widths': ['*', 'auto', 'auto', 'auto'],
                            'body': [
                                [
                                    {'text': 'Producto', 'style': 'tableHeader'},
                                    {'text': 'Cantidad', 'style': 'tableHeader'},
                                    {'text': 'Precio Unit.', 'style': 'tableHeader'},
                                    {'text': 'Subtotal', 'style': 'tableHeader'}
                                ]
                            ]
                        },
                        'layout': 'lightHorizontalLines',
                        'margin': [0, 0, 0, 20]
                    },
                    
                    # Totales
                    {
                        'text': 'TOTALES',
                        'fontSize': 12,
                        'bold': True,
                        'margin': [0, 20, 0, 10]
                    },
                    {
                        'text': [
                            {'text': 'Total: ', 'bold': True},
                            f"${resumen_pedido.total:,.2f}"
                        ],
                        'fontSize': 14,
                        'margin': [0, 0, 0, 20]
                    },
                    
                    # Notas
                    {
                        'text': 'NOTAS',
                        'fontSize': 12,
                        'bold': True,
                        'margin': [0, 20, 0, 10]
                    },
                    {
                        'text': 'Este es un resumen de su pedido. Gracias por su compra.',
                        'fontSize': 10,
                        'italic': True,
                        'color': '#666666'
                    }
                ],
                'styles': {
                    'tableHeader': {
                        'bold': True,
                        'fontSize': 10,
                        'color': 'black',
                        'alignment': 'center'
                    }
                }
            }
            
            # Agregar productos a la tabla
            productos_body = doc_definition['content'][8]['table']['body']
            for detalle in pedido.detalles.all():
                productos_body.append([
                    detalle.producto.nombre,
                    str(detalle.cantidad),
                    f"${detalle.precio_unitario:,.2f}",
                    f"${detalle.subtotal:,.2f}"
                ])
            
            return doc_definition
            
        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            return None

    @staticmethod
    def generar_pdf_frontend(resumen_pedido):
        """
        Genera la definición del documento para usar en el frontend con pdfmake
        """
        return PDFService.generar_resumen_pedido_pdf(resumen_pedido)

    @staticmethod
    def guardar_pdf_archivo(resumen_pedido, pdf_content):
        """
        Guarda el contenido PDF como archivo en el modelo
        """
        try:
            # Generar nombre de archivo
            nombre_archivo = f"resumen_pedido_{resumen_pedido.numero_resumen}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Guardar archivo
            resumen_pedido.archivo_pdf.save(
                nombre_archivo,
                ContentFile(pdf_content),
                save=True
            )
            
            return True
        except Exception as e:
            print(f"Error guardando PDF: {str(e)}")
            return False 