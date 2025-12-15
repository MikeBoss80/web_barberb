from django.urls import path
from admin_module.views import (
    VinculationDeleteView, CreateVinculationView, CitasView, CollapsView, 
    ServiciosView, ReportesView, SeguridadView, SoporteView, ContenidosView, 
    CalendarioBarberoView, CalendarioBarberMesAPIView, CalendarioBarberoDiaAPIView, 
    PerfilUsuarioView, CreateEstablishmentView, HomeadminView, DeleteEstablishmentView, 
    EditarBarberoEstadoView, CrearCitaRapidaView, cancelar_cita, 
    AdminSolicitudesListView, AdminSolicitudesDetailView, BarberRequestListView,
    BarberValidateVinculation, BarberRequestDetailView, BarberRequestCreateView, 
    SelecGrupoView,
    # Endpoints API Dashboard
    DashboardCitasHoyAPIView, DashboardIngresosAPIView, DashboardBarberosActivosAPIView,
    DashboardIngresosSemanalesAPIView, DashboardServiciosPopularesAPIView
)
from . import views
# from .schedule_views import (
#     configurar_horarios_establecimiento,
#     configurar_slots_avanzado,
#     bulk_schedule_config,
#     gestionar_disponibilidad_barberos,
#     preview_slots,
#     aplicar_configuracion_predefinida
# )  # DEPRECADO: Se usa establishment/views.py para configuración


"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'admin_module'

urlpatterns = [
    path('', HomeadminView.as_view(), name='main'),
    path('citas/', CitasView.as_view(), name='citas'),
    path('collaborators/', CollapsView.as_view(), name='collabs'),
    path('barberos/vinculation/', CreateVinculationView.as_view(), name='vinculation_request'),
    path('barberos/vinculation/eliminar/<int:pk>/', VinculationDeleteView.as_view(), name='vinculation_delete'),
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    # path('inventario/', InventarioView.as_view(), name='inventario'),
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('seguridad/', SeguridadView.as_view(), name='seguridad'),
    path('soporte/', SoporteView.as_view(), name='soporte'),
    path('establecimiento/', ContenidosView.as_view(), name='establecimiento'),
    path('barberos/<int:barbero_id>/calendario/', CalendarioBarberoView.as_view(), name='calendario_barbero'),
    path('calendario/barbero/<int:barbero_id>/mes/', CalendarioBarberMesAPIView.as_view(), name='calendario_barbero_mes_api'),
    path('calendario/barbero/<int:barbero_id>/dia/', CalendarioBarberoDiaAPIView.as_view(), name='calendario_barbero_dia_api'),
    path("perfil/", PerfilUsuarioView.as_view(), name="perfil_usuario"),
    path("perfil/seleccionar-rol/", SelecGrupoView.as_view(), name="seleccionar_rol"),
#    path('perfil/editar/', EditarPerfilView.as_view(), name='editar_perfil'),
    # path('producto/agregar/', ProductCreateView.as_view(), name='producto_create'),
    # path('producto/editar/<int:pk>/', ProductUpdateView.as_view(), name='product_update'),
    # path('producto/eliminar/<int:pk>/', ProductDeleteView.as_view(), name='product_delete'),
    path('registro_est/', CreateEstablishmentView.as_view(), name='registro_est'),
    path('eliminar_est/<int:pk>/', DeleteEstablishmentView.as_view(), name='eliminar_est'),
    path('citas/editar-rapido/<int:pk>/', EditarBarberoEstadoView.as_view(), name='editar_barbero_estado'),
    path('crear_cita_form/', CrearCitaRapidaView.as_view(), name='crear_cita'),  # para cargar y guardar una cita
    path('cancelar-cita/', cancelar_cita, name='cancelar-cita'),  # para cancelar una cita
    path('solicitudes/barberos/', AdminSolicitudesListView.as_view(), name='admin_solicitudes_list'),
    path('solicitudes/barberos/<int:pk>/', AdminSolicitudesDetailView.as_view(), name='admin_solicitud_detalle'),
    path('servicios/', views.ServiciosView.as_view(), name='servicios'),
    path('servicio/agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('servicio/editar/<int:id>/', views.editar_servicio, name='editar_servicio'),
    path('servicio/eliminar/<int:id>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('solicitudes/', BarberRequestListView.as_view(), name='barber_solicitudes_list'),
    path('solicitudes/validate/<int:pk>/<int:value>/', BarberValidateVinculation.as_view(), name='barber_vinculation_validate'),
    path('solicitud/<int:pk>/', BarberRequestDetailView.as_view(), name='barber_solicitud_detalle'),
    path('crear-solicitud/barbero/', BarberRequestCreateView.as_view(), name ='solicitud_barbero'),
    
    # ============================================================================
    # API ENDPOINTS PARA DASHBOARD EN TIEMPO REAL
    # ============================================================================
    path('api/dashboard/citas-hoy/', DashboardCitasHoyAPIView.as_view(), name='api_dashboard_citas_hoy'),
    path('api/dashboard/ingresos/', DashboardIngresosAPIView.as_view(), name='api_dashboard_ingresos'),
    path('api/dashboard/barberos-activos/', DashboardBarberosActivosAPIView.as_view(), name='api_dashboard_barberos_activos'),
    path('api/dashboard/ingresos-semanales/', DashboardIngresosSemanalesAPIView.as_view(), name='api_dashboard_ingresos_semanales'),
    path('api/dashboard/servicios-populares/', DashboardServiciosPopularesAPIView.as_view(), name='api_dashboard_servicios_populares'),
    
    # ============================================================================
    # URLs para Configuración de Horarios y Slots - DEPRECADO
    # ============================================================================
    # NOTA: Estas vistas han sido reemplazadas por establishment/views.py
    # path('horarios/configurar/', configurar_horarios_establecimiento, name='configurar_horarios_establecimiento'),
    # path('horarios/slots-avanzado/', configurar_slots_avanzado, name='configurar_slots_avanzado'),
    # path('horarios/bulk-config/', bulk_schedule_config, name='bulk_schedule_config'),
    # path('horarios/disponibilidad-barberos/', gestionar_disponibilidad_barberos, name='gestionar_disponibilidad_barberos'),
    # path('ajax/preview-slots/', preview_slots, name='preview_slots'),
    # path('ajax/aplicar-config-predefinida/', aplicar_configuracion_predefinida, name='aplicar_configuracion_predefinida'),


]   
