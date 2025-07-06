from django.urls import path

from admin_module.views import CitasView,InventarioListView,ProductCreateView,ProductUpdateView,ProductDeleteView, BarberosView, ServiciosView, InventarioView, ReportesView, SeguridadView, SoporteView, ContenidosView, CalendarioBarberoView, LogoutView, PerfilUsuarioView, EditarPerfilView, CreateEstablishmentView, HomeadminView,DeleteEstablishmentView, EditarBarberoEstadoView,CrearCitaRapidaView,CrearCitaFormView, cancelar_cita, AdminSolicitudesListView,AdminSolicitudesDetailView

from django.contrib.auth.views import LogoutView

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
    path('seguridad/', SeguridadView.as_view(), name='seguridad'),
    path('soporte/', SoporteView.as_view(), name='soporte'),
    path('contenidos/', ContenidosView.as_view(), name='contenidos'),
    path('barberos/<int:barbero_id>/calendario/', CalendarioBarberoView.as_view(), name='calendario_barbero'),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil_usuario"),
    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
    path('producto/agregar/', ProductCreateView.as_view(), name='producto_create'),
    path('producto/editar/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    path('producto/eliminar/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('registro_est/', CreateEstablishmentView.as_view(), name='registro_est'),
    path('eliminar_est/<int:pk>/', DeleteEstablishmentView.as_view(), name='eliminar_est'),
    path('citas/editar-rapido/<int:pk>/', EditarBarberoEstadoView.as_view(), name='editar_barbero_estado'),
    path('crear_cita_form/', CrearCitaFormView.as_view(), name='crear_cita_form'),  # para cargar
    path('crear_cita/', CrearCitaRapidaView.as_view(), name='crear_cita'),  # para guardar
    path('cancelar-cita/', cancelar_cita, name='cancelar-cita'),  # para guardar
    path('solicitudes/barberos/', AdminSolicitudesListView.as_view(), name='admin_solicitudes_list'),
    path('solicitudes/barberos/<int:pk>/', AdminSolicitudesDetailView.as_view(), name='admin_solicitud_detalle'),
    path('servicios/', views.ServiciosView.as_view(), name='servicios'),
    path('servicio/agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('servicio/editar/<int:id>/', views.editar_servicio, name='editar_servicio'),
    path('servicio/eliminar/<int:id>/', views.eliminar_servicio, name='eliminar_servicio'),

]   
