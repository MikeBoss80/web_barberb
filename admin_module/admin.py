
from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha', 'hora', 'barbero', 'servicio', 'estado')
    list_filter = ('fecha', 'estado', 'barbero')
    search_fields = ('cliente', 'barbero', 'servicio')
