from django.contrib import admin
from establishment.models import Establishment

# Register your models here.
@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_est', 'city_est', 'country_est', 'phone_est', 'active')
    search_fields = ('name_est', 'city_est', 'country_est')
    list_filter = ('active', 'created_date')