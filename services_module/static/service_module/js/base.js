window.App = {
    version: "1.0",
    
    // Datos del establecimiento
    establishment: {
        id: null,
        name: '',
        address: '',
        city: '',
        country: '',
        phone: '',
        email: '',
        description: '',
        lat: null,
        lng: null,
        image: null,
        qa_average: 0.0,
        active: true,
        
        // Configuración de slots
        slot_config: {
            default_slot_duration: 30,
            buffer_time: 5,
            advance_booking_days: 30,
            min_advance_hours: 2,
            allow_same_day: true,
            send_reminders: true,
            reminder_hours: 24,
            allow_cancellation: true,
            min_cancellation_hours: 2,
        },
        
        // Horarios del establecimiento por día
        schedules: [
            // {day_of_week: 1, day_name: 'Lunes', opening_time: '09:00', closing_time: '19:00', is_open: true}
        ],
        
        // Servicios disponibles (provienen de ProductEstablishment con category_type='service')
        services: {
            list: [],
            categories: [],
            selected: null,
            
            // Método para agregar servicio
            add(service) {
                this.list.push({
                    product_id: service.product_id,
                    name: service.name,
                    description: service.description || '',
                    sale_price: service.sale_price,
                    category: service.category || 'General',
                    category_type: service.category_type || 'service',
                    current_stock: service.current_stock || 0,
                    available_stock: service.available_stock || 0,
                    internal_reference: service.internal_reference,
                    barcode: service.barcode,
                });
            },
            
            // Método para obtener servicio por ID
            getById(productId) {
                return this.list.find(s => s.product_id === productId);
            },
            
            // Método para filtrar por categoría
            getByCategory(category) {
                return this.list.filter(s => s.category === category);
            },
            
            // Obtener categorías únicas
            getCategories() {
                const categories = [...new Set(this.list.map(s => s.category))];
                return categories.filter(c => c);
            }
        },
        
        // Barberos del establecimiento
        barbers: {
            list: [],
            selected: null,
            
            // Método para agregar barbero
            add(barber) {
                this.list.push({
                    id: barber.id,
                    first_name: barber.first_name,
                    last_name: barber.last_name,
                    full_name: barber.full_name,
                    email: barber.email,
                    qa_average: barber.qa_average || 0.0,
                    photo: barber.photo,
                    availabilities: barber.availabilities || [],
                });
            },
            
            // Obtener barbero por ID
            getById(barberId) {
                return this.list.find(b => b.id === barberId);
            },
            
            // Verificar disponibilidad de un barbero en un día específico
            isAvailable(barberId, dayOfWeek) {
                const barber = this.getById(barberId);
                if (!barber) return false;
                
                const dayAvailability = barber.availabilities.find(
                    a => a.day_of_week === dayOfWeek && a.is_available
                );
                
                return !!dayAvailability;
            },
            
            // Obtener horario de barbero en un día
            getSchedule(barberId, dayOfWeek) {
                const barber = this.getById(barberId);
                if (!barber) return null;
                
                return barber.availabilities.find(a => a.day_of_week === dayOfWeek);
            }
        },
        
        // Productos del establecimiento
        products: {
            list: [],
            
            // Agregar producto
            add(product) {
                this.list.push({
                    product_id: product.product_id,
                    name: product.name,
                    internal_reference: product.internal_reference,
                    barcode: product.barcode,
                    description: product.description,
                    category: product.category,
                    cost_price: product.cost_price,
                    sale_price: product.sale_price,
                    current_stock: product.current_stock,
                    available_stock: product.available_stock,
                    location: product.location,
                });
            },
            
            // Obtener producto por ID
            getById(productId) {
                return this.list.find(p => p.product_id === productId);
            },
            
            // Filtrar por categoría
            getByCategory(category) {
                return this.list.filter(p => p.category === category);
            },
            
            // Verificar disponibilidad de stock
            hasStock(productId, quantity = 1) {
                const product = this.getById(productId);
                return product && product.available_stock >= quantity;
            }
        }
    },
    
    // Datos de la reserva en proceso
    reserva: {
        establishment_id: null,
        barber_id: null,
        service_id: null,
        date: null,
        hour: null,
    },
    
    // Método para inicializar la aplicación con datos del servidor
    init(data) {
        // Cargar información del establecimiento
        if (data.establishment) {
            Object.assign(this.establishment, data.establishment);
        }
        
        // Cargar configuración de slots
        if (data.slot_config) {
            Object.assign(this.establishment.slot_config, data.slot_config);
        }
        
        // Cargar horarios del establecimiento
        if (data.schedules && Array.isArray(data.schedules)) {
            this.establishment.schedules = data.schedules;
        }
        
        // Cargar servicios
        if (data.services && Array.isArray(data.services)) {
            data.services.forEach(service => this.establishment.services.add(service));
        }
        
        // Cargar barberos con sus disponibilidades
        if (data.barbers && Array.isArray(data.barbers)) {
            data.barbers.forEach(barber => this.establishment.barbers.add(barber));
        }
        
        // Cargar productos
        if (data.products && Array.isArray(data.products)) {
            data.products.forEach(product => this.establishment.products.add(product));
        }
        
        console.log('App initialized with data:', {
            establishment: this.establishment.name,
            services: this.establishment.services.list.length,
            barbers: this.establishment.barbers.list.length,
            products: this.establishment.products.list.length,
            schedules: this.establishment.schedules.length,
        });
    },
    
    // Método de utilidad
    saludar(nombre) {
        console.log("Hola " + nombre);
    }
};