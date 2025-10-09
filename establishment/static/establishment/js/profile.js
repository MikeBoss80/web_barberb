/**
 * ProfileEstablishment - JavaScript para el tab de perfil del establecimiento
 * Optimizado para funcionar dentro del sistema de tabs sin interferir con el sidebar
 */

class ProfileEstablishment {
    constructor() {
        this.isLoading = false;
        this.animationDelay = 100;
        this.init();
    }

    init() {
        // Solo inicializar si estamos en el tab de profile
        if (!document.querySelector('.profile-tab')) {
            return;
        }
        
        this.setupEventListeners();
        this.setupEstablishmentSelector();
        this.setupCustomBackgrounds();
        this.initializeAnimations();
        this.setupAdvancedInteractions();
    }

    setupEventListeners() {
        // Usar eventos delegados para no interferir con el sistema de tabs
        document.addEventListener('DOMContentLoaded', () => {
            if (document.querySelector('.profile-tab')) {
                this.initializeComponents();
            }
        });
    }

    setupEstablishmentSelector() {
        const establishmentSelect = document.querySelector('.profile-tab #establishment-select');
        if (establishmentSelect) {
            establishmentSelect.addEventListener('change', (e) => {
                this.handleEstablishmentChange(e.target.value);
            });
        }
    }

    handleEstablishmentChange(establishmentId) {
        if (!establishmentId || this.isLoading) return;
        
        this.isLoading = true;
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.set('establishment_id', establishmentId);
        currentUrl.searchParams.set('tab', 'profile');
        
        this.showLoadingState();
        window.location.href = currentUrl.toString();
    }

    setupCustomBackgrounds() {
        const heroBackground = document.querySelector('.profile-tab .hero-background');
        if (heroBackground) {
            if (heroBackground.hasAttribute('data-bg')) {
                const bgImage = heroBackground.getAttribute('data-bg');
                this.preloadAndSetBackground(heroBackground, bgImage);
            }
        }
    }

    preloadAndSetBackground(element, imageUrl) {
        const img = new Image();
        img.onload = () => {
            element.style.backgroundImage = `url('${imageUrl}')`;
            element.classList.add('loaded');
        };
        img.onerror = () => {
            element.classList.add('default-bg');
        };
        img.src = imageUrl;
    }

    initializeAnimations() {
        this.setupAdvancedHovers();
        this.animateStarRatings();
        this.initializeIntersectionObserver();
    }

    setupAdvancedHovers() {
        const cards = document.querySelectorAll('.profile-tab .content-card, .profile-tab .info-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                this.cardEnterAnimation(e.target);
            });
            
            card.addEventListener('mouseleave', (e) => {
                this.cardLeaveAnimation(e.target);
            });

            // Efectos táctiles para móviles
            card.addEventListener('touchstart', () => {
                card.classList.add('touch-active');
            });
            
            card.addEventListener('touchend', () => {
                setTimeout(() => {
                    card.classList.remove('touch-active');
                }, 150);
            });
        });
    }

    cardEnterAnimation(card) {
        // Efectos simples como management.css
        if (window.innerWidth > 768) {
            card.style.transform = 'translateY(-2px)';
            card.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
            card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
        }
    }

    cardLeaveAnimation(card) {
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = '';
    }

    animateStarRatings() {
        const starContainers = document.querySelectorAll('.profile-tab .stars');
        starContainers.forEach(container => {
            const stars = container.querySelectorAll('i');
            stars.forEach((star, index) => {
                // Efectos simples
                star.addEventListener('mouseenter', () => {
                    star.style.transform = 'scale(1.1)';
                    star.style.transition = 'transform 0.2s ease';
                });
                
                star.addEventListener('mouseleave', () => {
                    star.style.transform = 'scale(1)';
                });
            });
        });
    }

    initializeIntersectionObserver() {
        // Simplificar o eliminar intersection observer que puede causar problemas
        // Solo aplicar efectos básicos
        const cards = document.querySelectorAll('.profile-tab .content-card, .profile-tab .info-card');
        cards.forEach(card => {
            // Asegurar que las cards estén visibles desde el inicio
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        });
    }

    animateElement(element) {
        const siblings = Array.from(element.parentElement.children);
        const index = siblings.indexOf(element);
        const delay = index * this.animationDelay;
        
        setTimeout(() => {
            element.classList.add('animate-fade-in-up');
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, delay);
    }

    setupAdvancedInteractions() {
        this.setupRippleEffects();
        this.setupPhoneLinks();
        this.setupImageLoading();
    }

    setupRippleEffects() {
        const buttons = document.querySelectorAll('.profile-tab .cta-button');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.createRipple(e, button);
            });
        });
    }

    createRipple(event, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            transform: scale(0);
            animation: rippleAnimation 0.8s ease-out;
            pointer-events: none;
        `;
        
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 800);
    }

    setupPhoneLinks() {
        const phoneLinks = document.querySelectorAll('.profile-tab a[href^="tel:"]');
        phoneLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.showCallFeedback(link);
            });
        });
    }

    showCallFeedback(link) {
        const originalText = link.innerHTML;
        
        link.innerHTML = '<i class="fas fa-phone-alt animate-pulse"></i> Conectando...';
        link.style.opacity = '0.8';
        
        setTimeout(() => {
            link.innerHTML = originalText;
            link.style.opacity = '1';
        }, 2000);
    }

    setupImageLoading() {
        const images = document.querySelectorAll('.profile-tab .content-card-image img');
        images.forEach(img => {
            if (!img.complete) {
                img.style.opacity = '0';
                img.style.transform = 'scale(1.1)';
            }
            
            img.addEventListener('load', () => {
                img.style.transition = 'all 0.6s ease';
                img.style.opacity = '1';
                img.style.transform = 'scale(1)';
                img.classList.add('loaded');
            });
            
            if (img.complete) {
                img.style.opacity = '1';
                img.style.transform = 'scale(1)';
                img.classList.add('loaded');
            }
        });
    }

    showLoadingState() {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay-premium';
        loadingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner-premium"></div>
                <h3>Cargando perfil...</h3>
                <p>Preparando la mejor experiencia</p>
            </div>
        `;
        
        // Solo aplicar al tab de profile
        const profileTab = document.querySelector('.profile-tab');
        if (profileTab) {
            profileTab.appendChild(loadingOverlay);
        }
        
        this.addLoadingStyles();
    }

    addLoadingStyles() {
        if (document.getElementById('profile-loading-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'profile-loading-styles';
        style.textContent = `
            .profile-tab .loading-overlay-premium {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(62, 26, 78, 0.95);
                backdrop-filter: blur(10px);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10; /* Z-index bajo */
                color: white;
                font-family: inherit;
                border-radius: var(--border-radius-lg);
            }
            
            .profile-tab .loading-content {
                text-align: center;
            }
            
            .profile-tab .loading-spinner-premium {
                width: 40px;
                height: 40px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top: 3px solid white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }

    initializeComponents() {
        // Solo inicializar componentes del tab de profile
        this.setupSmoothScrolling();
    }

    setupSmoothScrolling() {
        const internalLinks = document.querySelectorAll('.profile-tab a[href^="#"]');
        internalLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target && target.closest('.profile-tab')) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Inicializar solo cuando el DOM esté listo y sea el tab correcto
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.profile-tab')) {
        const profileEstablishment = new ProfileEstablishment();
        window.ProfileEstablishment = profileEstablishment;
    }
});

// También inicializar cuando se cambie a este tab (si es dinámico)
document.addEventListener('tab-changed', (e) => {
    if (e.detail && e.detail.tabName === 'profile' && document.querySelector('.profile-tab')) {
        const profileEstablishment = new ProfileEstablishment();
        window.ProfileEstablishment = profileEstablishment;
    }
});
