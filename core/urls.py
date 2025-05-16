from django.urls import path
from core.views import HomepageView, LoginView, SolicitudesView, VistaprincipalbarView, HistorialserviciosView
from core import views

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es mas moderno."""


urlpatterns = [
    path('', HomepageView.as_view(), name='main'),
    path('login/', LoginView.as_view(), name='login'),
    path('solicitudes/', SolicitudesView.as_view(), name='solicitudes'),
    path('historial_servicios/', HistorialserviciosView.as_view(), name='historial_servicios'), 
    path('vista_principal_bar/', VistaprincipalbarView.as_view(), name='vista_principal_bar'),  
]