# Generated migration for creating default product categories

from django.db import migrations


def create_default_categories(apps, schema_editor):
    """
    Crea las 3 categorías base del sistema
    """
    ProductCategory = apps.get_model('product', 'ProductCategory')
    
    categories_data = [
        {
            'name': 'Almacenable',
            'description': 'Productos físicos que se almacenan en inventario (herramientas, accesorios, etc.)',
            'category_type': 'storable',
            'is_active': True
        },
        {
            'name': 'Servicio',
            'description': 'Servicios que no requieren inventario (cortes, afeitados, tratamientos)',
            'category_type': 'service',
            'is_active': True
        },
        {
            'name': 'No Contable',
            'description': 'Productos consumibles que no se controlan en inventario (gel, shampoo, desinfectantes)',
            'category_type': 'consumable',
            'is_active': True
        }
    ]
    
    for cat_data in categories_data:
        ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'category_type': cat_data['category_type'],
                'is_active': cat_data['is_active']
            }
        )


def remove_default_categories(apps, schema_editor):
    """
    Elimina las categorías base en caso de rollback
    """
    ProductCategory = apps.get_model('product', 'ProductCategory')
    
    category_names = ['Almacenable', 'Servicio', 'No Contable']
    ProductCategory.objects.filter(name__in=category_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]
