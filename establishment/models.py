from django.db import models
from django.contrib.auth.models import User

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
    img_est = models.ImageField(upload_to="establishments/", null=True, blank=True)
    qa_average_est = models.FloatField(default=5.0)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=True)
    id_admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_est")

    class Meta:
        db_table = 'establishment'
        
    def __str__(self):
        return self.name_est
    
