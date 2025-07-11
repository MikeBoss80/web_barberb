from django.urls import path
from core.views import TestView,BaseView,HomepageView, LoginView, BarberoDashboardView, post, NotInGroup
from login_module.views import LoginView
app_name = 'core'
urlpatterns = [
    path('', HomepageView.as_view(), name='main'),
    path('login/', LoginView.as_view(), name='login'),
    path('validate/', post, name="validate"),
    path('groups/', NotInGroup.as_view(), name='not_in_group'),
    path('test/', TestView.as_view(), name='test'),
    # path('base/', BaseView.as_view(), name='base'),
]