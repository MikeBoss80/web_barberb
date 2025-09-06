from django.urls import path
from barber_module.views import  barberView, BarberCitasView, BarberReportesView, SoporteView, PerfilUsuarioView, EditarPerfilView, SoporteView, BarberSeguridadView, BarberContenidosView, HomeBarberView
from . import views
from django.contrib.auth.views import LogoutView


"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'barber_module'


urlpatterns = [
    path('', HomeBarberView.as_view(), name='barber_main'),
    path('', barberView.as_view(), name='barber'),
    path('citas/barbero', BarberCitasView.as_view(), name='citas_barbero'),
    path('reportes/', BarberReportesView.as_view(), name='reportes'),
    path('seguridad/', BarberSeguridadView.as_view(), name='seguridad'),
    path('soporte/', SoporteView.as_view(), name='soporte'),
    path('contenidos/', BarberContenidosView.as_view(), name='contenidos'),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil_usuario"),
    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
]   

