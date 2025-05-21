from django.views.generic import TemplateView

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