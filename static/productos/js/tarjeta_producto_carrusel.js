/*
Lógica para el carrusel de imágenes en las tarjetas de producto y modales, usando todas las imágenes adicionales del producto.
Unificada y optimizada para ambos contextos.
*/

document.addEventListener('DOMContentLoaded', function() {
    function inicializarCarrusel({imgSelector, dotsSelector, wrapperSelector, imagesAttr, dotClass = 'dot', activeClass = 'active'}) {
        document.querySelectorAll(imgSelector).forEach(function(img) {
            let images = [];
            try {
                images = JSON.parse(img.getAttribute(imagesAttr));
            } catch (e) { images = []; }
            if (!images || images.length < 2) return; // Solo inicializar si hay más de una imagen
            let current = 0;
            const wrapper = img.closest(wrapperSelector);
            const dotsContainer = wrapper ? wrapper.parentElement.querySelector(dotsSelector) : null;
            if (!dotsContainer) return;
            // Generar dots
            dotsContainer.innerHTML = '';
            images.forEach((_, i) => {
                const dot = document.createElement('span');
                dot.className = dotClass + (i === 0 ? ' ' + activeClass : '');
                dot.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    current = i;
                    updateImage();
                });
                dotsContainer.appendChild(dot);
            });
            // Flechas
            const prev = wrapper.querySelector('.prev-arrow');
            const next = wrapper.querySelector('.next-arrow');
            if (prev && next) {
                prev.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    current = (current - 1 + images.length) % images.length;
                    updateImage();
                });
                next.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    current = (current + 1) % images.length;
                    updateImage();
                });
            }
            function updateImage() {
                img.src = images[current].url || images[current];
                img.setAttribute('data-current-image', current);
                dotsContainer.querySelectorAll('.' + dotClass).forEach((dot, i) => {
                    dot.classList.toggle(activeClass, i === current);
                });
            }
            // Inicializar
            updateImage();
        });
    }
    // Carrusel en tarjetas de producto
    inicializarCarrusel({
        imgSelector: '.product-card .product-image',
        dotsSelector: '.image-dots',
        wrapperSelector: '.product-image-wrapper',
        imagesAttr: 'data-images',
        dotClass: 'dot',
        activeClass: 'active'
    });
    // Carrusel en modales de producto
    inicializarCarrusel({
        imgSelector: '.modal-product-image',
        dotsSelector: '.modal-image-dots',
        wrapperSelector: '.modal-image-wrapper',
        imagesAttr: 'data-images',
        dotClass: 'dot',
        activeClass: 'active'
    });
}); 