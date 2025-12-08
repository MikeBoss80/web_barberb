/**
 * Establishment Map Handler
 * Maneja el mapa de Google Maps para la selección de establecimientos
 */

(function() {
    'use strict';

    let map;
    let markers = [];
    let infoWindow;
    
    // Datos de los establecimientos (esto debería venir del backend)
    const establishments = [
        {
            id: 'sede1',
            name: 'Barbería Centro',
            address: 'Calle 10 #15-20',
            phone: '(601) 234-5678',
            hours: 'Lun - Sáb: 9:00 AM - 7:00 PM',
            rating: 4.8,
            reviews: 230,
            lat: 4.679531063698843,
            lng: -74.04015630448359
        },
        {
            id: 'sede2',
            name: 'Barbería Norte',
            address: 'Carrera 50 #80-35',
            phone: '(601) 345-6789',
            hours: 'Lun - Sáb: 10:00 AM - 8:00 PM',
            rating: 4.9,
            reviews: 345,
            lat: 4.710988643120845,
            lng: -74.04238891601562
        },
        {
            id: 'sede3',
            name: 'Barbería Sur',
            address: 'Avenida 30 #5-12',
            phone: '(601) 456-7890',
            hours: 'Lun - Dom: 9:00 AM - 9:00 PM',
            rating: 4.7,
            reviews: 198,
            lat: 4.595653,
            lng: -74.076363
        }
    ];

    // Inicializar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        // Solo inicializar si estamos en la página correcta
        const mapContainer = document.getElementById('establishmentMap');
        if (mapContainer) {
            loadGoogleMapsAPI();
        }
    });

    /**
     * Cargar la API de Google Maps
     */
    function loadGoogleMapsAPI() {
        fetch('/services_module/getmap/')
            .then(response => response.json())
            .then(data => {
                const apiKey = data.mapApiKey;
                loadMapScript(apiKey);
            })
            .catch(error => {
                console.error('Error loading Google Maps API key:', error);
                showMapError('Error al cargar la API de Google Maps');
            });
    }

    /**
     * Cargar el script de Google Maps
     */
    function loadMapScript(apiKey) {
        (g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})({
            key: apiKey,
            v: "weekly",
        });
        
        initMap();
    }

    /**
     * Inicializar el mapa
     */
    async function initMap() {
        try {
            const { Map } = await google.maps.importLibrary("maps");
            const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
            
            // Centro del mapa (Bogotá)
            const center = { lat: 4.679531063698843, lng: -74.04015630448359 };
            
            // Crear el mapa
            map = new Map(document.getElementById("establishmentMap"), {
                center: center,
                zoom: 12,
                mapId: 'DEMO_MAP_ID', // Requerido para AdvancedMarkerElement
            });

            // Crear InfoWindow
            infoWindow = new google.maps.InfoWindow();

            // Agregar marcadores para cada establecimiento
            establishments.forEach(establishment => {
                createMarker(establishment);
            });

            // Ajustar el mapa para mostrar todos los marcadores
            fitMapToMarkers();

            // Agregar listeners a las tarjetas de establecimientos
            setupEstablishmentCardListeners();

        } catch (error) {
            console.error('Error initializing map:', error);
            showMapError('Error al inicializar el mapa');
        }
    }

    /**
     * Crear marcador en el mapa
     */
    function createMarker(establishment) {
        const position = { lat: establishment.lat, lng: establishment.lng };
        
        // Crear elemento del marcador
        const markerContent = document.createElement('div');
        markerContent.className = 'custom-marker';
        markerContent.innerHTML = '<i class="bi bi-geo-alt-fill"></i>';
        markerContent.style.cssText = `
            background: #0d6efd;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            cursor: pointer;
        `;
        
        const icon = markerContent.querySelector('i');
        icon.style.transform = 'rotate(45deg)';
        icon.style.fontSize = '20px';

        // Crear marcador con API v3
        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: establishment.name,
            icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg width="40" height="50" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20,2 C11.2,2 4,9.2 4,18 C4,28 20,48 20,48 S36,28 36,18 C36,9.2 28.8,2 20,2 Z" fill="#0d6efd" stroke="white" stroke-width="2"/>
                        <circle cx="20" cy="18" r="8" fill="white"/>
                    </svg>
                `),
                scaledSize: new google.maps.Size(40, 50),
                anchor: new google.maps.Point(20, 50)
            }
        });

        // Agregar evento click al marcador
        marker.addListener('click', () => {
            showEstablishmentInfo(establishment, marker);
            
            // Seleccionar el establecimiento
            selectEstablishment(establishment.id);
        });

        markers.push({ id: establishment.id, marker: marker });
    }

    /**
     * Mostrar información del establecimiento
     */
    function showEstablishmentInfo(establishment, marker) {
        const content = `
            <div class="establishment-info-window">
                <h5 class="mb-2">${establishment.name}</h5>
                <p class="mb-1 text-muted small">
                    <i class="bi bi-geo-alt"></i> ${establishment.address}
                </p>
                <p class="mb-1 text-muted small">
                    <i class="bi bi-clock"></i> ${establishment.hours}
                </p>
                <p class="mb-1 text-muted small">
                    <i class="bi bi-telephone"></i> ${establishment.phone}
                </p>
                <p class="mb-0 small">
                    <i class="bi bi-star-fill text-warning"></i> ${establishment.rating} (${establishment.reviews} reseñas)
                </p>
            </div>
        `;

        infoWindow.setContent(content);
        infoWindow.open(map, marker);
    }

    /**
     * Ajustar el mapa para mostrar todos los marcadores
     */
    function fitMapToMarkers() {
        if (markers.length === 0) return;

        const bounds = new google.maps.LatLngBounds();
        markers.forEach(({ marker }) => {
            bounds.extend(marker.getPosition());
        });

        map.fitBounds(bounds);
        
        // Ajustar zoom si es necesario
        const listener = google.maps.event.addListener(map, "idle", function() {
            if (map.getZoom() > 13) map.setZoom(13);
            google.maps.event.removeListener(listener);
        });
    }

    /**
     * Configurar listeners para las tarjetas de establecimientos
     */
    function setupEstablishmentCardListeners() {
        const establishmentCards = document.querySelectorAll('.establishment-card-list');
        
        establishmentCards.forEach(card => {
            card.addEventListener('click', function() {
                const input = this.querySelector('input[name="establishment"]');
                const establishmentId = input.value;
                
                // Centrar el mapa en el establecimiento seleccionado
                centerMapOnEstablishment(establishmentId);
                
                // Mostrar info del establecimiento
                const establishment = establishments.find(e => e.id === establishmentId);
                const markerData = markers.find(m => m.id === establishmentId);
                if (establishment && markerData) {
                    showEstablishmentInfo(establishment, markerData.marker);
                }
            });
        });
    }

    /**
     * Centrar el mapa en un establecimiento
     */
    function centerMapOnEstablishment(establishmentId) {
        const establishment = establishments.find(e => e.id === establishmentId);
        if (establishment && map) {
            map.panTo({ lat: establishment.lat, lng: establishment.lng });
            map.setZoom(15);
        }
    }

    /**
     * Seleccionar un establecimiento
     */
    function selectEstablishment(establishmentId) {
        const radioButton = document.querySelector(`input[name="establishment"][value="${establishmentId}"]`);
        if (radioButton) {
            radioButton.checked = true;
            radioButton.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    /**
     * Mostrar error en el mapa
     */
    function showMapError(message) {
        const mapContainer = document.getElementById('establishmentMap');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div class="map-error">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    // Exponer funciones globales si es necesario
    window.EstablishmentMap = {
        centerOnEstablishment: centerMapOnEstablishment,
        selectEstablishment: selectEstablishment
    };

})();
