from django.shortcuts import render 
from django.views.generic import TemplateView, ListView


# Create your views here.

class HomeadminView(TemplateView):
    """Vista Principal Modulo Admin"""
    template_name = 'admin_module/main.html'
    


class CitasView(TemplateView):
    """Vista  citas"""
    template_name = 'admin_module/citas.html'



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
     
