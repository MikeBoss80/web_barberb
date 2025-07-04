
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
