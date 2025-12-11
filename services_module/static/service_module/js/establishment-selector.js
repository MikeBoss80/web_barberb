/**
 * Establishment Selector Module
 * ==============================
 * Controla la interfaz de selección de establecimientos
 * Carga datos dinámicamente desde la base de datos y gestiona la interacción del usuario
 * 
 * @version 1.0
 * @author BarberB Team
 */

const EstablishmentSelector = (function() {
    'use strict';

    // ============================================================================
    // VARIABLES PRIVADAS
    // ============================================================================
    let establishments = [];
    let selectedEstablishment = null;
    let map = null;
    let markers = [];

    // Elementos del DOM
    const elements = {
        listContainer: null,
        mapContainer: null,
        searchInput: null,
        filterButtons: null
    };

    // ============================================================================
    // INICIALIZACIÓN
    // ============================================================================
    
    /**
     * Inicializa el módulo de selección de establecimientos
     * @param {Array} data - Array de establecimientos desde el servidor
     */
    function init(data) {
        console.log('🏢 Inicializando Establishment Selector...');
        
        // Guardar datos de establecimientos
        establishments = data || [];
        
        // Obtener referencias del DOM
        cacheDOM();
        
        // Renderizar lista de establecimientos
        renderEstablishmentsList();
        
        // Configurar event listeners
        bindEvents();
        
        // Inicializar mapa si existe
        if (elements.mapContainer && window.EstablishmentMap) {
            window.EstablishmentMap.init(establishments);
        }
        
        console.log(`✅ ${establishments.length} establecimientos cargados`);
    }

    /**
     * Cachea referencias a elementos del DOM
     */
    function cacheDOM() {
        elements.listContainer = document.querySelector('.establishments-list');
        elements.mapContainer = document.getElementById('establishmentMap');
        elements.searchInput = document.getElementById('establishmentSearch');
        elements.filterButtons = document.querySelectorAll('[data-filter]');
    }

    /**
     * Vincula eventos a elementos del DOM
     */
    function bindEvents() {
        // Búsqueda de establecimientos
        if (elements.searchInput) {
            elements.searchInput.addEventListener('input', handleSearch);
        }

        // Filtros de establecimientos
        if (elements.filterButtons) {
            elements.filterButtons.forEach(btn => {
                btn.addEventListener('click', handleFilter);
            });
        }

        // Delegación de eventos para cards de establecimientos
        if (elements.listContainer) {
            elements.listContainer.addEventListener('click', handleEstablishmentClick);
        }
    }

    // ============================================================================
    // RENDERIZADO DE ESTABLECIMIENTOS
    // ============================================================================

    /**
     * Renderiza la lista completa de establecimientos
     */
    function renderEstablishmentsList(filteredData = null) {
        if (!elements.listContainer) return;

        const dataToRender = filteredData || establishments;
        
        if (dataToRender.length === 0) {
            elements.listContainer.innerHTML = `
                <div class="no-results">
                    <i class="bi bi-search"></i>
                    <p>No se encontraron establecimientos</p>
                </div>
            `;
            return;
        }

        elements.listContainer.innerHTML = dataToRender
            .map(est => createEstablishmentCard(est))
            .join('');
    }

    /**
     * Crea el HTML de una tarjeta de establecimiento
     * @param {Object} establishment - Datos del establecimiento
     * @returns {string} HTML de la tarjeta
     */
    function createEstablishmentCard(establishment) {
        const scheduleText = getScheduleText(establishment.schedules);
        const isSelected = selectedEstablishment?.id === establishment.id;
        
        return `
            <label class="establishment-card-list ${isSelected ? 'establishment-card-list--selected' : ''}" 
                   data-establishment-id="${establishment.id}">
                <input type="radio" 
                       name="establishment" 
                       value="${establishment.id}" 
                       class="establishment-input" 
                       ${isSelected ? 'checked' : ''}
                       required>
                <div class="establishment-card-content">
                    <div class="establishment-card-header">
                        <div class="establishment-icon-small">
                            ${establishment.image ? 
                                `<img src="${establishment.image}" alt="${establishment.name}" class="establishment-logo">` :
                                '<i class="bi bi-building-fill"></i>'
                            }
                        </div>
                        <div class="establishment-info">
                            <h4 class="establishment-name">${establishment.name}</h4>
                            <p class="establishment-address-small">
                                <i class="bi bi-geo-alt"></i> ${establishment.address}, ${establishment.city}
                            </p>
                        </div>
                        <div class="establishment-check-small">
                            <i class="bi bi-check-circle-fill"></i>
                        </div>
                    </div>
                    <div class="establishment-card-details">
                        <div class="detail-item">
                            <i class="bi bi-clock"></i>
                            <span>${scheduleText}</span>
                        </div>
                        <div class="detail-item">
                            <i class="bi bi-telephone"></i>
                            <span>${establishment.phone}</span>
                        </div>
                        <div class="detail-item">
                            <i class="bi bi-star-fill"></i>
                            <span>${establishment.qa_average.toFixed(1)} estrellas</span>
                        </div>
                        ${establishment.services.length > 0 ? `
                        <div class="detail-item">
                            <i class="bi bi-scissors"></i>
                            <span>${establishment.services.length} servicios disponibles</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </label>
        `;
    }

    /**
     * Genera texto legible del horario
     * @param {Array} schedules - Array de horarios
     * @returns {string} Texto del horario
     */
    function getScheduleText(schedules) {
        if (!schedules || schedules.length === 0) {
            return 'Horario no disponible';
        }

        // Buscar el primer día abierto
        const openDay = schedules.find(s => s.is_open);
        
        if (!openDay) {
            return 'Cerrado temporalmente';
        }

        // Encontrar días consecutivos con mismo horario
        const commonSchedule = schedules.filter(s => 
            s.is_open && 
            s.opening_time === openDay.opening_time && 
            s.closing_time === openDay.closing_time
        );

        if (commonSchedule.length >= 5) {
            return `Lun - Sáb: ${openDay.opening_time} - ${openDay.closing_time}`;
        }

        return `${openDay.day_name}: ${openDay.opening_time} - ${openDay.closing_time}`;
    }

    // ============================================================================
    // MANEJO DE EVENTOS
    // ============================================================================

    /**
     * Maneja el click en un establecimiento
     * @param {Event} e - Evento de click
     */
    function handleEstablishmentClick(e) {
        const card = e.target.closest('.establishment-card-list');
        if (!card) return;

        const establishmentId = parseInt(card.dataset.establishmentId);
        selectEstablishment(establishmentId);
    }

    /**
     * Maneja la búsqueda de establecimientos
     * @param {Event} e - Evento de input
     */
    function handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            renderEstablishmentsList();
            return;
        }

        const filtered = establishments.filter(est => {
            return est.name.toLowerCase().includes(searchTerm) ||
                   est.address.toLowerCase().includes(searchTerm) ||
                   est.city.toLowerCase().includes(searchTerm) ||
                   est.description.toLowerCase().includes(searchTerm);
        });

        renderEstablishmentsList(filtered);
    }

    /**
     * Maneja los filtros de establecimientos
     * @param {Event} e - Evento de click
     */
    function handleFilter(e) {
        const filterType = e.target.dataset.filter;
        
        // Actualizar botones activos
        elements.filterButtons.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');

        let filtered = [...establishments];

        switch(filterType) {
            case 'all':
                // Mostrar todos
                break;
            case 'highest-rated':
                filtered.sort((a, b) => b.qa_average - a.qa_average);
                break;
            case 'nearest':
                // TODO: Implementar ordenamiento por distancia usando geolocalización
                console.log('🗺️ Filtro por cercanía (requiere geolocalización)');
                break;
            case 'most-services':
                filtered.sort((a, b) => b.services.length - a.services.length);
                break;
            default:
                break;
        }

        renderEstablishmentsList(filtered);
    }

    // ============================================================================
    // SELECCIÓN DE ESTABLECIMIENTO
    // ============================================================================

    /**
     * Selecciona un establecimiento
     * @param {number} establishmentId - ID del establecimiento
     */
    function selectEstablishment(establishmentId) {
        const establishment = establishments.find(e => e.id === establishmentId);
        
        if (!establishment) {
            console.error('❌ Establecimiento no encontrado:', establishmentId);
            return;
        }

        selectedEstablishment = establishment;
        
        console.log('✅ Establecimiento seleccionado:', establishment.name);

        // Actualizar App.reserva global
        if (window.App) {
            window.App.reserva.establishment_id = establishmentId;
            window.App.reserva.establishment_name = establishment.name;
            window.App.reserva.establishment_address = establishment.address;
            
            // Cargar información del establecimiento en App.establishment
            loadEstablishmentData(establishment);
        }

        // Actualizar UI
        updateEstablishmentUI(establishment);

        // Centrar mapa en establecimiento seleccionado
        if (map && establishment.lat && establishment.lng) {
            centerMapOnEstablishment(establishment);
        }

        // Disparar evento personalizado
        document.dispatchEvent(new CustomEvent('establishmentSelected', {
            detail: { establishment }
        }));
    }

    /**
     * Carga los datos del establecimiento en el objeto App global
     * @param {Object} establishment - Datos del establecimiento
     */
    function loadEstablishmentData(establishment) {
        // Actualizar datos básicos
        Object.assign(window.App.establishment, {
            id: establishment.id,
            name: establishment.name,
            address: establishment.address,
            city: establishment.city,
            country: establishment.country,
            phone: establishment.phone,
            email: establishment.email,
            description: establishment.description,
            lat: establishment.lat,
            lng: establishment.lng,
            image: establishment.image,
            qa_average: establishment.qa_average,
            active: establishment.active
        });

        // Cargar horarios
        window.App.establishment.schedules = establishment.schedules || [];

        // Cargar configuración de slots
        if (establishment.slot_config) {
            Object.assign(window.App.establishment.slot_config, establishment.slot_config);
        }

        // Limpiar y cargar servicios
        window.App.establishment.services.list = [];
        if (establishment.services && establishment.services.length > 0) {
            establishment.services.forEach(service => {
                window.App.establishment.services.add(service);
            });
        }

        // Limpiar y cargar barberos
        window.App.establishment.barbers.list = [];
        if (establishment.barbers && establishment.barbers.length > 0) {
            establishment.barbers.forEach(barber => {
                window.App.establishment.barbers.add(barber);
            });
        }

        // Limpiar y cargar productos
        window.App.establishment.products.list = [];
        if (establishment.products && establishment.products.length > 0) {
            establishment.products.forEach(product => {
                window.App.establishment.products.add(product);
            });
        }

        console.log('📦 Datos del establecimiento cargados en App:', {
            servicios: window.App.establishment.services.list.length,
            barberos: window.App.establishment.barbers.list.length,
            productos: window.App.establishment.products.list.length,
            horarios: window.App.establishment.schedules.length
        });
    }

    /**
     * Actualiza la interfaz con la información del establecimiento seleccionado
     * @param {Object} establishment - Datos del establecimiento
     */
    function updateEstablishmentUI(establishment) {
        // Remover selección anterior
        document.querySelectorAll('.establishment-card-list').forEach(card => {
            card.classList.remove('establishment-card-list--selected');
        });

        // Agregar selección actual
        const selectedCard = document.querySelector(`[data-establishment-id="${establishment.id}"]`);
        if (selectedCard) {
            selectedCard.classList.add('establishment-card-list--selected');
            
            // Scroll suave hacia la tarjeta seleccionada
            selectedCard.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }

        // Mostrar información resumida
        showEstablishmentSummary(establishment);
        
        // Actualizar mapa si está disponible
        if (window.EstablishmentMap && window.EstablishmentMap.isInitialized()) {
            window.EstablishmentMap.centerOnEstablishment(establishment.id);
        }
    }

    /**
     * Muestra un resumen del establecimiento seleccionado
     * @param {Object} establishment - Datos del establecimiento
     */
    function showEstablishmentSummary(establishment) {
        // Buscar o crear contenedor de resumen
        let summaryContainer = document.getElementById('establishmentSummary');
        
        if (!summaryContainer) {
            summaryContainer = document.createElement('div');
            summaryContainer.id = 'establishmentSummary';
            summaryContainer.className = 'establishment-summary';
            
            // Insertar después del stepper
            const stepper = document.querySelector('.appointment-stepper');
            if (stepper) {
                stepper.insertAdjacentElement('afterend', summaryContainer);
            }
        }

        summaryContainer.innerHTML = `
            <div class="summary-content">
                <div class="summary-icon">
                    <i class="bi bi-check-circle-fill"></i>
                </div>
                <div class="summary-text">
                    <strong>${establishment.name}</strong>
                    <span>${establishment.address}, ${establishment.city}</span>
                </div>
            </div>
        `;
        
        summaryContainer.style.display = 'block';
    }

    // ============================================================================
    // INTEGRACIÓN CON MAPA
    // ============================================================================

    /**
     * Inicializa el mapa de establecimientos
     * DEPRECADO: El mapa ahora se inicializa a través de EstablishmentMap.init()
     */
    function initializeMap() {
        console.log('ℹ️ initializeMap() está deprecado. Usa EstablishmentMap.init() directamente.');
    }

    /**
     * Agrega un marcador al mapa
     * DEPRECADO: Los marcadores se agregan automáticamente en EstablishmentMap
     */
    function addMarkerToMap(establishment) {
        console.log('ℹ️ addMarkerToMap() está deprecado. Los marcadores se agregan automáticamente.');
    }

    /**
     * Centra el mapa en el establecimiento seleccionado
     * DEPRECADO: Usa EstablishmentMap.centerOnEstablishment()
     */
    function centerMapOnEstablishment(establishment) {
        if (window.EstablishmentMap) {
            window.EstablishmentMap.centerOnEstablishment(establishment.id);
        }
    }

    // ============================================================================
    // MÉTODOS PÚBLICOS
    // ============================================================================

    return {
        init,
        selectEstablishment,
        getSelected: () => selectedEstablishment,
        getAll: () => establishments,
        refresh: renderEstablishmentsList
    };

})();

// ============================================================================
// EXPORT PARA USO GLOBAL
// ============================================================================
window.EstablishmentSelector = EstablishmentSelector;
