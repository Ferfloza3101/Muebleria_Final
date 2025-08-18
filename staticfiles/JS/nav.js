document.addEventListener("DOMContentLoaded", function() {
    const navbar = document.querySelector(".nav-center");
    let lastScrollTop = 0;

    // Función para manejar el scroll y fijar la barra de navegación
    window.addEventListener("scroll", function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 50) {
            navbar.classList.add("fixed-nav");
        } else {
            navbar.classList.remove("fixed-nav");
        }
        
        lastScrollTop = scrollTop;
    });

    // Detectamos clic en los enlaces
    document.querySelector(".nav-center ul").addEventListener("click", function(event) {
        if (event.target.tagName === "A") {
            event.preventDefault(); 
            let targetId = event.target.getAttribute("href").replace("#", ""); 

            switch(targetId) {
                case "home":
                    window.scrollTo({ 
                        top: 0, 
                        behavior: "smooth" 
                    });
                    break;
                    
                case "products":
                    window.location.href = "/productos/";
                    break;
                    
                case "accessories":
                    window.location.href = "/productos/?categoria=accesorios";
                    break;
                    
                case "lookbook":
                    break;
                    
                case "contact":
                    const contactSection = document.querySelector("#contact-section");
                    if (contactSection) {
                        contactSection.scrollIntoView({ 
                            behavior: "smooth",
                            block: "start"
                        });
                    }
                    break;
            }
        }
    });
});
