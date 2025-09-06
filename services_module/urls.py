from django.urls import path
from services_module.views import MapServicesView, PlacesListView , getMap, getPlacesBySearch, HomeServicesView, SeguridadView, SoporteView, ServicesCitasView, LogoutView,EditarPerfilView,PerfilUsuarioView,ServiceDateCreateView
from django.contrib.auth.views import LogoutView

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'services_module'

urlpatterns = [
   path('map', MapServicesView.as_view(), name='map_services'),
    path('', HomeServicesView.as_view(), name='services_main'),
    path('create/', ServiceDateCreateView.as_view(), name='create_service_date'),
    path('getplacesbysearch/', getPlacesBySearch, name='getplacesbysearch'),
    path('getmap/', getMap, name='getmap'),
    path('citas/cliente/', ServicesCitasView.as_view(), name='citas_cliente'),
    path('seguridad/', SeguridadView.as_view(), name='seguridad'),
    path('soporte/', SoporteView.as_view(), name='soporte'),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil_usuario"),
    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
    path('logout/', LogoutView.as_view(next_page='login_module:login'), name='logout'),

]   
