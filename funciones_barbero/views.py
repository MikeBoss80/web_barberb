from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import admin


class SolicitudesView(TemplateView):
    #El barbero vea o haga solicitudes, como pedir vacaciones, días libres o cambiar su horario
    template_name = 'figaro/solicitudes.html'

class VistaprincipalbarView(TemplateView):
    #El barbero vea o haga solicitudes, como pedir vacaciones, días libres o cambiar su horario
    template_name = 'figaro/vista_principal_bar.html'

class HistorialserviciosView(TemplateView):
    #El barbero vea o haga solicitudes, como pedir vacaciones, días libres o cambiar su horario
    template_name = 'figaro/historial_servicios.html'