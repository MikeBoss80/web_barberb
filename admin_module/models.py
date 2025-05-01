from django.db import models

# Create your models here.
class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    cliente = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()
    barbero = models.CharField(max_length=100)  # Podrías hacer una relación a un modelo Barbero si existe
    servicio = models.CharField(max_length=100)  # Lo mismo aquí si tienes modelo Servicio
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # Para calcular ingresos

    def __str__(self):
        return f'{self.cliente} - {self.fecha} {self.hora}'