from django.urls import path
from admin_module.views import HomeadminView
from admin_module.views import CitasView, BarberosView, ServiciosView, InventarioView, ReportesView, SeguridadView, SoporteView, ContenidosView, CalendarioBarberoView, LogoutView, PerfilUsuarioView, EditarPerfilView, DashboardView
from . import views

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'admin_module'

urlpatterns = [
    path('', HomeadminView.as_view(), name='admin_main'),
    path('citas/', CitasView.as_view(), name='citas'),
    path('barberos/', BarberosView.as_view(), name='barberos'),
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    path('inventario/', InventarioView.as_view(), name='inventario'),
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('seguridad/', SeguridadView.as_view(), name='seguridad'),
    path('soporte/', SoporteView.as_view(), name='soporte'),
    path('contenidos/', ContenidosView.as_view(), name='contenidos'),
    path('barberos/<int:barbero_id>/calendario/', CalendarioBarberoView.as_view(), name='calendario_barbero'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil_usuario"),
    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
]   


""" 
"""
