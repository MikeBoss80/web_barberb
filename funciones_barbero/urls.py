from django.urls import path
from funciones_barbero.views import SolicitudesView, VistaprincipalbarView, HistorialserviciosView
from . import views

app_name = 'funciones_barbero'

urlpatterns = [
    path('solicitudes/', SolicitudesView.as_view(), name='solicitudes'),
    path('historial_servicios/', HistorialserviciosView.as_view(), name='historial_servicios'), 
    path('vista_principal_bar/', VistaprincipalbarView.as_view(), name='vista_principal_bar'),  
]
