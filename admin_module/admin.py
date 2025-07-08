
from django.contrib import admin
from .models import  (
    
    Day,
    Schedule,
    ScheduleAssignment,
    Product,
    Establishment,
    Service,
    EstablishmentService,
    Inventory,
    Category,
)


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'start_hour', 'end_hour')
    list_filter = ('day',)

@admin.register(ScheduleAssignment)
class ScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'schedule')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_product', 'amount', 'minimum_stock', 'price_product', 'updated_at')
    search_fields = ('name_product',)
    list_filter = ('updated_at',)

@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_est', 'city_est', 'country_est', 'phone_est', 'active')
    search_fields = ('name_est', 'city_est', 'country_est')
    list_filter = ('active', 'created_date')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'active')
    search_fields = ('name_service',)
    list_filter = ('active',)

@admin.register(EstablishmentService)
class EstablishmentServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'establishment', 'service')
    list_filter = ('establishment', 'service')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'establishment', 'product')
    list_filter = ('establishment',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')