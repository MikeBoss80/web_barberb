# Generated manually for data migration

from django.db import migrations


def migrate_service_data(apps, schema_editor):
    """
    Migra los datos del campo 'service' (ProductEstablishment) 
    a los nuevos campos 'product' y 'establishment'
    """
    ServiceDate = apps.get_model('services_module', 'ServiceDate')
    
    # Procesar todas las citas existentes
    citas_migradas = 0
    citas_sin_service = 0
    
    for cita in ServiceDate.objects.all():
        if cita.service:
            # ProductEstablishment tiene referencias a product y establishment
            cita.product = cita.service.product
            cita.establishment = cita.service.establishment
            cita.save(update_fields=['product', 'establishment'])
            citas_migradas += 1
        else:
            citas_sin_service += 1
    
    print(f"✓ Migración completada:")
    print(f"  - Citas migradas: {citas_migradas}")
    print(f"  - Citas sin servicio: {citas_sin_service}")


def reverse_migration(apps, schema_editor):
    """
    Reversión de la migración (copiar de product/establishment a service)
    Nota: Esta reversión puede no ser perfecta si hay múltiples ProductEstablishment
    para la misma combinación de product y establishment
    """
    ServiceDate = apps.get_model('services_module', 'ServiceDate')
    ProductEstablishment = apps.get_model('product', 'ProductEstablishment')
    
    for cita in ServiceDate.objects.all():
        if cita.product and cita.establishment and not cita.service:
            # Intentar encontrar el ProductEstablishment correspondiente
            try:
                product_est = ProductEstablishment.objects.get(
                    product=cita.product,
                    establishment=cita.establishment
                )
                cita.service = product_est
                cita.save(update_fields=['service'])
            except ProductEstablishment.DoesNotExist:
                print(f"⚠ No se encontró ProductEstablishment para cita {cita.id}")
            except ProductEstablishment.MultipleObjectsReturned:
                # Si hay múltiples, tomar el primero
                product_est = ProductEstablishment.objects.filter(
                    product=cita.product,
                    establishment=cita.establishment
                ).first()
                cita.service = product_est
                cita.save(update_fields=['service'])


class Migration(migrations.Migration):

    dependencies = [
        ('services_module', '0003_servicedate_establishment_servicedate_product_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_service_data, reverse_migration),
    ]
