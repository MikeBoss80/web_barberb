/**
 * Establishment Map Handler
 * ===========================
 * Maneja el mapa de Google Maps para la selección de establecimientos
 * Integrado con EstablishmentSelector para sincronización bidireccional
 * 
 * @version 2.0
 * @author BarberB Team
 */

const EstablishmentMap = (function() {
    'use strict';

    // ============================================================================
    // VARIABLES PRIVADAS
    // ============================================================================
    let map = null;
    let markers = [];
    let infoWindow = null;
    let establishments = [];
    let isInitialized = false;
    let googleMapsLoaded = false;

    // ============================================================================
    // INICIALIZACIÓN
    // ============================================================================

    /**
     * Inicializa el mapa con datos de establecimientos
     * @param {Array} data - Array de establecimientos desde la BD
     */
    function init(data) {
        console.log('Inicializando Establishment Map...');
        
        establishments = data || [];
        
        const mapContainer = document.getElementById('establishmentMap');
        if (!mapContainer) {
            console.warn('Contenedor del mapa no encontrado');
            return;
        }

        if (establishments.length === 0) {
            console.warn(' hay establecimientos para mostrar en el mapa');
            showMapPlaceholder();
            return;
        }

        // Cargar Google Maps API
        loadGoogleMapsAPI();
    }

    /**
     * Cargar la API de Google Maps
     */
    function loadGoogleMapsAPI() {
        // Verificar si ya está cargado
        if (googleMapsLoaded && window.google && window.google.maps) {
            initMap();
            return;
        }

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
        if (googleMapsLoaded) {
            initMap();
            return;
        }

        (g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})({
            key: apiKey,
            v: "weekly",
        });
        
        googleMapsLoaded = true;
        initMap();
    }

    /**
     * Inicializar el mapa
     */
    async function initMap() {
        if (isInitialized) {
            console.log('ℹMapa ya inicializado');
            return;
        }

        try {
            const { Map } = await google.maps.importLibrary("maps");
            
            // Calcular centro del mapa basado en establecimientos
            const center = calculateCenter();
            
            // Crear el mapa
            map = new Map(document.getElementById("establishmentMap"), {
                center: center,
                zoom: 12,
                mapId: 'BARBER_ESTABLISHMENT_MAP',
                zoomControl: true,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true,
            });

            // Crear InfoWindow
            infoWindow = new google.maps.InfoWindow();

            // Agregar marcadores para cada establecimiento
            establishments.forEach(establishment => {
                if (establishment.lat && establishment.lng) {
                    createMarker(establishment);
                }
            });

            // Ajustar el mapa para mostrar todos los marcadores
            fitMapToMarkers();

            isInitialized = true;
            console.log(` Mapa inicializado con ${markers.length} marcadores`);

        } catch (error) {
            console.error(' Error initializing map:', error);
            showMapError('Error al inicializar el mapa');
        }
    }

    // ============================================================================
    // MARCADORES
    // ============================================================================

    /**
     * Crear marcador en el mapa
     */
    function createMarker(establishment) {
        const position = { 
            lat: parseFloat(establishment.lat), 
            lng: parseFloat(establishment.lng) 
        };
        
        // Crear marcador con API v3
        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: establishment.name,
            animation: google.maps.Animation.DROP,
            icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg width="40" height="50" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                                <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.3"/>
                            </filter>
                        </defs>
                        <path d="M20,2 C11.2,2 4,9.2 4,18 C4,28 20,48 20,48 S36,28 36,18 C36,9.2 28.8,2 20,2 Z" 
                              fill="#0d6efd" stroke="white" stroke-width="2" filter="url(#shadow)"/>
                        <circle cx="20" cy="18" r="8" fill="white"/>
                        <text x="20" y="23" font-family="Arial" font-size="12" font-weight="bold" 
                              fill="#0d6efd" text-anchor="middle">B</text>
                    </svg>
                `),
                scaledSize: new google.maps.Size(40, 50),
                anchor: new google.maps.Point(20, 50)
            }
        });

        // Agregar evento click al marcador
        marker.addListener('click', () => {
            showEstablishmentInfo(establishment, marker);
            
            // Notificar al selector de establecimientos
            if (window.EstablishmentSelector) {
                window.EstablishmentSelector.selectEstablishment(establishment.id);
            }
        });

        markers.push({ 
            id: establishment.id, 
            marker: marker,
            data: establishment 
        });

        return marker;
    }

    /**
     * Mostrar información del establecimiento
     */
    function showEstablishmentInfo(establishment, marker) {
        // Obtener texto de horarios
        const scheduleText = establishment.schedules && establishment.schedules.length > 0
            ? getScheduleText(establishment.schedules)
            : 'Horario no disponible';

        const content = `
            <div class="establishment-info-window" style="max-width: 280px;">
                <div style="margin-bottom: 12px;">
                    <h5 style="margin: 0 0 8px 0; color: #212529; font-size: 1.1rem;">
                        ${establishment.name}
                    </h5>
                    <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 4px;">
                        <i class="bi bi-star-fill" style="color: #ffc107; font-size: 0.9rem;"></i>
                        <span style="font-weight: 600; color: #212529;">${establishment.qa_average.toFixed(1)}</span>
                        <span style="color: #6c757d; font-size: 0.85rem;">estrellas</span>
                    </div>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem;">
                    <div style="display: flex; align-items: start; gap: 8px; color: #495057;">
                        <i class="bi bi-geo-alt-fill" style="color: #0d6efd; flex-shrink: 0;"></i>
                        <span>${establishment.address}, ${establishment.city}</span>
                    </div>
                    
                    <div style="display: flex; align-items: center; gap: 8px; color: #495057;">
                        <i class="bi bi-clock-fill" style="color: #0d6efd;"></i>
                        <span>${scheduleText}</span>
                    </div>
                    
                    <div style="display: flex; align-items: center; gap: 8px; color: #495057;">
                        <i class="bi bi-telephone-fill" style="color: #0d6efd;"></i>
                        <span>${establishment.phone}</span>
                    </div>
                    
                    ${establishment.services && establishment.services.length > 0 ? `
                    <div style="display: flex; align-items: center; gap: 8px; color: #495057;">
                        <i class="bi bi-scissors" style="color: #0d6efd;"></i>
                        <span>${establishment.services.length} servicios disponibles</span>
                    </div>
                    ` : ''}
                </div>
                
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e9ecef;">
                    <button 
                        onclick="window.EstablishmentSelector?.selectEstablishment(${establishment.id})" 
                        style="width: 100%; padding: 8px 16px; background: #0d6efd; color: white; border: none; border-radius: 6px; font-weight: 500; cursor: pointer; font-size: 0.9rem;"
                        onmouseover="this.style.background='#0b5ed7'" 
                        onmouseout="this.style.background='#0d6efd'">
                        <i class="bi bi-check-circle"></i> Seleccionar este local
                    </button>
                </div>
            </div>
        `;

        infoWindow.setContent(content);
        infoWindow.open(map, marker);
        
        // Centrar ligeramente el mapa en el marcador
        map.panTo(marker.getPosition());
    }

    /**
     * Genera texto legible del horario
     */
    function getScheduleText(schedules) {
        const openDay = schedules.find(s => s.is_open);
        
        if (!openDay) return 'Cerrado';

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
    // UTILIDADES DE MAPA
    // ============================================================================

    /**
     * Calcular centro del mapa basado en establecimientos
     */
    function calculateCenter() {
        if (establishments.length === 0) {
            // Centro por defecto (Bogotá)
            return { lat: 4.679531063698843, lng: -74.04015630448359 };
        }

        if (establishments.length === 1) {
            return { 
                lat: parseFloat(establishments[0].lat), 
                lng: parseFloat(establishments[0].lng) 
            };
        }

        // Calcular promedio de coordenadas
        const total = establishments.reduce((acc, est) => {
            if (est.lat && est.lng) {
                acc.lat += parseFloat(est.lat);
                acc.lng += parseFloat(est.lng);
                acc.count++;
            }
            return acc;
        }, { lat: 0, lng: 0, count: 0 });

        return {
            lat: total.lat / total.count,
            lng: total.lng / total.count
        };
    }

    /**
     * Ajustar el mapa para mostrar todos los marcadores
     */
    function fitMapToMarkers() {
        if (markers.length === 0) return;

        if (markers.length === 1) {
            map.setCenter(markers[0].marker.getPosition());
            map.setZoom(14);
            return;
        }

        const bounds = new google.maps.LatLngBounds();
        markers.forEach(({ marker }) => {
            bounds.extend(marker.getPosition());
        });

        map.fitBounds(bounds);
        
        // Ajustar zoom máximo
        const listener = google.maps.event.addListener(map, "idle", function() {
            if (map.getZoom() > 15) map.setZoom(15);
            google.maps.event.removeListener(listener);
        });
    }

    /**
     * Centrar el mapa en un establecimiento específico
     * @param {number} establishmentId - ID del establecimiento
     */
    function centerOnEstablishment(establishmentId) {
        const markerData = markers.find(m => m.id === establishmentId);
        
        if (markerData && map) {
            const position = markerData.marker.getPosition();
            map.panTo(position);
            map.setZoom(15);
            
            // Animar el marcador
            markerData.marker.setAnimation(google.maps.Animation.BOUNCE);
            setTimeout(() => {
                markerData.marker.setAnimation(null);
            }, 2000);
            
            // Mostrar info del establecimiento
            showEstablishmentInfo(markerData.data, markerData.marker);
            
            console.log(`🎯 Mapa centrado en: ${markerData.data.name}`);
        } else {
            console.warn(`⚠️ No se encontró marcador para establecimiento ID: ${establishmentId}`);
        }
    }

    /**
     * Destacar un marcador específico
     * @param {number} establishmentId - ID del establecimiento
     */
    function highlightMarker(establishmentId) {
        // Restaurar todos los marcadores a su estado normal
        markers.forEach(({ marker }) => {
            marker.setAnimation(null);
        });

        // Destacar el marcador seleccionado
        const markerData = markers.find(m => m.id === establishmentId);
        if (markerData) {
            markerData.marker.setAnimation(google.maps.Animation.BOUNCE);
            setTimeout(() => {
                markerData.marker.setAnimation(null);
            }, 1500);
        }
    }

    // ============================================================================
    // MANEJO DE ERRORES Y PLACEHOLDERS
    // ============================================================================

    /**
     * Mostrar placeholder cuando no hay mapa
     */
    function showMapPlaceholder() {
        const mapContainer = document.getElementById('establishmentMap');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #6c757d;">
                    <i class="bi bi-map" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p style="margin: 0; font-size: 1rem;">No hay establecimientos para mostrar</p>
                </div>
            `;
        }
    }

    /**
     * Mostrar error en el mapa
     */
    function showMapError(message) {
        const mapContainer = document.getElementById('establishmentMap');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #dc3545;">
                    <i class="bi bi-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p style="margin: 0; font-size: 1rem; text-align: center; padding: 0 1rem;">${message}</p>
                </div>
            `;
        }
    }

    // ============================================================================
    // API PÚBLICA
    // ============================================================================

    return {
        init,
        centerOnEstablishment,
        highlightMarker,
        isInitialized: () => isInitialized,
        getMarkers: () => markers,
        getMap: () => map
    };

})();

// ============================================================================
// EXPORT PARA USO GLOBAL
// ============================================================================
window.EstablishmentMap = EstablishmentMap;
