from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth import views as auth_views
from login_module.views import (
    LoginView,
    LogoutView,
    PostLoginRedirectView,
    FillProfileView,
    RegistroAdministradorView,
    RegistroBarberoView,
    RegistroUsuarioView,
    RegistroEstablecimientoView,
    TerminosYCondicionesView,
    TipoRolView,
    CambiocontraseñaView,
    CustomLoginView,
    ResetPasswordView,
    ResetPasswordDoneView,
    ResetPasswordConfirmView,
    ResetPasswordCompleteView,
    RolSelectView,
    CustomChangePassw
    
)

app_name = 'login_module'


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('redirect-after-login/', PostLoginRedirectView.as_view(), name='redirect_after_login'),
    path("fill-profile/", FillProfileView.as_view(), name="fill_profile"),
    path('registro/administrador/', RegistroAdministradorView.as_view(), name='registroadministrador'),
    path('registro/barbero/', RegistroBarberoView.as_view(), name='registro_Barbero'),
    path('registro/usuario/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('registro/establecimiento/', RegistroEstablecimientoView.as_view(), name='registro_establecimiento'),
    path('terminos-condiciones/', TerminosYCondicionesView.as_view(), name='terminosycondiciones'),
    path('tipo-rol/', TipoRolView.as_view(), name='tipo_rol'),
    path('cambio_contraseña/', CambiocontraseñaView.as_view(), name='cambio_contraseña'),
    path("perfil/password/change/", CustomChangePassw.as_view(), name="change_password"),
    #auth vies django para restablecimiento
    path('password_reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password_reset/done/', ResetPasswordDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', ResetPasswordCompleteView.as_view(), name='password_reset_complete'),
    path('rol_actual/', login_required(RolSelectView.as_view()), name='rol_actual'),
    path('logout/', LogoutView.as_view(), name='logout'),



]
