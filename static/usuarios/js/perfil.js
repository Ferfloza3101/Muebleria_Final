
document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelectorAll('.perfil-dashboard__acceso').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const section = document.querySelector(href);
                if (section) {
                    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    
    const accesos = document.querySelectorAll('.perfil-dashboard__acceso');
    accesos.forEach(link => {
        link.addEventListener('click', function() {
            accesos.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    const sidebar = document.getElementById('perfilSidebar');
    const toggle = document.getElementById('perfilDrawerToggle');
    const overlay = document.getElementById('perfilDrawerOverlay');
    const links = document.querySelectorAll('.perfil-sidebar__link');
    const sectionViews = document.querySelectorAll('.perfil-section-view');

    function openDrawer() {
        sidebar.classList.add('open');
        overlay.style.display = 'block';
    }
    function closeDrawer() {
        sidebar.classList.remove('open');
        overlay.style.display = 'none';
    }
    if (toggle) {
        toggle.addEventListener('click', openDrawer);
    }
    if (overlay) {
        overlay.addEventListener('click', closeDrawer);
    }
    // Cerrar drawer al hacer clic en un link
    links.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 700) closeDrawer();
        });
    });

    // SPA: mostrar solo la sección seleccionada
    function showSection(section) {
        sectionViews.forEach(view => {
            view.classList.remove('active');
        });
        const target = document.getElementById('view-' + section);
        if (target) target.classList.add('active');
        // Resaltar link activo
        links.forEach(link => {
            if (link.dataset.section === section) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    function getSectionFromHash() {
        const hash = window.location.hash.replace('#', '');
        const valid = ['info-personal','pedidos','direcciones','metodos-pago','seguridad','contacto'];
        return valid.includes(hash) ? hash : 'info-personal';
    }
    function handleHashChange() {
        showSection(getSectionFromHash());
    }
    window.addEventListener('hashchange', handleHashChange);
    showSection(getSectionFromHash());


    const formDireccion = document.getElementById('form-direccion');
    const listaDirecciones = document.getElementById('direcciones-lista');
    const exitoDireccion = document.getElementById('direccion-exito');
    const errorDireccion = document.getElementById('direccion-error');
    let direcciones = [];
    let submitEnProgreso = false;

    // Delegación de eventos para botones de direcciones
    if (listaDirecciones) {
        listaDirecciones.addEventListener('click', function(e) {
            const btn = e.target.closest('button');
            if (!btn) return;
            // Eliminar dirección
            if (btn.classList.contains('perfil-btn-action--danger')) {
                const id = btn.dataset.id;
                if (!id) return;
                if (window.confirm('¿Estás seguro de que quieres eliminar esta dirección? Esta acción no se puede deshacer.')) {
                    btn.disabled = true;
                    btn.textContent = 'Eliminando...';
                    fetch(`/usuarios/direcciones/${id}/eliminar/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        btn.disabled = false;
                        btn.textContent = 'Eliminar';
                        if (data.success) {
                            mostrarMensajeGlobal({
                                mensaje: 'Dirección eliminada correctamente.',
                                tipo: 'success',
                                exitoEl: exitoDireccion,
                                errorEl: errorDireccion
                            });
                            cargarDirecciones();
                        } else {
                            mostrarMensajeGlobal({
                                mensaje: 'No se pudo eliminar la dirección.',
                                tipo: 'error',
                                exitoEl: exitoDireccion,
                                errorEl: errorDireccion
                            });
                        }
                    })
                    .catch(error => {
                        btn.disabled = false;
                        btn.textContent = 'Eliminar';
                        mostrarMensajeGlobal({
                            mensaje: 'Error de conexión al eliminar.',
                            tipo: 'error',
                            exitoEl: exitoDireccion,
                            errorEl: errorDireccion
                        });
                    });
                }
            }
            // Marcar como principal
            if (btn.classList.contains('perfil-btn-action--primary')) {
                const id = btn.dataset.id;
                if (!id) return;
                btn.disabled = true;
                btn.textContent = 'Marcando...';
                fetch(`/usuarios/direcciones/${id}/principal/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    btn.disabled = false;
                    btn.textContent = 'Principal';
                    if (data.success) {
                        mostrarMensajeGlobal({
                            mensaje: 'Dirección marcada como principal.',
                            tipo: 'success',
                            exitoEl: exitoDireccion,
                            errorEl: errorDireccion
                        });
                        cargarDirecciones();
                    } else {
                        mostrarMensajeGlobal({
                            mensaje: 'No se pudo marcar como principal.',
                            tipo: 'error',
                            exitoEl: exitoDireccion,
                            errorEl: errorDireccion
                        });
                    }
                })
                .catch(error => {
                    btn.disabled = false;
                    btn.textContent = 'Principal';
                    mostrarMensajeGlobal({
                        mensaje: 'Error de conexión al marcar como principal.',
                        tipo: 'error',
                        exitoEl: exitoDireccion,
                        errorEl: errorDireccion
                    });
                });
            }
        });
    }

    // Cargar direcciones al inicio
    if (listaDirecciones) {
        cargarDirecciones();
    }

    function cargarDirecciones() {
        fetch('/usuarios/direcciones/')
            .then(response => response.json())
            .then(data => {
                direcciones = data.direcciones;
                renderDirecciones();
            })
            .catch(error => {
                console.error('Error al cargar direcciones:', error);
                mostrarMensajeGlobal({
                    mensaje: 'Error al cargar direcciones.',
                    tipo: 'error',
                    exitoEl: exitoDireccion,
                    errorEl: errorDireccion
                });
            });
    }

    function renderDirecciones() {
        if (!listaDirecciones) return;
        if (direcciones.length === 0) {
            listaDirecciones.innerHTML = '<div class="perfil-placeholder">No tienes direcciones guardadas.</div>';
        } else {
            listaDirecciones.innerHTML = direcciones.map(dir => `
                <div class="perfil-placeholder perfil-direccion-item">
                    <div class="perfil-direccion-header">
                        <strong>${dir.nombre}</strong>
                        ${dir.principal ? '<span class="perfil-badge perfil-badge--primary">Principal</span>' : ''}
                    </div>
                    <div class="perfil-direccion-detalle">${dir.direccion_completa}</div>
                    <div class="perfil-direccion-acciones">
                        ${!dir.principal ? `<button type="button" class="perfil-btn-action perfil-btn-action--primary" data-id="${dir.id}">Principal</button>` : ''}
                        <button type="button" class="perfil-btn-action perfil-btn-action--danger" data-id="${dir.id}">Eliminar</button>
                    </div>
                </div>
            `).join('');
        }
    }

    // Función utilitaria global para mostrar mensajes de éxito/error en cualquier sección
    function mostrarMensajeGlobal({mensaje, tipo, exitoEl, errorEl, tiempoExito = 3000, tiempoError = 5000}) {
        if (tipo === 'success') {
            if (exitoEl) {
                exitoEl.textContent = mensaje;
                exitoEl.style.display = 'block';
                if (errorEl) errorEl.style.display = 'none';
                setTimeout(() => { exitoEl.style.display = 'none'; }, tiempoExito);
            }
        } else {
            if (errorEl) {
                errorEl.textContent = mensaje;
                errorEl.style.display = 'block';
                if (exitoEl) exitoEl.style.display = 'none';
                setTimeout(() => { errorEl.style.display = 'none'; }, tiempoError);
            }
        }
    }

    // Reemplazo showMessage en direcciones
    function showMessage(message, type) {
        mostrarMensajeGlobal({
            mensaje: message,
            tipo: type,
            exitoEl: exitoDireccion,
            errorEl: errorDireccion
        });
    }

    // Métodos de pago (solo frontend, sin seguridad; persiste en localStorage por usuario)
    const perfilRoot = document.getElementById('perfil-root');
    const perfilUsername = perfilRoot ? (perfilRoot.dataset.username || 'anon') : 'anon';
    const LS_KEY_PAGOS = `perfil_pagOS_${perfilUsername}`;

    const formPago = document.getElementById('form-pago');
    const listaPagos = document.getElementById('pagos-lista');
    const exitoPago = document.getElementById('pago-exito');
    const errorPago = document.getElementById('pago-error');

    let pagos = [];

    function cargarPagos() {
        try {
            const raw = localStorage.getItem(LS_KEY_PAGOS);
            pagos = raw ? JSON.parse(raw) : [];
        } catch (_) {
            pagos = [];
        }
    }
    function guardarPagos() {
        try {
            localStorage.setItem(LS_KEY_PAGOS, JSON.stringify(pagos));
        } catch (_) {}
    }
    function mascaraNumeroTarjeta(numero) {
        const limpio = (numero || '').replace(/\s+/g, '');
        return `**** **** **** ${limpio.slice(-4)}`;
    }
    function renderPagos() {
        if (!listaPagos) return;
        if (!pagos || pagos.length === 0) {
            listaPagos.innerHTML = '<div class="perfil-placeholder">No tienes métodos de pago guardados.</div>';
            return;
        }
        listaPagos.innerHTML = pagos.map((pago, idx) => `
            <div class="perfil-placeholder perfil-pago-item" data-index="${idx}">
                <div><strong>${pago.nombre || 'Tarjeta'}</strong></div>
                <div>${mascaraNumeroTarjeta(pago.numero)}</div>
                <div>Vence: ${pago.vencimiento || ''}</div>
                <div class="perfil-direccion-acciones" style="margin-top:8px;display:flex;gap:8px;">
                    <button type="button" class="perfil-btn-action perfil-btn-action--danger pago-eliminar">Eliminar</button>
                </div>
            </div>
        `).join('');
    }
    function bindAccionesPagos() {
        if (!listaPagos) return;
        listaPagos.addEventListener('click', function(e) {
            const btnEliminar = e.target.closest('.pago-eliminar');
            if (btnEliminar) {
                const item = btnEliminar.closest('[data-index]');
                const idx = item ? parseInt(item.dataset.index) : -1;
                if (idx >= 0) {
                    pagos.splice(idx, 1);
                    guardarPagos();
                    renderPagos();
                }
            }
        });
    }
    // Validaciones
    function luhnValido(numero) {
        const digits = (numero || '').replace(/\D/g, '');
        let sum = 0;
        let alt = false;
        for (let i = digits.length - 1; i >= 0; i--) {
            let n = parseInt(digits.charAt(i), 10);
            if (alt) {
                n *= 2;
                if (n > 9) n -= 9;
            }
            sum += n;
            alt = !alt;
        }
        return sum % 10 === 0 && digits.length >= 12 && digits.length <= 19;
    }
    function detectarMarca(numeroDigits) {
        // Reglas básicas (no exhaustivas):
        // Visa: 4
        // MasterCard: 51-55, 2221-2720
        // Amex: 34, 37
        // Discover: 6011, 65, 644-649
        const n = numeroDigits;
        if (/^4\d{0,}$/.test(n)) return 'visa';
        if (/^(5[1-5]\d{0,}|2(2[2-9]\d|2[3-9]\d{2}|[3-6]\d{3}|7([01]\d{2}|20\d))\d*)$/.test(n)) return 'mastercard';
        if (/^3[47]\d{0,}$/.test(n)) return 'amex';
        if (/^(6011|65|64[4-9])\d*$/.test(n)) return 'discover';
        return 'desconocida';
    }
    function actualizarIconoMarca(numero) {
        const iconSpan = document.getElementById('pago-numero-brand-icon');
        if (!iconSpan) return;
        const digits = (numero || '').replace(/\D/g, '');
        const marca = detectarMarca(digits);
        let iconClass = 'far fa-credit-card';
        if (marca === 'visa') iconClass = 'fab fa-cc-visa';
        else if (marca === 'mastercard') iconClass = 'fab fa-cc-mastercard';
        else if (marca === 'amex') iconClass = 'fab fa-cc-amex';
        else if (marca === 'discover') iconClass = 'fab fa-cc-discover';
        iconSpan.innerHTML = `<i class="${iconClass}" aria-hidden="true"></i>`;
        iconSpan.title = marca.charAt(0).toUpperCase() + marca.slice(1);
    }
    function formatearNumeroTarjeta(input) {
        const limpio = input.value.replace(/\D/g, '').slice(0, 19);
        const grupos = limpio.match(/.{1,4}/g) || [];
        input.value = grupos.join(' ');
        actualizarIconoMarca(input.value);
    }
    function vencimientoValido(mmYY) {
        const match = /^(\d{2})\/(\d{2})$/.exec(mmYY || '');
        if (!match) return false;
        let mm = parseInt(match[1], 10);
        let yy = parseInt(match[2], 10);
        if (mm < 1 || mm > 12) return false;
        const ahora = new Date();
        const yearBase = Math.floor(ahora.getFullYear() / 100) * 100; // siglo actual
        const fullYear = yearBase + yy + (yy < (ahora.getFullYear() % 100) ? 100 : 0); // manejar cambio de siglo
        // último día del mes de vencimiento
        const expDate = new Date(fullYear, mm, 0, 23, 59, 59);
        return expDate >= ahora;
    }
    function cvcValido(cvc) { return /^\d{3,4}$/.test((cvc || '').trim()); }
    function mostrarErrorPago(msg) {
        if (!errorPago) return;
        errorPago.textContent = msg;
        errorPago.style.display = 'block';
        if (exitoPago) exitoPago.style.display = 'none';
    }
    function limpiarErrorPago() {
        if (errorPago) errorPago.style.display = 'none';
    }

    function initPagos() {
        cargarPagos();
        renderPagos();
        bindAccionesPagos();
        if (formPago) {
            // Enmascarar/formatos on-the-fly
            const inputNumero = formPago['numero'];
            const inputVenc = formPago['vencimiento'];
            const inputCvc = formPago['cvc'];
            if (inputNumero) {
                inputNumero.addEventListener('input', function() { formatearNumeroTarjeta(inputNumero); limpiarErrorPago(); });
                actualizarIconoMarca(inputNumero.value);
            }
            if (inputVenc) {
                inputVenc.addEventListener('input', function() {
                    let v = inputVenc.value.replace(/\D/g, '').slice(0, 4);
                    if (v.length >= 3) v = v.slice(0,2) + '/' + v.slice(2);
                    inputVenc.value = v; limpiarErrorPago();
                });
            }
            if (inputCvc) {
                inputCvc.addEventListener('input', function() { inputCvc.value = inputCvc.value.replace(/\D/g, '').slice(0,4); limpiarErrorPago(); });
            }
            formPago.addEventListener('submit', function(e) {
                e.preventDefault();
                const data = {
                    nombre: formPago['nombre'].value,
                    numero: formPago['numero'].value,
                    vencimiento: formPago['vencimiento'].value,
                    cvc: formPago['cvc'].value
                };
                // Validaciones
                if (!data.nombre || data.nombre.trim().length < 3) {
                    return mostrarErrorPago('Ingresa el nombre tal como aparece en la tarjeta.');
                }
                if (!luhnValido(data.numero)) {
                    return mostrarErrorPago('Número de tarjeta inválido. Verifica los dígitos.');
                }
                if (!vencimientoValido(data.vencimiento)) {
                    return mostrarErrorPago('Vencimiento inválido o en el pasado. Usa formato MM/AA.');
                }
                if (!cvcValido(data.cvc)) {
                    return mostrarErrorPago('CVC inválido. Debe ser de 3 o 4 dígitos.');
                }
                limpiarErrorPago();
                pagos.push(data);
                guardarPagos();
                renderPagos();
                formPago.reset();
                mostrarMensajeGlobal({
                    mensaje: 'Método de pago guardado (local).',
                    tipo: 'success',
                    exitoEl: exitoPago
                });
            });
        }
    }
    initPagos();

    // --- Pedidos AJAX ---
    function cargarPedidosAJAX() {
        const pedidosSection = document.getElementById('view-pedidos');
        if (!pedidosSection) {
            return;
        }
        
        pedidosSection.innerHTML = '<div class="perfil-placeholder">Cargando pedidos...</div>';
        
        fetch('/usuarios/pedidos/fragment/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.html) {
                pedidosSection.innerHTML = data.html;
            } else {
                throw new Error('No se recibió HTML en la respuesta');
            }
        })
        .catch((error) => {
            pedidosSection.innerHTML = '<div class="perfil-placeholder perfil-message perfil-message--error">Error al cargar los pedidos: ' + error.message + '</div>';
        });
    }
    
    // Cargar pedidos al hacer clic en el menú de pedidos
    document.querySelectorAll('.perfil-sidebar__link[data-section="pedidos"]').forEach(link => {
        link.addEventListener('click', function(e) {
            setTimeout(cargarPedidosAJAX, 100);
        });
    });
    
    // Si la URL ya tiene #pedidos al cargar, cargar AJAX automáticamente
    if (window.location.hash === '#pedidos') {
        setTimeout(cargarPedidosAJAX, 500);
    }
    
    // También cargar cuando se cambie el hash a #pedidos
    window.addEventListener('hashchange', function() {
        if (window.location.hash === '#pedidos') {
            setTimeout(cargarPedidosAJAX, 100);
        }
    });
}); 