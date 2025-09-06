from django.db import migrations

def create_initial_categories(apps, schema_editor):
    Category = apps.get_model('admin_module', 'Category')

    categorias = [
        {
            'name': 'Almacenable',
            'description': 'Productos físicos que pueden mantenerse en inventario durante largos períodos sin deteriorarse. Ej: tijeras, máquinas de afeitar, toallas.'
        },
        {
            'name': 'Consumible',
            'description': 'Insumos que se agotan con el uso frecuente y deben reponerse regularmente. Ej: espumas, cremas, lociones.'
        },
        {
            'name': 'Servicio',
            'description': 'Actividades o atenciones brindadas directamente al cliente. Ej: corte, afeitado, limpieza facial.'
        },
    ]

    for cat in categorias:
        Category.objects.get_or_create(name=cat['name'], defaults={'description': cat['description']})

class Migration(migrations.Migration):

    dependencies = [
       ('admin_module', '0005_create_initial_establishments'),  
    ]

    operations = [
        migrations.RunPython(create_initial_categories),
    ]
