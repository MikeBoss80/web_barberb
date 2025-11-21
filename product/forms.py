from django import forms
from django.core.exceptions import ValidationError
from .models import (
    ProductCategory, 
    Product, 
    ProductComposition, 
    StockMovement, 
    ProductEstablishment
)


class ProductCategoryForm(forms.ModelForm):
    """Formulario para crear/editar categorías de productos"""
    
    class Meta:
        model = ProductCategory
        fields = ['name', 'description', 'category_type', 'parent_category', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'category_type': forms.Select(attrs={'class': 'form-control'}),
            'parent_category': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_parent_category(self):
        """Validar que la categoría padre no sea la misma que se está editando"""
        parent = self.cleaned_data.get('parent_category')
        if parent and self.instance and parent == self.instance:
            raise ValidationError("Una categoría no puede ser su propia categoría padre.")
        return parent


class ProductForm(forms.ModelForm):
    """Formulario para crear/editar productos"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'internal_reference', 'barcode', 'description', 
            'category', 'product_type', 'cost_price', 'sale_price',
            'track_inventory', 'minimum_stock', 'maximum_stock',
            'unit_of_measure', 'is_active'
        ]
        labels = {
            'name': 'Nombre del Producto',
            'internal_reference': 'Referencia Interna',
            'barcode': 'Código de Barras',
            'description': 'Descripción',
            'category': 'Categoría',
            'product_type': 'Tipo de Producto',
            'cost_price': 'Precio de Costo',
            'sale_price': 'Precio de Venta',
            'track_inventory': 'Controlar Inventario',
            'minimum_stock': 'Stock Mínimo',
            'maximum_stock': 'Stock Máximo',
            'unit_of_measure': 'Unidad de Medida',
            'is_active': 'Activo',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre del producto'
            }),
            'internal_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código interno (opcional)'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de barras (opcional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'product_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'track_inventory': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'minimum_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'maximum_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0 (sin límite)'
            }),
            'unit_of_measure': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ej: unidad, litro, metro'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar categorías activas
        self.fields['category'].queryset = ProductCategory.objects.filter(is_active=True)
        
        # Configurar valores por defecto
        if not self.instance.pk:  # Solo para nuevos productos
            self.fields['track_inventory'].initial = True
            self.fields['is_active'].initial = True
            self.fields['unit_of_measure'].initial = 'unidad'

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        
        # Si la categoría es de servicio o consumible, no debe controlar inventario
        if category and category.category_type in ['service', 'consumable']:
            cleaned_data['track_inventory'] = False
            
        return cleaned_data


class ProductCompositionForm(forms.ModelForm):
    """Formulario para la composición de productos (lista de materiales)"""
    
    class Meta:
        model = ProductComposition
        fields = ['parent_product', 'component_product', 'quantity_needed', 'unit_of_measure', 'notes']
        widgets = {
            'parent_product': forms.Select(attrs={'class': 'form-control'}),
            'component_product': forms.Select(attrs={'class': 'form-control'}),
            'quantity_needed': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001'
            }),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas opcionales'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos compuestos para el padre
        self.fields['parent_product'].queryset = Product.objects.filter(
            product_type='composite',
            is_active=True
        )
        # Filtrar productos activos para componentes
        self.fields['component_product'].queryset = Product.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent_product')
        component = cleaned_data.get('component_product')
        
        # Evitar referencias circulares
        if parent and component and parent == component:
            raise ValidationError("Un producto no puede ser componente de sí mismo.")
            
        return cleaned_data


class StockMovementForm(forms.ModelForm):
    """Formulario para movimientos de inventario"""
    
    class Meta:
        model = StockMovement
        fields = [
            'product', 'establishment', 'movement_type', 'reason',
            'quantity', 'unit_cost', 'reference', 'notes'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'establishment': forms.Select(attrs={'class': 'form-control'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de factura, orden, etc.'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones del movimiento'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos que controlan inventario
        self.fields['product'].queryset = Product.objects.filter(
            track_inventory=True,
            is_active=True
        )


class QuickStockAdjustmentForm(forms.Form):
    """Formulario rápido para ajustes de inventario"""
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(track_inventory=True, is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Producto"
    )
    establishment = forms.ModelChoiceField(
        queryset=None,  # Se definirá en __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Establecimiento"
    )
    current_stock = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.001',
            'readonly': True
        }),
        label="Stock Actual"
    )
    new_stock = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.001'
        }),
        label="Nuevo Stock"
    )
    reason = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Motivo del ajuste'
        }),
        label="Motivo"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Importar aquí para evitar importaciones circulares
        from establishment.models import Establishment
        self.fields['establishment'].queryset = Establishment.objects.filter(active=True)


class LowStockReportForm(forms.Form):
    """Formulario para reportes de stock bajo"""
    
    establishment = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todos los establecimientos",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Establecimiento"
    )
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(
            category_type='storable',
            is_active=True
        ),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Categoría"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from establishment.models import Establishment
        self.fields['establishment'].queryset = Establishment.objects.filter(active=True)