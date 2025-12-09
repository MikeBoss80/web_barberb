window.App = {
    version: "1.0",
    
    // Datos del establecimiento
    establishment: {
        id: null,
        name: '',
        address: '',
        phone: '',
        email: '',
        timezone: 'America/Santiago',
        logo: null,
        settings: {
            currency: 'CLP',
            booking_advance_days: 30,
            cancellation_hours: 24,
            allow_online_booking: true,
            require_customer_verification: false
        },
        services: {
            list: [],
            categories: [],
            selected: null,
            
            // Método para agregar servicio
            add(service) {
                this.list.push({
                    id: service.id,
                    name: service.name,
                    description: service.description || '',
                    duration: service.duration, // en minutos
                    price: service.price,
                    category: service.category || 'general',
                    is_active: service.is_active !== false,
                    requires_deposit: service.requires_deposit || false,
                    deposit_amount: service.deposit_amount || 0,
                    image: service.image || null
                });
            },
            
            // Método para obtener servicio por ID
            getById(id) {
                return this.list.find(s => s.id === id);
            },
            
            // Método para filtrar por categoría
            getByCategory(category) {
                return this.list.filter(s => s.category === category);
            }
        },
        barbers: {
            list: [
                {
                    id: null,
                    name: '',
                    bio: '',
                    photo: null,
                    schedule: {
                        working_hours: {
                            monday: { is_available: true, start: '09:00', end: '20:00' },
                            tuesday: { is_available: true, start: '09:00', end: '20:00' },
                            wednesday: { is_available: true, start: '09:00', end: '20:00' },
                            thursday: { is_available: true, start: '09:00', end: '20:00' },
                            friday: { is_available: true, start: '09:00', end: '20:00' },
                            saturday: { is_available: true, start: '09:00', end: '18:00' },
                            sunday: { is_available: false, start: null, end: null }
                        },
                    }
                },
                {}
            ],
            selected: null,
            
            
            // Verificar disponibilidad de un barbero en un día específico
            isAvailable(barberId, dayOfWeek) {
                const barber = this.getById(barberId);
                if (!barber) return false;
                
                const daySchedule = barber.schedule.working_hours[dayOfWeek.toLowerCase()];
                return daySchedule && daySchedule.is_available;
            }
        },
    },
    reserva:{
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
        
        // Cargar horarios del establecimiento
        if (data.schedule) {
            Object.assign(this.schedule, data.schedule);
        }
        
        // Cargar servicios
        if (data.services && Array.isArray(data.services)) {
            data.services.forEach(service => this.services.add(service));
        }
        
        // Cargar categorías de servicios
        if (data.service_categories) {
            this.services.categories = data.service_categories;
        }
        
        // Cargar barberos
        if (data.barbers && Array.isArray(data.barbers)) {
            data.barbers.forEach(barber => this.barbers.add(barber));
        }
        
        console.log('App initialized with data:', {
            establishment: this.establishment.name,
            services: this.services.list.length,
            barbers: this.barbers.list.length
        });
    },
    
    // Método de utilidad
    saludar(nombre) {
        console.log("Hola " + nombre);
    }
};