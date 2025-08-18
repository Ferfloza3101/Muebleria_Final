    // Funciones del modal
function openProductModal(id) {
    console.log('Opening modal for product:', id);
    const modal = document.getElementById(`modal-${id}`);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        console.log('Modal opened successfully');
    } else {
        console.error('Modal not found for product:', id);
    }
}

function closeProductModal(id) {
    console.log('Closing modal for product:', id);
    const modal = document.getElementById(`modal-${id}`);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
        console.log('Modal closed successfully');
    } else {
        console.error('Modal not found for product:', id);
    }
}

function navigateModalImage(productId, direction) {
    console.log('Navigating modal image:', productId, direction);
    const modal = document.getElementById(`modal-${productId}`);
    if (!modal) {
        console.error('Modal not found for navigation');
        return;
    }
    
    const img = modal.querySelector('.modal-product-image');
    if (!img) {
        console.error('Image element not found in modal');
        return;
    }
    
    const productCard = modal.closest('.product-card');
    if (!productCard) {
        console.error('Product card not found for modal');
        return;
    }
    
    const images = JSON.parse(productCard.dataset.images || '[]');
    const currentIndex = parseInt(img.dataset.currentImage || 0);
    const totalImages = images.length;
    
    if (totalImages === 0) {
        console.error('No images found for product');
        return;
    }
    
    let newIndex;
    if (direction === 'next') {
        newIndex = (currentIndex + 1) % totalImages;
    } else {
        newIndex = (currentIndex - 1 + totalImages) % totalImages;
    }
    
    img.src = images[newIndex].url;
    img.dataset.currentImage = newIndex;
    console.log('Image navigation successful');
}

// --- Wishlist/Favoritos ---
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

function toggleWishlistButton(btn, added) {
    if (added) {
        btn.classList.add('active');
        const icon = btn.querySelector('i');
        if (icon) { icon.classList.remove('far'); icon.classList.add('fas'); }
        // Animación pop al agregar a favoritos
        btn.classList.add('pop');
        setTimeout(() => btn.classList.remove('pop'), 350);
    } else {
        btn.classList.remove('active');
        const icon = btn.querySelector('i');
        if (icon) { icon.classList.remove('fas'); icon.classList.add('far'); }
        // Animación pop al quitar de favoritos
        btn.classList.add('pop');
        setTimeout(() => btn.classList.remove('pop'), 350);
    }
}

async function updateWishlistMenu() {
    const res = await fetch('/productos/wishlist/menu/', {headers: {'X-Requested-With': 'XMLHttpRequest'}});
    const html = await res.text();
    const menu = document.querySelector('.dropdown-wishlist');
    if (menu) menu.innerHTML = html;
    // Actualizar badge de cantidad
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const badge = doc.getElementById('wishlist-badge');
    const navbarBadge = document.getElementById('wishlist-badge');
    if (badge && navbarBadge) {
        navbarBadge.textContent = badge.textContent;
        navbarBadge.style.display = badge.textContent.trim() ? 'flex' : 'none';
    }
    // Reasignar eventos a los nuevos botones del menú
    document.querySelectorAll('.wishlist-remove-btn').forEach(btn => {
        btn.addEventListener('click', async e => {
            e.stopPropagation();
            const id = btn.dataset.productId;
            const res = await fetch(`/productos/wishlist/toggle/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            await updateWishlistMenu();
            // Actualizar corazones en cards y modales
            document.querySelectorAll(`.wishlist-btn[data-product-id="${id}"]`).forEach(b => toggleWishlistButton(b, false));
            document.querySelectorAll(`.modal-wishlist-btn[data-product-id="${id}"]`).forEach(b => toggleWishlistButton(b, false));
        });
    });
    document.querySelectorAll('.wishlist-cart-btn').forEach(btn => {
        btn.addEventListener('click', async e => {
            e.stopPropagation();
            const productId = btn.getAttribute('data-product-id');
            const res = await fetch(`/productos/carrito/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: new URLSearchParams({cantidad: 1})
            });
            const data = await res.json();
            if (data.ok) {
                await updateCartMenu();
                document.querySelectorAll(`.cart-btn[data-product-id="${productId}"]`).forEach(b => toggleCartButton(b, true));
                document.querySelectorAll(`.modal-cart-btn[data-product-id="${productId}"]`).forEach(b => toggleCartButton(b, true));
                mostrarMensajeCarrito('El producto se ha agregado al carrito');
            } else {
                alert(data.error || 'No se pudo agregar al carrito');
            }
        });
    });
}

function setupCartMenuEvents() {
    const menu = document.querySelector('.dropdown-cart');
    if (!menu) return;
    menu.removeEventListener('click', cartMenuHandler); // Evita duplicados
    menu.addEventListener('click', cartMenuHandler);
    // Vaciar carrito
    const clearBtn = menu.querySelector('.cart-clear-btn');
    if (clearBtn) {
        clearBtn.onclick = async function(e) {
            e.preventDefault();
            if (!confirm('¿Vaciar todo el carrito?')) return;
            const res = await fetch('/productos/carrito/clear/', {
                method: 'POST',
                headers: {'X-CSRFToken': getCookie('csrftoken')}
            });
            const data = await res.json();
            if (data.ok) {
                await updateCartMenu();
                updateCartCount(0);
            }
        };
    }
}

async function cartMenuHandler(e) {
    const btn = e.target.closest('.cart-qty-btn, .cart-remove-btn');
    if (!btn) return;
    const productId = btn.dataset.productId;
    if (btn.classList.contains('cart-qty-plus')) {
        await changeCartQty(productId, 1);
    } else if (btn.classList.contains('cart-qty-minus')) {
        await changeCartQty(productId, -1);
    } else if (btn.classList.contains('cart-remove-btn')) {
        await removeFromCart(productId);
    }
    await updateCartMenu();
    // Actualiza el contador
    const menu = document.querySelector('.dropdown-cart');
    if (menu) {
        const count = menu.querySelectorAll('.cart-item-row').length;
        updateCartCount(count);
    }
}

async function changeCartQty(productId, delta) {
    const row = document.querySelector(`.cart-item-row [data-product-id='${productId}']`)?.closest('.cart-item-row');
    let cantidad = 1;
    if (row) {
        const qtySpan = row.querySelector('.cart-qty');
        cantidad = parseInt(qtySpan.textContent) + delta;
        if (cantidad < 1) cantidad = 1;
    }
    const res = await fetch(`/productos/carrito/add/${productId}/`, {
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        body: new URLSearchParams({cantidad})
    });
    const data = await res.json();
    if (!data.ok) alert(data.error || 'No se pudo actualizar cantidad');
}

async function removeFromCart(productId) {
    const res = await fetch(`/productos/carrito/remove/${productId}/`, {
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')}
    });
    const data = await res.json();
    if (!data.ok) alert(data.error || 'No se pudo eliminar del carrito');
    document.querySelectorAll(`.cart-btn[data-product-id="${productId}"]`).forEach(b => toggleCartButton(b, false));
    document.querySelectorAll(`.modal-cart-btn[data-product-id="${productId}"]`).forEach(b => toggleCartButton(b, false));
}

async function updateCartIconsFromMenu() {
    // Obtiene los IDs de productos en el carrito desde el menú
    const menu = document.querySelector('.dropdown-cart');
    if (!menu) return;
    const ids = Array.from(menu.querySelectorAll('.cart-item-row .cart-remove-btn')).map(btn => btn.dataset.productId);
    document.querySelectorAll('.cart-btn').forEach(btn => {
        if (ids.includes(btn.dataset.productId)) {
            toggleCartButton(btn, true);
        } else {
            toggleCartButton(btn, false);
        }
    });
    document.querySelectorAll('.modal-cart-btn').forEach(btn => {
        if (ids.includes(btn.dataset.productId)) {
            toggleCartButton(btn, true);
        } else {
            toggleCartButton(btn, false);
        }
    });
}

async function updateCartMenu() {
    const res = await fetch('/productos/carrito/menu/', {headers: {'X-Requested-With': 'XMLHttpRequest'}});
    const html = await res.text();
    const menu = document.querySelector('.dropdown-cart');
    if (menu) menu.innerHTML = html;
    setupCartMenuEvents();
    await updateCartIconsFromMenu();
}

function updateCartCount(count) {
    document.querySelectorAll('.cart-count').forEach(el => {
        el.textContent = count;
        el.style.display = (parseInt(count) > 0) ? 'flex' : 'none';
    });
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = (parseInt(count) > 0) ? 'flex' : 'none';
    }
}

function toggleCartButton(btn, added) {
    if (added) {
        btn.classList.add('active');
        const icon = btn.querySelector('i');
        if (icon) { icon.classList.add('cart-filled'); }
        btn.classList.add('pop');
        setTimeout(() => btn.classList.remove('pop'), 350);
    } else {
        btn.classList.remove('active');
        const icon = btn.querySelector('i');
        if (icon) { icon.classList.remove('cart-filled'); }
        btn.classList.add('pop');
        setTimeout(() => btn.classList.remove('pop'), 350);
    }
}

// Inicializar eventos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing modal events');
    
    // Configurar eventos de cierre para todos los modales
    const modals = document.querySelectorAll('.product-modal');
    console.log('Found modals:', modals.length);
    
    modals.forEach(modal => {
        // Cerrar al hacer clic en el botón de cerrar
        const closeButton = modal.querySelector('.close-modal');
        if (closeButton) {
            console.log('Adding close button event listener for modal:', modal.id);
            closeButton.addEventListener('click', (e) => {
                e.stopPropagation();
                const productId = modal.id.split('-')[1];
                closeProductModal(productId);
            });
        } else {
            console.error('Close button not found in modal:', modal.id);
        }

        // Cerrar al hacer clic fuera del contenido
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                const productId = modal.id.split('-')[1];
                closeProductModal(productId);
            }
        });
    });

    // Cerrar modal con la tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.product-modal.active');
            if (activeModal) {
                const productId = activeModal.id.split('-')[1];
                closeProductModal(productId);
            }
        }
    });
    
    console.log('Modal events initialization complete');

    // Wishlist/favoritos para tarjetas
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', async e => {
            e.stopPropagation();
            const id = btn.dataset.productId;
            const res = await fetch(`/productos/wishlist/toggle/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            const data = await res.json();
            toggleWishlistButton(btn, data.added);
            // Actualizar todos los corazones del mismo producto
            document.querySelectorAll(`.modal-wishlist-btn[data-product-id="${id}"]`).forEach(b => toggleWishlistButton(b, data.added));
            document.querySelectorAll(`.wishlist-btn[data-product-id="${id}"]`).forEach(b => toggleWishlistButton(b, data.added));
            await updateWishlistMenu();
        });
    });

    // Wishlist/favoritos para modal
    document.querySelectorAll('.modal-wishlist-btn').forEach(btn => {
        btn.addEventListener('click', async e => {
            e.stopPropagation();
            const id = btn.dataset.productId;
            if (!id) return;
            const res = await fetch(`/productos/wishlist/toggle/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            const data = await res.json();
            toggleWishlistButton(btn, data.added);
            // Actualizar todos los corazones del mismo producto
            document.querySelectorAll(`.modal-wishlist-btn[data-product-id="${id}"]`).forEach(b => toggleWishlistButton(b, data.added));
            document.querySelectorAll(`.wishlist-btn[data-product-id="${id}"]`).forEach(b => toggleWishlistButton(b, data.added));
            await updateWishlistMenu();
        });
    });

    // Delegación para botones de carrito en tarjetas y modales
    document.body.addEventListener('click', async function(e) {
        const btn = e.target.closest('.cart-btn, .modal-cart-btn, [data-action="add-cart"]');
        if (!btn) return;
        e.preventDefault();
        e.stopPropagation();
        const id = btn.dataset.productId;
        const cantidad = 1; // Siempre agregar solo 1
        const res = await fetch(`/productos/carrito/add/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({cantidad})
        });
        const data = await res.json();
        if (!data.ok) {
            alert(data.error || 'No se pudo agregar al carrito');
            return;
        }
        document.querySelectorAll('.cart-count').forEach(el => el.textContent = data.count);
        if (typeof updateCartMenu === 'function') {
            await updateCartMenu();
        }
        document.querySelectorAll(`.cart-btn[data-product-id="${id}"]`).forEach(b => toggleCartButton(b, true));
        document.querySelectorAll(`.modal-cart-btn[data-product-id="${id}"]`).forEach(b => toggleCartButton(b, true));
    });

    document.querySelectorAll('.cart-btn').forEach(btn => {
        btn.addEventListener('click', async e => {
            e.stopPropagation();
            const id = btn.dataset.productId;
            const cantidad = 1;
            const res = await fetch(`/productos/carrito/add/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: new URLSearchParams({cantidad})
            });
            const data = await res.json();
            if (!data.ok) {
                alert(data.error || 'No se pudo agregar al carrito');
                return;
            }
            document.querySelectorAll('.cart-count').forEach(el => el.textContent = data.count);
            if (typeof updateCartMenu === 'function') {
                await updateCartMenu();
            }
            document.querySelectorAll(`.cart-btn[data-product-id="${id}"]`).forEach(b => toggleCartButton(b, true));
            document.querySelectorAll(`.modal-cart-btn[data-product-id="${id}"]`).forEach(b => toggleCartButton(b, true));
        });
    });

    document.querySelectorAll('.modal-cart-btn').forEach(btn => {
        btn.addEventListener('click', async e => {
            e.stopPropagation();
            const id = btn.dataset.productId;
            const cantidad = 1;
            const res = await fetch(`/productos/carrito/add/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: new URLSearchParams({cantidad})
            });
            const data = await res.json();
            if (!data.ok) {
                alert(data.error || 'No se pudo agregar al carrito');
                return;
            }
            document.querySelectorAll('.cart-count').forEach(el => el.textContent = data.count);
            if (typeof updateCartMenu === 'function') {
                await updateCartMenu();
            }
            document.querySelectorAll(`.cart-btn[data-product-id="${id}"]`).forEach(b => toggleCartButton(b, true));
            document.querySelectorAll(`.modal-cart-btn[data-product-id="${id}"]`).forEach(b => toggleCartButton(b, true));
        });
    });

    updateWishlistMenu(); // Para asignar eventos a los botones del menú al cargar
    updateCartMenu().then(() => {
        // Actualiza el contador al cargar el menú
        const menu = document.querySelector('.dropdown-cart');
        if (menu) {
            const count = menu.querySelectorAll('.cart-item-row').length;
            updateCartCount(count);
        }
        setupCartMenuEvents();
        updateCartIconsFromMenu();
    });
});

// Agrego la función para mostrar el mensaje
function mostrarMensajeCarrito(msg) {
    let aviso = document.getElementById('mensaje-carrito-aviso');
    if (!aviso) {
        aviso = document.createElement('div');
        aviso.id = 'mensaje-carrito-aviso';
        aviso.className = 'mensaje-carrito-aviso';
        document.body.appendChild(aviso);
    }
    aviso.textContent = msg;
    aviso.style.display = 'block';
    aviso.style.opacity = '1';
    setTimeout(() => {
        aviso.style.opacity = '0';
        setTimeout(() => { aviso.style.display = 'none'; }, 200);
    }, 1800);
} 