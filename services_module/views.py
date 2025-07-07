from django.shortcuts import render, redirect
from django.contrib import admin
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from urllib.request import urlopen, Request
import json
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView 
from .utils.mixins import BreadcrumbMixins
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView
from datetime import date, time
from django.utils import timezone
from admin_module.models import Establishment, EstablishmentService, Service , Schedule, ScheduleAssignment



# Create your views here.

class HomeServicesView(BreadcrumbMixins, TemplateView):
    """Vista Principal Modulo Services"""
    template_name = 'services_module/main.html'
    login_url = '/login_module/login/'
    context_object_name = 'barberias'

    def get_breadcrumb(self):
        return []

    def get_queryset(self):
        # Filtramos solo establecimientos que sean barberías
        # Asumiendo que tienes un campo 'type' o similar en Establishment
        return Establishment.objects.get()  # Ajusta según tu modelo
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Puedes agregar más contexto si lo necesitas
        return context

   
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
