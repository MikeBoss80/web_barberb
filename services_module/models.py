
from django.db import models
from admin_module.models import EstablishmentService, Day
from django.contrib.auth.models import User


# Tabla: services_module_dates
class ServiceDate(models.Model):
    service = models.ForeignKey(EstablishmentService, on_delete=models.CASCADE, related_name="service_dates")
    date = models.DateTimeField()
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_dates")
    barber = models.ForeignKey(User, on_delete=models.CASCADE, related_name="barber_dates")
    status = models.CharField(max_length=10)
    comments = models.TextField()
    price_total = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.service} on {self.date}"

# Tabla intermedia: services_module_dates_x_dates (relación muchos a muchos con días)
class ServiceDateDay(models.Model):
    service_date = models.ForeignKey(ServiceDate, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    
""" 
class SolicitudCita(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, null=True)
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
 """