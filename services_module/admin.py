from django.contrib import admin
from .models import ServiceDate, ServiceDateDay

@admin.register(ServiceDate)
class ServiceDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'establishment', 'date', 'customer', 'barber', 'status', 'price_total')
    search_fields = ('customer__username', 'barber__username', 'product__name', 'establishment__name_est')
    list_filter = ('date', 'status', 'establishment')

@admin.register(ServiceDateDay)
class ServiceDateDayAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_date', 'day')
