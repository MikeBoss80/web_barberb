from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('admin', 'Administrador'),
        ('barbero', 'Barbero'),
        ('cliente', 'Cliente'),
    ]

    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    
    groups = models.ManyToManyField(
        Group,
        related_name='usuario_set',  # Evita conflicto con auth.User.groups
        blank=True,
        verbose_name='grupos',
        help_text='Grupos a los que pertenece este usuario.'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuario_permissions_set',  # Evita conflicto con auth.User.user_permissions
        blank=True,
        verbose_name='permisos de usuario',
        help_text='Permisos específicos para este usuario.'
    )

class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    documento_identidad = models.CharField(max_length=20)

    def __str__(self):
        return f"Administrador: {self.usuario.username}"

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cliente: {self.usuario.username}"

# Barbero va en barber_module con OneToOne hacia Usuario
