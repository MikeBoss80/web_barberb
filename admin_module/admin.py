
from django.contrib import admin
from establishment.models import Establishment
from .models import  (
    Day,
    Schedule,
    ScheduleAssignment,
    Product,
    Service,
    EstablishmentService,
    Inventory,
    Category,
    EstablishmentSchedule,
    BarberAvailability,
)
from .slot_config_models import EstablishmentSlotConfiguration


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


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_service', 'price_service', 'category', 'active')
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


# ============================================================================
# ADMINISTRADORES PARA EL SISTEMA DE SLOTS
# ============================================================================

@admin.register(EstablishmentSchedule)
class EstablishmentScheduleAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'get_day_name', 'opening_time', 'closing_time', 'is_open')
    list_filter = ('day_of_week', 'is_open', 'establishment')
    search_fields = ('establishment__name',)
    ordering = ('establishment', 'day_of_week')
    
    def get_day_name(self, obj):
        return dict(EstablishmentSchedule.DAYS_OF_WEEK)[obj.day_of_week]
    get_day_name.short_description = 'Día de la semana'


@admin.register(BarberAvailability)
class BarberAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('barber', 'establishment', 'get_day_name', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'establishment')
    search_fields = ('barber__first_name', 'barber__last_name', 'establishment__name')
    ordering = ('establishment', 'barber', 'day_of_week')
    
    def get_day_name(self, obj):
        return dict(BarberAvailability.DAYS_OF_WEEK)[obj.day_of_week]
    get_day_name.short_description = 'Día de la semana'


@admin.register(EstablishmentSlotConfiguration)
class EstablishmentSlotConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'establishment', 
        'default_slot_duration', 
        'advance_booking_days',
        'send_appointment_reminders',
        'updated_at'
    )
    search_fields = ('establishment__name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Establecimiento', {
            'fields': ('establishment',)
        }),
        ('Configuración de Slots', {
            'fields': ('default_slot_duration', 'buffer_time_between_appointments'),
            'description': 'Configuración básica de duración y espaciado de los slots'
        }),
        ('Configuración de Reservas', {
            'fields': (
                'advance_booking_days', 
                'min_advance_booking_hours', 
                'allow_same_day_booking',
                'allow_online_cancellation',
                'min_cancellation_hours'
            ),
            'description': 'Reglas para el agendamiento y cancelación de citas'
        }),
        ('Notificaciones', {
            'fields': (
                'send_appointment_reminders',
                'reminder_hours_before',
                'send_confirmation_immediately'
            ),
            'description': 'Configuración de notificaciones automáticas'
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )