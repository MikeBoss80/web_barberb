// JS para configuración de slots en establecimiento
// Versión corregida y funcional usando FormData y credenciales

(function() {
    function getEstablishmentId() {
        return window.selectedEstablishmentId || document.getElementById('selectEstablecimiento')?.value;
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showAlert(message, type = 'success') {
        if (window.mostrarAlerta) {
            window.mostrarAlerta(type, message);
        } else {
            const alert = document.getElementById('configAlert');
            if (alert) {
                alert.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
                setTimeout(() => alert.innerHTML = '', 3000);
            }
        }
    }

    // Función principal para inicializar componentes del tab configuración
    window.initializeConfigComponents = function() {
        console.log('🔧 Inicializando componentes de configuración...');

        const form = document.getElementById('configForm');
        if (!form) {
            console.error('❌ No se encontró el formulario #configForm');
            return;
        }
        
        console.log('✅ Formulario de configuración encontrado');

        // Configurar event listener para el formulario
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('🚀 SUBMIT CAPTURADO - Guardando configuración...');

            const establishmentId = getEstablishmentId();
            console.log('🏢 Establishment ID:', establishmentId);
            
            if (!establishmentId) {
                console.error('❌ No hay establecimiento seleccionado');
                showAlert('Debes seleccionar un establecimiento', 'danger');
                return;
            }

            const formData = new FormData(form);
            formData.append('establishment_id', establishmentId);

            console.log('📤 Enviando a URL:', window.configSaveUrl);

            fetch(window.configSaveUrl, {
                method: 'POST',
                body: formData,
                credentials: 'include',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('📨 Respuesta HTTP:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('📄 Data recibida:', data);
                if (data.success) {
                    showAlert('<i class="fas fa-check"></i> ' + data.message, 'success');
                } else {
                    showAlert('<i class="fas fa-exclamation-triangle"></i> ' + data.message, 'danger');
                }
            })
            .catch(err => {
                console.error('💥 Error en fetch:', err);
                showAlert('<i class="fas fa-exclamation-triangle"></i> Error al guardar: ' + err.message, 'danger');
            });
        });

        // Configurar el selector de establecimiento
        const selectEst = document.getElementById('selectEstablecimiento');
        if (selectEst) {
            selectEst.addEventListener('change', function() {
                window.selectedEstablishmentId = this.value;
                console.log('🏢 Establecimiento seleccionado:', this.value);
                if (this.value && window.cargarConfiguracion) {
                    cargarConfiguracion(this.value);
                }
            });
        }

        // Auto-seleccionar si solo hay uno
        if (window.selectedEstablishmentId) {
            console.log('🏢 Auto-seleccionado establecimiento ID:', window.selectedEstablishmentId);
            cargarConfiguracion(window.selectedEstablishmentId);
        }

        console.log('✅ Componentes de configuración inicializados correctamente');
    };

    // Función para cargar configuración existente
    function cargarConfiguracion(establishmentId) {
        if (!window.configLoadUrl || !establishmentId) return;

        const url = window.configLoadUrl.replace('0', establishmentId);
        
        console.log('📥 Cargando configuración desde:', url);
        
        fetch(url, {
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.log('ℹ️ No hay configuración existente, usando valores por defecto');
                return;
            }

            const config = data.data;
            console.log('📋 Cargando configuración:', config);

            // Cargar horarios
            const setInput = (name, value) => {
                const input = document.querySelector(`input[name="${name}"]`);
                if (input && value) input.value = value;
            };

            setInput('lunes_inicio', config.monday_open);
            setInput('lunes_fin', config.monday_close);
            setInput('martes_inicio', config.tuesday_open);
            setInput('martes_fin', config.tuesday_close);
            setInput('miercoles_inicio', config.wednesday_open);
            setInput('miercoles_fin', config.wednesday_close);
            setInput('jueves_inicio', config.thursday_open);
            setInput('jueves_fin', config.thursday_close);
            setInput('viernes_inicio', config.friday_open);
            setInput('viernes_fin', config.friday_close);
            setInput('sabado_inicio', config.saturday_open);
            setInput('sabado_fin', config.saturday_close);
            setInput('domingo_inicio', config.sunday_open);
            setInput('domingo_fin', config.sunday_close);

            // Cargar configuración de slots
            const setSelect = (name, value) => {
                const select = document.querySelector(`select[name="${name}"]`);
                if (select && value) select.value = value;
            };

            setSelect('duracion_slot', config.slot_duration_minutes);
            setSelect('tiempo_descanso', config.break_duration_minutes);
            setSelect('horas_recordatorio', config.reminder_hours_before);

            const diasInput = document.querySelector('input[name="dias_anticipacion"]');
            if (diasInput && config.advance_booking_days) {
                diasInput.value = config.advance_booking_days;
            }

            // Cargar checkboxes
            const setCheckbox = (name, value) => {
                const checkbox = document.querySelector(`input[name="${name}"]`);
                if (checkbox) checkbox.checked = value !== false;
            };

            setCheckbox('permitir_mismo_dia', config.allow_same_day_booking);
            setCheckbox('enviar_confirmacion', config.send_confirmation_email);
            setCheckbox('enviar_recordatorio', config.send_reminder_email);
            setCheckbox('enviar_cancelacion', config.send_cancellation_email);

            console.log('✅ Configuración cargada en el formulario');
        })
        .catch(err => {
            console.error('❌ Error cargando configuración:', err);
        });
    }

    // Exportar función para uso externo
    window.cargarConfiguracion = cargarConfiguracion;

    // Mantener compatibilidad con versión anterior (deprecado)
    window.initConfigEstablishment = function() {
        console.warn('⚠️ initConfigEstablishment está deprecado, usar initializeConfigComponents');
        window.initializeConfigComponents();
    };
})();
