/**
 * ============================================================================
 * BARBER SELECTION MODULE
 * ============================================================================
 * Gestiona la selección de barberos y horarios basándose en el establecimiento
 * y servicio elegido. Genera slots dinámicos según la configuración del establecimiento.
 */

const BarberSelection = (function() {
    'use strict';

    // ============================================================================
    // ESTADO PRIVADO
    // ============================================================================
    let state = {
        establishments: [],
        currentEstablishmentId: null,
        currentServiceId: null,
        selectedBarber: null,
        selectedDate: null,
        selectedTime: null,
        availableSlots: [],
        slotConfig: null
    };

    // ============================================================================
    // ELEMENTOS DEL DOM
    // ============================================================================
    const elements = {
        barbersGrid: null,
        dateInput: null,
        slotsContainer: null,
        barberInputs: null
    };

    // ============================================================================
    // INICIALIZACIÓN
    // ============================================================================
    function init(establishmentsData) {
        console.log('💈 Inicializando BarberSelection...');
        
        state.establishments = establishmentsData;
        cacheElements();
        attachEventListeners();
        
        console.log('✅ BarberSelection inicializado');
    }

    function cacheElements() {
        elements.barbersGrid = document.querySelector('#available-barbers');
        elements.dateInput = document.querySelector('#selectedDate');
        elements.slotsContainer = document.querySelector('#time-options');
        
        if (!elements.barbersGrid) {
            console.error('❌ No se encontró el contenedor #available-barbers');
        }
        
        if (!elements.slotsContainer) {
            console.error('❌ No se encontró el contenedor #time-options');
        }
    }

    function attachEventListeners() {
        // Escuchar cuando se selecciona un establecimiento
        document.addEventListener('establishmentSelected', handleEstablishmentSelected);
        
        // Escuchar cuando se selecciona un servicio
        document.addEventListener('serviceSelected', handleServiceSelected);
        
        // Escuchar cuando se selecciona un barbero
        document.addEventListener('click', function(e) {
            if (e.target.closest('.barber-card')) {
                handleBarberSelection(e.target.closest('.barber-card'));
            }
        });
        
        // Escuchar cuando se selecciona una fecha - MEJORADO
        if (elements.dateInput) {
            // Método 1: Event listener directo (más confiable)
            elements.dateInput.addEventListener('change', function() {
                handleDateChange();
            });
            
            // Método 2: MutationObserver como respaldo
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                        handleDateChange();
                    }
                });
            });
            
            observer.observe(elements.dateInput, {
                attributes: true,
                attributeFilter: ['value']
            });
            
            console.log('✅ Event listeners de fecha configurados');
        }
        
        // Escuchar cuando se selecciona un slot de tiempo
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('time-slot')) {
                handleTimeSlotSelection(e.target);
            }
        });
    }

    // ============================================================================
    // MANEJADORES DE EVENTOS
    // ============================================================================
    function handleEstablishmentSelected(event) {
        const establishment = event.detail.establishment;
        console.log('🏢 Establecimiento seleccionado para barberos:', establishment);
        
        state.currentEstablishmentId = establishment.id;
        
        // Guardar configuración de slots
        if (establishment.slot_config) {
            state.slotConfig = establishment.slot_config;
            console.log('⚙️ Configuración de slots:', state.slotConfig);
        }
        
        // Limpiar selecciones previas
        clearBarberSelection();
    }

    function handleServiceSelected(event) {
        const service = event.detail.service;
        console.log('✂️ Servicio seleccionado para barberos:', service);
        
        state.currentServiceId = service.id;
        loadBarbers();
    }

    function handleBarberSelection(card) {
        const barberId = card.dataset.barberId;
        
        if (!barberId) return;
        
        // Obtener información del barbero
        const establishment = state.establishments.find(
            est => est.id === state.currentEstablishmentId
        );
        
        if (!establishment) return;
        
        const barber = establishment.barbers.find(
            b => b.id === parseInt(barberId)
        );
        
        if (!barber) return;
        
        // Remover selección anterior
        document.querySelectorAll('.barber-card').forEach(c => {
            c.classList.remove('selected');
        });
        
        // Marcar como seleccionado
        card.classList.add('selected');
        
        state.selectedBarber = barber;
        
        console.log('💈 Barbero seleccionado:', state.selectedBarber);
        
        // Actualizar input oculto para validación
        const barberInput = document.getElementById('selectedBarber');
        if (barberInput) {
            barberInput.value = barber.id;
            console.log('✅ Input #selectedBarber actualizado:', barber.id);
        }
        
        // Actualizar reserva global
        if (window.App && window.App.reserva) {
            window.App.reserva.barber_id = barber.id;
            window.App.reserva.barber_name = barber.full_name;
            window.App.reserva.barber_email = barber.email;
            window.App.reserva.barber_rating = barber.qa_average;
        }
        
        // Emitir evento personalizado
        document.dispatchEvent(new CustomEvent('barberSelected', {
            detail: { barber: state.selectedBarber }
        }));
        
        // Si ya hay una fecha seleccionada, regenerar slots inmediatamente
        if (state.selectedDate) {
            console.log('🔄 Regenerando slots para la fecha ya seleccionada:', state.selectedDate);
            generateTimeSlots(state.selectedDate);
        } else {
            // Verificar si hay fecha en el input
            const dateValue = elements.dateInput ? elements.dateInput.value : null;
            if (dateValue) {
                state.selectedDate = dateValue;
                console.log('🔄 Fecha encontrada en input, generando slots:', dateValue);
                generateTimeSlots(dateValue);
            } else {
                console.log('ℹ️ Selecciona una fecha para ver los horarios disponibles');
            }
        }
    }

    function handleDateChange() {
        // Leer directamente del input
        const dateValue = elements.dateInput ? elements.dateInput.value : null;
        
        if (!dateValue) {
            console.log('⚠️ No hay fecha seleccionada');
            return;
        }
        
        console.log('📅 Fecha seleccionada:', dateValue);
        state.selectedDate = dateValue;
        
        // Solo generar slots si hay un barbero seleccionado
        if (state.selectedBarber) {
            generateTimeSlots(dateValue);
        } else {
            console.warn('⚠️ Selecciona un barbero antes de ver los horarios disponibles');
            showNoSlotsAvailable('Primero selecciona un barbero');
        }
    }

    function handleTimeSlotSelection(slotElement) {
        const timeValue = slotElement.dataset.time;
        
        if (!timeValue || slotElement.classList.contains('occupied')) {
            return;
        }
        
        // Remover selección anterior y checks
        document.querySelectorAll('.time-slot').forEach(slot => {
            slot.classList.remove('selected');
            // Remover check si existe
            const existingCheck = slot.querySelector('.slot-check');
            if (existingCheck) {
                existingCheck.remove();
            }
        });
        
        // Marcar como seleccionado
        slotElement.classList.add('selected');
        
        // Agregar check solo a este slot
        const checkElement = document.createElement('div');
        checkElement.className = 'slot-check';
        checkElement.innerHTML = '<i class="bi bi-check-circle-fill"></i>';
        slotElement.appendChild(checkElement);  
        
        state.selectedTime = timeValue;
        
        console.log('⏰ Horario seleccionado:', state.selectedTime);
        
        // 🆕 Actualizar input oculto para validación
        const selectedTimeInput = document.getElementById('selectedTime');
        if (selectedTimeInput) {
            selectedTimeInput.value = timeValue;
            console.log('✅ Input #selectedTime actualizado:', timeValue);
        } else {
            console.warn('⚠️ Input #selectedTime no encontrado');
        }
        
        // Actualizar reserva global
        if (window.App && window.App.reserva) {
            window.App.reserva.date = state.selectedDate;
            window.App.reserva.time = state.selectedTime;
            window.App.reserva.datetime = `${state.selectedDate} ${state.selectedTime}:00`;
        }
        
        // Emitir evento personalizado
        document.dispatchEvent(new CustomEvent('timeSlotSelected', {
            detail: { 
                date: state.selectedDate,
                time: state.selectedTime,
                datetime: `${state.selectedDate} ${state.selectedTime}:00`
            }
        }));
    }

    // ============================================================================
    // LÓGICA DE NEGOCIO
    // ============================================================================
    function loadBarbers() {
        console.log('🔍 Buscando barberos para establecimiento:', state.currentEstablishmentId);
        
        // Buscar el establecimiento
        const establishment = state.establishments.find(
            est => est.id === state.currentEstablishmentId
        );
        
        if (!establishment) {
            console.error('❌ No se encontró el establecimiento:', state.currentEstablishmentId);
            showEmptyState();
            return;
        }
        
        if (!establishment.barbers || establishment.barbers.length === 0) {
            console.warn('⚠️ El establecimiento no tiene barberos disponibles');
            showEmptyState();
            return;
        }
        
        console.log('👨‍💼 Barberos encontrados:', establishment.barbers);
        renderBarbers(establishment.barbers);
    }

    function renderBarbers(barbers) {
        if (!elements.barbersGrid) {
            console.error('❌ No se puede renderizar: barbersGrid no existe');
            return;
        }
        
        // Limpiar barberos anteriores
        elements.barbersGrid.innerHTML = '';
        
        // Renderizar cada barbero
        barbers.forEach((barber, index) => {
            const barberCard = createBarberCard(barber, index);
            elements.barbersGrid.appendChild(barberCard);
        });
        
        console.log(`✅ ${barbers.length} barberos renderizados`);
    }

    function createBarberCard(barber, index) {
        const div = document.createElement('div');
        div.className = 'barber-card';
        div.dataset.barberId = barber.id;
        
        // Determinar imagen del barbero - usar data URL para evitar errores de red
        let barberImage;
        if (barber.photo && barber.photo.startsWith('http')) {
            barberImage = barber.photo;
        } else {
            // Crear un placeholder SVG inline para evitar peticiones de red fallidas
            const initial = barber.first_name ? barber.first_name.charAt(0).toUpperCase() : '?';
            barberImage = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect width='100' height='100' fill='%233e1a4e'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='48' fill='white'%3E${initial}%3C/text%3E%3C/svg%3E`;
        }
        
        // Calcular calificación con estrellas
        const stars = generateStarRating(barber.qa_average || 0);
        
        div.innerHTML = `
            <div class="barber-card-inner">
                <div class="barber-image-container">
                    <img src="${barberImage}" 
                         alt="${barber.full_name}" 
                         class="barber-image">
                </div>
                <div class="barber-info">
                    <h3 class="barber-name">${barber.full_name}</h3>
                    <div class="barber-rating">
                        ${stars}
                        <span class="rating-value">${(barber.qa_average || 0).toFixed(1)}</span>
                    </div>
                    <div class="barber-email">${barber.email || ''}</div>
                </div>
                <div class="barber-check">
                    <i class="bi bi-check-circle-fill"></i>
                </div>
            </div>
        `;
        
        return div;
    }

    function generateStarRating(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        let stars = '';
        
        // Estrellas llenas
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="bi bi-star-fill"></i>';
        }
        
        // Media estrella
        if (hasHalfStar) {
            stars += '<i class="bi bi-star-half"></i>';
        }
        
        // Estrellas vacías
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="bi bi-star"></i>';
        }
        
        return stars;
    }

    async function generateTimeSlots(selectedDate) {
        console.log('🕐 Generando slots para fecha:', selectedDate);
        
        if (!state.selectedBarber) {
            console.error('❌ No hay barbero seleccionado');
            return;
        }
        
        if (!elements.slotsContainer) {
            console.error('❌ No se encontró el contenedor de slots');
            return;
        }
        
        // Obtener día de la semana (1-7, donde 1=Lunes, 7=Domingo)
        const date = new Date(selectedDate + 'T00:00:00');
        const dayOfWeek = date.getDay(); // 0=Domingo, 1=Lunes, ..., 6=Sábado
        
        // Convertir a formato usado en el sistema (1=Lunes, 7=Domingo)
        const systemDayOfWeek = dayOfWeek === 0 ? 7 : dayOfWeek;
        
        console.log('📆 Día de la semana:', systemDayOfWeek);
        
        // Obtener el establecimiento actual
        const establishment = state.establishments.find(
            est => est.id === state.currentEstablishmentId
        );
        
        if (!establishment) {
            console.error('❌ No se encontró el establecimiento');
            return;
        }
        
        // ESTRATEGIA 1: Buscar disponibilidad específica del barbero
        let availability = null;
        if (state.selectedBarber.availabilities && state.selectedBarber.availabilities.length > 0) {
            availability = state.selectedBarber.availabilities.find(
                av => av.day_of_week === systemDayOfWeek && av.is_available
            );
            
            if (availability) {
                console.log('✅ Usando disponibilidad específica del barbero:', availability);
            }
        }
        
        // ESTRATEGIA 2 (FALLBACK): Usar horario del establecimiento
        if (!availability && establishment.schedules && establishment.schedules.length > 0) {
            const establishmentSchedule = establishment.schedules.find(
                sch => sch.day_of_week === systemDayOfWeek && sch.is_open
            );
            
            if (establishmentSchedule) {
                console.log('✅ Usando horario del establecimiento:', establishmentSchedule);
                availability = {
                    day_of_week: establishmentSchedule.day_of_week,
                    start_time: establishmentSchedule.opening_time,
                    end_time: establishmentSchedule.closing_time,
                    is_available: true
                };
            }
        }
        
        // Si no hay disponibilidad del barbero ni del establecimiento
        if (!availability) {
            console.warn('⚠️ No hay horarios disponibles para este día');
            showNoSlotsAvailable(`No hay horarios disponibles para los ${getDayName(systemDayOfWeek)}s`);
            return;
        }
        
        console.log('✅ Horario para generar slots:', availability);
        
        // Obtener duración del slot (en minutos)
        const slotDuration = state.slotConfig?.default_slot_duration || 30;
        const bufferTime = state.slotConfig?.buffer_time_between_appointments || 0;
        const totalInterval = slotDuration + bufferTime;
        
        console.log(`⏱️ Duración de slot: ${slotDuration}min + buffer: ${bufferTime}min = ${totalInterval}min`);
        
        // Generar slots desde start_time hasta end_time
        const slots = [];
        const startTime = parseTime(availability.start_time);
        const endTime = parseTime(availability.end_time);
        
        let currentTime = startTime;
        
        while (currentTime + slotDuration <= endTime) {
            const hours = Math.floor(currentTime / 60);
            const minutes = currentTime % 60;
            const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
            
            slots.push({
                time: timeString,
                available: true, // Se actualizará con checkOccupiedSlots
                datetime: `${selectedDate} ${timeString}:00`
            });
            
            currentTime += totalInterval;
        }
        
        console.log(`📋 ${slots.length} slots generados`);
        
        // Verificar slots ocupados
        await checkOccupiedSlots(selectedDate, slots);
        
        state.availableSlots = slots;
        renderTimeSlots(slots);
    }
    
    /**
     * Consulta al servidor para obtener slots ocupados y marcarlos como no disponibles
     * @param {string} date - Fecha en formato YYYY-MM-DD
     * @param {Array} slots - Array de slots generados
     */
    async function checkOccupiedSlots(date, slots) {
        try {
            console.log('🔍 Verificando slots ocupados...');
            
            // Construir URL del endpoint
            const url = `/services_module/api/barber/${state.selectedBarber.id}/occupied-slots/?date=${date}`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                console.warn('⚠️ No se pudo verificar disponibilidad:', response.status);
                return; // Continuar con todos los slots disponibles
            }
            
            const data = await response.json();
            
            if (data.occupied_slots && data.occupied_slots.length > 0) {
                console.log(`🚫 ${data.occupied_slots.length} slots ocupados encontrados`);
                
                // Marcar slots como no disponibles
                const occupiedTimes = data.occupied_slots.map(slot => slot.time);
                
                slots.forEach(slot => {
                    if (occupiedTimes.includes(slot.time)) {
                        slot.available = false;
                        console.log(`  ⛔ ${slot.time} - OCUPADO`);
                    }
                });
            } else {
                console.log('✅ Todos los slots están disponibles');
            }
            
        } catch (error) {
            console.error('❌ Error al verificar slots ocupados:', error);
            // En caso de error, continuar mostrando todos los slots como disponibles
        }
    }

    function renderTimeSlots(slots) {
        if (!elements.slotsContainer) {
            console.error('❌ No se puede renderizar: slotsContainer no existe');
            return;
        }
        
        // Limpiar slots anteriores
        elements.slotsContainer.innerHTML = '';
        
        if (slots.length === 0) {
            showNoSlotsAvailable('No hay horarios disponibles para esta fecha');
            return;
        }
        
        // Filtrar solo los slots disponibles (no ocupados)
        const availableSlots = slots.filter(slot => slot.available);
        
        if (availableSlots.length === 0) {
            showNoSlotsAvailable('No hay horarios disponibles para esta fecha');
            return;
        }
        
        // Renderizar solo los slots disponibles
        availableSlots.forEach((slot, index) => {
            const slotElement = createTimeSlotElement(slot, index);
            elements.slotsContainer.appendChild(slotElement);
        });
        
    }

    function createTimeSlotElement(slot, index) {
        const div = document.createElement('div');
        div.className = 'time-slot';
        div.dataset.time = slot.time;
        div.dataset.datetime = slot.datetime;
        
        if (!slot.available) {
            div.classList.add('occupied');
            div.title = 'No disponible';
        }
        
        div.innerHTML = `<span class="time-text">${slot.time}</span>`;
        
        return div;
    }

    function showEmptyState() {
        if (!elements.barbersGrid) return;
        
        elements.barbersGrid.innerHTML = `
            <div class="barbers-empty-state">
                <i class="bi bi-person-x"></i>
                <h3>No hay barberos disponibles</h3>
                <p>Por favor, selecciona otro establecimiento</p>
            </div>
        `;
    }

    function showNoSlotsAvailable(message) {
        if (!elements.slotsContainer) return;
        
        elements.slotsContainer.innerHTML = `
            <div class="slots-empty-state">
                <i class="bi bi-clock-history"></i>
                <p>${message}</p>
            </div>
        `;
    }

    function clearBarberSelection() {
        state.selectedBarber = null;
        state.selectedDate = null;
        state.selectedTime = null;
        state.availableSlots = [];
        
        if (elements.barbersGrid) {
            elements.barbersGrid.innerHTML = '';
        }
        
        if (elements.slotsContainer) {
            elements.slotsContainer.innerHTML = '';
        }
    }

    // ============================================================================
    // UTILIDADES
    // ============================================================================
    
    /**
     * Convierte un string de tiempo "HH:MM" a minutos desde medianoche
     * @param {string} timeStr - Tiempo en formato "HH:MM"
     * @returns {number} - Minutos desde medianoche
     */
    function parseTime(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        return hours * 60 + minutes;
    }

    /**
     * Obtiene el nombre del día en español
     * @param {number} dayOfWeek - Número del día (1=Lunes, 7=Domingo)
     * @returns {string} - Nombre del día
     */
    function getDayName(dayOfWeek) {
        const days = {
            1: 'Lune',
            2: 'Marte',
            3: 'Miércole',
            4: 'Jueve',
            5: 'Vierne',
            6: 'Sábado',
            7: 'Domingo'
        };
        return days[dayOfWeek] || '';
    }

    // ============================================================================
    // API PÚBLICA
    // ============================================================================
    return {
        init,
        getSelectedBarber: () => state.selectedBarber,
        getSelectedDate: () => state.selectedDate,
        getSelectedTime: () => state.selectedTime,
        getAvailableSlots: () => state.availableSlots,
        getCurrentEstablishmentId: () => state.currentEstablishmentId
    };
})();

// Exponer globalmente
window.BarberSelection = BarberSelection;
