// JS para configuración de slots en establecimiento
// Versión corregida y funcional usando FormData y credenciales

console.log('🔌 Archivo configuration.js cargado correctamente');

(function() {
    console.log('🚀 Ejecutando IIFE de configuration.js');
    
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

    console.log('🎯 Definiendo window.initializeConfigComponents...');
    
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
            console.log('📋 Datos del formulario:');
            for (let [key, value] of formData.entries()) {
                console.log(`  ${key}: ${value}`);
            }

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
                    // Intentar obtener el error del servidor
                    return response.text().then(text => {
                        console.log('❌ Respuesta de error del servidor:', text);
                        throw new Error(`HTTP ${response.status}: ${text}`);
                    });
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
            // ⚠️ IMPORTANTE: Cargar configuración automáticamente
            setTimeout(() => {
                console.log('⏱️ Cargando configuración automáticamente después de 500ms...');
                cargarConfiguracion(window.selectedEstablishmentId);
            }, 500);
        }

        console.log('✅ Componentes de configuración inicializados correctamente');
    };

    // Función para cargar configuración existente
    function cargarConfiguracion(establishmentId) {
        if (!window.configLoadUrl || !establishmentId) {
            console.warn('⚠️ No se puede cargar configuración: URL o ID faltante', {
                url: window.configLoadUrl,
                id: establishmentId
            });
            return;
        }

        const url = window.configLoadUrl.replace('0', establishmentId);
        
        console.log('📥 Cargando configuración desde:', url);
        console.log('🔍 Establishment ID usado:', establishmentId);
        
        fetch(url, {
            credentials: 'include',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            console.log('📨 Respuesta HTTP de carga:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos de configuración recibidos:', data);
            
            if (!data.success) {
                console.log('ℹ️ No hay configuración existente, manteniendo valores por defecto');
                console.log('💬 Mensaje del servidor:', data.message);
                return;
            }

            const config = data.data;
            console.log('📋 Aplicando configuración:', config);

            // Cargar configuración de slots
            const setSelect = (name, value) => {
                const select = document.querySelector(`select[name="${name}"]`);
                if (select && value) select.value = value;
            };

            setSelect('duracion_slot', config.duracion_slot || 30);
            setSelect('tiempo_descanso', config.tiempo_descanso || 5);
            setSelect('dias_anticipacion', config.dias_anticipacion || 30);
            setSelect('horas_recordatorio', config.horas_recordatorio || 24);

            // Cargar checkboxes
            const setCheckbox = (name, value) => {
                const checkbox = document.querySelector(`input[name="${name}"]`);
                if (checkbox) checkbox.checked = value !== false;
            };

            setCheckbox('permitir_mismo_dia', config.permitir_mismo_dia);
            setCheckbox('enviar_confirmacion', config.enviar_confirmacion);
            setCheckbox('enviar_recordatorio', config.enviar_recordatorio);
            setCheckbox('enviar_cancelacion', config.enviar_cancelacion);

            // ============================================================================
            // CARGAR HORARIOS POR DÍA
            // ============================================================================
            
            const days = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
            console.log('📅 Iniciando carga de horarios...');
            
            days.forEach(day => {
                console.log(`🔍 Procesando día: ${day}`);
                
                // Cargar horarios de inicio y fin
                const inicioInput = document.querySelector(`input[name="${day}_inicio"]`);
                const finInput = document.querySelector(`input[name="${day}_fin"]`);
                
                console.log(`📝 Inputs encontrados para ${day}:`, {
                    inicio: !!inicioInput,
                    fin: !!finInput,
                    inicioName: inicioInput?.name,
                    finName: finInput?.name
                });
                
                // Mapear nombres con acentos a nombres sin acentos para config data
                const dayMap = {
                    'lunes': 'lunes',
                    'martes': 'martes', 
                    'miércoles': 'miercoles',
                    'jueves': 'jueves',
                    'viernes': 'viernes',
                    'sábado': 'sabado',
                    'domingo': 'domingo'
                };
                
                const configDay = dayMap[day];
                console.log(`🗂️ Mapeando ${day} → ${configDay}`);
                
                if (inicioInput && config[`${configDay}_inicio`]) {
                    const valorAnterior = inicioInput.value;
                    inicioInput.value = config[`${configDay}_inicio`];
                    console.log(`⏰ ${day} inicio: ${valorAnterior} → ${config[`${configDay}_inicio`]}`);
                }
                
                if (finInput && config[`${configDay}_fin`]) {
                    const valorAnterior = finInput.value;
                    finInput.value = config[`${configDay}_fin`];
                    console.log(`⏰ ${day} fin: ${valorAnterior} → ${config[`${configDay}_fin`]}`);
                }
                
                // Si hay checkbox para día activo/inactivo (futuro)
                const activoCheckbox = document.querySelector(`input[name="${day}_activo"]`);
                if (activoCheckbox && config[`${configDay}_activo`] !== undefined) {
                    activoCheckbox.checked = config[`${configDay}_activo`];
                    console.log(`✅ ${day} activo: ${config[`${configDay}_activo`]}`);
                }
            });

            console.log('✅ Configuración y horarios cargados en el formulario');
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
    
    console.log('✅ Funciones de configuración definidas globalmente');
})();

// Verificar inmediatamente que la función está disponible
console.log('🔍 Verificando función:', typeof window.initializeConfigComponents);