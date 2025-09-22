document.addEventListener('DOMContentLoaded', function() {
    // Animación de entrada para elementos del hero (EXCLUYENDO el título)
    const heroElements = document.querySelectorAll('.hero .btn, .hero .hero-subtitle, .hero .hero-description');
    const heroElementsObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.animation = 'fadeInUp 0.8s ease forwards';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 200);
                heroElementsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    heroElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        heroElementsObserver.observe(element);
    });

    // Efecto de hover en botones del hero
    const heroButtons = document.querySelectorAll('.hero .btn');
    heroButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.classList.add('btn-hover-effect');
        });

        button.addEventListener('mouseleave', function() {
            this.classList.remove('btn-hover-effect');
        });
    });

});
