from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ProductCategory, 
    Product, 
    ProductComposition, 
    StockMovement, 
    ProductEstablishment
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'parent_category', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']


class ProductCompositionInline(admin.TabularInline):
    model = ProductComposition
    fk_name = 'parent_product'
    extra = 1
    fields = ['component_product', 'quantity_needed', 'unit_of_measure', 'notes']


class ProductEstablishmentInline(admin.TabularInline):
    model = ProductEstablishment
    extra = 0
    readonly_fields = ['current_stock', 'available_stock']
    fields = ['establishment', 'current_stock', 'reserved_stock', 'available_stock', 'location']

    def available_stock(self, obj):
        if obj.pk:
            return obj.available_stock
        return 0
    available_stock.short_description = 'Stock Disponible'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'internal_reference', 'category', 'product_type', 
        'sale_price', 'current_stock_display', 'stock_status', 'is_active'
    ]
    list_filter = [
        'category__category_type', 'product_type', 'is_active', 
        'track_inventory', 'created_at'
    ]
    search_fields = ['name', 'internal_reference', 'barcode', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'current_stock_display']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'internal_reference', 'barcode', 'description', 'category', 'product_type')
        }),
        ('Precios', {
            'fields': ('cost_price', 'sale_price', 'unit_of_measure')
        }),
        ('Inventario', {
            'fields': ('track_inventory', 'minimum_stock', 'maximum_stock', 'current_stock_display'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ProductCompositionInline, ProductEstablishmentInline]
    
    def current_stock_display(self, obj):
        if obj.pk and obj.track_inventory:
            stock = obj.current_stock
            return f"{stock} {obj.unit_of_measure}"
        return "N/A"
    current_stock_display.short_description = 'Stock Actual'
    
    def stock_status(self, obj):
        if not obj.track_inventory:
            return format_html('<span style="color: gray;">Sin inventario</span>')
        
        if obj.pk:
            if obj.is_low_stock:
                return format_html('<span style="color: red;">Stock Bajo</span>')
            else:
                return format_html('<span style="color: green;">Stock OK</span>')
        return "Nuevo"
    stock_status.short_description = 'Estado Stock'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo producto
            obj.created_by = request.user
        else:  # Si es una actualización
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductComposition)
class ProductCompositionAdmin(admin.ModelAdmin):
    list_display = ['parent_product', 'component_product', 'quantity_needed', 'unit_of_measure']
    list_filter = ['parent_product__category', 'component_product__category']
    search_fields = ['parent_product__name', 'component_product__name']
    autocomplete_fields = ['parent_product', 'component_product']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'product', 'establishment', 'movement_type', 
        'reason', 'quantity', 'unit_cost', 'total_cost_display', 'created_by'
    ]
    list_filter = [
        'movement_type', 'reason', 'establishment', 'created_at',
        'product__category'
    ]
    search_fields = ['product__name', 'reference', 'notes']
    readonly_fields = ['created_at', 'total_cost_display']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('product', 'establishment', 'movement_type', 'reason')
        }),
        ('Cantidades y Costos', {
            'fields': ('quantity', 'unit_cost', 'total_cost_display')
        }),
        ('Referencias', {
            'fields': ('reference', 'notes')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def total_cost_display(self, obj):
        if obj.pk:
            return f"${obj.total_cost:,.2f}"
        return "$0.00"
    total_cost_display.short_description = 'Costo Total'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductEstablishment)
class ProductEstablishmentAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'establishment', 'current_stock', 'reserved_stock', 
        'available_stock_display', 'location', 'last_updated'
    ]
    list_filter = ['establishment', 'product__category', 'last_updated']
    search_fields = ['product__name', 'establishment__name', 'location']
    readonly_fields = ['last_updated', 'available_stock_display']
    
    def available_stock_display(self, obj):
        return f"{obj.available_stock} {obj.product.unit_of_measure}"
    available_stock_display.short_description = 'Stock Disponible'
