"""
Modelo simplificado para configuración de slots de establecimiento
================================================================

Modelo esencial para configuraciones básicas del sistema de slots
sin complejidades innecesarias.

Autor: Equipo BarberB
Fecha: Diciembre 2025
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from establishment.models import Establishment


class EstablishmentSlotConfiguration(models.Model):
    """
    Configuraciones esenciales para el sistema de slots del establecimiento.
    Modelo simple y funcional.
    """
    
    establishment = models.OneToOneField(
        Establishment,
        on_delete=models.CASCADE,
        related_name='slot_config',
        help_text="Establecimiento al que aplica esta configuración"
    )
    
    # ============================================================================
    # CONFIGURACIÓN BÁSICA DE SLOTS
    # ============================================================================
    
    default_slot_duration = models.IntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(120)],
        help_text="Duración por defecto de cada slot en minutos (15-120)"
    )
    
    buffer_time_between_appointments = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text="Tiempo de descanso entre citas en minutos (0-30)"
    )
    
    # ============================================================================
    # CONFIGURACIÓN DE RESERVAS
    # ============================================================================
    
    advance_booking_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        help_text="Días de anticipación máxima para agendar citas"
    )
    
    min_advance_booking_hours = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(72)],
        help_text="Horas mínimas de anticipación para agendar"
    )
    
    allow_same_day_booking = models.BooleanField(
        default=True,
        help_text="¿Permitir reservas el mismo día?"
    )
    
    # ============================================================================
    # CONFIGURACIÓN DE NOTIFICACIONES
    # ============================================================================
    
    send_appointment_reminders = models.BooleanField(
        default=True,
        help_text="¿Enviar recordatorios de citas por email/SMS?"
    )
    
    reminder_hours_before = models.IntegerField(
        default=24,
        validators=[MinValueValidator(1), MaxValueValidator(168)],
        help_text="Horas antes de la cita para enviar recordatorio (1-168)"
    )
    
    send_confirmation_immediately = models.BooleanField(
        default=True,
        help_text="¿Enviar confirmación inmediata al agendar?"
    )
    
    allow_online_cancellation = models.BooleanField(
        default=True,
        help_text="¿Permitir cancelación online de citas?"
    )
    
    min_cancellation_hours = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(48)],
        help_text="Horas mínimas antes de la cita para poder cancelar (0-48)"
    )
    
    # ============================================================================
    # METADATOS
    # ============================================================================
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración de Slots'
        verbose_name_plural = 'Configuraciones de Slots'
        db_table = 'admin_module_establishmentslotconfiguration'
    
    def __str__(self):
        return f"Configuración de {self.establishment.name_est}"

    def get_slot_duration_display(self):
        """Devuelve la duración formateada para mostrar"""
        if self.default_slot_duration >= 60:
            hours = self.default_slot_duration // 60
            minutes = self.default_slot_duration % 60
            if minutes > 0:
                return f"{hours}h {minutes}min"
            return f"{hours}h"
        return f"{self.default_slot_duration}min"