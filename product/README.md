# Módulo de Productos - BarberB

Este módulo maneja la gestión completa de productos e inventario para el sistema BarberB, siguiendo un esquema simplificado inspirado en Odoo.

## Características Principales

### 1. Categorización de Productos
- **Almacenables**: Productos físicos que requieren control de inventario
- **Servicios**: Servicios que no requieren inventario (cortes, afeitados)
- **No Contables**: Productos consumibles que se usan pero no se controlan estrictamente

### 2. Gestión de Inventario
- Control de entradas, salidas y ajustes
- Stock por establecimiento
- Alertas de stock mínimo
- Reservas de stock
- Histórico completo de movimientos

### 3. Productos Compuestos
- Lista de materiales (BOM) simplificada
- Cálculo automático de costos basado en componentes
- Verificación de disponibilidad de componentes
- Consumo automático al producir

## Modelos Principales

### ProductCategory
Categorías con tipos específicos que determinan el comportamiento del inventario.

### Product
Modelo principal con información completa del producto, precios, stock mínimo y configuración de inventario.

### ProductComposition
Lista de materiales para productos compuestos (como kits de servicios).

### StockMovement
Registro de todos los movimientos de inventario con trazabilidad completa.

### ProductEstablishment
Stock actual y reservado por establecimiento.

## Utilidades

### InventoryManager
Clase utilitaria para:
- Crear movimientos de stock
- Ajustar inventarios
- Reservar/liberar stock
- Reportes de stock bajo
- Sincronización de datos

### ProductCompositionManager
Gestión de productos compuestos:
- Cálculo de costos
- Verificación de componentes
- Consumo de materiales

## Comandos de Administración

### sync_stock
Sincroniza el stock calculado con el registrado:
```bash
python manage.py sync_stock
python manage.py sync_stock --product-id 1
python manage.py sync_stock --dry-run
```

### low_stock_report
Genera reportes de stock bajo:
```bash
python manage.py low_stock_report
python manage.py low_stock_report --establishment-id 1
python manage.py low_stock_report --export-csv
```

## Instalación y Configuración

1. El módulo ya está incluido en `INSTALLED_APPS` como `'product'`

2. Generar y aplicar migraciones:
```bash
python manage.py makemigrations product
python manage.py migrate product
```

3. Poblar datos de ejemplo:
```bash
python manage.py shell < product/populate_data.py
```

## API y Vistas

### URLs Principales
- `/product/` - Lista de productos
- `/product/product/<id>/` - Detalle de producto
- `/product/movements/` - Movimientos de inventario
- `/product/reports/low-stock/` - Reporte de stock bajo

### AJAX Endpoints
- `/product/ajax/stock/<product_id>/<establishment_id>/` - Obtener stock actual

## Formularios Incluidos

### ProductForm
Creación y edición de productos con validaciones automáticas.

### StockMovementForm
Registro de movimientos con filtros por productos que controlan inventario.

### QuickStockAdjustmentForm
Ajuste rápido de inventarios.

## Características Técnicas

### Validaciones Automáticas
- Productos de servicio no controlan inventario automáticamente
- Validación de referencias circulares en composiciones
- Validación de stock disponible para reservas

### Señales Django
- Actualización automática de stock al crear movimientos
- Sincronización al eliminar movimientos

### Permisos
Todas las vistas requieren login (`@login_required`)

## Integración con otros Módulos

### establishment
- Stock por establecimiento
- Filtros de reportes por local

### admin_module
- Integración con categorías existentes
- Usuarios para auditoría

## Desarrollo y Extensión

### Agregar nuevos tipos de movimiento
1. Modificar `MOVEMENT_TYPES` en `StockMovement`
2. Actualizar lógica en `InventoryManager.update_establishment_stock()`
3. Agregar opciones en formularios

### Campos personalizados
El modelo `Product` puede extenderse fácilmente agregando campos específicos del negocio.

### Reportes adicionales
Usar `InventoryManager` como base para nuevos reportes y análisis.

## Testing

Ejecutar tests del módulo:
```bash
python manage.py test product
```

Los tests cubren:
- Creación de modelos
- Propiedades calculadas
- Lógica de negocio básica
- Utilidades de inventario

## Notas de Implementación

- Todos los cálculos monetarios usan `Decimal` para precisión
- Stock se maneja con 3 decimales de precisión
- Auditoría completa con `created_by`, `updated_by` y timestamps
- Soft delete mediante campo `is_active`