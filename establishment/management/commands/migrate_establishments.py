from django.core.management.base import BaseCommand
from django.db import transaction
from admin_module.models import Establishment as OldEstablishment
from establishment.models import Establishment as NewEstablishment
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Migra datos de admin_module.Establishment a establishment.Establishment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta sin hacer cambios reales (solo muestra qué se haría)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: No se harán cambios reales'))
        
        # Contar registros
        old_count = OldEstablishment.objects.count()
        new_count = NewEstablishment.objects.count()
        
        self.stdout.write(f'Establecimientos en admin_module: {old_count}')
        self.stdout.write(f'Establecimientos en establishment: {new_count}')
        
        if old_count == 0:
            self.stdout.write(self.style.SUCCESS('No hay establecimientos que migrar.'))
            return
        
        migrated = 0
        skipped = 0
        
        with transaction.atomic():
            for old_est in OldEstablishment.objects.all():
                # Verificar si ya existe
                existing = NewEstablishment.objects.filter(
                    name_est=old_est.name_est,
                    id_admin=old_est.id_admin
                ).first()
                
                if existing:
                    self.stdout.write(f'SKIP: {old_est.name_est} ya existe')
                    skipped += 1
                    continue
                
                if not dry_run:
                    # Crear nuevo establecimiento
                    new_est = NewEstablishment.objects.create(
                        name_est=old_est.name_est,
                        address_est=old_est.address_est,
                        city_est=old_est.city_est,
                        country_est=old_est.country_est,
                        phone_est=old_est.phone_est,
                        email_est=old_est.email_est,
                        description=old_est.description,
                        lat_est=old_est.lat_est,
                        lng_est=old_est.lng_est,
                        img_est=old_est.img_est,
                        qa_average_est=old_est.qa_average_est,
                        created_date=old_est.created_date,
                        active=old_est.active,
                        id_admin=old_est.id_admin,
                    )
                    self.stdout.write(f'MIGRADO: {old_est.name_est} -> ID {new_est.id}')
                else:
                    self.stdout.write(f'SERÍA MIGRADO: {old_est.name_est}')
                
                migrated += 1
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Migración completada: {migrated} migrados, {skipped} omitidos'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY-RUN completado: {migrated} serían migrados, {skipped} serían omitidos'
                )
            )