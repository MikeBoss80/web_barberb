from django.shortcuts import render 
from django.views.generic import TemplateView, ListView
from datetime import date, time
from django.utils import timezone
from django.views import View
from .utils.mixins import BreadcrumbMixin  # ← Importa desde tu nueva ruta
from django.urls import reverse





# Create your views here.

class HomeadminView(BreadcrumbMixin, TemplateView):
    """Vista Principal Modulo Admin"""
    template_name = 'admin_module/main.html'
    
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



class CitasView(BreadcrumbMixin, TemplateView):
    """Vista citas"""
    template_name = 'admin_module/citas.html'

    def get_breadcrumb(self):
        return [{'label': 'Citas', 'url': reverse('admin_module:citas')}]


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


class BarberosView(BreadcrumbMixin, TemplateView):
     template_name= 'admin_module/barberos.html'
     
     def get_breadcrumb(self):
        return [{'label': 'Barberos', 'url': reverse('admin_module:barberos')}]

     #DATOS TEMPORALES
     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barberos'] = [
            {
                'id': 1,
                'nombre': 'Carlos Pérez',
                'foto_url': 'https://via.placeholder.com/150',
                'especialidades': 'Cortes modernos, Barba',
                'horario': 'Lunes a Viernes, 10am - 6pm',
                'ingresos_generados': 450.00,  # Aquí van los ingresos estáticos
                'rating': 4.8,
            },
            {
                'id': 2,
                'nombre': 'Luis Martínez',
                'foto_url': 'https://via.placeholder.com/150',
                'especialidades': 'Afeitados, Degradados',
                'horario': 'Martes a Sábado, 12pm - 8pm',
                'ingresos_generados': 320.00,  # Ingresos estáticos también
                'rating': 4.5,
            },
            {
                'id': 3,
                'nombre': 'Ana Gómez',
                'foto_url': 'https://via.placeholder.com/150',
                'especialidades': 'Cortes femeninos, Tinte',
                'horario': 'Lunes a Miércoles, 9am - 5pm',
                'ingresos_generados': 500.00,  # Ejemplo de otro barbero
                'rating': 4.9,
            },
        ]
        return context
     
class CalendarioBarberoView(View):
    def get(self, request, barbero_id):
        # Aquí podrías cargar datos específicos del barbero, por ahora lo haremos estático
        context = {
            'barbero_id': barbero_id,
            'nombre_barbero': 'Carlos Pérez',  # Lo puedes modificar según el barbero
        }
        return render(request, 'calendario_barbero.html', context)
    

class ServiciosView(BreadcrumbMixin, TemplateView):
     template_name= 'admin_module/servicios.html'
     def get_breadcrumb(self):
        return [{'label': 'Servicios', 'url': reverse('admin_module:servicios')}]

class ContenidosView(BreadcrumbMixin, TemplateView):
     template_name= 'admin_module/contenidos.html'
     def get_breadcrumb(self):
        return [{'label': 'Contenidos', 'url': reverse('admin_module:contenidos')}]
     
class InventarioView(BreadcrumbMixin, TemplateView):
     template_name= 'admin_module/inventario.html'
     def get_breadcrumb(self):
        return [{'label': 'Inventario', 'url': reverse('admin_module:inventario')}]

     
     
class ReportesView(BreadcrumbMixin, TemplateView):
     template_name= 'admin_module/reportes.html'
     def get_breadcrumb(self):
        return [{'label': 'Reportes', 'url': reverse('admin_module:reportes')}]



class SeguridadView(BreadcrumbMixin, TemplateView):
     template_name= 'admin_module/seguridad.html'
     def get_breadcrumb(self):
        return [{'label': 'Seguridad', 'url': reverse('admin_module:seguridad')}]


class SoporteView(BreadcrumbMixin, TemplateView):
     template_name= 'admin_module/soporte.html'
     def get_breadcrumb(self):
        return [{'label': 'Soporte', 'url': reverse('admin_module:soporte')}]
