from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from login_module.models import Profile
from establishment.models import Establishment
import requests
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView, PasswordResetConfirmView,PasswordResetCompleteView,PasswordChangeView
from django.views.generic.edit import FormView
from .forms import UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, View
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth import update_session_auth_hash


class CustomLoginView(LoginView):
    template_name = 'login_custom.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


    def get_success_url(self):
        user = self.request.user
        #obtener nombres de grupos del usuario
        user_groups = user.groups.values_list('name', flat=True)

        #Validacion si esta en los grupos Barberos y administrator
        if 'Barbero' in user_groups and 'Administrador' in user_groups:
            return '/login_module/rol_actual/' 

        #Si solo esta en un grupo se dirige segun el grupo
        elif 'Barbero' in user_groups:
            return '/admin_module/' 
        elif 'Administrador' in user_groups:
            return '/admin_module/'
        else:
            #Si no es barbero o administrador su rol es como cliente
            return '/admin_module/'
        
class RolSelectView(LoginRequiredMixin,TemplateView):
    template_name='rol_actual.html'
    login_url = '/login/' 

    def post(self, request, *args, **kwargs):
        rol_seleccionado = request.POST.get('rol')

        # Validar que el usuario tiene el rol seleccionado
        user = request.user
        user_groups = user.groups.values_list('name', flat=True)

        if rol_seleccionado in user_groups:
            # Guardar en sesión el rol activo
            request.session['current_role'] = rol_seleccionado

            return redirect('/admin_module/')
        else:
            # Si intenta seleccionar un rol que no tiene, redirigir o mostrar error
            return redirect('/not_authorized/')
        
class LoginView(TemplateView):
    template_name = 'login.html'
    
class LogoutView(LoginRequiredMixin, DjangoLogoutView):
    """
    Vista personalizada para manejar el logout.
    - Mantiene el comportamiento estándar de Django.
    - Revoca token de Google si existe.
    """

    next_page = "login_module:login"  # Redirección tras logout (ajusta según tu proyecto)

    def dispatch(self, request, *args, **kwargs):
        # 1. Revocar token de Google si existe (django-allauth)
        if request.user.is_authenticated:
            social = request.user.socialaccount_set.filter(provider="google").first()
            if social:
                token = social.socialtoken_set.first()
                if token:
                    # Revocar token en Google
                    requests.post(
                        "https://accounts.google.com/o/oauth2/revoke",
                        params={"token": token.token},
                        headers={"content-type": "application/x-www-form-urlencoded"},
                    )
                    token.delete()  # Eliminar token en la BD

        # 2. Ejecutar el logout estándar de Django
        return super().dispatch(request, *args, **kwargs)

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

        return redirect('login_module:login')  # O a un dashboard
    
class RegistroBarberoView(TemplateView):
    template_name = 'registro_barbero.html'

class RegistroEstablecimientoView(TemplateView):
    template_name = 'registro_establecimiento.html'

class RegistroUsuarioView(FormView):
    template_name = 'registro_usuario.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('login_module:login')

    def form_valid(self, form):
        user = form.save()
        group = form.cleaned_data['type_group']
        user.groups.add(group) 
        return super().form_valid(form)

class TerminosYCondicionesView(TemplateView):
    template_name = 'terminosycondiciones.html'

class TipoRolView(LoginRequiredMixin,TemplateView):
    template_name = 'tipo_rol.html'
    login_url = '/login/'  # Opcional, si no usas settings.LOGIN_URL

    # Validación: solo los usuarios en el grupo 'Administrador' pueden acceder
    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()

    # Redirección si no tiene permiso
    def handle_no_permission(self):
        return redirect('not_in_group')

class CambiocontraseñaView(TemplateView):
    template_name = 'cambio_contraseña.html'
    
#Formulario donde se solicita correo electronico para el envio del reseteo de contraseña
class ResetPasswordView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'registration/custom_reset_email.txt'   # respaldo en texto
    html_email_template_name = 'registration/custom_reset_email.html'  # plantilla HTML
    subject_template_name = 'registration/custom_reset_subject.txt'

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
        return '/login_module/reset/done/'

class ResetPasswordCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


class CustomChangePassw(PasswordChangeView):
    template_name = "perfil/perfil_usuario.html"  # mismo template donde tienes las tabs
    success_url = reverse_lazy("admin_module:perfil_usuario")  # redirige al perfil al guardar

    def get_form_kwargs(self):
        """Se asegura de pasar el usuario logueado al PasswordChangeForm"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Guardar la nueva contraseña
        user = form.save()
        # Mantener al usuario logueado tras el cambio
        messages.success(self.request, "Contraseña cambiada correctamente.")
        return super().form_valid(form) 
    
    def form_invalid(self, form):
        messages.error(self.request, "Hubo errores al cambiar la contraseña.")
        return super().form_invalid(form)
    
##Vista para completar perfil despues del registro con google
class FillProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "login_module/fill_profile.html"
    fields = ["phone", "address", "birth_date", "document"]  
    success_url = reverse_lazy("admin_module:main")  # Redirige a home después de guardar

    def get_object(self, queryset=None):
        """
        Se asegura de que el perfil editado siempre sea el del usuario autenticado.
        """
        return self.request.user.profile

    def form_valid(self, form):
        """
        Antes de guardar, valida si el perfil está completo para marcar `data_complete=True`.
        """
        profile = form.save(commit=False)

        # Validamos si todos los campos requeridos están diligenciados
        if profile.phone and profile.address and profile.birth_date and profile.document:
            profile.data_complete = True
        else:
            profile.data_complete = False

        profile.save()
        return super().form_valid(form)

class PostLoginRedirectView(LoginRequiredMixin, View):
    """
    Punto único de entrada después del login (Google o clásico).
    - Si el perfil NO está completo -> redirige a FillProfileView.
    - Si está completo           -> redirige al dashboard ('main').
    - Si hay 'next' y el perfil está completo, respeta 'next'.
    """
    def get(self, request, *args, **kwargs):
        # Garantiza que exista Profile (por si es su primer login social)
        profile, _ = Profile.objects.get_or_create(user=request.user)

        # ¿perfil completo?
        if not profile.data_complete:
            return redirect('fill_profile')

        # Respeta ?next=/ruta si existe y el perfil está completo
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)

        return redirect('main')