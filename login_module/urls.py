from django.urls import path
from django.contrib.auth import views as auth_views
from login_module.views import (
    LoginView,
    RegistroAdministradorView,
    RegistroBarberoView,
    RegistroUsuarioView,
    RegistroEstablecimientoView,
    TerminosYCondicionesView,
    TipoRolView,
    CambiocontraseñaView,
    CustomLoginView,
    ResetPasswordView,
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registro/administrador/', RegistroAdministradorView.as_view(), name='registroadministrador'),
    path('registro/barbero/', RegistroBarberoView.as_view(), name='registro_Barbero'),
    path('registro/usuario/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('registro/establecimiento/', RegistroEstablecimientoView.as_view(), name='registro_establecimiento'),
    path('terminos-condiciones/', TerminosYCondicionesView.as_view(), name='terminosycondiciones'),
    path('tipo-rol/', TipoRolView.as_view(), name='tipo_rol'),
    path('cambio_contraseña/', CambiocontraseñaView.as_view(), name='cambio_contraseña'),
    #auth vies django para restablecimiento
    path('password_reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
