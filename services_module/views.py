from django.shortcuts import render 
from django.views.generic import TemplateView
from django.contrib import admin
from django.http import JsonResponse
from django.conf import settings
# Create your views here.

class MapServicesView(TemplateView):
    """Vista Principal Servicios"""
    template_name = 'map_services.html'

def getMap(request):
    #Devuelve la clave de la API de Google Maps como respuesta JSON
    return JsonResponse({'mapApiKey': settings.MAPS_APIKEY})