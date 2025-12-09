"""
Script para poblar datos iniciales del módulo de productos
Ejecutar con: python manage.py shell < product/populate_data.py
"""

from product.models import ProductCategory, Product, ProductEstablishment
from establishment.models import Establishment
from django.contrib.auth.models import User
from decimal import Decimal

# Crear categorías básicas (solo 3 tipos según el modelo)
print("Creando categorías de productos...")

categories_data = [
    {
        'name': 'Almacenable',
        'description': 'Productos físicos que se almacenan en inventario (herramientas, accesorios, etc.)',
        'category_type': 'storable'
    },
    {
        'name': 'Servicio',
        'description': 'Servicios que no requieren inventario (cortes, afeitados, tratamientos)',
        'category_type': 'service'
    },
    {
        'name': 'No Contable',
        'description': 'Productos consumibles que no se controlan en inventario (gel, shampoo, desinfectantes)',
        'category_type': 'consumable'
    }
]

for cat_data in categories_data:
    category, created = ProductCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={
            'description': cat_data['description'],
            'category_type': cat_data['category_type']
        }
    )
    if created:
        print(f"✓ Categoría creada: {category.name}")
    else:
        print(f"- Categoría ya existe: {category.name}")

# Obtener primer usuario para asignar como creador
try:
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.first()
except:
    admin_user = None

print(f"\nUsuario asignado como creador: {admin_user}")

# Crear productos de ejemplo
print("\nCreando productos de ejemplo...")

products_data = [
    # ALMACENABLES - Productos físicos con control de inventario
    {
        'name': 'Máquina de Corte Wahl Senior',
        'internal_reference': 'WAHL-001',
        'description': 'Máquina de corte profesional con motor rotativo',
        'category': 'Almacenable',
        'cost_price': Decimal('150.00'),
        'sale_price': Decimal('200.00'),
        'minimum_stock': 2,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Tijeras de Corte 6.5"',
        'internal_reference': 'TIJ-001',
        'description': 'Tijeras profesionales de acero japonés',
        'category': 'Almacenable',
        'cost_price': Decimal('80.00'),
        'sale_price': Decimal('120.00'),
        'minimum_stock': 5,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Peine de Carbono Profesional',
        'internal_reference': 'PEI-001',
        'description': 'Peine antiestático de carbono',
        'category': 'Almacenable',
        'cost_price': Decimal('3.00'),
        'sale_price': Decimal('8.00'),
        'minimum_stock': 25,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Toalla de Microfibra',
        'internal_reference': 'TOA-001',
        'description': 'Toalla de secado rápido para barbería',
        'category': 'Almacenable',
        'cost_price': Decimal('4.00'),
        'sale_price': Decimal('10.00'),
        'minimum_stock': 30,
        'unit_of_measure': 'unidad'
    },
    
    # SERVICIOS - Sin control de inventario
    {
        'name': 'Corte Clásico',
        'internal_reference': 'SERV-001',
        'description': 'Corte de cabello clásico masculino',
        'category': 'Servicio',
        'cost_price': Decimal('5.00'),
        'sale_price': Decimal('15.00'),
        'track_inventory': False,
        'unit_of_measure': 'servicio'
    },
    {
        'name': 'Afeitado Completo',
        'internal_reference': 'SERV-002',
        'description': 'Afeitado completo con navaja y toallas calientes',
        'category': 'Servicio',
        'cost_price': Decimal('3.00'),
        'sale_price': Decimal('20.00'),
        'track_inventory': False,
        'unit_of_measure': 'servicio'
    },
    {
        'name': 'Tratamiento Capilar',
        'internal_reference': 'SERV-003',
        'description': 'Tratamiento hidratante para el cabello',
        'category': 'Servicio',
        'cost_price': Decimal('8.00'),
        'sale_price': Decimal('25.00'),
        'track_inventory': False,
        'unit_of_measure': 'servicio'
    },
    
    # NO CONTABLES - Productos consumibles sin control estricto de inventario
    {
        'name': 'Gel Fijador Fuerte 500ml',
        'internal_reference': 'GEL-001',
        'description': 'Gel de fijación fuerte para peinados',
        'category': 'No Contable',
        'cost_price': Decimal('8.00'),
        'sale_price': Decimal('15.00'),
        'minimum_stock': 0,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Shampoo Anticaspa 1L',
        'internal_reference': 'SHA-001',
        'description': 'Shampoo medicado para caspa',
        'category': 'No Contable',
        'cost_price': Decimal('12.00'),
        'sale_price': Decimal('22.00'),
        'minimum_stock': 0,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Aftershave Lotion 200ml',
        'internal_reference': 'AFS-001',
        'description': 'Loción aftershave con aloe vera',
        'category': 'No Contable',
        'cost_price': Decimal('6.00'),
        'sale_price': Decimal('12.00'),
        'minimum_stock': 0,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Barbicida Desinfectante 1L',
        'internal_reference': 'BAR-001',
        'description': 'Desinfectante para herramientas de barbería',
        'category': 'No Contable',
        'cost_price': Decimal('8.00'),
        'sale_price': Decimal('16.00'),
        'minimum_stock': 0,
        'unit_of_measure': 'unidad'
    }
]

for prod_data in products_data:
    try:
        # Buscar la categoría
        category = ProductCategory.objects.get(name=prod_data['category'])
        
        product, created = Product.objects.get_or_create(
            internal_reference=prod_data['internal_reference'],
            defaults={
                'name': prod_data['name'],
                'description': prod_data['description'],
                'category': category,
                'cost_price': prod_data['cost_price'],
                'sale_price': prod_data['sale_price'],
                'minimum_stock': prod_data.get('minimum_stock', 0),
                'unit_of_measure': prod_data['unit_of_measure'],
                'track_inventory': prod_data.get('track_inventory', True),
                'created_by': admin_user
            }
        )
        
        if created:
            print(f"✓ Producto creado: {product.name}")
        else:
            print(f"- Producto ya existe: {product.name}")
            
    except ProductCategory.DoesNotExist:
        print(f"✗ Error: Categoría '{prod_data['category']}' no encontrada")
    except Exception as e:
        print(f"✗ Error creando producto '{prod_data['name']}': {e}")

print("\n¡Datos de ejemplo creados exitosamente!")
print(f"Categorías totales: {ProductCategory.objects.count()}")
print(f"Productos totales: {Product.objects.count()}")

# Crear relaciones ProductEstablishment
print("\nCreando relaciones Producto-Establecimiento...")

# Obtener todos los establecimientos
establishments = Establishment.objects.all()

if establishments.exists():
    print(f"Establecimientos encontrados: {establishments.count()}")
    
    # Para cada producto creado, crear stock en cada establecimiento
    created_products = Product.objects.all()
    
    for product in created_products:
        for establishment in establishments:
            # Definir stock inicial según el tipo de categoría
            if product.category.category_type == 'storable':
                # Productos almacenables tienen stock inicial
                initial_stock = product.minimum_stock * 2 if product.minimum_stock > 0 else 10
            elif product.category.category_type == 'consumable':
                # Productos no contables pueden tener stock informativo
                initial_stock = 5
            else:
                # Servicios no tienen stock
                initial_stock = 0
            
            product_est, created = ProductEstablishment.objects.get_or_create(
                product=product,
                establishment=establishment,
                defaults={
                    'current_stock': initial_stock,
                    'reserved_stock': 0,
                    'location': 'Almacén Principal'
                }
            )
            
            if created:
                print(f"✓ Stock creado: {product.name} en {establishment.name_est} - Stock: {initial_stock}")
            else:
                print(f"- Stock ya existe: {product.name} en {establishment.name_est}")
else:
    print("⚠ No se encontraron establecimientos. Ejecuta primero las migraciones de establishment.")

print(f"\nRelaciones Producto-Establecimiento totales: {ProductEstablishment.objects.count()}")