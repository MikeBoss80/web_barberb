from django.shortcuts import render 
from django.views.generic import TemplateView
from django.contrib import admin
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from urllib.request import urlopen, Request
import json
# Create your views here.

class MapServicesView(TemplateView):
    """Vista Principal Servicios"""
    template_name = 'map_services.html'

class PlacesListView(View):
    def get(self, request):
        context = {
        }
        return render(request, 'places_list.html', context)
    
class FormServicesView(View):
    def get(self, request):
        context = {
        }
        return render(request, 'form_services.html', context)

def getMap(request):
    return JsonResponse({'mapApiKey': settings.MAPS_APIKEY})

def getPlacesBySearch(request):
    print(request)
    query = request.GET.get('query')
    # lat = request.GET.get('lat')
    # lng = request.GET.get('lng')
    loc = request.GET.get('location')
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&location={loc}&key={settings.MAPS_APIKEY}"
    print(url)
    req = Request(url)
    with urlopen(req) as response:
        datos = response.read()
        data = json.loads(datos)
    return JsonResponse(data)