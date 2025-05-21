from django.db import models

# Create your models here.

from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Para guardar hashes seguros

    class Meta:
        db_table = 'tb_users'  # Nombre real de la tabla en la base de datos

    def __str__(self):
        return self.usuario




