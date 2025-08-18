// Galería de imágenes reutilizable para productos
// Uso: galeriaImagenes({
//   contenedor: elemento contenedor,
//   imgSelector: selector de la imagen principal,
//   dotsSelector: selector de los dots,
//   prevSelector: selector del botón anterior,
//   nextSelector: selector del botón siguiente,
//   imagenes: array de URLs de imágenes
// })

function galeriaImagenes({contenedor, imgSelector, dotsSelector, prevSelector, nextSelector, imagenes}) {
    if (!contenedor || !imagenes || !imagenes.length) return;
    let imagenActual = 0;
    const img = contenedor.querySelector(imgSelector);
    const dots = contenedor.querySelectorAll(dotsSelector);
    const btnPrev = contenedor.querySelector(prevSelector);
    const btnNext = contenedor.querySelector(nextSelector);

    function mostrarImagen(idx) {
        imagenActual = (idx + imagenes.length) % imagenes.length;
        if (img) {
            img.src = imagenes[imagenActual];
            img.dataset.currentImage = imagenActual;
        }
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === imagenActual);
        });
    }

    if (btnPrev) {
        btnPrev.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarImagen(imagenActual - 1);
        });
    }
    if (btnNext) {
        btnNext.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarImagen(imagenActual + 1);
        });
    }
    dots.forEach((dot, i) => {
        dot.addEventListener('click', function() {
            mostrarImagen(i);
        });
    });
    // Inicializar
    mostrarImagen(0);
} 