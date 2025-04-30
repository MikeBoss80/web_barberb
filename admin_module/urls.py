from django.urls import path
from admin_module.views import HomeadminView
from admin_module.views import CitasView, BarberosView, ServiciosView, InventarioView, ReportesView, SeguridadView, SoporteView, ContenidosView

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'admin_module'

urlpatterns = [
    path('', HomeadminView.as_view(), name='admin_main'),
    path('citas/', CitasView.as_view(), name='citas'),
    path('barberos/', BarberosView.as_view(), name='barberos'),
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    path('inventario/', InventarioView.as_view(), name='inventario'),
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('seguridad/', SeguridadView.as_view(), name='seguridad'),
    path('soporte/', SoporteView.as_view(), name='soporte'),
    path('soporte/', ContenidosView.as_view(), name='contenidos'),
    
]


""" 
"""
