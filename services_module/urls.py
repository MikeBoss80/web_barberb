from django.urls import path
from services_module.views import MapServicesView, PlacesListView , getMap, getPlacesBySearch

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'services_module'

urlpatterns = [
    path('', MapServicesView.as_view(), name='map_services'),
    path('getplacesbysearch/', getPlacesBySearch, name='getplacesbysearch'),
    path('getmap/', getMap, name='getmap'),
]   
