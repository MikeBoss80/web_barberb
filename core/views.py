from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import admin


# Create your views here.

class HomepageView(TemplateView):
    """Vista principal Main//Home"""
    
    template_name = 'core/main.html'

class LoginView(TemplateView):
    template_name = 'login/login.html'
    """Vista de inicio de sesión Login"""
    
    template_name = 'core/Login.html'
    
    #edirect_authenticated_user = True
    
    #success_url = reverse_lazy('administrador:dashboard')
    # def get_success_url(self):
        #return self.success_url

class BarberoDashboardView(TemplateView):
    template_name = 'core/Solicitudes.html'

class BarberoOpcionesUsuarioView(TemplateView):
    #las opciones que tiene el barbero como usuario (perfil, configuración, etc.)
    template_name = 'barbero/opciones_usuario.html'

class BarberoHistorialServiciosView(TemplateView):
    #mostrar el historial de los servicios que el barbero ha realizado, como cortes pasados o citas atendidas
    template_name = 'barbero/historial_servicios.html'

class BarberoHomeView(TemplateView):
    #Vista principal del barbero, la usaré como pantalla de inicio antes de entrar al dashboard
    template_name = 'barbero/home.html'

class SolicitudesView(TemplateView):
    #El barbero vea o haga solicitudes, como pedir vacaciones, días libres o cambiar su horario
    template_name = 'core/solicitudes.html'
  
class VistaprincipalbarView(TemplateView):
    #El barbero vea o haga solicitudes, como pedir vacaciones, días libres o cambiar su horario
    template_name = 'core/vista_principal_bar.html'

class HistorialserviciosView(TemplateView):
    #El barbero vea o haga solicitudes, como pedir vacaciones, días libres o cambiar su horario
    template_name = 'core/historial_servicios.html'