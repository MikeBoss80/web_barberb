// Función para inicializar componentes del módulo de gestión
function initializeManagementComponents() {
    $('#tablaEstablecimientos').DataTable({
        language: {
            url: 'https://cdn.datatables.net/plug-ins/2.3.2/i18n/es-ES.json'
        },
        dom: '<"d-flex justify-content-between mb-2"fB>rt<"d-flex justify-content-between mt-2"lip>',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        pageLength: 10,
    });

    // Configurar CSRF token para todas las peticiones AJAX
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
            }
        }
    });

    // Manejar el envío del formulario de nuevo establecimiento
    $('#form-modal-est').on('submit', function (e) {
        // Prevenir el envío normal del formulario
        e.preventDefault();

        // Mostrar indicador de carga
        $('#submit-spinner').removeClass('d-none');
        $('#submit-text').text('Guardando...');

        // Obtener todos los datos del formulario
        const formData = new FormData(this);

        // Log para depuración
        console.log('Enviando datos del formulario:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }

        // Realizar la petición AJAX
        $.ajax({
            url: $(this).attr('action'),
            method: 'POST',
            data: formData,
            processData: false,  // Necesario para FormData
            contentType: false,  // Necesario para FormData
            success: function (response) {
                if (response.success) {
                    // Mostrar mensaje de éxito
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: 'Establecimiento creado correctamente',
                        showConfirmButton: true
                    }).then((result) => {
                        // Recargar la página para mostrar el nuevo establecimiento
                        window.location.reload();
                    });
                } else {
                    // Mostrar errores si hay
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: response.message || 'Hubo un error al guardar el establecimiento'
                    });
                }
            },
            error: async function (xhr, status, error) {
                console.error('Error en la petición:', error);

                // Limpiar errores anteriores
                $('.invalid-feedback').empty();
                $('.is-invalid').removeClass('is-invalid');

                if (xhr.status === 400) {
                    try {
                        const data = await xhr.responseJSON;
                        console.error("Errores de validación:", data);

                        // Mostrar los errores de validación
                        if (data.errors) {
                            Object.entries(data.errors).forEach(([field, messages]) => {
                                const errorDiv = $(`#error-${field}`);
                                const input = $(`#id_${field}`);
                                if (errorDiv.length) {
                                    errorDiv.text(Array.isArray(messages) ? messages.join(' ') : messages);
                                    input.addClass('is-invalid');
                                }
                            });
                        }

                        // Mostrar errores no asociados a campos específicos
                        if (data.non_field_errors && data.non_field_errors.length > 0) {
                            $('#modal-nonfield-errors')
                                .removeClass('d-none')
                                .text(data.non_field_errors.join(' '));
                        }

                        // Mostrar mensaje general de error
                        Swal.fire({
                            icon: 'warning',
                            title: 'Validación',
                            text: data.message || 'Por favor corrige los errores en el formulario'
                        });
                    } catch (jsonError) {
                        console.error('Error al procesar la respuesta JSON:', jsonError);
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error al procesar la respuesta del servidor'
                        });
                    }
                } else {
                    // Errores del servidor (500, etc.)
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: xhr.responseJSON?.message || 'Hubo un error al procesar la solicitud'
                    });
                }
            },

            complete: function () {
                // Restaurar el botón de envío
                $('#submit-spinner').addClass('d-none');
                $('#submit-text').text('Guardar');
            }
        });
    });

    $('.btnActualizarEst').on('click', function () {
        // Llenar los campos del formulario
        $('#establishment_id').val($(this).data('id'));
        $('#inputNombre').val($(this).data('nombre'));
        $('#inputDireccionUpd').val($(this).data('direccion'));
        $('#inputCiudadUpd').val($(this).data('ciudad'));
        $('#inputPaisUpd').val($(this).data('pais'));
        $('#inputTelefono').val($(this).data('telefono'));
        $('#inputCorreo').val($(this).data('email'));
        $('#inputDescripcion').val($(this).data('descripcion'));
        $('#inputLatUpd').val(formatCoordinate($(this).data('lat')));
        $('#inputLngUpd').val(formatCoordinate($(this).data('lng')));

        $('#formUpdateEstablishment').attr('action', `./management/update/${$(this).data('id')}/`);
    });

    $('.btnDelEstablishment').on('click', function () {
        $('#labelEstName').text($(this).data('name'));
        $('#formEliminarEst').attr('action', `./management/delete/${$(this).data('id')}/`);
    });

    //Variables globales para mantener el estado del formulario que se abre
    let isMapApiLoaded = false;
    let modalGlobal;
    let currentInputAddress, currentInputLat, currentInputLng, currentInputCity, currentInputCountry;
    const modalIds = ['addEstablishmentModal', 'updEstablishmentModal'];

    function initializeFormVariables(modal) {
        currentInputAddress = modal.querySelector('.inputDireccion').id;
        currentInputCity = modal.querySelector('.inputCity').id;
        currentInputCountry = modal.querySelector('.inputCountry').id;
        currentInputLat = modal.querySelector('.inputLat').id;
        currentInputLng = modal.querySelector('.inputLng').id;
    }

    function formatCoordinate(value) {
        if (!value) return '';
        const numValue = parseFloat(value.toString().replace(',', '.'));
        return isNaN(numValue) ? '' : numValue.toFixed(6);
    }

    function parseCoordinate(value, defaultValue = 0) {
        if (!value) return defaultValue;
        const numValue = parseFloat(value.toString().replace(',', '.'));
        return isNaN(numValue) ? defaultValue : numValue;
    }

    modalIds.forEach(modalId => {
        const modalMap = document.getElementById(modalId);
        if (modalMap) {
            // Agregar listeners para formateo automático de coordenadas
            modalMap.addEventListener('shown.bs.modal', () => {
                // Formatear campos de coordenadas cuando pierdan el foco
                const latInput = modalMap.querySelector('.inputLat');
                const lngInput = modalMap.querySelector('.inputLng');
                
                if (latInput) {
                    latInput.addEventListener('blur', function() {
                        this.value = formatCoordinate(this.value);
                    });
                }
                
                if (lngInput) {
                    lngInput.addEventListener('blur', function() {
                        this.value = formatCoordinate(this.value);
                    });
                }
            });

            modalMap.addEventListener('shown.bs.modal', () => {
                modalGlobal = modalMap; //Aqui se asgina el modal actual a la variable global
                initializeFormVariables(modalGlobal);
                //Si los recursos del mapa ya se cargaron, solo iniciamos el mapa
                if (isMapApiLoaded) {
                    initMap();
                } else {
                    isMapApiLoaded = true;
                    fetch('http://127.0.0.1:8000/services_module/getmap/')
                        .then(response => {
                            if (response.ok) {
                                response.json().then(data => {
                                    (g => {
                                        var h, a, k, p = "The Google Maps JavaScript API",
                                            c = "google", l = "importLibrary", q = "__ib__",
                                            m = document, b = window;
                                        b = b[c] || (b[c] = {});
                                        var d = b.maps || (b.maps = {}),
                                            r = new Set, e = new URLSearchParams,
                                            u = () => h || (h = new Promise(async (f, n) => {
                                                await (a = m.createElement("script"));
                                                e.set("libraries", [...r] + "");
                                                for (k in g) e.set(k.replace(/[A-Z]/g, t => "_" + t[0].toLowerCase()), g[k]);
                                                e.set("callback", c + ".maps." + q);
                                                a.src = `https://maps.${c}apis.com/maps/api/js?` + e;
                                                d[q] = f;
                                                a.onerror = () => h = n(Error(p + " could not load."));
                                                a.nonce = m.querySelector("script[nonce]")?.nonce || "";
                                                m.head.append(a)
                                            }));
                                        d[l] ? console.warn(p + " only loads once. Ignoring:", g) : d[l] = (f, ...n) => r.add(f) && u().then(() => d[l](f, ...n))
                                    })({
                                        key: data.mapApiKey,
                                        v: "weekly"
                                    });
                                    initMap();
                                });
                            }
                        });
                } 
            });
        }
    });

    let map;
    let marker;
    let autocomplete;

    async function initMap() {
        const { Map } = await google.maps.importLibrary("maps");
        const { Autocomplete, Place } = await google.maps.importLibrary("places");
        const { Geocoder } = await google.maps.importLibrary("geocoding");

        // Obtener las coordenadas iniciales (desde los campos ocultos si existen)
        let initialLatValue = document.getElementById(currentInputLat).value || '4.628886';
        let initialLngValue = document.getElementById(currentInputLng).value || '-74.146605';
        let initialLat = parseCoordinate(initialLatValue, 4.628886);
        let initialLng = parseCoordinate(initialLngValue, -74.146605);
        const defaultLocation = { lat: parseFloat(initialLat), lng: parseFloat(initialLng) };

        // Inicializar el mapa
        map = new Map(document.getElementById(modalGlobal.querySelector(".map").id), {
            center: defaultLocation,
            zoom: 15,
            mapTypeControl: true,
            streetViewControl: true,
            fullscreenControl: true
        });

        // Crear el marcador inicial
        marker = new google.maps.Marker({
            position: defaultLocation,
            map: map,
            draggable: true, // Permite arrastrar el marcador
            animation: google.maps.Animation.DROP // Animación al crear el marcador
        });

        // Inicializar el autocompletado
        autocomplete = new Autocomplete(
            document.getElementById(currentInputAddress),
            {
                types: ['address', 'establishment'],
                componentRestrictions: { country: 'CO' },
                fields: ['address_components', 'formatted_address', 'geometry', 'name', 'place_id']
            }
        );

        // Vincular el autocompletado al mapa
        autocomplete.bindTo('bounds', map);

        // Manejar la selección de un lugar
        autocomplete.addListener('place_changed', function () {
            const place = autocomplete.getPlace();

            if (!place.geometry) {
                console.log("No se encontró información del lugar seleccionado");
                return;
            }

            // Actualizar el mapa y los campos
            updateMapAndFields(place);
        });

        // Configurar los listeners del marcador y mapa
        setupMarkerListeners();
    }

    function updateMapAndFields(place) {
        if (!place || !place.geometry) {
            console.log('No hay información de lugar disponible');
            return;
        }

        const location = place.geometry.location;
        map.setCenter(location);
        map.setZoom(17);
        marker.setPosition(location);

        let address = '';
        let city = '';
        let country = '';

        // Procesar componentes de dirección si están disponibles
        if (place.address_components) {
            // Crear un mapa para los componentes de dirección
            const addressMap = {};
            place.address_components.forEach(component => {
                const type = component.types[0];
                addressMap[type] = component.long_name;
            });

            // Construir la dirección
            const streetNumber = addressMap['street_number'] || '';
            const route = addressMap['route'] || '';
            address = route + (streetNumber ? ' ' + streetNumber : '');

            // Obtener ciudad (intentar diferentes niveles administrativos)
            city = addressMap['locality'] ||
                addressMap['administrative_area_level_2'] ||
                addressMap['administrative_area_level_1'] || '';

            // Obtener país
            country = addressMap['country'] || '';
        }

        const autocompleteField = document.getElementById(currentInputAddress);
        if (autocompleteField) {
            autocompleteField.value = place.formatted_address || address;
        }

        const cityField = document.getElementById(currentInputCity);
        if (cityField) {
            cityField.value = city;
        }

        const countryField = document.getElementById(currentInputCountry);
        if (countryField) {
            countryField.value = country;
        }

        // Actualizar coordenadas usando función helper
        if (location) {
            const lat = location.lat();
            const lng = location.lng();
            
            // Usar función helper para formato consistente
            document.getElementById(currentInputLat).value = formatCoordinate(lat);
            document.getElementById(currentInputLng).value = formatCoordinate(lng);
        }

        console.log('Campos actualizados:', {
            address: place.formatted_address || address,
            city: city,
            country: country,
            lat: location ? location.lat() : null,
            lng: location ? location.lng() : null
        });
    }

    async function reverseGeocode(position) {
        try {
            // Actualizar marcador y coordenadas inmediatamente
            marker.setPosition(position);
            map.setCenter(position);

            const lat = position.lat();
            const lng = position.lng();
            document.getElementById(currentInputLat).value = formatCoordinate(lat);
            document.getElementById(currentInputLng).value = formatCoordinate(lng);

            // Usar la nueva API Place para obtener los detalles de la ubicación
            const { Place } = await google.maps.importLibrary("places");
            const searchRequest = {
                location: { lat: lat, lng: lng },
                radius: 1  // metros - buscar en el punto exacto
            };

            try {
                const placeResult = await Place.searchNearby(searchRequest);
                if (placeResult && placeResult.places && placeResult.places.length > 0) {
                    const place = placeResult.places[0];
                    const placeDetails = await place.fetchFields({
                        fields: ['formatted_address', 'address_components', 'geometry']
                    });
                    updateMapAndFields(placeDetails);
                } else {
                    // Si no encontramos un lugar cercano, usar el geocoder como respaldo
                    const geocoder = new google.maps.Geocoder();
                    const response = await geocoder.geocode({
                        location: { lat: lat, lng: lng }
                    });

                    if (response.results && response.results[0]) {
                        updateMapAndFields(response.results[0]);
                    }
                }
            } catch (searchError) {
                console.warn('No se encontró un lugar cercano en la búsqueda, se usara geocoder:', searchError);
                // Usar geocoder como respaldo
                const geocoder = new google.maps.Geocoder();
                const response = await geocoder.geocode({
                    location: { lat: lat, lng: lng }
                });

                if (response.results && response.results[0]) {
                    updateMapAndFields(response.results[0]);
                }
            }
        } catch (e) {
            console.error('Error al actualizar la ubicación:', e);
        }
    }

    // Función para configurar los listeners del marcador
    function setupMarkerListeners() {
        // Click en el mapa para mover el marcador
        google.maps.event.addListener(map, 'click', function (event) {
            const clickPosition = event.latLng;
            marker.setPosition(clickPosition);
            reverseGeocode(clickPosition);
        });

        // Arrastrar el marcador
        google.maps.event.addListener(marker, 'dragend', function () {
            const newPosition = marker.getPosition();
            reverseGeocode(newPosition);
        });
    }
}
