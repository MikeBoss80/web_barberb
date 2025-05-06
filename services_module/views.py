from django.shortcuts import render 
from django.views.generic import TemplateView
from django.views import View
# Create your views here.

class MapServicesView(TemplateView):
    """Vista Principal Servicios"""
    template_name = 'map_services.html'
