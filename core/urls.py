from django.urls import path
from core.views import HomepageView, LoginView, BarberoDashboardView, post

from core.views import HomepageView, BarberoDashboardView 
from login_module.views import LoginView

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es mas moderno."""


urlpatterns = [
    path('', HomepageView.as_view(), name='main'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate/', post, name="validate")
   # path('', HomeadminView.as_view(), name='admin_main'), 
    
]