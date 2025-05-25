from django.db import models

# Create your models here.


from django.db import models
from Login_Module.models import Usuario
from admin_module.models import Establecimiento, Cita

class SolicitudCita(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_deseada = models.TimeField()
    servicios_solicitados = models.TextField(help_text="Lista de IDs de servicios solicitados separados por coma")
    comentario = models.TextField(blank=True, null=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitud de {self.cliente.username} - {self.fecha}"

class CalificacionBarbero(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    barbero = models.ForeignKey('barber_module.Barbero', on_delete=models.CASCADE)
    calificacion = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.barbero.usuario.username} - {self.calificacion} estrellas"

class HistorialCitasCliente(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)

    def __str__(self):
        return f"Historial - {self.cliente.username} - {self.cita.id}"

class PerfilCliente(models.Model):
    cliente = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    preferencias = models.TextField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.cliente.username}"
