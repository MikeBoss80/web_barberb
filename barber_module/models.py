# Create your models here.
from django.db import models
from establishment.models import Establishment
from django.contrib.auth.models import User


# Tipos de solicitud
TIPO_SOLICITUD_CHOICES = [
    ('permiso', 'Permiso Personal'),
    ('vacaciones', 'Vacaciones'),
    ('incapacidad', 'Incapacidad Médica'),
    ('licencia', 'Licencia (ej. luto u otras razones)'),
]

# Estados posibles de la solicitud
ESTADO_SOLICITUD_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('aprobada', 'Aprobada'),
    ('rechazada', 'Rechazada'),
]

class BarberRequest(models.Model):
    # Relación con el barbero que hace la solicitud
    barber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_barbero')
    # Relación con el establecimiento donde trabaja el barbero
    establecimiento = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name='solicitudes_barbero')
    # Tipo de solicitud (permiso, vacaciones, etc.)
    tipo = models.CharField(max_length=20, choices=TIPO_SOLICITUD_CHOICES)
    # Fechas de inicio y fin de la solicitud
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    # Comentario del barbero (opcional)
    comentario = models.TextField(blank=True, null=True)
    # Estado de la solicitud
    estado = models.CharField(max_length=20, choices=ESTADO_SOLICITUD_CHOICES, default=ESTADO_SOLICITUD_CHOICES[0][0])
    # Fecha de creación y respuesta
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)
    # Respuesta del administrador
    respuesta_admin = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Solicitud de {self.barber.first_name} {self.barber.last_name} - {self.get_tipo_display()} ({self.get_estado_display()})"

    class Meta:
        verbose_name = "Solicitud de Barbero"
        verbose_name_plural = "Solicitudes de Barberos"
        ordering = ['-fecha_solicitud']