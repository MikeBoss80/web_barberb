from django.db import models
from login_module.models import Usuario




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



class Establecimiento(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    telefono_contacto = models.CharField(max_length=20)
    correo_contacto = models.EmailField()
    descripcion = models.TextField(blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    imagen_destacada = models.ImageField(upload_to='establecimientos/', blank=True, null=True)
    medios_pago = models.CharField(max_length=255, help_text="Separados por coma, ej: Efectivo, Tarjeta, Nequi")
    calificacion_promedio = models.FloatField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class HorarioEstablecimiento(models.Model):
    DIAS_SEMANA = [
        ('LU', 'Lunes'), ('MA', 'Martes'), ('MI', 'Miércoles'),
        ('JU', 'Jueves'), ('VI', 'Viernes'), ('SA', 'Sábado'), ('DO', 'Domingo')
    ]
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE,  null=True)
    dia_semana = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    trabaja = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.establecimiento.nombre} - {self.get_dia_semana_display()}"

class Servicio(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion_min = models.PositiveIntegerField(help_text="Duración del servicio en minutos")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, null=True)
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_producto} ({self.establecimiento.nombre})"

class Cita(models.Model):
    ESTADOS_CITA = [
        ('confirmada', 'Confirmada'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='citas_cliente')
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, null=True)
    barbero = models.ForeignKey('barber_module.Barbero', on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_CITA)
    comentarios_cliente = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2 , default=0.00)

    def __str__(self):
        return f"Cita de {self.cliente.nombres} - {self.fecha}"

class CitaServicio(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cita} - {self.servicio.nombre}"

class CalificacionEstablecimiento(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE,null=True)
    calificacion = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.establecimiento.nombre} - {self.calificacion} estrellas"

class ConfiguracionEstablecimiento(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE,null=True)
    campo = models.CharField(max_length=100)
    valor = models.TextField()

    def __str__(self):
        return f"{self.establecimiento.nombre} - {self.campo}"

class FAQ(models.Model):
    TIPO_USUARIO = [
        ('admin', 'Administrador'),
        ('barbero', 'Barbero'),
        ('cliente', 'Cliente'),
    ]
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO)

    def __str__(self):
        return self.titulo
