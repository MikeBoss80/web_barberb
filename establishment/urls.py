from django.urls import path
from establishment.views import (
    EstablishmentMainView, 
    EstablishmentManagementView, 
    CreateEstablishmentView, 
    DeleteEstablishmentView, 
    UpdateEstablishmentView,
    ProfileEstablishmentView,
    ConfigurationEstablishmentView,
    # Nuevas vistas AJAX
    SaveHorariosAjaxView,
    SaveSlotsConfigAjaxView,
    SaveNotificationsConfigAjaxView,
    SaveReportesConfigAjaxView,
    LoadConfigurationAjaxView,
    SaveFullConfigurationAjaxView
)

"""//Usamos Class-Based View."""
app_name = 'establishment'

urlpatterns = [
    path('', EstablishmentMainView.as_view(), name='establishment_main'),
    path('management/', EstablishmentManagementView.as_view(), name='management'),
    path('management/add/', CreateEstablishmentView.as_view(), name='add'),
    path('management/update/<int:pk>/', UpdateEstablishmentView.as_view(), name='update'),
    path('management/delete/<int:pk>/', DeleteEstablishmentView.as_view(), name='delete'),
    path('profile/', ProfileEstablishmentView.as_view(), name='profile_est'),
    path('configuration/', ConfigurationEstablishmentView.as_view(), name='configuration'),
    
    # URLs AJAX para configuración
    path('ajax/save-horarios/', SaveHorariosAjaxView.as_view(), name='ajax_save_horarios'),
    path('ajax/save-slots-config/', SaveSlotsConfigAjaxView.as_view(), name='ajax_save_slots_config'),
    path('ajax/save-notifications/', SaveNotificationsConfigAjaxView.as_view(), name='ajax_save_notifications'),
    path('ajax/save-reportes/', SaveReportesConfigAjaxView.as_view(), name='ajax_save_reportes'),
    path('ajax/load-configuration/<int:establishment_id>/', LoadConfigurationAjaxView.as_view(), name='ajax_load_configuration'),
    path('ajax/save-configuration/', SaveFullConfigurationAjaxView.as_view(), name='ajax_save_configuration'),
]   
