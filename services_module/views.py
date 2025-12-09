from django.shortcuts import render, redirect
from django.contrib import admin, messages
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from urllib.request import urlopen, Request
import json
from datetime import timedelta, datetime, date, time
from django.contrib.auth.models import User, Group
from django.views.generic import ListView, TemplateView, UpdateView, CreateView, DeleteView 
from .utils.mixins import BreadcrumbMixins
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, FloatField, Prefetch
from django.core.serializers.json import DjangoJSONEncoder

# Models
from establishment.models import Establishment
from admin_module.models import Schedule, ScheduleAssignment, EstablishmentSlotConfiguration, EstablishmentSchedule, BarberAvailability
from services_module.models import ServiceDate
from admin_module.forms import ServiceDateForm
from product.models import ProductEstablishment

# Create your views here.

class HomeServicesView(BreadcrumbMixins, TemplateView):
    template_name = 'services_module/base.html'
    login_url = '/login_module/login/'

    def get_breadcrumb(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
  
        # Obtener toda la información de establecimientos usando la función centralizada
        establishments_data = get_active_establishments_data()
        
        # Pasar datos al template
        context['establishments_data'] = establishments_data
        context['establishments_data_json'] = json.dumps(establishments_data, cls=DjangoJSONEncoder)
        
        # Horarios disponibles
        today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        slots = []
        for i in range(9):
            slot_time = today + timedelta(hours=i)
            slots.append(slot_time.strftime("%H:%M"))
        context['available_slots'] = slots    

        return context

class ServiceDateCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear una cita (ServiceDate) tras la confirmación del voucher.
    Usa CreateView para manejar el POST y guardar la cita en la base de datos.
    """

    model = ServiceDate
    form_class = ServiceDateForm
    template_name = 'services_module/confirm_appointment.html'
    success_url = reverse_lazy('admin_module:citas')  # Redirige a ver las citas del cliente

    def get_form_kwargs(self):
        """
        Pasa la request al formulario por si es necesario utilizar el usuario
        para validaciones adicionales.
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """
        Si el formulario es válido, guarda la cita y muestra mensaje de éxito.
        """
        #Asigna el precio automáticamente según el servicio seleccionado
        form.instance.price_total = form.instance.service.service.price_service


        #Asigna un comentario por defecto si deseas
        form.instance.comments = "Agendada desde el portal."
        response = super().form_valid(form)
        messages.success(self.request, "¡Tu cita ha sido agendada exitosamente!")
        
        print("Creando cita:")
        print(f"Cliente: {form.instance.customer}")
        print(f"Barbero: {form.instance.barber}")
        print(f"Servicio: {form.instance.service}")
        print(f"Fecha: {form.instance.date}")
        print(f"Precio Total: {form.instance.price_total}")

        return response

    def form_invalid(self, form):
        """
        Si el formulario es inválido, muestra mensaje de error y logea errores en consola para depuración.
        """
        print(form.errors)

        messages.error(self.request, "Hubo un error al agendar tu cita. Por favor revisa los datos.")
        print("Errores en el formulario de creación de cita:", form.errors)
        return super().form_invalid(form)
    
class ServicesCitasView(BreadcrumbMixins, TemplateView):
    template_name = 'citas_cliente.html'


    def get_breadcrumb(self):
        return [{'label': 'Citas Agendadas', 'url': reverse('services_module:citas_cliente')}]


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hoy = date.today()
        #citas = Cita.objects.filter(fecha=hoy)
        citas = [
            {
                'id': 1,
                'cliente': 'Juan Pérez',
                'fecha': date.today(),
                'hora': time(10, 00),
                'barbero': 'Carlos',
                'servicio': 'Corte de cabello',
                'estado': 'completada',
                'notas': 'Cliente puntual',
            },
            {
                'id': 2,
                'cliente': 'Laura Gómez',
                'fecha': date.today(),
                'hora': time(11, 30),
                'barbero': 'Luis',
                'servicio': 'Barba + Corte',
                'estado': 'pendiente',
                'notas': '',
            },
            {
                'id': 3,
                'cliente': 'Andrés Ramírez',
                'fecha': date.today(),
                'hora': time(13, 00),
                'barbero': 'Carlos',
                'servicio': 'Color y corte',
                'estado': 'cancelada',
                'notas': 'Canceló por WhatsApp',
            },
        ]

     
        resumen = {
            'total_citas': len(citas),
            'completadas': len([c for c in citas if c['estado'] == 'completada']),
            'pendientes': len([c for c in citas if c['estado'] == 'pendiente']),
            'canceladas': len([c for c in citas if c['estado'] == 'cancelada']),
        }

        context['citas'] = citas
        context['resumen'] = resumen
        context['fecha_actual'] = date.today()

        return context

class MapServicesView(TemplateView):
    """Vista Principal Servicios"""
    template_name = 'map_services.html'

class PlacesListView(View):
    def get(self, request):
        context = {
        }
        return render(request, 'places_list.html', context)
    
class FormServicesView(View):
    def get(self, request):
        context = {
        }
        return render(request, 'form_services.html', context)

def getMap(request):
    return JsonResponse({'mapApiKey': settings.MAPS_APIKEY})

def getPlacesBySearch(request):
    print(request)
    query = request.GET.get('query')
    # lat = request.GET.get('lat')
    # lng = request.GET.get('lng')
    loc = request.GET.get('location')
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={loc}&key={settings.MAPS_APIKEY}"
    print(url)
    req = Request(url)
    with urlopen(req) as response:
        datos = response.read()
        data = json.loads(datos)
    return JsonResponse(data)

class SeguridadView(BreadcrumbMixins, TemplateView):
     template_name= 'serv_seguridad.html'
     def get_breadcrumb(self):
        return [{'label': 'Seguridad', 'url': reverse('services_module:seguridad')}]

class SoporteView(BreadcrumbMixins, TemplateView):
     template_name= 'serv_soporte.html'
     def get_breadcrumb(self):
        return [{'label': 'Soporte', 'url': reverse('services_module:soporte')}]

class PerfilUsuarioView(BreadcrumbMixins, TemplateView):
     template_name ='perfil_usuario.html'
     def get_breadcrumb(self):
        return [{'label': 'Perfil', 'url': reverse('services_module:perfil_usuario')}]
    
    
     def get_context_data(self, **kwargs):
        usuario = "Miguel Bolivar"
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user  # Agrega el usuario autenticado al contexto
        return context

# Editar perfil (nombre y email básico)
class EditarPerfilView(LoginRequiredMixin, UpdateView):
#    model = usuario
    fields = ['first_name', 'last_name', 'email']
    template_name = 'perfil/editar_perfil.html'
    success_url = reverse_lazy('perfil:perfil_usuario')

    def get_object(self):
        return self.request.user

def get_active_establishments_data():
    """
    Función centralizada para obtener toda la información de establecimientos activos.
    
    Retorna una lista completa de establecimientos con:
    - Información básica del establecimiento
    - Servicios/Productos disponibles (ProductEstablishment)
    - Barberos con sus disponibilidades
    - Horarios del establecimiento (EstablishmentSchedule)
    - Configuración de slots (EstablishmentSlotConfiguration)
    
    Returns:
        list: Lista de diccionarios con toda la información de establecimientos
    """

    
    # Query optimizado con prefetch_related y select_related
    establishments = Establishment.objects.filter(active=True).prefetch_related(
        
        # Horarios del establecimiento
        Prefetch(
            'schedules',
            queryset=EstablishmentSchedule.objects.all().order_by('day_of_week'),
            to_attr='est_schedules'
        ),
        # Disponibilidades de barberos
        Prefetch(
            'barber_availabilities',
            queryset=BarberAvailability.objects.select_related('barber', 'barber__profile').filter(is_available=True),
            to_attr='est_barber_availabilities'
        ),
        # Servicios y productos del establecimiento
        Prefetch(
            'products_stock',
            queryset=ProductEstablishment.objects.select_related('product', 'product__category').filter(
                product__is_active=True
                # No filtrar por stock aquí porque los servicios tienen stock=0
            ),
            to_attr='est_products'
        )
    ).select_related('slot_config')  # Configuración de slots (relación OneToOne)
    
    # Obtener grupo de barberos
    try:
        grupo_barbero = Group.objects.get(name="Barbero")
    except Group.DoesNotExist:
        grupo_barbero = None
    
    establishments_data = []
    
    for est in establishments:
        # ========================================
        # 1. INFORMACIÓN BÁSICA DEL ESTABLECIMIENTO
        # ========================================
        establishment_info = {
            'id': est.id,
            'name': est.name_est,
            'address': est.address_est,
            'city': est.city_est,
            'country': est.country_est,
            'phone': est.phone_est,
            'email': est.email_est,
            'description': est.description,
            'lat': float(est.lat_est),
            'lng': float(est.lng_est),
            'image': est.img_est.url if est.img_est else '/static/img/default_barber.jpg',
            'qa_average': est.qa_average_est,
            'active': est.active,
        }
        
        # ========================================
        # 2. SERVICIOS/PRODUCTOS DEL ESTABLECIMIENTO
        # ========================================
        # Separar productos entre servicios y productos físicos
        services_data = []
        products_data = []
        
        for product_est in est.est_products:
            category_type = product_est.product.category.category_type if product_est.product.category else 'storable'
            
            product_data = {
                'product_id': product_est.product.id,
                'name': product_est.product.name,
                'internal_reference': product_est.product.internal_reference,
                'barcode': product_est.product.barcode,
                'description': product_est.product.description,
                'category': product_est.product.category.name if product_est.product.category else 'Sin categoría',
                'category_type': category_type,
                'cost_price': float(product_est.product.cost_price),
                'sale_price': float(product_est.product.sale_price),
                'current_stock': float(product_est.current_stock),
                'available_stock': float(product_est.available_stock),
                'location': product_est.location,
            }
            
            # Si es un servicio (category_type='service'), agregarlo a servicios
            if category_type == 'service':
                services_data.append(product_data)
            else:
                # Es un producto físico (storable o consumable)
                # Solo incluir si tiene stock disponible
                if product_est.available_stock > 0:
                    products_data.append(product_data)
        
        # ========================================
        # 3. HORARIOS DEL ESTABLECIMIENTO
        # ========================================
        schedules_data = []
        for schedule in est.est_schedules:
            schedules_data.append({
                'day_of_week': schedule.day_of_week,
                'day_name': schedule.get_day_of_week_display(),
                'opening_time': schedule.opening_time.strftime('%H:%M'),
                'closing_time': schedule.closing_time.strftime('%H:%M'),
                'is_open': schedule.is_open,
            })
        
        # ========================================
        # 4. CONFIGURACIÓN DE SLOTS
        # ========================================
        slot_config_data = None
        if hasattr(est, 'slot_config') and est.slot_config:
            slot_config = est.slot_config
            slot_config_data = {
                'default_slot_duration': slot_config.default_slot_duration,
                'buffer_time': slot_config.buffer_time_between_appointments,
                'advance_booking_days': slot_config.advance_booking_days,
                'min_advance_hours': slot_config.min_advance_booking_hours,
                'allow_same_day': slot_config.allow_same_day_booking,
                'send_reminders': slot_config.send_appointment_reminders,
                'reminder_hours': slot_config.reminder_hours_before,
                'allow_cancellation': slot_config.allow_online_cancellation,
                'min_cancellation_hours': slot_config.min_cancellation_hours,
            }
        
        # ========================================
        # 5. BARBEROS Y SUS DISPONIBILIDADES
        # ========================================
        barbers_data = []
        
        # Obtener barberos únicos de las disponibilidades
        if grupo_barbero:
            barbers = User.objects.filter(
                groups=grupo_barbero,
                is_active=True,
                profile__establishment=est,
            ).select_related('profile').distinct()
            
            for barber in barbers:
                # Obtener disponibilidades de este barbero en este establecimiento
                barber_availabilities = [
                    {
                        'day_of_week': avail.day_of_week,
                        'day_name': avail.get_day_of_week_display(),
                        'start_time': avail.start_time.strftime('%H:%M'),
                        'end_time': avail.end_time.strftime('%H:%M'),
                        'is_available': avail.is_available,
                    }
                    for avail in est.est_barber_availabilities 
                    if avail.barber_id == barber.id
                ]
                
                barbers_data.append({
                    'id': barber.id,
                    'first_name': barber.first_name,
                    'last_name': barber.last_name,
                    'full_name': barber.get_full_name(),
                    'email': barber.email,
                    'qa_average': barber.profile.qa_average if hasattr(barber, 'profile') else 0.0,
                    #'photo': barber.profile.photo.url if hasattr(barber, 'profile') and barber.profile.photo else None,
                    'availabilities': barber_availabilities,
                })
        

        
        # ========================================
        # CONSOLIDAR TODA LA INFORMACIÓN
        # ========================================
        establishment_info.update({
            'services': services_data,
            'schedules': schedules_data,
            'slot_config': slot_config_data,
            'barbers': barbers_data,
            'products': products_data,
        })
        
        establishments_data.append(establishment_info)
    
    return establishments_data