from django.db import models

# Create your models here.
from django.db import models
from Login_Module.models import Usuario
from admin_module.models import Establecimiento

class Barbero(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    especialidades = models.TextField(blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='barberos/', blank=True, null=True)

    def __str__(self):
        return self.usuario.username

class HorarioBarbero(models.Model):
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=[(i, dia) for i, dia in enumerate(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.barbero.usuario.username} - {self.get_dia_semana_display()}"

class SolicitudCambioHorario(models.Model):
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True, null=True)
    nuevo_horario = models.TextField(help_text="Formato sugerido: día: inicio-fin;...", blank=True, null=True)

    def __str__(self):
        return f"Solicitud de cambio de horario - {self.barbero.usuario.username}"

class PerfilBarbero(models.Model):
    barbero = models.OneToOneField(Barbero, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, null=True)
    experiencia = models.PositiveIntegerField(help_text="Años de experiencia", blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.barbero.usuario.username}"

class SeguridadBarbero(models.Model):
    barbero = models.OneToOneField(Barbero, on_delete=models.CASCADE)
    pregunta_seguridad = models.CharField(max_length=255, blank=True, null=True)
    respuesta_seguridad = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Seguridad - {self.barbero.usuario.username}"
