import django.http
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import admin
from core.models import Usuario  # Ajusta el import si tu app se llama distinto
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from urllib.request import urlopen, Request
import json 



# Create your views here.

class HomepageView(TemplateView):
    """Vista principal Main//Home"""
    
    template_name = 'core/main.html'


class LoginView(TemplateView):
    """
    Vista de inicio de sesión para validar usuarios de la tabla 'usuarios'.
    Renderiza el formulario y procesa los datos cuando se envían por POST.
    """
    template_name = 'core/login.html'  # Ruta de la plantilla HTML
    
def post(request):
    """
    Método que maneja el envío del formulario de login (método POST).
    Compara los datos ingresados con los registros en la tabla 'usuarios'.
    """
    users = Usuario.objects.all().values('id','username','password')
    usuario_input = request.GET.get('usuario')     # Obtiene el campo del usuario
    contrasena_input = request.GET.get('contrasena')  # Obtiene el campo de contraseña
    print (usuario_input, contrasena_input)
    
    
    return JsonResponse(list(users),safe=False)
    
    
""" 
        try:
            # Buscar el usuario en la base de datos por su correo
            usuario = Usuario.objects.get(correo_usuario=usuario_input)

            # Validar contraseña (aquí asumimos que es texto plano, puedes usar hash si es necesario)
            if usuario.ident_usuario == contrasena_input:
                # Si las credenciales son correctas, guardar datos en la sesión
                request.session['usuario_id'] = usuario.id_usuario
                request.session['nombre'] = usuario.nombre_usuario
                request.session['tipo'] = usuario.tipo_usuario_id

                return redirect('admin_module')  # Cambia esta ruta por la que necesites

            else:
                messages.error(request, 'Contraseña incorrecta.')

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')

        # Si hay error, se vuelve a mostrar la misma plantilla con los mensajes
        return self.get(request, *args, **kwargs)

    

 """
 
         
    
class BarberoDashboardView(TemplateView):
    #La página principal para los barberos cuando inician sesión.
    template_name = 'core/barbero/dashboard.html'
     
class BarberoOpcionesUsuarioView(TemplateView):
    #las opciones que tiene el barbero como usuario (perfil, configuración, etc.)
    template_name = 'barbero/opciones_usuario.html'

class BarberoHistorialServiciosView(TemplateView):
    #mostrar el historial de los servicios que el barbero ha realizado, como cortes pasados o citas atendidas
    template_name = 'barbero/historial_servicios.html'

class BarberoHomeView(TemplateView):
    #Vista principal del barbero, la usaré como pantalla de inicio antes de entrar al dashboard
    template_name = 'barbero/home.html'

class BarberoSolicitudesView(TemplateView):
    #El barbero vea o haga solicitudes, como pedir vacaciones, días libres o cambiar su horario
    template_name = 'barbero/solicitudes.html'


    