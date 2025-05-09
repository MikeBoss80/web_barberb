from django.urls import path
from core.views import HomepageView, LoginView, BarberoDashboardView 

"""//🔥 Nota: Usamos Class-Based View (HomePageView) lo cual es mas moderno."""


urlpatterns = [
    path('', HomepageView.as_view(), name='main'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', BarberoDashboardView.as_view(), name='dashboard'),

]