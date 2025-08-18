// ver carrito
document.addEventListener('DOMContentLoaded', () => {
    const carritoContainer = document.querySelector('.carrito-container');
    if (!carritoContainer) return;

    // Función utilitaria para mostrar errores
    function mostrarError(msg) {
        alert(msg || 'Ocurrió un error.');
    }

    // Delegación de eventos para botones de cantidad y eliminar
    carritoContainer.addEventListener('click', (e) => {
        // Aumentar/disminuir cantidad
        const btnCantidad = e.target.closest('.carrito-btn-cantidad');
        if (btnCantidad) {
            const item = btnCantidad.closest('.carrito-item');
            const cantidadSpan = item.querySelector('.cantidad');
            const productoId = item.dataset.id;
            const action = btnCantidad.dataset.action;
            if (action === 'increase') {
                fetch(`/productos/carrito/add/${productoId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    credentials: 'same-origin',
                    body: 'cantidad=1',
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data.ok) {
                        let cantidad = parseInt(cantidadSpan.textContent);
                        cantidad++;
                        cantidadSpan.textContent = cantidad;
                        const precio = parseFloat(item.querySelector('.carrito-item-precio').textContent.replace('$',''));
                        item.querySelector('.carrito-item-subtotal').textContent = 'Subtotal: $' + (cantidad * precio).toFixed(2);
                        actualizarTotal();
                    } else {
                        mostrarError(data.error || 'No se pudo aumentar la cantidad.');
                    }
                })
                .catch(() => {
                    mostrarError('Error al aumentar la cantidad.');
                });
            } else if (action === 'decrease') {
                fetch(`/productos/carrito/decrease/${productoId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin',
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data.ok) {
                        let cantidad = parseInt(cantidadSpan.textContent);
                        if (cantidad > 1) {
                            cantidad--;
                            cantidadSpan.textContent = cantidad;
                            const precio = parseFloat(item.querySelector('.carrito-item-precio').textContent.replace('$',''));
                            item.querySelector('.carrito-item-subtotal').textContent = 'Subtotal: $' + (cantidad * precio).toFixed(2);
                        } else {
                            item.remove();
                            mostrarVacioSiEsNecesario();
                        }
                        actualizarTotal();
                    } else {
                        mostrarError(data.error || 'No se pudo disminuir la cantidad.');
                    }
                })
                .catch(() => {
                    mostrarError('Error al disminuir la cantidad.');
                });
            }
            return;
        }
        // Eliminar producto
        const btnEliminar = e.target.closest('.carrito-btn-eliminar');
        if (btnEliminar) {
            const item = btnEliminar.closest('.carrito-item');
            const productoId = item.dataset.id;
            fetch(`/productos/carrito/remove/${productoId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            })
            .then(response => response.json())
            .then(data => {
                if (data.ok) {
                    item.remove();
                    actualizarTotal();
                    mostrarVacioSiEsNecesario();
                } else {
                    mostrarError(data.error || 'No se pudo eliminar el producto.');
                }
            })
            .catch(() => {
                mostrarError('Error al eliminar el producto.');
            });
            return;
        }
    });
    // Vaciar carrito
    const vaciarBtn = document.getElementById('vaciarCarrito');
    if (vaciarBtn) {
        vaciarBtn.addEventListener('click', () => {
            fetch('/productos/carrito/clear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.ok) {
                    document.querySelectorAll('.carrito-item').forEach(item => item.remove());
                    actualizarTotal();
                    mostrarVacioSiEsNecesario();
                } else {
                    mostrarError('No se pudo vaciar el carrito.');
                }
            })
            .catch(() => {
                mostrarError('Error al vaciar el carrito.');
            });
        });
    }
    // Habilitar el botón 'Pagar' si hay productos en el carrito
    const btnPagar = document.querySelector('.carrito-btn-pagar');
    function actualizarEstadoPagar() {
        if (!btnPagar) return;
        const hayProductos = document.querySelectorAll('.carrito-item').length > 0;
        btnPagar.disabled = !hayProductos;
    }
    actualizarEstadoPagar();
    // Actualizar estado al modificar el carrito
    function actualizarTotal() {
        let total = 0;
        document.querySelectorAll('.carrito-item').forEach(item => {
            const cantidad = parseInt(item.querySelector('.cantidad').textContent);
            const precio = parseFloat(item.querySelector('.carrito-item-precio').textContent.replace('$',''));
            total += cantidad * precio;
        });
        const totalMonto = document.querySelector('.carrito-total-monto');
        if (totalMonto) totalMonto.textContent = '$' + total.toFixed(2);
        actualizarEstadoPagar();
    }
    // Evento para el botón 'Proceder con el pago'
    const btnProcederPago = document.getElementById('btnProcederPago');
    if (btnProcederPago) {
        btnProcederPago.addEventListener('click', () => {
            window.location.href = '/productos/carrito/seleccionar-direccion/';
        });
    }
    // Muestra mensaje si el carrito está vacío
    function mostrarVacioSiEsNecesario() {
        if (document.querySelectorAll('.carrito-item').length === 0) {
            const lista = document.querySelector('.carrito-lista');
            if (lista) lista.remove();
            const total = document.querySelector('.carrito-total');
            if (total) total.remove();
            const acciones = document.querySelector('.carrito-acciones');
            if (acciones) acciones.remove();
            const vacio = document.createElement('div');
            vacio.className = 'carrito-vacio';
            vacio.textContent = 'Tu carrito está vacío.';
            const links = document.querySelector('.carrito-links');
            if (links) document.querySelector('.carrito-container').insertBefore(vacio, links);
        }
    }
    // Función para obtener el token CSRF de la cookie
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }
}); 