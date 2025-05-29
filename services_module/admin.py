from django.contrib import admin
from .models import ServiceDate, ServiceDateDay

@admin.register(ServiceDate)
class ServiceDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'date', 'customer', 'barber', 'status', 'price_total')
    search_fields = ('customer__username', 'barber__username')
    list_filter = ('date', 'status')

@admin.register(ServiceDateDay)
class ServiceDateDayAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_date', 'day')
