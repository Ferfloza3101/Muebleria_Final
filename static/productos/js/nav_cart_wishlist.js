document.addEventListener('DOMContentLoaded', function() {
  // Abre/cierra un menú de navegación (wishlist, carrito, perfil)
  function setupDropdownMenu(dropdownId, menuClass) {
    const dropdown = document.getElementById(dropdownId);
    const menu = dropdown ? dropdown.querySelector(menuClass) : null;
    let hover = false;
    if (dropdown && menu) {
      function open() { dropdown.classList.add('active'); }
      function close() { dropdown.classList.remove('active'); }
      dropdown.addEventListener('mouseenter', open);
      dropdown.addEventListener('mouseleave', () => setTimeout(() => { if (!hover) close(); }, 80));
      menu.addEventListener('mouseenter', () => { hover = true; open(); });
      menu.addEventListener('mouseleave', () => { hover = false; close(); });
    }
  }
  setupDropdownMenu('wishlistDropdown', '.dropdown-wishlist');
  setupDropdownMenu('cartDropdown', '.dropdown-cart');
  setupDropdownMenu('profileDropdown', '.dropdown-profile');

  // Búsqueda mejorada (inline a la derecha del icono)
  const searchToggle = document.querySelector('.search-toggle');
  const searchForm = document.querySelector('.nav-right .search-form');
  const navRight = document.querySelector('.nav-right');
  const searchInput = searchForm ? searchForm.querySelector('input[type="text"]') : null;
  
  if (searchToggle && searchForm && navRight) {
    let isSearchActive = false;
    
    function toggleSearch() {
      isSearchActive = !isSearchActive;
      
      if (isSearchActive) {
        // Mostrar formulario inline
        searchForm.classList.add('active');
        searchToggle.classList.add('active');
        // Ocultar SOLO los iconos a la derecha (marcados con .hide-on-search)
        navRight.classList.add('search-open');
        
        // Enfocar el input
        if (searchInput) {
          setTimeout(() => { searchInput.focus(); }, 50);
        }
      } else {
        // Ocultar formulario
        searchForm.classList.remove('active');
        searchToggle.classList.remove('active');
        navRight.classList.remove('search-open');
        if (searchInput) searchInput.value = '';
      }
    }
    
    // Click en el icono de búsqueda
    searchToggle.addEventListener('click', function(e) {
      e.preventDefault();
      toggleSearch();
    });
    
    // Cerrar búsqueda al hacer click fuera
    document.addEventListener('click', function(e) {
      if (isSearchActive && !navRight.contains(e.target)) {
        toggleSearch();
      }
    });
    
    // Cerrar búsqueda con Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && isSearchActive) toggleSearch();
    });
    
    // Enviar formulario
    searchForm.addEventListener('submit', function(e) {
      if (!searchInput || !searchInput.value.trim()) {
        e.preventDefault();
        return;
      }
      // Cerrar tras enviar
      setTimeout(() => { if (isSearchActive) toggleSearch(); }, 100);
    });
  }

  // Aumenta o disminuye cantidad en el carrito
  document.querySelectorAll('.cart-qty-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const item = btn.closest('.cart-item-row');
      const cantidadSpan = item.querySelector('.cart-qty');
      const productoId = btn.dataset.productId;
      const action = btn.classList.contains('cart-qty-plus') ? 'increase' : 'decrease';
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
        .then(response => response.json())
        .then(data => {
          if (data.ok) {
            let cantidad = parseInt(cantidadSpan.textContent);
            cantidad++;
            cantidadSpan.textContent = cantidad;
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
        .then(response => response.json())
        .then(data => {
          if (data.ok) {
            let cantidad = parseInt(cantidadSpan.textContent);
            if (cantidad > 1) {
              cantidad--;
              cantidadSpan.textContent = cantidad;
            } else {
              item.remove();
            }
          } else {
            mostrarError(data.error || 'No se pudo disminuir la cantidad.');
          }
        })
        .catch(() => {
          mostrarError('Error al disminuir la cantidad.');
        });
      }
    });
  });

  // Elimina producto del carrito
  document.querySelectorAll('.cart-remove-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const item = btn.closest('.cart-item-row');
      const productoId = btn.dataset.productId;
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
        } else {
          mostrarError(data.error || 'No se pudo eliminar el producto.');
        }
      })
      .catch(() => {
        mostrarError('Error al eliminar el producto.');
      });
    });
  });

  // Vacía el carrito
  const vaciarBtn = document.querySelector('.cart-clear-btn');
  if (vaciarBtn) {
    vaciarBtn.addEventListener('click', function() {
      fetch('/productos/carrito/clear/', {
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
          document.querySelectorAll('.cart-item-row').forEach(item => item.remove());
        } else {
          mostrarError('No se pudo vaciar el carrito.');
        }
      })
      .catch(() => {
        mostrarError('Error al vaciar el carrito.');
      });
    });
  }

  // Muestra un error simple
  function mostrarError(msg) {
    console.error(msg);
    // Aquí puedes implementar una notificación visual
  }

  function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
  }
}); 