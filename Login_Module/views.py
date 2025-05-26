from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'login_custom.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


    def get_success_url(self):
        return '/admin_module/' 


class LoginView(TemplateView):
    template_name = 'login.html'

class RegistroAdministradorView(TemplateView):
    template_name = 'registroadministrador.html'

class RegistroBarberoView(TemplateView):
    template_name = 'registro_barbero.html'

class RegistroEstablecimientoView(TemplateView):
    template_name = 'registro_establecimiento.html'

class RegistroUsuarioView(TemplateView):
    template_name = 'registro_usuario.html'

class TerminosYCondicionesView(TemplateView):
    template_name = 'terminosycondiciones.html'

class TipoRolView(TemplateView):
    template_name = 'tipo_rol.html'

class CambiocontraseñaView(TemplateView):
    template_name = 'cambio_contraseña.html'