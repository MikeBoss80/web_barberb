"""
Script para poblar datos iniciales del módulo de productos
Ejecutar con: python manage.py shell < product/populate_data.py
"""

from product.models import ProductCategory, Product
from django.contrib.auth.models import User
from decimal import Decimal

# Crear categorías básicas
print("Creando categorías de productos...")

categories_data = [
    {
        'name': 'Herramientas de Corte',
        'description': 'Tijeras, máquinas de corte, navajas, etc.',
        'category_type': 'storable'
    },
    {
        'name': 'Productos para el Cabello',
        'description': 'Shampoos, acondicionadores, geles, ceras, etc.',
        'category_type': 'consumable'
    },
    {
        'name': 'Servicios de Barbería',
        'description': 'Cortes, afeitados, tratamientos, etc.',
        'category_type': 'service'
    },
    {
        'name': 'Productos de Cuidado Facial',
        'description': 'Cremas, lociones, aftershave, etc.',
        'category_type': 'consumable'
    },
    {
        'name': 'Accesorios',
        'description': 'Peines, cepillos, toallas, capas, etc.',
        'category_type': 'storable'
    },
    {
        'name': 'Productos de Limpieza',
        'description': 'Desinfectantes, toallitas, barbicida, etc.',
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
    # Herramientas de Corte
    {
        'name': 'Máquina de Corte Wahl Senior',
        'internal_reference': 'WAHL-001',
        'description': 'Máquina de corte profesional con motor rotativo',
        'category': 'Herramientas de Corte',
        'cost_price': Decimal('150.00'),
        'sale_price': Decimal('200.00'),
        'minimum_stock': 2,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Tijeras de Corte 6.5"',
        'internal_reference': 'TIJ-001',
        'description': 'Tijeras profesionales de acero japonés',
        'category': 'Herramientas de Corte',
        'cost_price': Decimal('80.00'),
        'sale_price': Decimal('120.00'),
        'minimum_stock': 5,
        'unit_of_measure': 'unidad'
    },
    
    # Productos para el Cabello
    {
        'name': 'Gel Fijador Fuerte 500ml',
        'internal_reference': 'GEL-001',
        'description': 'Gel de fijación fuerte para peinados',
        'category': 'Productos para el Cabello',
        'cost_price': Decimal('8.00'),
        'sale_price': Decimal('15.00'),
        'minimum_stock': 20,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Shampoo Anticaspa 1L',
        'internal_reference': 'SHA-001',
        'description': 'Shampoo medicado para caspa',
        'category': 'Productos para el Cabello',
        'cost_price': Decimal('12.00'),
        'sale_price': Decimal('22.00'),
        'minimum_stock': 15,
        'unit_of_measure': 'unidad'
    },
    
    # Servicios
    {
        'name': 'Corte Clásico',
        'internal_reference': 'SERV-001',
        'description': 'Corte de cabello clásico masculino',
        'category': 'Servicios de Barbería',
        'cost_price': Decimal('5.00'),
        'sale_price': Decimal('15.00'),
        'track_inventory': False,
        'unit_of_measure': 'servicio'
    },
    {
        'name': 'Afeitado Completo',
        'internal_reference': 'SERV-002',
        'description': 'Afeitado completo con navaja y toallas calientes',
        'category': 'Servicios de Barbería',
        'cost_price': Decimal('3.00'),
        'sale_price': Decimal('20.00'),
        'track_inventory': False,
        'unit_of_measure': 'servicio'
    },
    
    # Productos de Cuidado Facial
    {
        'name': 'Aftershave Lotion 200ml',
        'internal_reference': 'AFS-001',
        'description': 'Loción aftershave con aloe vera',
        'category': 'Productos de Cuidado Facial',
        'cost_price': Decimal('6.00'),
        'sale_price': Decimal('12.00'),
        'minimum_stock': 10,
        'unit_of_measure': 'unidad'
    },
    
    # Accesorios
    {
        'name': 'Peine de Carbono Profesional',
        'internal_reference': 'PEI-001',
        'description': 'Peine antiestático de carbono',
        'category': 'Accesorios',
        'cost_price': Decimal('3.00'),
        'sale_price': Decimal('8.00'),
        'minimum_stock': 25,
        'unit_of_measure': 'unidad'
    },
    {
        'name': 'Toalla de Microfibra',
        'internal_reference': 'TOA-001',
        'description': 'Toalla de secado rápido para barbería',
        'category': 'Accesorios',
        'cost_price': Decimal('4.00'),
        'sale_price': Decimal('10.00'),
        'minimum_stock': 30,
        'unit_of_measure': 'unidad'
    },
    
    # Productos de Limpieza
    {
        'name': 'Barbicida Desinfectante 1L',
        'internal_reference': 'BAR-001',
        'description': 'Desinfectante para herramientas de barbería',
        'category': 'Productos de Limpieza',
        'cost_price': Decimal('8.00'),
        'sale_price': Decimal('16.00'),
        'minimum_stock': 12,
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