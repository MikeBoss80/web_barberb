"""
Comando para generar reporte de productos con stock bajo
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from product.utils.inventory import InventoryManager
from product.models import ProductCategory
from establishment.models import Establishment


class Command(BaseCommand):
    help = 'Genera un reporte de productos con stock bajo'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--establishment-id',
            type=int,
            help='ID específico de establecimiento'
        )
        parser.add_argument(
            '--category-id',
            type=int,
            help='ID específico de categoría'
        )
        parser.add_argument(
            '--export-csv',
            action='store_true',
            help='Exportar resultados a CSV'
        )
    
    def handle(self, *args, **options):
        establishment = None
        category = None
        
        # Filtros opcionales
        if options['establishment_id']:
            try:
                establishment = Establishment.objects.get(id=options['establishment_id'])
                self.stdout.write(f"Establecimiento: {establishment.name}")
            except Establishment.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Establecimiento con ID {options['establishment_id']} no existe")
                )
                return
        
        if options['category_id']:
            try:
                category = ProductCategory.objects.get(id=options['category_id'])
                self.stdout.write(f"Categoría: {category.name}")
            except ProductCategory.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Categoría con ID {options['category_id']} no existe")
                )
                return
        
        # Obtener productos con stock bajo
        low_stock_products = InventoryManager.get_low_stock_products(
            establishment=establishment,
            category=category
        )
        
        if not low_stock_products:
            self.stdout.write(
                self.style.SUCCESS("✓ No se encontraron productos con stock bajo")
            )
            return
        
        # Mostrar reporte
        self.stdout.write("\n" + "="*80)
        self.stdout.write(f"REPORTE DE STOCK BAJO - {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        self.stdout.write("="*80)
        
        # Cabecera
        self.stdout.write(
            f"{'PRODUCTO':<30} {'ESTABLECIMIENTO':<20} {'ACTUAL':<10} {'MÍNIMO':<10} {'DIFERENCIA':<10}"
        )
        self.stdout.write("-"*80)
        
        total_products = len(low_stock_products)
        critical_count = 0  # Stock cero o negativo
        
        # Datos para CSV si se solicita
        csv_data = []
        
        for item in low_stock_products:
            product = item['product']
            est = item['establishment']
            current = float(item['current_stock'])
            minimum = item['minimum_stock']
            difference = float(item['difference'])
            
            # Determinar criticidad
            is_critical = current <= 0
            if is_critical:
                critical_count += 1
            
            # Formatear línea
            style = self.style.ERROR if is_critical else self.style.WARNING
            line = f"{product.name[:29]:<30} {est.name[:19]:<20} {current:<10.1f} {minimum:<10} {difference:<10.1f}"
            
            self.stdout.write(style(line))
            
            # Agregar a datos CSV
            if options['export_csv']:
                csv_data.append([
                    product.name,
                    product.internal_reference or '',
                    product.category.name,
                    est.name,
                    current,
                    minimum,
                    difference,
                    'CRÍTICO' if is_critical else 'BAJO'
                ])
        
        # Resumen
        self.stdout.write("-"*80)
        self.stdout.write(f"Total productos con stock bajo: {total_products}")
        self.stdout.write(f"Productos críticos (stock ≤ 0): {critical_count}")
        
        # Exportar CSV si se solicita
        if options['export_csv']:
            self._export_csv(csv_data)
    
    def _export_csv(self, data):
        """Exporta los datos a un archivo CSV"""
        import csv
        from django.conf import settings
        import os
        
        # Crear directorio de reportes si no existe
        reports_dir = os.path.join(settings.BASE_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Nombre del archivo
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_bajo_{timestamp}.csv"
        filepath = os.path.join(reports_dir, filename)
        
        # Escribir CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Cabecera
            writer.writerow([
                'Producto',
                'Referencia Interna',
                'Categoría',
                'Establecimiento',
                'Stock Actual',
                'Stock Mínimo',
                'Diferencia',
                'Estado'
            ])
            
            # Datos
            writer.writerows(data)
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Reporte exportado a: {filepath}")
        )