document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.custom-navbar');
    const navLinks = document.querySelectorAll('.nav-link');
    const loginBtn = document.querySelector('.btn-login');
    
    // Efecto de scroll avanzado para el navbar (SIN ocultarlo)
    let lastScrollY = window.scrollY;
    let ticking = false;
    
    function updateNavbar() {
    const scrollY = window.scrollY;
    
    // Solo cambiar el estilo del navbar, NUNCA ocultarlo
    if (scrollY > 50) {
        navbar.classList.add('navbar-scrolled');
    } else {
        navbar.classList.remove('navbar-scrolled');
    }
    
    // ELIMINAR el efecto de ocultación - El navbar SIEMPRE debe estar visible
    // NO agregar transform que mueva el navbar fuera de la pantalla
    
    lastScrollY = scrollY;
    ticking = false;
    }
    
    window.addEventListener('scroll', function() {
    if (!ticking) {
        requestAnimationFrame(updateNavbar);
        ticking = true;
    }
    });
    
    // Navegación suave mejorada con indicador de progreso
    navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#inicio') {
        e.preventDefault();
        
        // Efecto de carga
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = '';
        }, 150);
        
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        }
    });
    
    // Efecto de hover mejorado
    link.addEventListener('mouseenter', function() {
        this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    });
    });
    
    // Efecto de partículas interactivas en el navbar
    navbar.addEventListener('mousemove', function(e) {
    const rect = navbar.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    const before = window.getComputedStyle(navbar, '::before');
    navbar.style.setProperty('--mouse-x', x + '%');
    navbar.style.setProperty('--mouse-y', y + '%');
    });
    
    // Animación del botón de login
    loginBtn.addEventListener('click', function(e) {
    // Crear efecto de ondas
    const ripple = document.createElement('div');
    ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    `;
    
    const rect = this.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
    ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
    
    this.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
    });
    
    // Indicador de carga de página
    window.addEventListener('load', function() {
    navbar.style.animation = 'slideInDown 0.8s ease forwards';
    });
    
    // Efecto de hover en el logo
    const logo = document.querySelector('.navbar-brand');
    logo.addEventListener('mouseenter', function() {
    this.style.transform = 'scale(1.05) rotate(2deg)';
    });
    
    logo.addEventListener('mouseleave', function() {
    this.style.transform = 'scale(1) rotate(0deg)';
    });

    // ================================
    // EFECTOS PARA EL FOOTER MODERNO
    // ================================
    
    // Animación de entrada cuando el footer es visible
    const footer = document.querySelector('.modern-footer');
    const footerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('footer-visible');
                
                // Animar elementos del footer con delay progresivo
                const footerElements = entry.target.querySelectorAll('.footer-brand, .footer-heading, .social-link');
                footerElements.forEach((element, index) => {
                    setTimeout(() => {
                        element.style.animation = 'fadeInUp 0.6s ease forwards';
                        element.style.opacity = '1';
                        element.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            }
        });
    }, { threshold: 0.1 });

    if (footer) {
        footerObserver.observe(footer);
    }

    // Efecto parallax sutil en las ondas del footer
    window.addEventListener('scroll', function() {
        const footerWaves = document.querySelector('.footer-waves');
        if (footerWaves) {
            const scrollTop = window.pageYOffset;
            const rate = scrollTop * -0.5;
            footerWaves.style.transform = `rotate(180deg) translateY(${rate}px)`;
        }
    });

    // Efecto de hover mejorado para enlaces del footer
    const footerLinks = document.querySelectorAll('.footer-links a');
    footerLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            // Crear efecto de partícula
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: 4px;
                height: 4px;
                background: #d6b3ff;
                border-radius: 50%;
                pointer-events: none;
                animation: particleFly 0.6s ease-out forwards;
            `;
            
            const rect = this.getBoundingClientRect();
            particle.style.left = (rect.left + Math.random() * rect.width) + 'px';
            particle.style.top = (rect.top + rect.height) + 'px';
            
            document.body.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 600);
        });
    });

    // Efecto de pulsación sutil en redes sociales
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.animation = 'socialPulse 0.6s ease';
        });
        
        link.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });

    // Contador animado para el copyright (año actual)
    const copyrightText = document.querySelector('.copyright-text');
    if (copyrightText) {
        const currentYear = new Date().getFullYear();
        copyrightText.innerHTML = copyrightText.innerHTML.replace('2025', currentYear);
    }
});
    
// Agregar estilos CSS dinámicos para efectos
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
    }
    
    .custom-navbar {
    --mouse-x: 50%;
    --mouse-y: 50%;
    }
    
    .custom-navbar::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(
        circle 150px at var(--mouse-x) var(--mouse-y),
        rgba(214, 179, 255, 0.05),
        transparent
    );
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease;
    }
    
    .custom-navbar:hover::after {
    opacity: 1;
    }
    
    .btn-login {
    position: relative;
    overflow: hidden;
    }

    /* Nuevos estilos para el footer */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes particleFly {
        to {
            transform: translateY(-20px);
            opacity: 0;
        }
    }

    @keyframes socialPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }

    .modern-footer .footer-brand,
    .modern-footer .footer-heading,
    .modern-footer .social-link {
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.6s ease;
    }

    .footer-visible .footer-brand,
    .footer-visible .footer-heading,
    .footer-visible .social-link {
        opacity: 1;
        transform: translateY(0);
    }
`;
document.head.appendChild(style);


