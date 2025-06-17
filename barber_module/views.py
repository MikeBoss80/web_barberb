from django.shortcuts import render, redirect
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView 
from datetime import date, time
from django.utils import timezone
from django.views import View
from .utils.mixins import BreadcrumbMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages


from django.views.generic import TemplateView


# Create your views here.

class HomeBarberView(BreadcrumbMixin, TemplateView):
    """Vista Principal Modulo Barber"""
    template_name = 'barber_module/main.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return []

    #DATPS TEMPORALES
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'user': self.request.user,
            'today': timezone.now(),
            'citas_hoy': 8,
            'ingresos_hoy': 420.00,
            'barberos_activos': 3,
            'bajo_stock': 2,
            'proximas_citas': [
                {'hora': '10:00', 'cliente': 'Carlos Pérez', 'servicio': 'Corte', 'barbero': 'Andrés'},
                {'hora': '11:00', 'cliente': 'Luis Soto', 'servicio': 'Barba', 'barbero': 'Miguel'}
            ],
            'labels': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
            'ingresos_data': [100, 200, 150, 300, 250],
            'servicios_labels': ['Corte', 'Barba', 'Corte + Barba'],
            'servicios_data': [10, 5, 8],
            'notificaciones': [
                'Hay 2 productos con stock bajo.',
                'Un barbero no ha iniciado su turno.',
            ]
        })

        return context

class barberView(TemplateView):
    template_name = 'historial_servicios.html'
    
class BarberCitasView(UserPassesTestMixin, BreadcrumbMixin, TemplateView):
    template_name = 'citas_barbero.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Administrator').exists()

    def handle_no_permission(self):
        return redirect('not_in_group')
    
    def get_breadcrumb(self):
        return [{'label': 'Citas Barbero', 'url': reverse('barber_module:citas_barbero')}]


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

class BarberContenidosView(BreadcrumbMixin, TemplateView):
     template_name= 'contenidos_barbero.html'
     def get_breadcrumb(self):
        return [{'label': 'Contenidos', 'url': reverse('barber_module:contenidos')}]
     
class InventarioView(BreadcrumbMixin, TemplateView):
     template_name= 'inventario.html'
     def get_breadcrumb(self):
        return [{'label': 'Inventario', 'url': reverse('barber_module:inventario')}]


class BarberReportesView(BreadcrumbMixin, TemplateView):
     template_name= 'reportes.html'
     def get_breadcrumb(self):
        return [{'label': 'Reportes', 'url': reverse('barber_module:reportes')}]



class BarberSeguridadView(BreadcrumbMixin, TemplateView):
     template_name= 'seguridad.html'
     def get_breadcrumb(self):
        return [{'label': 'Seguridad', 'url': reverse('barber_module:seguridad')}]


class SoporteView(BreadcrumbMixin, TemplateView):
     template_name= 'soporte.html'
     def get_breadcrumb(self):
        return [{'label': 'Soporte', 'url': reverse('barber_module:soporte')}]


class PerfilUsuarioView(BreadcrumbMixin, TemplateView):
     template_name ='perfil_usuario.html'
     def get_breadcrumb(self):
        return [{'label': 'Perfil', 'url': reverse('barber_module:perfil_usuario')}]
    
    
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
    
class LogoutView(BreadcrumbMixin, TemplateView):
    template_name='core/login.html'
