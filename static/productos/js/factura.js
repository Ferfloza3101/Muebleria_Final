/**
 * JavaScript para generar PDFs de resumen de pedido usando pdfmake
 */

// Variable global para pdfmake
let pdfMake = null;

/**
 * Carga pdfmake dinámicamente
 */
function cargarPdfMake() {
    return new Promise((resolve, reject) => {
        // Si ya está cargado, resolver inmediatamente
        if (window.pdfMake) {
            pdfMake = window.pdfMake;
            resolve(pdfMake);
            return;
        }
        
        // Cargar pdfmake.min.js
        const script1 = document.createElement('script');
        script1.src = '/static/PDFmake/pdfmake.min.js';
        script1.onload = () => {
            // Cargar vfs_fonts.js
            const script2 = document.createElement('script');
            script2.src = '/static/PDFmake/vfs_fonts.js';
            script2.onload = () => {
                pdfMake = window.pdfMake;
                resolve(pdfMake);
            };
            script2.onerror = (error) => {
                console.error('Error cargando vfs_fonts.js:', error);
                reject(error);
            };
            document.head.appendChild(script2);
        };
        script1.onerror = (error) => {
            console.error('Error cargando pdfmake.min.js:', error);
            reject(error);
        };
        document.head.appendChild(script1);
    });
}

/**
 * Genera un PDF de resumen de pedido en el frontend
 * @param {Object} datosPedido - Datos del pedido
 * @param {string} nombreArchivo - Nombre del archivo PDF
 */
async function generarPDFResumenPedido(datosPedido, nombreArchivo = 'resumen_pedido.pdf') {
    try {
        // Cargar pdfmake si no está disponible
        if (!pdfMake) {
            await cargarPdfMake();
        }
        
        // Definición del documento PDF
        const docDefinition = {
            pageSize: 'A4',
            pageMargins: [40, 60, 40, 60],
            header: {
                text: 'RESUMEN DE PEDIDO',
                alignment: 'center',
                margin: [0, 20, 0, 0],
                fontSize: 18,
                bold: true
            },
            footer: {
                text: `Generado el ${new Date().toLocaleDateString('es-ES')} ${new Date().toLocaleTimeString('es-ES')}`,
                alignment: 'center',
                margin: [0, 0, 0, 20],
                fontSize: 8,
                color: '#666666'
            },
            content: [
                // Información del pedido
                {
                    text: `Pedido #${datosPedido.numero_pedido}`,
                    fontSize: 16,
                    bold: true,
                    margin: [0, 0, 0, 10]
                },
                {
                    text: `Fecha: ${datosPedido.fecha_pedido}`,
                    fontSize: 10,
                    margin: [0, 0, 0, 20]
                },
                
                // Información del cliente
                {
                    text: 'DATOS DEL CLIENTE',
                    fontSize: 12,
                    bold: true,
                    margin: [0, 20, 0, 10]
                },
                {
                    text: [
                        {text: 'Nombre: ', bold: true},
                        datosPedido.cliente.nombre || 'No especificado'
                    ],
                    fontSize: 10,
                    margin: [0, 0, 0, 5]
                },
                {
                    text: [
                        {text: 'Email: ', bold: true},
                        datosPedido.cliente.email || 'No especificado'
                    ],
                    fontSize: 10,
                    margin: [0, 0, 0, 5]
                },
                {
                    text: [
                        {text: 'Teléfono: ', bold: true},
                        datosPedido.cliente.telefono || 'No especificado'
                    ],
                    fontSize: 10,
                    margin: [0, 0, 0, 20]
                },
                
                // Información de envío
                {
                    text: 'DIRECCIÓN DE ENVÍO',
                    fontSize: 12,
                    bold: true,
                    margin: [0, 20, 0, 10]
                },
                {
                    text: [
                        {text: 'Dirección: ', bold: true},
                        datosPedido.envio.direccion_completa || 'No especificada'
                    ],
                    fontSize: 10,
                    margin: [0, 0, 0, 5]
                },
                {
                    text: [
                        {text: 'Teléfono: ', bold: true},
                        datosPedido.envio.telefono || 'No especificado'
                    ],
                    fontSize: 10,
                    margin: [0, 0, 0, 20]
                },
                
                // Productos
                {
                    text: 'PRODUCTOS',
                    fontSize: 12,
                    bold: true,
                    margin: [0, 20, 0, 10]
                },
                // Tabla de productos
                {
                    table: {
                        headerRows: 1,
                        widths: ['*', 'auto', 'auto', 'auto'],
                        body: [
                            [
                                {text: 'Producto', style: 'tableHeader'},
                                {text: 'Cantidad', style: 'tableHeader'},
                                {text: 'Precio Unit.', style: 'tableHeader'},
                                {text: 'Subtotal', style: 'tableHeader'}
                            ]
                        ]
                    },
                    layout: 'lightHorizontalLines',
                    margin: [0, 0, 0, 20]
                },
                
                // Totales
                {
                    text: 'TOTALES',
                    fontSize: 12,
                    bold: true,
                    margin: [0, 20, 0, 10]
                },
                {
                    text: [
                        {text: 'Total: ', bold: true},
                        `$${datosPedido.total.toFixed(2)}`
                    ],
                    fontSize: 14,
                    margin: [0, 0, 0, 20]
                },
                
                // Notas
                {
                    text: 'NOTAS',
                    fontSize: 12,
                    bold: true,
                    margin: [0, 20, 0, 10]
                },
                {
                    text: 'Este es un resumen de su pedido. Gracias por su compra.',
                    fontSize: 10,
                    italic: true,
                    color: '#666666'
                }
            ],
            styles: {
                tableHeader: {
                    bold: true,
                    fontSize: 10,
                    color: 'black',
                    alignment: 'center'
                }
            }
        };
        
        // Agregar productos a la tabla
        const productosBody = docDefinition.content[8].table.body;
        datosPedido.productos.forEach(producto => {
            productosBody.push([
                producto.nombre,
                producto.cantidad.toString(),
                `$${producto.precio_unitario.toFixed(2)}`,
                `$${producto.subtotal.toFixed(2)}`
            ]);
        });
        
        // Generar y descargar PDF
        pdfMake.createPdf(docDefinition).download(nombreArchivo);
        
        console.log('PDF generado exitosamente:', nombreArchivo);
        return true;
        
    } catch (error) {
        console.error('Error generando PDF:', error);
        alert('Error al generar el PDF. Por favor, intente nuevamente.');
        return false;
    }
}

/**
 * Previsualiza un PDF en el navegador
 * @param {Object} datosPedido - Datos del pedido
 */
async function previsualizarPDFResumenPedido(datosPedido) {
    try {
        // Cargar pdfmake si no está disponible
        if (!pdfMake) {
            await cargarPdfMake();
        }
        
        // Usar la misma definición que generarPDFResumenPedido
        const docDefinition = {
            // ... (misma definición que arriba)
        };
        
        // Abrir en nueva ventana
        pdfMake.createPdf(docDefinition).open();
        
        console.log('PDF previsualizado exitosamente');
        return true;
        
    } catch (error) {
        console.error('Error previsualizando PDF:', error);
        alert('Error al previsualizar el PDF. Por favor, intente nuevamente.');
        return false;
    }
}

/**
 * Envía datos del pedido al backend para generar PDF y enviar por email
 * @param {number} pedidoId - ID del pedido
 * @param {string} emailDestino - Email de destino (opcional)
 */
async function enviarResumenPorEmail(pedidoId, emailDestino = null) {
    try {
        const response = await fetch('/productos/enviar-resumen-email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                pedido_id: pedidoId,
                email_destino: emailDestino
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Resumen enviado por email exitosamente.');
            return true;
        } else {
            alert(data.error || 'Error al enviar el resumen por email.');
            return false;
        }
        
    } catch (error) {
        console.error('Error enviando resumen por email:', error);
        alert('Error de conexión al enviar el resumen por email.');
        return false;
    }
}

/**
 * Obtiene el token CSRF de las cookies
 * @param {string} name - Nombre de la cookie
 * @returns {string} Valor de la cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Exportar funciones para uso global
window.PDFResumenPedido = {
    cargarPdfMake,
    generarPDFResumenPedido,
    previsualizarPDFResumenPedido,
    enviarResumenPorEmail
}; 