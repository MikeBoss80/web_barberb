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
    name = models.CharField(max_length=50)
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

# Tabla: admin_module_establishment
class Establishment(models.Model):
    name_est = models.CharField(max_length=50)
    address_est = models.CharField(max_length=80)
    city_est = models.CharField(max_length=20)
    country_est = models.CharField(max_length=20)
    phone_est = models.CharField(max_length=20)
    email_est = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    lat_est = models.DecimalField(max_digits=9, decimal_places=6)
    lng_est = models.DecimalField(max_digits=9, decimal_places=6)
    img_est = models.ImageField(upload_to="establishments/")
    qa_average_est = models.FloatField(default=5.0)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=True)
    id_admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_est")


    def __str__(self):
        return self.name_est

# Tabla: admin_module_services
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    active = models.BooleanField(default=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# Relación muchos a muchos entre establecimiento y servicios
class EstablishmentService(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

# Tabla: admin_module_inventory
class Inventory(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)




