from django.db import models
from django.contrib.auth.models import User, Group
from admin_module.models import Establishment


# Tabla: login_module_profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.BigIntegerField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=80)
    birth_date = models.DateField()
    document = models.CharField(max_length=80)
    data_complete = models.BooleanField(default=False)
    establishment = models.ForeignKey(Establishment, on_delete=models.SET_NULL, null=True)
    qa_average = models.FloatField()

    def __str__(self):
        return self.user.username