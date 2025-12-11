/**
 * ============================================================================
 * SERVICE SELECTION MODULE
 * ============================================================================
 * Gestiona la selección de servicios basándose en el establecimiento elegido
 */

const ServiceSelection = (function() {
    'use strict';

    // ============================================================================
    // ESTADO PRIVADO
    // ============================================================================
    let state = {
        establishments: [],
        currentEstablishmentId: null,
        selectedService: null
    };

    // ============================================================================
    // ELEMENTOS DEL DOM
    // ============================================================================
    const elements = {
        servicesGrid: null,
        serviceInputs: null
    };

    // ============================================================================
    // INICIALIZACIÓN
    // ============================================================================
    function init(establishmentsData) {
        console.log('🎨 Inicializando ServiceSelection...');
        
        state.establishments = establishmentsData;
        cacheElements();
        attachEventListeners();
        
        console.log('✅ ServiceSelection inicializado');
    }

    function cacheElements() {
        elements.servicesGrid = document.getElementById('services-container') || document.querySelector('.services-grid');
        
        if (!elements.servicesGrid) {
            console.error('❌ No se encontró el contenedor de servicios');
        } else {
            console.log('✅ Contenedor de servicios encontrado:', elements.servicesGrid.id || elements.servicesGrid.className);
        }
    }

    function attachEventListeners() {
        // Escuchar cuando se selecciona un establecimiento
        document.addEventListener('establishmentSelected', handleEstablishmentSelected);
        
        // Escuchar cuando se selecciona un servicio
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('service-input')) {
                handleServiceSelection(e.target);
            }
        });
    }

    // ============================================================================
    // MANEJADORES DE EVENTOS
    // ============================================================================
    function handleEstablishmentSelected(event) {
        const establishment = event.detail.establishment;
        console.log('🏢 Establecimiento seleccionado para servicios:', establishment);
        
        state.currentEstablishmentId = establishment.id;
        loadServices(establishment.id);
    }

    function handleServiceSelection(input) {
        const serviceCard = input.closest('.service-card');
        
        if (!serviceCard) {
            console.warn('⚠️ No se encontró .service-card para el servicio');
            return;
        }
        
        // ✅ Leer ID desde dataset IGUAL QUE EL BARBERO
        const serviceId = serviceCard.dataset.serviceId;
        
        console.log('✂️ Servicio seleccionado - ID:', serviceId);
        
        if (!serviceId) {
            console.error('❌ No se encontró serviceId en el dataset');
            return;
        }
        
        // Obtener información del servicio desde la tarjeta
        const serviceName = serviceCard.querySelector('.service-title')?.textContent || 'Servicio';
        const servicePrice = serviceCard.querySelector('.service-price')?.textContent || '$0';
        const serviceDuration = serviceCard.querySelector('.service-duration')?.textContent || '0 min';
        
        state.selectedService = {
            id: parseInt(serviceId),
            name: serviceName,
            price: servicePrice,
            duration: serviceDuration
        };
        
        console.log('✅ Servicio completo:', state.selectedService);
        
        // Actualizar reserva global
        if (window.App && window.App.reserva) {
            window.App.reserva.service_id = parseInt(serviceId);
            window.App.reserva.service_name = serviceName;
            window.App.reserva.service_price = servicePrice;
            window.App.reserva.service_duration = serviceDuration;
            
            console.log('✅ App.reserva.service_id actualizado:', window.App.reserva.service_id);
        }
        
        // Emitir evento personalizado
        document.dispatchEvent(new CustomEvent('serviceSelected', {
            detail: { service: state.selectedService }
        }));
    }

    // ============================================================================
    // LÓGICA DE NEGOCIO
    // ============================================================================
    function loadServices(establishmentId) {
        console.log('🔍 Buscando servicios para establecimiento:', establishmentId);
        
        // Buscar el establecimiento
        const establishment = state.establishments.find(est => est.id === establishmentId);
        
        if (!establishment) {
            console.error('❌ No se encontró el establecimiento:', establishmentId);
            showEmptyState();
            return;
        }
        
        if (!establishment.services || establishment.services.length === 0) {
            console.warn('⚠️ El establecimiento no tiene servicios disponibles');
            showEmptyState();
            return;
        }
        
        console.log('📋 Servicios encontrados:', establishment.services);
        renderServices(establishment.services);
    }

    function renderServices(services) {
        if (!elements.servicesGrid) {
            console.error('❌ No se puede renderizar: servicesGrid no existe');
            return;
        }
        
        // Limpiar servicios anteriores
        elements.servicesGrid.innerHTML = '';
        
        // Renderizar cada servicio
        services.forEach((service, index) => {
            const serviceCard = createServiceCard(service, index);
            elements.servicesGrid.appendChild(serviceCard);
        });
        
        console.log(`✅ ${services.length} servicios renderizados`);
    }

    function createServiceCard(service, index) {
        const label = document.createElement('label');
        label.className = 'service-card';
        label.dataset.serviceId = service.id;  // ✅ ID de EstablishmentService
        
        // Determinar si es servicio destacado (popular)
        const isPopular = service.is_popular || false;
        const badgeHTML = isPopular ? '<div class="service-badge">Popular</div>' : '';
        const iconClass = isPopular ? 'service-icon service-icon--featured' : 'service-icon';
        
        // Determinar icono según el tipo de servicio
        const icon = getServiceIcon(service.name);
        
        label.innerHTML = `
            <input type="radio" 
                   name="service" 
                   value="${service.id}" 
                   class="service-input" 
                   required>
            <div class="service-card-inner">
                ${badgeHTML}
                <div class="service-header">
                    <div class="service-info">
                        <h3 class="service-title">${service.name}</h3>
                        <div class="service-price">$${formatPrice(service.sale_price)}</div>
                    </div>
                    <div class="${iconClass}">
                        <i class="bi bi-${icon}"></i>
                    </div>
                </div>
                <p class="service-description">${service.descripcion || 'Servicio de calidad profesional'}</p>
                <div class="service-check">
                    <i class="bi bi-check-circle-fill"></i>
                </div>
            </div>
        `;
        
        return label;
    }

    function getServiceIcon(serviceName) {
        const name = serviceName.toLowerCase();
        
        if (name.includes('corte') || name.includes('cabello')) {
            return 'scissors';
        } else if (name.includes('barba')) {
            return 'person';
        } else if (name.includes('combo') || name.includes('completo')) {
            return 'star-fill';
        } else if (name.includes('afeitado')) {
            return 'bezier';
        } else if (name.includes('color') || name.includes('tinte')) {
            return 'palette';
        } else if (name.includes('niño')) {
            return 'person-fill';
        }
        
        return 'scissors'; // Icono por defecto
    }

    function formatPrice(price) {
        // Formatear precio con separador de miles
        return new Intl.NumberFormat('es-CO').format(price);
    }

    function showEmptyState() {
        if (!elements.servicesGrid) return;
        
        elements.servicesGrid.innerHTML = `
            <div class="services-empty-state">
                <i class="bi bi-inbox"></i>
                <h3>No hay servicios disponibles</h3>
                <p>Por favor, selecciona otro establecimiento</p>
            </div>
        `;
    }

    // ============================================================================
    // API PÚBLICA
    // ============================================================================
    return {
        init,
        getSelectedService: () => state.selectedService,
        getCurrentEstablishmentId: () => state.currentEstablishmentId
    };
})();

// Exponer globalmente
window.ServiceSelection = ServiceSelection;
