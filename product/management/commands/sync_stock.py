"""
Comando para sincronizar el stock calculado con el stock registrado
"""
from django.core.management.base import BaseCommand
from product.models import Product, ProductEstablishment
from product.utils.inventory import InventoryManager
from establishment.models import Establishment


class Command(BaseCommand):
    help = 'Sincroniza el stock calculado basado en movimientos con el registrado en ProductEstablishment'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='ID específico de producto a sincronizar'
        )
        parser.add_argument(
            '--establishment-id',
            type=int,
            help='ID específico de establecimiento'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría sin hacer cambios'
        )
    
    def handle(self, *args, **options):
        products = Product.objects.filter(track_inventory=True, is_active=True)
        establishments = Establishment.objects.filter(active=True)
        
        # Filtrar por producto específico si se proporciona
        if options['product_id']:
            products = products.filter(id=options['product_id'])
            
        # Filtrar por establecimiento específico si se proporciona
        if options['establishment_id']:
            establishments = establishments.filter(id=options['establishment_id'])
        
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: No se realizarán cambios')
            )
        
        total_synced = 0
        total_differences = 0
        
        for product in products:
            for establishment in establishments:
                # Obtener stock calculado basado en movimientos
                calculated_stock = InventoryManager.get_current_stock(product, establishment)
                
                # Obtener o crear registro de stock por establecimiento
                stock_record, created = ProductEstablishment.objects.get_or_create(
                    product=product,
                    establishment=establishment,
                    defaults={'current_stock': calculated_stock}
                )
                
                if created:
                    self.stdout.write(
                        f"✓ Creado registro: {product.name} en {establishment.name} = {calculated_stock}"
                    )
                    total_synced += 1
                elif stock_record.current_stock != calculated_stock:
                    difference = calculated_stock - stock_record.current_stock
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ Diferencia encontrada: {product.name} en {establishment.name}\n"
                            f"   Registrado: {stock_record.current_stock}\n"
                            f"   Calculado: {calculated_stock}\n"
                            f"   Diferencia: {difference}"
                        )
                    )
                    
                    if not dry_run:
                        stock_record.current_stock = calculated_stock
                        stock_record.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"   ✓ Sincronizado")
                        )
                    
                    total_differences += 1
                    total_synced += 1
        
        # Resumen
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"Productos procesados: {products.count()}")
        self.stdout.write(f"Establecimientos procesados: {establishments.count()}")
        self.stdout.write(f"Registros sincronizados: {total_synced}")
        self.stdout.write(f"Diferencias encontradas: {total_differences}")
        
        if dry_run and total_differences > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\nEjecuta sin --dry-run para aplicar los {total_differences} cambios"
                )
            )
        elif total_differences == 0:
            self.stdout.write(
                self.style.SUCCESS("\n✓ Todos los stocks están sincronizados")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ {total_differences} registros sincronizados exitosamente")
            )