from django.urls import path
from establishment.views import (
    EstablishmentMainView, 
    EstablishmentManagementView, 
    CreateEstablishmentView, 
    DeleteEstablishmentView, 
    UpdateEstablishmentView
)

"""//Usamos Class-Based View."""
app_name = 'establishment'

urlpatterns = [
    path('', EstablishmentMainView.as_view(), name='establishment_main'),
    path('management/', EstablishmentManagementView.as_view(), name='management'),
    path('management/add/', CreateEstablishmentView.as_view(), name='add'),
    path('management/update/<int:pk>/', UpdateEstablishmentView.as_view(), name='update'),
    path('management/delete/<int:pk>/', DeleteEstablishmentView.as_view(), name='delete'),
]   
