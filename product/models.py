from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class ProductCategory(models.Model):
    """
    Categorías de productos con diferentes tipos según su naturaleza contable
    """
    CATEGORY_TYPES = [
        ('storable', 'Almacenable'),      # Productos físicos que se almacenan
        ('service', 'Servicio'),          # Servicios que no requieren inventario
        ('consumable', 'No Contable'),    # Productos que se consumen (ej: gel, papel)
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    category_type = models.CharField(
        max_length=20, 
        choices=CATEGORY_TYPES, 
        default='storable',
        verbose_name="Tipo de categoría"
    )
    parent_category = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='subcategories',
        verbose_name="Categoría padre"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Product(models.Model):
    """
    Modelo principal de productos
    """
    PRODUCT_TYPES = [
        ('simple', 'Producto Simple'),
        ('composite', 'Producto Compuesto'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre del producto")
    internal_reference = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="Referencia interna"
    )
    barcode = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="Código de barras"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    # Información de categoría
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Categoría"
    )
    
    # Tipo de producto
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES,
        default='simple',
        verbose_name="Tipo de producto"
    )
    
    # Precios y costos
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio de costo"
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio de venta"
    )
    
    # Información de inventario (solo para productos almacenables)
    track_inventory = models.BooleanField(
        default=True, 
        verbose_name="Controlar inventario"
    )
    minimum_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock mínimo"
    )
    maximum_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock máximo",
        help_text="0 = sin límite máximo"
    )
    
    # Unidades de medida
    unit_of_measure = models.CharField(
        max_length=20,
        default='unidad',
        verbose_name="Unidad de medida",
        help_text="ej: unidad, litro, metro, gramo"
    )
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_by = models.ForeignKey(
        User, 
        related_name='products_created', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        User, 
        related_name='products_updated', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def current_stock(self):
        """Calcula el stock actual del producto"""
        if not self.track_inventory or self.category.category_type != 'storable':
            return 0
        
        # Suma todas las entradas y resta todas las salidas
        from django.db.models import Sum, Q
        
        entries = StockMovement.objects.filter(
            product=self,
            movement_type__in=['in', 'adjustment_in']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        exits = StockMovement.objects.filter(
            product=self,
            movement_type__in=['out', 'adjustment_out']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return entries - exits

    @property
    def is_low_stock(self):
        """Verifica si el producto tiene stock bajo"""
        if not self.track_inventory:
            return False
        return self.current_stock <= self.minimum_stock

    def save(self, *args, **kwargs):
        # Si es un producto de servicio o consumible, no controlar inventario
        if self.category.category_type in ['service', 'consumable']:
            self.track_inventory = False
        super().save(*args, **kwargs)


class ProductComposition(models.Model):
    """
    Lista de materiales para productos compuestos (BOM simplificada)
    """
    parent_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='components',
        verbose_name="Producto padre",
        limit_choices_to={'product_type': 'composite'}
    )
    component_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='used_in',
        verbose_name="Componente"
    )
    quantity_needed = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Cantidad necesaria"
    )
    unit_of_measure = models.CharField(
        max_length=20,
        verbose_name="Unidad de medida"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas"
    )

    class Meta:
        verbose_name = "Composición de Producto"
        verbose_name_plural = "Composiciones de Productos"
        unique_together = ['parent_product', 'component_product']

    def __str__(self):
        return f"{self.parent_product.name} -> {self.quantity_needed} {self.unit_of_measure} de {self.component_product.name}"


class StockMovement(models.Model):
    """
    Movimientos de inventario (entradas, salidas, ajustes)
    """
    MOVEMENT_TYPES = [
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('adjustment_in', 'Ajuste Positivo'),
        ('adjustment_out', 'Ajuste Negativo'),
        ('transfer', 'Transferencia'),
    ]

    MOVEMENT_REASONS = [
        ('purchase', 'Compra'),
        ('sale', 'Venta'),
        ('return', 'Devolución'),
        ('damaged', 'Producto dañado'),
        ('expired', 'Producto vencido'),
        ('inventory_adjustment', 'Ajuste de inventario'),
        ('initial_stock', 'Stock inicial'),
        ('production', 'Producción'),
        ('consumption', 'Consumo'),
        ('transfer', 'Transferencia'),
        ('other', 'Otro'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name="Producto"
    )
    establishment = models.ForeignKey(
        'establishment.Establishment',
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name="Establecimiento"
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        verbose_name="Tipo de movimiento"
    )
    reason = models.CharField(
        max_length=30,
        choices=MOVEMENT_REASONS,
        verbose_name="Motivo"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Cantidad"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Costo unitario"
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Referencia",
        help_text="Número de factura, orden, etc."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    # Metadatos
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    @property
    def total_cost(self):
        """Calcula el costo total del movimiento"""
        return self.quantity * self.unit_cost


class ProductEstablishment(models.Model):
    """
    Stock de productos por establecimiento
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='establishments_stock'
    )
    establishment = models.ForeignKey(
        'establishment.Establishment',
        on_delete=models.CASCADE,
        related_name='products_stock'
    )
    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
        verbose_name="Stock actual"
    )
    reserved_stock = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0.000,
        verbose_name="Stock reservado"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ubicación",
        help_text="Estante, anaquel, etc."
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Stock por Establecimiento"
        verbose_name_plural = "Stock por Establecimientos"
        unique_together = ['product', 'establishment']

    def __str__(self):
        return f"{self.product.name} en {self.establishment.name}: {self.current_stock}"

    @property
    def available_stock(self):
        """Stock disponible (actual - reservado)"""
        return self.current_stock - self.reserved_stock
