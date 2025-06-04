from django.urls import path
from core.views import HomepageView, LoginView, BarberoDashboardView, post, NotInGroup
from login_module.views import LoginView

urlpatterns = [
    path('', HomepageView.as_view(), name='main'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate/', post, name="validate"),
    path('groups/', NotInGroup.as_view(), name='not_in_group'),
]