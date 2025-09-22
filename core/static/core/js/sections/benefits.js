/**
 * BENEFITS SECTION - JAVASCRIPT MODERNO Y MINIMALISTA
 * Efectos sutiles y modernos para la sección de beneficios
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configuración para intersection observer
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px 0px -50px 0px'
    };

    // Animación de entrada para las tarjetas
    const benefitCards = document.querySelectorAll('.benefit-card');
    
    if (benefitCards.length > 0) {
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        benefitCards.forEach(card => {
            cardObserver.observe(card);
        });
    }

    // Efecto de paralaje sutil en el fondo
    const benefitsSection = document.querySelector('.benefits');
    if (benefitsSection) {
        window.addEventListener('scroll', throttle(() => {
            const scrolled = window.pageYOffset;
            const sectionTop = benefitsSection.offsetTop;
            const sectionHeight = benefitsSection.offsetHeight;
            const windowHeight = window.innerHeight;
            
            // Solo aplicar efecto cuando la sección esté visible
            if (scrolled + windowHeight > sectionTop && scrolled < sectionTop + sectionHeight) {
                const yPos = -(scrolled - sectionTop) * 0.1;
                benefitsSection.style.backgroundPositionY = yPos + 'px';
            }
        }, 16));
    }

    // Efecto de hover mejorado con delay para iconos
    benefitCards.forEach(card => {
        const icon = card.querySelector('.benefit-icon');
        if (icon) {
            card.addEventListener('mouseenter', () => {
                setTimeout(() => {
                    if (card.matches(':hover')) {
                        icon.style.transform = 'scale(1.1) rotate(5deg)';
                    }
                }, 50);
            });

            card.addEventListener('mouseleave', () => {
                icon.style.transform = '';
            });
        }
    });

    // Contador animado para números (si hay métricas)
    const animateNumbers = () => {
        const numberElements = document.querySelectorAll('.benefit-number');
        numberElements.forEach(element => {
            const target = parseInt(element.dataset.number);
            const duration = 1500;
            const start = 0;
            const increment = target / (duration / 16);
            let current = start;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                element.textContent = Math.floor(current);
            }, 16);
        });
    };

    // Observar si hay elementos con números para animar
    const numberObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateNumbers();
                numberObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const numbersContainer = document.querySelector('.benefits-numbers');
    if (numbersContainer) {
        numberObserver.observe(numbersContainer);
    }

    // Efecto de ripple en las tarjetas al hacer clic
    benefitCards.forEach(card => {
        card.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(214, 179, 255, 0.3);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
            `;

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Añadir estilos CSS dinámicos para efectos
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .benefit-card {
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }
        
        .benefit-icon {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .benefits {
            background-attachment: fixed;
        }
    `;
    document.head.appendChild(style);
});

/**
 * Función throttle para optimizar el rendimiento del scroll
 * @param {Function} func - Función a ejecutar
 * @param {number} limit - Límite de tiempo en ms
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Función para manejar la visibilidad de elementos
 * Útil para animaciones y efectos de entrada
 */
function handleElementVisibility() {
    const elements = document.querySelectorAll('[data-animate]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const animationType = entry.target.dataset.animate;
                entry.target.classList.add(`animate-${animationType}`);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    elements.forEach(element => {
        observer.observe(element);
    });
}
