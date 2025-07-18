from django.db import migrations, models

def create_initial_services(apps, schema_editor):
    Service = apps.get_model('admin_module', 'Service')
    Establishment = apps.get_model('admin_module', 'Establishment')
    EstablishmentService = apps.get_model('admin_module', 'EstablishmentService')
    Category = apps.get_model('admin_module', 'Category')

    # Obtener la categoría "Servicio"
    try:
        servicio_cat = Category.objects.get(name='Servicio')
    except Category.DoesNotExist:
        return  # Evita error si por alguna razón aún no se ha creado

    # Obtener establecimientos
    est1 = Establishment.objects.get(name_est='Establecimiento 1')
    est2 = Establishment.objects.get(name_est='Establecimiento 2')

    # Servicios para Establecimiento 1
    servicios_est1 = [
        {
            'name': 'Corte Clásico',
            'desc': 'Corte de cabello tradicional con tijeras y máquina.',
            'precio': 20000,
            'duracion': 30,
        },
        {
            'name': 'Afeitado Profesional',
            'desc': 'Afeitado al ras con toalla caliente.',
            'precio': 15000,
            'duracion': 20,
        },
        {
            'name': 'Limpieza Facial Express',
            'desc': 'Limpieza rápida con productos dermatológicos.',
            'precio': 30000,
            'duracion': 25,
        }
    ]

    # Servicios para Establecimiento 2
    servicios_est2 = [
        {
            'name': 'Corte Fade',
            'desc': 'Corte degradado con estilo moderno.',
            'precio': 25000,
            'duracion': 35,
        },
        {
            'name': 'Barba Estilizada',
            'desc': 'Perfilado y diseño de barba personalizado.',
            'precio': 18000,
            'duracion': 20,
        },
        {
            'name': 'Mascarilla Facial',
            'desc': 'Aplicación de mascarilla hidratante y limpieza profunda.',
            'precio': 35000,
            'duracion': 30,
        }
    ]

    def crear_servicios(servicios, establecimiento):
        for data in servicios:
            service, _ = Service.objects.get_or_create(
                name_service=data['name'],
                defaults={
                    'description_service': data['desc'],
                    'price_service': data['precio'],
                    'duration': data['duracion'],
                    'active': True,
                    'category': servicio_cat
                }
            )
            EstablishmentService.objects.get_or_create(
                establishment=establecimiento,
                service=service
            )

    crear_servicios(servicios_est1, est1)
    crear_servicios(servicios_est2, est2)

class Migration(migrations.Migration):

    dependencies = [
        ('admin_module', '0006_create_initial_categorys'),
    ]

    operations = [
        migrations.RunPython(create_initial_services),
    ]
