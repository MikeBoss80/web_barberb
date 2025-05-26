from django.urls import path
from Login_Module.views import (
    LoginView,
    RegistroAdministradorView,
    RegistroBarberoView,
    RegistroUsuarioView,
    RegistroEstablecimientoView,
    TerminosYCondicionesView,
    TipoRolView,
    CambiocontraseñaView,
    CustomLoginView
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registro/administrador/', RegistroAdministradorView.as_view(), name='registroadministrador'),
    path('registro/barbero/', RegistroBarberoView.as_view(), name='registro_Barbero'),
    path('registro/usuario/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('registro/establecimiento/', RegistroEstablecimientoView.as_view(), name='registro_establecimiento'),
    path('terminos-condiciones/', TerminosYCondicionesView.as_view(), name='terminosycondiciones'),
    path('tipo-rol/', TipoRolView.as_view(), name='tipo_rol'),
    path('cambio/contraseña/', CambiocontraseñaView.as_view(), name='cambio_contraseña'),
]
