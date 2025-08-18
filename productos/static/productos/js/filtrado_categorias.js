document.addEventListener('DOMContentLoaded', () => {
  const categorias = document.querySelectorAll('.categorias-list a');
  const gridContainer = document.getElementById('productos-grid-container');
  if (!gridContainer || !categorias.length) return;

  function filtrarProductos(categoria) {
    const params = new URLSearchParams();
    if (categoria) params.append('categoria', categoria);
    fetch('/productos/filtrar/?' + params.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then((r) => r.json())
      .then((data) => {
        if (!data || !data.html) return;
        gridContainer.innerHTML = data.html;
        if (typeof initProductModals === 'function') initProductModals();
        if (typeof initProductCardCarousel === 'function') initProductCardCarousel();
        if (typeof initModalEvents === 'function') initModalEvents();
        if (typeof initWishlistButtons === 'function') initWishlistButtons();
      })
      .catch(() => {});
  }

  categorias.forEach((cat) => {
    cat.addEventListener('click', (e) => {
      e.preventDefault();
      categorias.forEach((c) => c.classList.remove('active'));
      cat.classList.add('active');
      const categoriaActual = cat.dataset.categoria || '';
      filtrarProductos(categoriaActual);
    });
  });
});

// Funciones para reinicializar scripts tras AJAX
function initProductModals() {
    document.querySelectorAll('.product-card.open-modal-btn').forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.closest('button')) return;
            const productId = this.getAttribute('data-product-id');
            if (productId) openProductModal(productId);
        });
    });
}

function initProductCardCarousel() {
    document.querySelectorAll('.product-card .product-image').forEach(function(img) {
        const images = JSON.parse(img.getAttribute('data-images'));
        let current = 0;
        const wrapper = img.closest('.product-image-wrapper');
        const dotsContainer = wrapper.parentElement.querySelector('.image-dots');
        if (!dotsContainer) return;
        dotsContainer.innerHTML = '';
        images.forEach((_, i) => {
            const dot = document.createElement('span');
            dot.className = 'dot' + (i === 0 ? ' active' : '');
            dot.addEventListener('click', function(e) {
                e.stopPropagation();
                current = i;
                updateImage();
            });
            dotsContainer.appendChild(dot);
        });
        const prev = wrapper.querySelector('.prev-arrow');
        const next = wrapper.querySelector('.next-arrow');
        if (prev && next) {
            prev.addEventListener('click', function(e) {
                e.stopPropagation();
                current = (current - 1 + images.length) % images.length;
                updateImage();
            });
            next.addEventListener('click', function(e) {
                e.stopPropagation();
                current = (current + 1) % images.length;
                updateImage();
            });
        }
        function updateImage() {
            img.src = images[current].url;
            img.setAttribute('data-current-image', current);
            dotsContainer.querySelectorAll('.dot').forEach((dot, i) => {
                dot.classList.toggle('active', i === current);
            });
        }
    });
}

// Nueva función para reinicializar eventos de cierre de modales
function initModalEvents() {
    document.querySelectorAll('.product-modal').forEach(modal => {
        // Cerrar al hacer clic en el botón de cerrar
        const closeButton = modal.querySelector('.close-modal');
        if (closeButton) {
            closeButton.onclick = function(e) {
                e.stopPropagation();
                const productId = modal.id.split('-')[1];
                if (typeof closeProductModal === 'function') closeProductModal(productId);
            };
        }
        // Cerrar al hacer clic fuera del contenido
        modal.onclick = function(e) {
            if (e.target === modal) {
                const productId = modal.id.split('-')[1];
                if (typeof closeProductModal === 'function') closeProductModal(productId);
            }
        };
    });
    // Cerrar modal con la tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.product-modal.active');
            if (activeModal) {
                const productId = activeModal.id.split('-')[1];
                if (typeof closeProductModal === 'function') closeProductModal(productId);
            }
        }
    });
}

// Nueva función para reinicializar eventos de favoritos
function initWishlistButtons() {
    // Para tarjetas
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.onclick = async function(e) {
            e.stopPropagation();
            const id = btn.dataset.productId;
            const res = await fetch(`/productos/wishlist/toggle/${id}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            const data = await res.json();
            if (typeof toggleWishlistButton === 'function') toggleWishlistButton(btn, data.added);
            document.querySelectorAll(`.modal-wishlist-btn[data-product-id="${id}"]`).forEach(b => {
                if (typeof toggleWishlistButton === 'function') toggleWishlistButton(b, data.added);
            });
            document.querySelectorAll(`.wishlist-btn[data-product-id="${id}"]`).forEach(b => {
                if (typeof toggleWishlistButton === 'function') toggleWishlistButton(b, data.added);
            });
            if (typeof updateWishlistMenu === 'function') await updateWishlistMenu();
        }
    });
    // Para modales
    document.querySelectorAll('.modal-wishlist-btn').forEach(btn => {
        btn.onclick = async function(e) {
            e.stopPropagation();
            const id = btn.dataset.productId;
            if (!id) return;
            const res = await fetch(`/productos/wishlist/toggle/${id}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            const data = await res.json();
            if (typeof toggleWishlistButton === 'function') toggleWishlistButton(btn, data.added);
            document.querySelectorAll(`.modal-wishlist-btn[data-product-id="${id}"]`).forEach(b => {
                if (typeof toggleWishlistButton === 'function') toggleWishlistButton(b, data.added);
            });
            document.querySelectorAll(`.wishlist-btn[data-product-id="${id}"]`).forEach(b => {
                if (typeof toggleWishlistButton === 'function') toggleWishlistButton(b, data.added);
            });
            if (typeof updateWishlistMenu === 'function') await updateWishlistMenu();
        }
    });
} 