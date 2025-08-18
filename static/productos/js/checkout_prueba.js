// static/productos/js/checkout_prueba.js

// Espera a que el DOM esté listo
window.addEventListener('DOMContentLoaded', function() {
    // Solo ejecuta si hay un elemento con id 'detallePedidoPrueba'
    const detallePedido = document.getElementById('detallePedidoPrueba');
    if (!detallePedido) return;

    // NUEVO: Verificar si el PDF ya existe
    const pdfExiste = detallePedido.getAttribute('data-pdf-existe');
    if (pdfExiste) {
        console.log('El PDF ya existe, no se generará ni subirá de nuevo.');
        return;
    }

    // Cargar pdfmake dinámicamente si no está presente
    function cargarPdfMake() {
        return new Promise((resolve, reject) => {
            // Si ya está cargado, resolver inmediatamente
            if (window.pdfMake && typeof window.pdfMake.createPdf === 'function') {
                console.log('pdfMake ya está cargado');
                return resolve();
            }

            console.log('Cargando pdfMake...');
            
            // Cargar pdfmake.min.js primero
            const script1 = document.createElement('script');
            script1.src = '/static/productos/js/pdfmake.min.js';
            script1.onload = () => {
                console.log('pdfmake.min.js cargado');
                // Cargar vfs_fonts.js después
                const script2 = document.createElement('script');
                script2.src = '/static/productos/js/vfs_fonts.js';
                script2.onload = () => {
                    console.log('vfs_fonts.js cargado');
                    
                    // Asegurar contexto global
                    if (typeof window.pdfMake === 'undefined' && typeof pdfMake !== 'undefined') {
                        window.pdfMake = pdfMake;
                        console.log('pdfMake asignado a window');
                    }
                    
                    // Verificar que pdfMake esté disponible
                    if (window.pdfMake && typeof window.pdfMake.createPdf === 'function') {
                        console.log('pdfMake inicializado correctamente');
                        resolve();
                    } else {
                        console.error('pdfMake no disponible después de cargar scripts');
                        console.log('window.pdfMake:', window.pdfMake);
                        console.log('typeof window.pdfMake:', typeof window.pdfMake);
                        reject(new Error('pdfMake no se inicializó correctamente'));
                    }
                };
                script2.onerror = () => reject(new Error('Error cargando vfs_fonts.js'));
                document.body.appendChild(script2);
            };
            script1.onerror = () => reject(new Error('Error cargando pdfmake.min.js'));
            document.body.appendChild(script1);
        });
    }

    // Obtiene los datos del pedido desde atributos data
    function obtenerDatosPedido() {
        try {
            const datos = JSON.parse(detallePedido.dataset.pedido);
            console.log('Datos del pedido obtenidos:', datos);
            return datos;
        } catch (e) {
            console.error('Error al obtener los datos del pedido:', e);
            alert('Error al obtener los datos del pedido para el PDF.');
            return null;
        }
    }

    // Genera la definición del PDF (estructura simple y profesional)
    function generarDocDefinition(datos) {
        return {
            pageSize: 'A4',
            pageMargins: [40, 60, 40, 60],
            content: [
                { text: 'RESUMEN DE PEDIDO', style: 'header', alignment: 'center', margin: [0,0,0,20] },
                { text: `Pedido #${datos.numero_pedido}`, style: 'subheader' },
                { text: `Fecha: ${datos.fecha_pedido}`, margin: [0,0,0,10] },
                { text: 'Datos del Cliente', style: 'section' },
                { ul: [
                    `Nombre: ${datos.cliente.nombre}`,
                    `Email: ${datos.cliente.email}`,
                    `Teléfono: ${datos.cliente.telefono || ''}`
                ]},
                { text: 'Dirección de Envío', style: 'section' },
                { ul: [
                    `Dirección: ${datos.envio.direccion_completa}`,
                    `Teléfono: ${datos.envio.telefono || ''}`
                ]},
                { text: 'Productos', style: 'section' },
                {
                    table: {
                        headerRows: 1,
                        widths: ['*', 'auto', 'auto', 'auto'],
                        body: [
                            ['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal'],
                            ...datos.productos.map(p => [p.nombre, p.cantidad, `$${p.precio_unitario.toFixed(2)}`, `$${p.subtotal.toFixed(2)}`])
                        ]
                    },
                    layout: 'lightHorizontalLines',
                    margin: [0,0,0,10]
                },
                { text: `Total: $${datos.total.toFixed(2)}`, style: 'total', alignment: 'right', margin: [0,10,0,0] },
                { text: 'Gracias por su compra.', style: 'footer', alignment: 'center', margin: [0,30,0,0] }
            ],
            styles: {
                header: { fontSize: 18, bold: true },
                subheader: { fontSize: 14, bold: true },
                section: { fontSize: 12, bold: true, margin: [0,10,0,5] },
                total: { fontSize: 14, bold: true },
                footer: { fontSize: 10, italics: true, color: '#666' }
            }
        };
    }

    // Sube el PDF al backend
    function subirPDF(resumenId, blob) {
        console.log('Subiendo PDF al backend...');
        const formData = new FormData();
        formData.append('pdf', blob, `resumen_pedido_${resumenId}.pdf`);
        fetch(`/productos/resumen/${resumenId}/subir_pdf/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.success) {
                console.log('PDF subido correctamente.');
                // Recargar la página para que aparezcan los botones de PDF
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                console.error('Error al subir PDF:', data.error);
                alert(data.error || 'Error al subir el PDF.');
            }
        })
        .catch((error) => {
            console.error('Error de red al subir el PDF:', error);
            alert('Error de red al subir el PDF.');
        });
    }

    // Utilidad para CSRF
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

    // Función para intentar generar PDF con múltiples verificaciones
    function intentarGenerarPDF(datos) {
        console.log('Verificando pdfMake antes de generar...');
        console.log('window.pdfMake:', window.pdfMake);
        console.log('typeof window.pdfMake:', typeof window.pdfMake);
        
        if (!window.pdfMake) {
            console.error('pdfMake no está disponible en window');
            return false;
        }
        
        if (typeof window.pdfMake.createPdf !== 'function') {
            console.error('pdfMake.createPdf no es una función');
            return false;
        }
        
        try {
            console.log('Creando PDF con pdfMake...');
            const docDefinition = generarDocDefinition(datos);
            window.pdfMake.createPdf(docDefinition).getBlob(function(blob) {
                console.log('PDF generado, subiendo al backend...');
                subirPDF(datos.resumen_id, blob);
            });
            return true;
        } catch (error) {
            console.error('Error al crear PDF:', error);
            return false;
        }
    }

    // Flujo principal: generar y subir PDF automáticamente
    console.log('Iniciando generación de PDF...');
    cargarPdfMake()
        .then(() => {
            console.log('pdfMake cargado, obteniendo datos...');
            const datos = obtenerDatosPedido();
            if (!datos) {
                console.error('No se pudieron obtener los datos del pedido');
                return;
            }
            console.log('Generando definición del PDF...');
            
            // Intentar generar PDF con verificaciones adicionales
            if (!intentarGenerarPDF(datos)) {
                console.error('No se pudo generar el PDF');
                alert('Error: No se pudo generar el PDF. Verifica la consola para más detalles.');
            }
        })
        .catch((error) => {
            console.error('Error en el flujo de generación de PDF:', error);
            alert('Error al generar el PDF: ' + error.message);
        });
});