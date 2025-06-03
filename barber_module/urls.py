from django.urls import path
from barber_module.views import barberView


"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es moderno."""
app_name = 'barber_module'

urlpatterns = [
    path('', barberView.as_view(), name='barber'),

   
]   
