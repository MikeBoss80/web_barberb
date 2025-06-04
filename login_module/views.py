from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from login_module.models import Profile
from admin_module.models import Establishment
import requests
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView, PasswordResetConfirmView,PasswordResetCompleteView
from django.views.generic.edit import FormView
from .forms import UserProfileForm


class CustomLoginView(LoginView):
    template_name = 'login_custom.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


    def get_success_url(self):
        return '/admin_module/' 


class LoginView(TemplateView):
    template_name = 'login.html'

class RegistroAdministradorView(TemplateView):
    template_name = 'registro_administrador.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        contrasena = request.POST['contrasena']
        nombre_establishment = request.POST['nombre_Establishment']
        direccion = request.POST['direccion']

        # Crear usuario
        usuario = Profile.objects.create_user(
            username=correo,
            email=correo,
            password=contrasena,
            nombre=nombre,
            tipo_usuario='administrador'
        )

        # Crear Establishment asociado
        Establishment.objects.create(
            administrador=usuario,
            nombre=nombre_establishment,
            direccion=direccion,
            # agregar demás campos...
        )

        return redirect('login')  # O a un dashboard
    
class RegistroBarberoView(TemplateView):
    template_name = 'registro_barbero.html'

class RegistroEstablecimientoView(TemplateView):
    template_name = 'registro_establecimiento.html'

class RegistroUsuarioView(FormView):
    template_name = 'registro_usuario.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class TerminosYCondicionesView(TemplateView):
    template_name = 'terminosycondiciones.html'

class TipoRolView(TemplateView):
    template_name = 'tipo_rol.html'

class CambiocontraseñaView(TemplateView):
    template_name = 'cambio_contraseña.html'
    
#Formulario donde se solicita correo electronico para el envio del reseteo de contraseña
class ResetPasswordView(PasswordResetView):
    template_name = 'password_reset_form.html'
    form_class = PasswordResetForm

    def get_success_url(self):
        return '/login_module/password_reset/done/'

#Confirmacion de envio de correco electronico exitoso.
class ResetPasswordDoneView(PasswordResetDoneView):
    template_name='password_reset_done.html'
    form_class = PasswordResetForm

#Formulario cambio de contraseña.  
class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name='password_reset_confirm.html'
    form_class = SetPasswordForm

    def get_success_url(self):
        return 'reset/done/'

class ResetPasswordCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
