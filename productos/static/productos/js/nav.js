// Variables para el control del scroll
let lastScrollTop = 0;
const navbar = document.querySelector('.main-nav');
const scrollThreshold = 50; 

// Función para manejar el scroll
function handleScroll() {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    
    // Solo activar el comportamiento después de pasar el umbral
    if (currentScroll > scrollThreshold) {
        if (currentScroll > lastScrollTop) {
            // Scroll hacia abajo
            navbar.classList.add('nav-hidden');
            navbar.classList.remove('nav-visible');
        } else {
            // Scroll hacia arriba
            navbar.classList.remove('nav-hidden');
            navbar.classList.add('nav-visible');
        }
    } else {
        // En la parte superior, siempre mostrar la navbar
        navbar.classList.remove('nav-hidden');
        navbar.classList.remove('nav-visible');
    }
    
    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
}

// Añadir el event listener para el scroll
window.addEventListener('scroll', handleScroll, { passive: true });

// Asegurar que la navbar esté visible al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    navbar.classList.remove('nav-hidden');
    navbar.classList.add('nav-visible');
}); 