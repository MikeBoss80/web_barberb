from django.urls import path
from .views import HomepageView
from core.views import HomepageView, LoginView, MapServicesView 

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es mas moderno."""


urlpatterns = [
    path('', HomepageView.as_view(), name='main'),
    path('login/', LoginView.as_view(), name='login'),
    path('services/', MapServicesView.as_view(), name='login'),
    
]
