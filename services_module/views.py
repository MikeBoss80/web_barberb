from django.shortcuts import render, redirect
from django.contrib import admin,messages
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from urllib.request import urlopen, Request
import json
from datetime import timedelta
from django.contrib.auth.models import User, Group
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView 
from .utils.mixins import BreadcrumbMixins
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView
from datetime import date, time
from django.utils import timezone
from admin_module.models import Establishment, EstablishmentService, Service , Schedule, ScheduleAssignment
from services_module.models import ServiceDate
from admin_module.utils.slots import generate_available_slots
from django.db.models import F, ExpressionWrapper, FloatField
from services_module.models import ServiceDate
from admin_module.forms import ServiceDateForm
from datetime import datetime, timedelta


# Create your views here.

class HomeServicesView(BreadcrumbMixins, TemplateView):
    """Vista Principal Modulo Services"""
    template_name = 'services_module/main.html'
    login_url = '/login_module/login/'

    def get_breadcrumb(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
  
        # 1️ Obtener establecimientos activos
        establishments = Establishment.objects.filter(active=True)

        # 2 Preparar datos de cada establecimiento
        establishments_data = []
        for est in establishments:
            services = Service.objects.filter(establishmentservice__establishment_id=est).annotate(
            duration_minutes=ExpressionWrapper(F('duration') / 60.0, output_field=FloatField())
            )
            grupo =Group.objects.get(name="Barbero")
            barbers = User.objects.filter(
                groups=grupo,
                is_active=True,
                profile__establishment=est,
            )

            establishments_data.append({
                
                'id': est.id,
                'name': est.name_est,
                'address': est.address_est,
                'city': est.city_est,
                'image': est.img_est if est.img_est else '/static/img/default_barber.jpg',
                'services': list(services.values('id', 'name_service', 'price_service', 'duration_minutes')),
                'barbers': list(barbers.values('id', 'first_name', 'last_name', 'profile__qa_average')),
            })

        # 3️ Incluir en el contexto
        context['establishments_data'] = establishments_data
        
        # Simulación de slots: genera de 9:00 a 17:00 cada hora
        today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        slots = []
        for i in range(9):  # 9 slots de 1 hora
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
    success_url = reverse_lazy('services_module:citas_cliente')  # Redirige a ver las citas del cliente

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
        # ✅ Asigna el precio automáticamente según el servicio seleccionado
        form.instance.price_total = form.instance.service.service.price_service


        # ✅ Asigna un comentario por defecto si deseas
        form.instance.comments = "Agendada desde el portal."
        response = super().form_valid(form)
        messages.success(self.request, "✅ ¡Tu cita ha sido agendada exitosamente!")
        
        print("📌 Creando cita:")
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

        messages.error(self.request, "❌ Hubo un error al agendar tu cita. Por favor revisa los datos.")
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
    
class LogoutView(BreadcrumbMixins, TemplateView):
    template_name='core/login.html'
