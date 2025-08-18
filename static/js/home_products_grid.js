/** JavaScript para el grid de productos de la página de inicio*/

document.addEventListener('DOMContentLoaded', function() {
    // Función para agregar eventos de clic a las tarjetas de producto (abrir modal)
    function addModalOpenEvents() {
        document.querySelectorAll('.open-modal-btn').forEach(card => {
            card.addEventListener('click', function(e) {
                const productId = this.dataset.productId;
                if (productId) {
                    // Abrir modal del producto
                    if (typeof openProductModal === 'function') {
                        openProductModal(productId);
                    } else if (typeof openProductModalGlobal === 'function') {
                        openProductModalGlobal(productId);
                    }
                }
            });
        });
    }

    // Inicializar funcionalidades
    function init() {
        // Agregar eventos de clic SOLO a las tarjetas de producto con modal
        addModalOpenEvents();
    }

    // Iniciar cuando el DOM esté listo
    init();

    // Contador de tiempo para el banner promocional
    var countdown = document.querySelector('.promo-banner-countdown');
    if (countdown) {
        var end = countdown.getAttribute('data-end');
        var endDate = new Date(end.replace(/-/g, '/'));
        function updateCountdown() {
            var now = new Date();
            var diff = endDate - now;
            if (diff <= 0) {
                var banner = document.getElementById('promo-banner');
                if (banner) banner.style.display = 'none';
                return;
            }
            var days = Math.floor(diff / (1000 * 60 * 60 * 24));
            var hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
            var mins = Math.floor((diff / (1000 * 60)) % 60);
            var secs = Math.floor((diff / 1000) % 60);
            countdown.innerHTML = `
                <div class="countdown-box"><div class="countdown-value">${days.toString().padStart(2, '0')}</div><div class="countdown-label">DÍAS</div></div>
                <div class="countdown-box"><div class="countdown-value">${hours.toString().padStart(2, '0')}</div><div class="countdown-label">HORAS</div></div>
                <div class="countdown-box"><div class="countdown-value">${mins.toString().padStart(2, '0')}</div><div class="countdown-label">MIN</div></div>
                <div class="countdown-box"><div class="countdown-value">${secs.toString().padStart(2, '0')}</div><div class="countdown-label">SEG</div></div>
            `;
        }
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }
});

// Función global para abrir modales (compatible con el sistema existente)
function openProductModalGlobal(productId) {
    // Usar el modal 
    if (typeof openProductModal === 'function') {
        openProductModal(productId);
    } else {
        window.location.href = `/productos/detalle/${productId}/`;
    }
}
