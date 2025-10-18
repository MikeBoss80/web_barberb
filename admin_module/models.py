from django.utils import timezone
from django.db import models
# from login_module.models import Profile
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User, Group
from django import forms


# Tabla: admin_module_days
class Day(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

# Tabla: admin_module_schedulesch
class Schedule(models.Model):
    day = models.IntegerField()
    start_hour = models.DateTimeField()
    end_hour = models.DateTimeField()

    def __str__(self):
        return f"{self.day} | {self.start_hour} - {self.end_hour}"

class ScheduleAssignment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)


# tabla de categoria de producto
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# Tabla: admin_module_products
class Product(models.Model):
    name_product = models.CharField(max_length=30)
    description_product = models.CharField(max_length=80)
    amount = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0)
    price_product = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name="productos", default=1)
    created_by = models.ForeignKey(User, related_name='products_created', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(User, related_name='products_updated', on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name_product

# Tabla: admin_module_services
class Service(models.Model):
    name_service = models.CharField(max_length=100)
    description_service = models.TextField()
    price_service = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    active = models.BooleanField(default=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_service

# Relación muchos a muchos entre establecimiento y servicios
class EstablishmentService(models.Model):
    establishment = models.ForeignKey('establishment.Establishment', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

# Tabla: admin_module_inventory
class Inventory(models.Model):
    establishment = models.ForeignKey('establishment.Establishment', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


# ============================================================================
# SISTEMA PROFESIONAL DE HORARIOS Y SLOTS
# ============================================================================

# Tabla: admin_module_establishmentschedule
class EstablishmentSchedule(models.Model):
    """
    Horarios de operación de cada establecimiento por día de la semana.
    Define cuándo está abierto cada local.
    """
    DAYS_OF_WEEK = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]
    
    establishment = models.ForeignKey(
        'establishment.Establishment', 
        on_delete=models.CASCADE, 
        related_name='schedules'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    opening_time = models.TimeField(help_text="Hora de apertura (ej: 09:00)")
    closing_time = models.TimeField(help_text="Hora de cierre (ej: 19:00)")
    is_open = models.BooleanField(default=True, help_text="¿El local abre este día?")
    
    class Meta:
        unique_together = ['establishment', 'day_of_week']
        ordering = ['establishment', 'day_of_week']
        verbose_name = 'Horario de Establecimiento'
        verbose_name_plural = 'Horarios de Establecimientos'
    
    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        if self.is_open:
            return f"{self.establishment.name} - {day_name}: {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        return f"{self.establishment.name} - {day_name}: CERRADO"


# Tabla: admin_module_barberavailability
class BarberAvailability(models.Model):
    """
    Disponibilidad de cada barbero por día de la semana.
    Permite que cada barbero tenga horarios personalizados.
    """
    DAYS_OF_WEEK = [
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]
    
    barber = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Barbero'},
        related_name='availabilities'
    )
    establishment = models.ForeignKey(
        'establishment.Establishment', 
        on_delete=models.CASCADE,
        related_name='barber_availabilities'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(help_text="Hora de inicio del turno")
    end_time = models.TimeField(help_text="Hora de fin del turno")
    is_available = models.BooleanField(
        default=True, 
        help_text="¿El barbero trabaja este día?"
    )
    
    class Meta:
        unique_together = ['barber', 'establishment', 'day_of_week']
        ordering = ['establishment', 'barber', 'day_of_week']
        verbose_name = 'Disponibilidad de Barbero'
        verbose_name_plural = 'Disponibilidades de Barberos'
    
    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        if self.is_available:
            return f"{self.barber.get_full_name()} - {day_name}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        return f"{self.barber.get_full_name()} - {day_name}: NO DISPONIBLE"


# Tabla: admin_module_barbertimeoff
class BarberTimeOff(models.Model):
    """
    Ausencias temporales de barberos (vacaciones, permisos, días libres).
    Permite bloquear slots específicos.
    """
    barber = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Barbero'},
        related_name='time_offs'
    )
    start_date = models.DateField(help_text="Fecha de inicio de la ausencia")
    end_date = models.DateField(help_text="Fecha de fin de la ausencia")
    start_time = models.TimeField(
        null=True, 
        blank=True, 
        help_text="Hora de inicio (opcional, para ausencias parciales)"
    )
    end_time = models.TimeField(
        null=True, 
        blank=True, 
        help_text="Hora de fin (opcional, para ausencias parciales)"
    )
    all_day = models.BooleanField(
        default=True, 
        help_text="¿Es ausencia de todo el día?"
    )
    reason = models.CharField(
        max_length=200, 
        help_text="Motivo de la ausencia (vacaciones, permiso médico, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Ausencia de Barbero'
        verbose_name_plural = 'Ausencias de Barberos'
    
    def __str__(self):
        if self.all_day:
            return f"{self.barber.get_full_name()}: {self.start_date} - {self.end_date} (Todo el día)"
        return f"{self.barber.get_full_name()}: {self.start_date} {self.start_time} - {self.end_date} {self.end_time}"
