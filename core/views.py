from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.

class HomepageView(TemplateView):
    """Vista principal Main//Home"""
    
    template_name = 'core/main.html'

class LoginView(TemplateView):
    """Vista de inicio de sesión Login"""
    
    template_name = 'core/Login.html'

class MapServicesView(TemplateView):
    """Vista de mapas Maps"""
    
    template_name = 'services/map_services.html'