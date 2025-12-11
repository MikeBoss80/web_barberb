/**
 * Appointment Booking System
 * Handles multi-step form navigation and validation
 */

(function() {
    'use strict';

    // State Management
    let currentStep = 1;
    const totalSteps = 4;
    const formData = {
        establishment: null,
        service: null,
        barber: null,
        date: null,
        time: null
    };

    // Establishment data mapping
    const establishmentData = {
        sede1: {
            name: 'Barbería Centro',
            address: 'Calle 10 #15-20'
        },
        sede2: {
            name: 'Barbería Norte',
            address: 'Carrera 50 #80-35'
        },
        sede3: {
            name: 'Barbería Sur',
            address: 'Avenida 30 #5-12'
        }
    };

    // Service data mapping
    const serviceData = {
        corte: {
            name: 'Corte de Cabello',
            price: '$15.000',
            duration: '30 min'
        },
        barba: {
            name: 'Arreglo de Barba',
            price: '$10.000',
            duration: '20 min'
        },
        combo: {
            name: 'Combo Completo',
            price: '$20.000',
            duration: '45 min'
        }
    };

    // Barber data mapping
    const barberData = {
        barber1: {
            name: 'Carlos Martínez',
            rating: '4.8'
        },
        barber2: {
            name: 'Juan López',
            rating: '4.9'
        },
        barber3: {
            name: 'Pedro Sánchez',
            rating: '4.7'
        }
    };

    // DOM Elements
    const form = document.getElementById('appointmentForm');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const steps = document.querySelectorAll('.appointment-step');
    const stepperItems = document.querySelectorAll('.stepper-item');
    const stepperLines = document.querySelectorAll('.stepper-line');

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        init();
    });

    function init() {
        setupEventListeners();
        updateNavigationButtons();
        setMinDate();
        generateTimeSlots();
    }

    /**
     * Setup all event listeners
     */
    function setupEventListeners() {
        // Navigation buttons
        prevBtn.addEventListener('click', goToPreviousStep);
        nextBtn.addEventListener('click', goToNextStep);
        
        // Form submission
        form.addEventListener('submit', handleFormSubmit);

        // Establishment selection
        const establishmentInputs = document.querySelectorAll('input[name="establishment"]');
        establishmentInputs.forEach(input => {
            input.addEventListener('change', handleEstablishmentSelection);
        });

        // Service selection
        const serviceInputs = document.querySelectorAll('input[name="service"]');
        serviceInputs.forEach(input => {
            input.addEventListener('change', handleServiceSelection);
        });

        // Barber selection
        const barberInputs = document.querySelectorAll('input[name="barber"]');
        barberInputs.forEach(input => {
            input.addEventListener('change', handleBarberSelection);
        });

        // Date selection
        const dateInput = document.getElementById('appointmentDate');
        if (dateInput) {
            dateInput.addEventListener('change', handleDateSelection);
        }
    }

    /**
     * Navigate to the next step
     */
    function goToNextStep() {
        if (!validateCurrentStep()) {
            return;
        }

        if (currentStep < totalSteps) {
            currentStep++;
            updateStepDisplay();
            updateNavigationButtons();
            
            // If entering confirmation step, update summary
            if (currentStep === 4) {
                updateSummary();
            }
        }
    }

    /**
     * Navigate to the previous step
     */
    function goToPreviousStep() {
        if (currentStep > 1) {
            currentStep--;
            updateStepDisplay();
            updateNavigationButtons();
        }
    }

    /**
     * Validate current step
     */
    function validateCurrentStep() {
        switch(currentStep) {
            case 1:
                return validateEstablishmentSelection();
            case 2:
                return validateServiceSelection();
            case 3:
                return validateBarberAndDateTime();
            default:
                return true;
        }
    }

    /**
     * Validate establishment selection
     */
    function validateEstablishmentSelection() {
        const selectedEstablishment = document.querySelector('input[name="establishment"]:checked');
        
        if (!selectedEstablishment) {
            showNotification('Por favor selecciona un establecimiento', 'warning');
            return false;
        }
        
        formData.establishment = selectedEstablishment.value;
        return true;
    }

    /**
     * Validate service selection
     */
    function validateServiceSelection() {
        const selectedService = document.querySelector('input[name="service"]:checked');
        
        if (!selectedService) {
            showNotification('Por favor selecciona un servicio', 'warning');
            return false;
        }
        
        formData.service = selectedService.value;
        return true;
    }

    /**
     * Validate barber, date and time selection
     */
    function validateBarberAndDateTime() {
        const selectedBarberInput = document.getElementById('selectedBarber');
        const dateInput = document.getElementById('appointmentDate');
        const selectedTime = document.getElementById('selectedTime');

        console.log('🔍 Validando Step 3:');
        console.log('  - selectedBarber input:', selectedBarberInput);
        console.log('  - selectedBarber value:', selectedBarberInput?.value);
        console.log('  - App.reserva.barber_id:', window.App?.reserva?.barber_id);

        // Validar barbero (usar App.reserva como fuente principal)
        const hasBarber = (window.App?.reserva?.barber_id) || (selectedBarberInput && selectedBarberInput.value);
        
        if (!hasBarber) {
            console.error('❌ Validación falló: No hay barbero seleccionado');
            showNotification('Por favor selecciona un barbero', 'warning');
            return false;
        }

        console.log('✅ Barbero validado');

        if (!dateInput.value) {
            console.error('❌ Validación falló: No hay fecha seleccionada');
            showNotification('Por favor selecciona una fecha', 'warning');
            dateInput.classList.add('is-invalid');
            return false;
        }

        console.log('✅ Fecha validada:', dateInput.value);

        if (!selectedTime || !selectedTime.value) {
            console.error('❌ Validación falló: No hay hora seleccionada');
            console.error('  - selectedTime element:', selectedTime);
            console.error('  - selectedTime.value:', selectedTime?.value);
            console.error('  - App.reserva.time:', window.App?.reserva?.time);
            showNotification('Por favor selecciona una hora', 'warning');
            return false;
        }

        console.log('✅ Hora validada:', selectedTime.value);
        console.log('✅ Step 3 validado completamente');

        dateInput.classList.remove('is-invalid');
        dateInput.classList.add('is-valid');
        
        // Actualizar formData
        formData.barber = selectedBarberInput?.value || window.App.reserva.barber_id;
        formData.date = dateInput.value;
        formData.time = selectedTime.value;
        
        return true;
    }

    /**
     * Update step display
     */
    function updateStepDisplay() {
        // Update step content
        steps.forEach((step, index) => {
            if (index + 1 === currentStep) {
                step.classList.add('appointment-step--active');
            } else {
                step.classList.remove('appointment-step--active');
            }
        });

        // Update stepper
        stepperItems.forEach((item, index) => {
            const stepNumber = index + 1;
            
            if (stepNumber < currentStep) {
                item.classList.add('stepper-item--completed');
                item.classList.remove('stepper-item--active');
            } else if (stepNumber === currentStep) {
                item.classList.add('stepper-item--active');
                item.classList.remove('stepper-item--completed');
            } else {
                item.classList.remove('stepper-item--active', 'stepper-item--completed');
            }
        });

        // Update stepper lines
        stepperLines.forEach((line, index) => {
            if (index < currentStep - 1) {
                line.classList.add('stepper-line--completed');
            } else {
                line.classList.remove('stepper-line--completed');
            }
        });

        // Update step header text
        updateStepHeaderText();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Update step header text in navigation
     */
    function updateStepHeaderText() {
        const stepTitle = document.getElementById('stepTitle');
        const stepDescription = document.getElementById('stepDescription');
        
        const stepTexts = {
            1: {
                title: 'Busca y compará',
                description: 'Elige donde deseas tu cita'
            },
            2: {
                title: 'Selecciona tu Servicio',
                description: 'Elige el servicio que deseas reservar'
            },
            3: {
                title: 'Barbero, Fecha y Hora',
                description: 'Selecciona tu barbero preferido y horario'
            },
            4: {
                title: 'Confirma tu Cita',
                description: 'Revisa los detalles antes de confirmar'
            }
        };

        if (stepTitle && stepDescription && stepTexts[currentStep]) {
            stepTitle.textContent = stepTexts[currentStep].title;
            stepDescription.textContent = stepTexts[currentStep].description;
        }
    }

    /**
     * Update navigation buttons
     */
    function updateNavigationButtons() {
        // Previous button
        if (currentStep === 1) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'flex';
        }

        // Next and Submit buttons
        if (currentStep === totalSteps) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'flex';
        } else {
            nextBtn.style.display = 'flex';
            submitBtn.style.display = 'none';
        }
    }

    /**
     * Handle establishment selection
     */
    function handleEstablishmentSelection(event) {
        formData.establishment = event.target.value;
    }

    /**
     * Handle service selection
     */
    function handleServiceSelection(event) {
        formData.service = event.target.value;
    }

    /**
     * Handle barber selection
     */
    function handleBarberSelection(event) {
        formData.barber = event.target.value;
        // Regenerate time slots based on selected barber
        generateTimeSlots();
    }

    /**
     * Handle date selection
     */
    function handleDateSelection(event) {
        formData.date = event.target.value;
        generateTimeSlots();
    }

    /**
     * Set minimum date for appointment
     */
    function setMinDate() {
        const dateInput = document.getElementById('appointmentDate');
        if (!dateInput) return;

        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const minDate = tomorrow.toISOString().split('T')[0];
        dateInput.setAttribute('min', minDate);
    }

    /**
     * Generate available time slots
     */
    function generateTimeSlots() {
        const timeSlotsContainer = document.getElementById('timeSlots');
        if (!timeSlotsContainer) return;

        timeSlotsContainer.innerHTML = '';

        // Generate time slots from 9 AM to 7 PM
        const startHour = 9;
        const endHour = 19;
        const interval = 30; // 30 minutes

        for (let hour = startHour; hour < endHour; hour++) {
            for (let minute = 0; minute < 60; minute += interval) {
                const timeString = formatTime(hour, minute);
                const timeSlot = createTimeSlot(timeString);
                timeSlotsContainer.appendChild(timeSlot);
            }
        }
    }

    /**
     * Create a time slot button
     */
    function createTimeSlot(time) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'time-slot';
        button.textContent = time;
        
        // Randomly disable some slots for demo (replace with real availability check)
        if (Math.random() > 0.7) {
            button.classList.add('time-slot--disabled');
            button.disabled = true;
        } else {
            button.addEventListener('click', function() {
                selectTimeSlot(this, time);
            });
        }

        return button;
    }

    /**
     * Select a time slot
     */
    function selectTimeSlot(element, time) {
        // Remove selection from all slots
        const allSlots = document.querySelectorAll('.time-slot');
        allSlots.forEach(slot => slot.classList.remove('time-slot--selected'));

        // Add selection to clicked slot
        element.classList.add('time-slot--selected');

        // Update hidden input
        const selectedTimeInput = document.getElementById('selectedTime');
        if (selectedTimeInput) {
            selectedTimeInput.value = time;
        }

        formData.time = time;
    }

    /**
     * Format time to 12-hour format
     */
    function formatTime(hour, minute) {
        const period = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
        const displayMinute = minute.toString().padStart(2, '0');
        return `${displayHour}:${displayMinute} ${period}`;
    }

    /**
     * Update summary in confirmation step
     */
    function updateSummary() {
        // Usar datos de window.App.reserva que tiene toda la información
        const reserva = window.App.reserva;
        
        // Establishment
        const establishmentName = reserva.establishment_name || 'N/A';
        document.getElementById('summaryEstablishment').textContent = establishmentName;

        // Service
        const serviceName = reserva.service_name || 'N/A';
        document.getElementById('summaryService').textContent = serviceName;

        // Barber
        const barberName = reserva.barber_name || 'N/A';
        document.getElementById('summaryBarber').textContent = barberName;

        // Date
        const formattedDate = formatDate(reserva.date);
        document.getElementById('summaryDate').textContent = formattedDate;

        // Time
        document.getElementById('summaryTime').textContent = reserva.time || '-';
    }

    /**
     * Format date to readable format
     */
    function formatDate(dateString) {
        if (!dateString) return '-';

        const date = new Date(dateString + 'T00:00:00');
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('es-ES', options);
    }

    /**
     * Handle form submission
     */
    function handleFormSubmit(event) {
        event.preventDefault();

        if (!validateCurrentStep()) {
            return;
        }

        // Validar que tengamos todos los datos en App.reserva
        const validation = window.App.reserva.validate();
        if (!validation.valid) {
            showNotification(validation.errors.join('\n'), 'warning');
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';

        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Obtener datos desde App.reserva
        const appointmentData = window.App.reserva.getSubmitData();

        // Submit via AJAX to API endpoint
        fetch('/services_module/api/appointments/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(appointmentData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar voucher con los datos de la cita
                showAppointmentVoucher(data.appointment);
                
                // Reset form
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check-circle"></i><span>Confirmar Cita</span>';
            } else {
                showNotification(data.error || 'Error al confirmar la cita', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check-circle"></i><span>Confirmar Cita</span>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error al procesar la solicitud. Por favor intenta nuevamente.', 'danger');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check-circle"></i><span>Confirmar Cita</span>';
        });
    }

    /**
     * Show notification
     */
    function showNotification(message, type = 'info') {
        // Check if Bootstrap toast container exists
        let toastContainer = document.querySelector('.toast-container');
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toastId = 'toast-' + Date.now();
        const bgColor = {
            'success': 'bg-success',
            'danger': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info'
        }[type] || 'bg-info';

        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgColor} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });

        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    /**
     * Show appointment voucher modal
     * @param {Object} appointment - Datos de la cita creada
     */
    function showAppointmentVoucher(appointment) {
        // Crear modal del voucher
        const voucherModal = createVoucherModal(appointment);
        document.body.appendChild(voucherModal);
        
        // Mostrar modal usando Bootstrap
        const modal = new bootstrap.Modal(voucherModal);
        modal.show();
        
        // Limpiar modal al cerrar
        voucherModal.addEventListener('hidden.bs.modal', function() {
            voucherModal.remove();
        });
    }

    /**
     * Create voucher modal HTML
     * @param {Object} appointment - Appointment data
     * @returns {HTMLElement} - Modal element
     */
    function createVoucherModal(appointment) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'voucherModal';
        modal.tabIndex = -1;
        
        const currentDate = new Date().toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="bi bi-check-circle-fill me-2"></i>
                            ¡Cita Confirmada Exitosamente!
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    
                    <div class="modal-body p-0">
                        <!-- Voucher Container -->
                        <div id="appointment-voucher" class="voucher-container">
                            <!-- Header del Voucher -->
                            <div class="voucher-header">
                                <div class="voucher-logo">
                                    <i class="bi bi-scissors"></i>
                                    <h3>BarberB</h3>
                                </div>
                                <div class="voucher-number">
                                    <small>Código de Cita</small>
                                    <strong>#${String(appointment.id).padStart(6, '0')}</strong>
                                </div>
                            </div>
                            
                            <!-- Información del Establecimiento -->
                            <div class="voucher-section">
                                <div class="voucher-section-title">
                                    <i class="bi bi-shop"></i>
                                    <span>Establecimiento</span>
                                </div>
                                <div class="voucher-info">
                                    <h4>${appointment.establishment}</h4>
                                    <p class="text-muted mb-0">${window.App.reserva.establishment_address || ''}</p>
                                </div>
                            </div>
                            
                            <!-- Detalles de la Cita -->
                            <div class="voucher-section">
                                <div class="voucher-section-title">
                                    <i class="bi bi-calendar-check"></i>
                                    <span>Detalles de la Cita</span>
                                </div>
                                <div class="voucher-details">
                                    <div class="detail-row">
                                        <span class="detail-label">
                                            <i class="bi bi-scissors"></i> Servicio
                                        </span>
                                        <span class="detail-value">${appointment.service}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-label">
                                            <i class="bi bi-person-badge"></i> Barbero
                                        </span>
                                        <span class="detail-value">${appointment.barber}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-label">
                                            <i class="bi bi-calendar3"></i> Fecha
                                        </span>
                                        <span class="detail-value">${formatDate(appointment.date)}</span>
                                    </div>
                                    <div class="detail-row">
                                        <span class="detail-label">
                                            <i class="bi bi-clock"></i> Hora
                                        </span>
                                        <span class="detail-value">${appointment.time}</span>
                                    </div>
                                    <div class="detail-row detail-total">
                                        <span class="detail-label">
                                            <i class="bi bi-cash-coin"></i> Total a Pagar
                                        </span>
                                        <span class="detail-value">${formatCurrency(appointment.price_total)}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Estado -->
                            <div class="voucher-status">
                                <span class="status-badge status-confirmed">
                                    <i class="bi bi-check-circle"></i>
                                    ${appointment.status}
                                </span>
                            </div>
                            
                            <!-- Footer -->
                            <div class="voucher-footer">
                                <p class="mb-2">
                                    <i class="bi bi-info-circle"></i>
                                    Por favor llega 5 minutos antes de tu cita
                                </p>
                                <small class="text-muted">Confirmado el ${currentDate}</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle"></i> Cerrar
                        </button>
                        <button type="button" class="btn btn-primary" onclick="printVoucher()">
                            <i class="bi bi-printer"></i> Imprimir
                        </button>
                        <button type="button" class="btn btn-success" onclick="downloadVoucherPDF()">
                            <i class="bi bi-download"></i> Descargar PDF
                        </button>
                        <!-- Preparado para futuro: Enviar por correo -->
                        <button type="button" class="btn btn-info d-none" id="sendEmailBtn" onclick="sendVoucherByEmail(${appointment.id})">
                            <i class="bi bi-envelope"></i> Enviar por Correo
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    /**
     * Format date to Spanish locale
     */
    function formatDate(dateStr) {
        const date = new Date(dateStr + 'T00:00:00');
        return date.toLocaleDateString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    /**
     * Format currency
     */
    function formatCurrency(amount) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(amount);
    }

    /**
     * Print voucher
     */
    window.printVoucher = function() {
        const voucherContent = document.getElementById('appointment-voucher').innerHTML;
        const printWindow = window.open('', '', 'height=600,width=800');
        
        printWindow.document.write(`
            <html>
                <head>
                    <title>Voucher de Cita - BarberB</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
                    <style>${getVoucherStyles()}</style>
                </head>
                <body>
                    ${voucherContent}
                    <script>
                        window.onload = function() {
                            window.print();
                            window.onafterprint = function() { window.close(); };
                        };
                    </script>
                </body>
            </html>
        `);
        
        printWindow.document.close();
    };

    /**
     * Download voucher as PDF (preparado para futuro)
     */
    window.downloadVoucherPDF = function() {
        alert('Funcionalidad de descarga PDF en desarrollo. Por ahora usa Imprimir > Guardar como PDF.');
    };

    /**
     * Send voucher by email (preparado para integración futura)
     * @param {number} appointmentId - ID de la cita
     */
    window.sendVoucherByEmail = function(appointmentId) {
        // TODO: Implementar endpoint backend /api/appointments/{id}/send-email/
        alert('Funcionalidad de envío por correo será implementada próximamente.');
    };

    /**
     * Get voucher CSS styles
     */
    function getVoucherStyles() {
        return `
            body { margin: 20px; }
            .voucher-container { max-width: 800px; margin: 0 auto; padding: 40px; font-family: 'Segoe UI', sans-serif; }
            .voucher-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 30px; border-bottom: 3px solid #3e1a4e; margin-bottom: 30px; }
            .voucher-logo { display: flex; align-items: center; gap: 15px; }
            .voucher-logo i { font-size: 3rem; color: #3e1a4e; }
            .voucher-logo h3 { font-size: 2rem; font-weight: 700; color: #3e1a4e; margin: 0; }
            .voucher-number { text-align: right; }
            .voucher-number small { display: block; color: #6c757d; font-size: 0.875rem; }
            .voucher-number strong { font-size: 1.5rem; color: #3e1a4e; }
            .voucher-section { margin-bottom: 30px; }
            .voucher-section-title { display: flex; align-items: center; gap: 10px; font-size: 1.25rem; font-weight: 600; color: #3e1a4e; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e9ecef; }
            .voucher-section-title i { font-size: 1.5rem; }
            .voucher-info h4 { font-size: 1.5rem; font-weight: 600; color: #212529; margin-bottom: 5px; }
            .voucher-details { background: #f8f9fa; border-radius: 10px; padding: 20px; }
            .detail-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #dee2e6; }
            .detail-row:last-child { border-bottom: none; }
            .detail-label { font-weight: 500; color: #6c757d; display: flex; align-items: center; gap: 8px; }
            .detail-value { font-weight: 600; color: #212529; font-size: 1.1rem; }
            .detail-total { margin-top: 15px; padding-top: 20px; border-top: 2px solid #3e1a4e !important; }
            .detail-total .detail-value { color: #28a745; font-size: 1.5rem; }
            .voucher-status { text-align: center; margin: 30px 0; }
            .status-badge { display: inline-flex; align-items: center; gap: 8px; padding: 12px 30px; border-radius: 50px; font-weight: 600; font-size: 1.1rem; }
            .status-confirmed { background: #d4edda; color: #155724; border: 2px solid #28a745; }
            .voucher-footer { text-align: center; padding-top: 30px; border-top: 2px dashed #dee2e6; color: #6c757d; }
            @media print { .voucher-container { padding: 20px; } }
        `;
    }

})();
