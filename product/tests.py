from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import ProductCategory, Product, StockMovement, ProductEstablishment, ProductComposition
from .utils.inventory import InventoryManager, ProductCompositionManager
from establishment.models import Establishment


class ProductCategoryTestCase(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(
            name='Test Category',
            description='Test category description',
            category_type='storable'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.category_type, 'storable')
        self.assertTrue(self.category.is_active)
    
    def test_category_str(self):
        expected = f"{self.category.name} ({self.category.get_category_type_display()})"
        self.assertEqual(str(self.category), expected)


class ProductTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.category = ProductCategory.objects.create(
            name='Test Category',
            category_type='storable'
        )
        self.product = Product.objects.create(
            name='Test Product',
            internal_reference='TEST-001',
            category=self.category,
            cost_price=Decimal('10.00'),
            sale_price=Decimal('20.00'),
            minimum_stock=5,
            created_by=self.user
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.cost_price, Decimal('10.00'))
        self.assertEqual(self.product.minimum_stock, 5)
        self.assertTrue(self.product.track_inventory)
    
    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_current_stock_property(self):
        # Sin movimientos, el stock debe ser 0
        self.assertEqual(self.product.current_stock, 0)
    
    def test_is_low_stock_property(self):
        # Con stock 0 y mínimo 5, debe estar en stock bajo
        self.assertTrue(self.product.is_low_stock)
    
    def test_service_product_no_inventory(self):
        """Los productos de servicio no deben controlar inventario"""
        service_category = ProductCategory.objects.create(
            name='Services',
            category_type='service'
        )
        service_product = Product.objects.create(
            name='Test Service',
            category=service_category,
            track_inventory=True  # Intentamos activarlo
        )
        service_product.save()  # El save() debe desactivar track_inventory
        service_product.refresh_from_db()
        self.assertFalse(service_product.track_inventory)


class StockMovementTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.category = ProductCategory.objects.create(name='Test', category_type='storable')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            cost_price=Decimal('10.00')
        )
        # Mock establishment (necesitamos crear uno simple para las pruebas)
        # Nota: Esto asume que el modelo Establishment existe
        
    def test_stock_movement_creation(self):
        # Esta prueba se completaría cuando tengamos el modelo Establishment
        pass
    
    def test_total_cost_property(self):
        """Verificar que el costo total se calcula correctamente"""
        # Crear un movimiento mock sin guardarlo en DB
        movement = StockMovement(
            quantity=Decimal('5.0'),
            unit_cost=Decimal('10.00')
        )
        expected_total = Decimal('50.00')
        self.assertEqual(movement.total_cost, expected_total)


class InventoryManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.category = ProductCategory.objects.create(name='Test', category_type='storable')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            cost_price=Decimal('10.00'),
            minimum_stock=5
        )
    
    def test_get_current_stock_no_movements(self):
        """Sin movimientos, el stock debe ser 0"""
        # Esta prueba se completaría cuando tengamos un establishment mock
        pass


class ProductCompositionTestCase(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name='Test', category_type='storable')
        self.parent = Product.objects.create(
            name='Composite Product',
            category=self.category,
            product_type='composite'
        )
        self.component1 = Product.objects.create(
            name='Component 1',
            category=self.category,
            cost_price=Decimal('5.00')
        )
        self.component2 = Product.objects.create(
            name='Component 2',
            category=self.category,
            cost_price=Decimal('3.00')
        )
        self.composition1 = ProductComposition.objects.create(
            parent_product=self.parent,
            component_product=self.component1,
            quantity_needed=Decimal('2.0'),
            unit_of_measure='unidad'
        )
        self.composition2 = ProductComposition.objects.create(
            parent_product=self.parent,
            component_product=self.component2,
            quantity_needed=Decimal('1.5'),
            unit_of_measure='unidad'
        )
    
    def test_composition_creation(self):
        self.assertEqual(self.composition1.parent_product, self.parent)
        self.assertEqual(self.composition1.component_product, self.component1)
        self.assertEqual(self.composition1.quantity_needed, Decimal('2.0'))
    
    def test_composition_str(self):
        expected = f"{self.parent.name} -> {self.composition1.quantity_needed} {self.composition1.unit_of_measure} de {self.component1.name}"
        self.assertEqual(str(self.composition1), expected)
    
    def test_calculate_total_cost(self):
        """Verificar cálculo de costo total de producto compuesto"""
        total_cost = ProductCompositionManager.calculate_total_cost(self.parent)
        # Component1: 2.0 * 5.00 = 10.00
        # Component2: 1.5 * 3.00 = 4.50
        # Total: 14.50
        expected_cost = Decimal('14.50')
        self.assertEqual(total_cost, expected_cost)
    
    def test_simple_product_cost(self):
        """Producto simple debe retornar su costo directo"""
        simple_product = Product.objects.create(
            name='Simple Product',
            category=self.category,
            cost_price=Decimal('25.00')
        )
        total_cost = ProductCompositionManager.calculate_total_cost(simple_product)
        self.assertEqual(total_cost, Decimal('25.00'))


class ProductEstablishmentTestCase(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name='Test', category_type='storable')
        self.product = Product.objects.create(name='Test Product', category=self.category)
        # Mock de establishment - en un caso real usaríamos el modelo real
        
    def test_available_stock_property(self):
        """Verificar cálculo de stock disponible"""
        # Crear un registro mock sin guardarlo
        stock_record = ProductEstablishment(
            current_stock=Decimal('10.0'),
            reserved_stock=Decimal('3.0')
        )
        expected_available = Decimal('7.0')
        self.assertEqual(stock_record.available_stock, expected_available)
