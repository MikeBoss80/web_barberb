from django.shortcuts import render 
from django.views.generic import TemplateView, ListView
from datetime import date, time
from .models import Cita  # 👈 Esta línea es clave




# Create your views here.

class HomeadminView(TemplateView):
    """Vista Principal Modulo Admin"""
    template_name = 'admin_module/main.html'
    


class CitasView(TemplateView):
    """Vista citas"""
    template_name = 'admin_module/citas.html'

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


class BarberosView(TemplateView):
     template_name= 'admin_module/barberos.html'
     
     
class ServiciosView(TemplateView):
     template_name= 'admin_module/servicios.html'

class ContenidosView(TemplateView):
     template_name= 'admin_module/contenidos.html'

     
class InventarioView(TemplateView):
     template_name= 'admin_module/inventario.html'


class ReportesView(TemplateView):
     template_name= 'admin_module/reportes.html'


class SeguridadView(TemplateView):
     template_name= 'admin_module/seguridad.html'
     

class SoporteView(TemplateView):
     template_name= 'admin_module/soporte.html'
     
