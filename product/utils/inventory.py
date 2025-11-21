"""
Utilidades para el manejo de inventario y productos
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import Product, StockMovement, ProductEstablishment, ProductComposition


class InventoryManager:
    """Gestor de inventario para operaciones complejas"""
    
    @staticmethod
    def create_stock_movement(product, establishment, movement_type, quantity, 
                            unit_cost=0, reason='other', reference='', notes='', user=None):
        """
        Crea un movimiento de stock y actualiza el inventario
        """
        with transaction.atomic():
            # Crear el movimiento
            movement = StockMovement.objects.create(
                product=product,
                establishment=establishment,
                movement_type=movement_type,
                reason=reason,
                quantity=quantity,
                unit_cost=unit_cost,
                reference=reference,
                notes=notes,
                created_by=user
            )
            
            # Actualizar stock por establecimiento
            InventoryManager.update_establishment_stock(product, establishment)
            
            return movement
    
    @staticmethod
    def update_establishment_stock(product, establishment):
        """
        Actualiza el stock actual de un producto en un establecimiento
        basándose en los movimientos registrados
        """
        if not product.track_inventory:
            return
            
        # Calcular stock basado en movimientos
        from django.db.models import Sum, Q
        
        entries = StockMovement.objects.filter(
            product=product,
            establishment=establishment,
            movement_type__in=['in', 'adjustment_in']
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        exits = StockMovement.objects.filter(
            product=product,
            establishment=establishment,
            movement_type__in=['out', 'adjustment_out']
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0')
        
        current_stock = entries - exits
        
        # Actualizar o crear registro de stock por establecimiento
        stock_record, created = ProductEstablishment.objects.get_or_create(
            product=product,
            establishment=establishment,
            defaults={'current_stock': current_stock}
        )
        
        if not created:
            stock_record.current_stock = current_stock
            stock_record.save()
        
        return stock_record
    
    @staticmethod
    def adjust_stock(product, establishment, new_quantity, reason='inventory_adjustment', 
                    reference='', notes='', user=None):
        """
        Ajusta el stock de un producto a una cantidad específica
        """
        if not product.track_inventory:
            raise ValueError("Este producto no controla inventario")
        
        # Obtener stock actual
        current_stock = InventoryManager.get_current_stock(product, establishment)
        difference = new_quantity - current_stock
        
        if difference == 0:
            return None  # No hay cambios
        
        # Determinar tipo de movimiento
        if difference > 0:
            movement_type = 'adjustment_in'
            quantity = difference
        else:
            movement_type = 'adjustment_out'
            quantity = abs(difference)
        
        return InventoryManager.create_stock_movement(
            product=product,
            establishment=establishment,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason,
            reference=reference,
            notes=notes,
            user=user
        )
    
    @staticmethod
    def get_current_stock(product, establishment):
        """
        Obtiene el stock actual de un producto en un establecimiento
        """
        try:
            stock_record = ProductEstablishment.objects.get(
                product=product,
                establishment=establishment
            )
            return stock_record.current_stock
        except ProductEstablishment.DoesNotExist:
            return Decimal('0')
    
    @staticmethod
    def get_available_stock(product, establishment):
        """
        Obtiene el stock disponible (actual - reservado) de un producto
        """
        try:
            stock_record = ProductEstablishment.objects.get(
                product=product,
                establishment=establishment
            )
            return stock_record.available_stock
        except ProductEstablishment.DoesNotExist:
            return Decimal('0')
    
    @staticmethod
    def reserve_stock(product, establishment, quantity):
        """
        Reserva una cantidad de stock para una venta o uso futuro
        """
        if not product.track_inventory:
            return True
        
        stock_record, created = ProductEstablishment.objects.get_or_create(
            product=product,
            establishment=establishment,
            defaults={'current_stock': Decimal('0'), 'reserved_stock': Decimal('0')}
        )
        
        available = stock_record.available_stock
        if available >= quantity:
            stock_record.reserved_stock += quantity
            stock_record.save()
            return True
        
        return False  # No hay suficiente stock disponible
    
    @staticmethod
    def release_stock(product, establishment, quantity):
        """
        Libera stock reservado
        """
        try:
            stock_record = ProductEstablishment.objects.get(
                product=product,
                establishment=establishment
            )
            if stock_record.reserved_stock >= quantity:
                stock_record.reserved_stock -= quantity
                stock_record.save()
                return True
        except ProductEstablishment.DoesNotExist:
            pass
        
        return False
    
    @staticmethod
    def get_low_stock_products(establishment=None, category=None):
        """
        Obtiene productos con stock bajo
        """
        queryset = Product.objects.filter(
            track_inventory=True,
            is_active=True
        )
        
        if category:
            queryset = queryset.filter(category=category)
        
        low_stock_products = []
        
        for product in queryset:
            if establishment:
                current_stock = InventoryManager.get_current_stock(product, establishment)
                if current_stock <= product.minimum_stock:
                    low_stock_products.append({
                        'product': product,
                        'establishment': establishment,
                        'current_stock': current_stock,
                        'minimum_stock': product.minimum_stock,
                        'difference': product.minimum_stock - current_stock
                    })
            else:
                # Verificar en todos los establecimientos
                from establishment.models import Establishment
                for est in Establishment.objects.filter(active=True):
                    current_stock = InventoryManager.get_current_stock(product, est)
                    if current_stock <= product.minimum_stock:
                        low_stock_products.append({
                            'product': product,
                            'establishment': est,
                            'current_stock': current_stock,
                            'minimum_stock': product.minimum_stock,
                            'difference': product.minimum_stock - current_stock
                        })
        
        return low_stock_products


class ProductCompositionManager:
    """Gestor para productos compuestos y lista de materiales"""
    
    @staticmethod
    def calculate_total_cost(product):
        """
        Calcula el costo total de un producto basado en sus componentes
        """
        if product.product_type != 'composite':
            return product.cost_price
        
        total_cost = Decimal('0')
        
        for composition in product.components.all():
            component_cost = composition.component_product.cost_price
            total_cost += component_cost * composition.quantity_needed
        
        return total_cost
    
    @staticmethod
    def check_component_availability(product, establishment, quantity_needed=1):
        """
        Verifica si hay suficientes componentes para producir un producto compuesto
        """
        if product.product_type != 'composite':
            return True, []
        
        missing_components = []
        
        for composition in product.components.all():
            required_quantity = composition.quantity_needed * quantity_needed
            available_stock = InventoryManager.get_available_stock(
                composition.component_product,
                establishment
            )
            
            if available_stock < required_quantity:
                missing_components.append({
                    'component': composition.component_product,
                    'required': required_quantity,
                    'available': available_stock,
                    'missing': required_quantity - available_stock
                })
        
        return len(missing_components) == 0, missing_components
    
    @staticmethod
    def consume_components(product, establishment, quantity_produced=1, user=None):
        """
        Consume los componentes necesarios para producir un producto compuesto
        """
        if product.product_type != 'composite':
            return []
        
        # Verificar disponibilidad antes de consumir
        available, missing = ProductCompositionManager.check_component_availability(
            product, establishment, quantity_produced
        )
        
        if not available:
            raise ValueError(f"Componentes insuficientes: {missing}")
        
        movements = []
        
        with transaction.atomic():
            for composition in product.components.all():
                quantity_to_consume = composition.quantity_needed * quantity_produced
                
                movement = InventoryManager.create_stock_movement(
                    product=composition.component_product,
                    establishment=establishment,
                    movement_type='out',
                    quantity=quantity_to_consume,
                    reason='production',
                    reference=f"Producción de {product.name}",
                    notes=f"Consumo para producir {quantity_produced} unidades",
                    user=user
                )
                
                movements.append(movement)
        
        return movements
    
    @staticmethod
    def get_production_cost(product, quantity=1):
        """
        Calcula el costo de producción basado en los costos actuales de componentes
        """
        if product.product_type != 'composite':
            return product.cost_price * quantity
        
        total_cost = Decimal('0')
        
        for composition in product.components.all():
            component_cost = composition.component_product.cost_price
            total_cost += component_cost * composition.quantity_needed
        
        return total_cost * quantity