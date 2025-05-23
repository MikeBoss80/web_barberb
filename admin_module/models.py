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
    


# admin_module/models.py
from django.db import models
from django.core.validators import MinValueValidator

class Producto(models.Model):
    CATEGORIAS = [
        ('COS', 'Cosmético'),
        ('HER', 'Herramienta'),
        ('DES', 'Desechable'),
        ('EQU', 'Equipo'),
    ]
    
    UNIDADES = [
        ('UND', 'Unidades'),
        ('LTS', 'Litros'),
        ('ML', 'Mililitros'),
        ('GR', 'Gramos'),
    ]
    
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=3, choices=CATEGORIAS)
    cantidad = models.IntegerField(validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    unidad = models.CharField(max_length=3, choices=UNIDADES, default='UND')
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        editable=False
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Productos"
        ordering = ['-fecha_actualizacion']
