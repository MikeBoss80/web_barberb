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
        const selectedBarber = document.querySelector('input[name="barber"]:checked');
        const dateInput = document.getElementById('appointmentDate');
        const selectedTime = document.getElementById('selectedTime');

        if (!selectedBarber) {
            showNotification('Por favor selecciona un barbero', 'warning');
            return false;
        }

        if (!dateInput.value) {
            showNotification('Por favor selecciona una fecha', 'warning');
            dateInput.classList.add('is-invalid');
            return false;
        }

        if (!selectedTime.value) {
            showNotification('Por favor selecciona una hora', 'warning');
            return false;
        }

        dateInput.classList.remove('is-invalid');
        dateInput.classList.add('is-valid');
        formData.barber = selectedBarber.value;
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
        // Establishment
        const establishmentName = establishmentData[formData.establishment]?.name || formData.establishment;
        document.getElementById('summaryEstablishment').textContent = establishmentName;

        // Service
        const serviceName = serviceData[formData.service]?.name || formData.service;
        document.getElementById('summaryService').textContent = serviceName;

        // Barber
        const barberName = barberData[formData.barber]?.name || formData.barber;
        document.getElementById('summaryBarber').textContent = barberName;

        // Date
        const formattedDate = formatDate(formData.date);
        document.getElementById('summaryDate').textContent = formattedDate;

        // Time
        document.getElementById('summaryTime').textContent = formData.time || '-';
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

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';

        // Simulate form submission (replace with actual AJAX call)
        setTimeout(() => {
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Prepare form data
            const formDataToSend = new FormData();
            formDataToSend.append('establishment', formData.establishment);
            formDataToSend.append('service', formData.service);
            formDataToSend.append('barber', formData.barber);
            formDataToSend.append('date', formData.date);
            formDataToSend.append('time', formData.time);
            formDataToSend.append('csrfmiddlewaretoken', csrfToken);

            // Submit form via AJAX
            fetch(form.action, {
                method: 'POST',
                body: formDataToSend,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('¡Cita confirmada exitosamente!', 'success');
                    // Redirect or reset form
                    setTimeout(() => {
                        window.location.href = data.redirect || '/';
                    }, 2000);
                } else {
                    showNotification(data.message || 'Error al confirmar la cita', 'danger');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-check-circle"></i><span>Confirmar Cita</span>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error al procesar la solicitud', 'danger');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check-circle"></i><span>Confirmar Cita</span>';
            });
        }, 1000);
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

})();
