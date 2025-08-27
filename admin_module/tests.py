from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from .models import (
    Day, Schedule, ScheduleAssignment, Category, Product, 
    Establishment, Service, EstablishmentService, Inventory
)

class AdminModuleModelsTest(TestCase):
    def setUp(self):
        # Usuarios y grupos
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')

        # Día
        self.day = Day.objects.create(name='Lunes')

        # Horario
        self.schedule = Schedule.objects.create(
            day=1,
            start_hour=timezone.now(),
            end_hour=timezone.now() + timezone.timedelta(hours=1)
        )

        # Asignación de horario
        self.schedule_assignment = ScheduleAssignment.objects.create(
            group=self.group,
            schedule=self.schedule
        )

        # Categoría
        self.category = Category.objects.create(
            name='Belleza',
            description='Servicios de belleza y cuidado personal'
        )

        # Producto
        self.product = Product.objects.create(
            name_product='Tijeras',
            description_product='Tijeras profesionales',
            amount=10,
            minimum_stock=2,
            price_product=15000.00,
            category=self.category,
            created_by=self.user,
            updated_by=self.user
        )

        # Establecimiento
        self.establishment = Establishment.objects.create(
            name_est='Peluquería Elite',
            address_est='Cra 123 #45-67',
            city_est='Bogotá',
            country_est='Colombia',
            phone_est='3001234567',
            email_est='elite@correo.com',
            description='Cortes y tratamientos capilares',
            lat_est=4.6097100,
            lng_est=-74.0817500,
            img_est='establishments/sample.jpg',
            id_admin=self.user
        )

        # Servicio
        self.service = Service.objects.create(
            name_service='Corte Masculino',
            description_service='Corte de cabello estilo libre',
            price_service=20000.00,
            duration=30,
            category=self.category
        )

        # Relación establecimiento-servicio
        self.est_service = EstablishmentService.objects.create(
            establishment=self.establishment,
            service=self.service
        )

        # Inventario
        self.inventory = Inventory.objects.create(
            establishment=self.establishment,
            product=self.product
        )

    def test_day_str(self):
        self.assertEqual(str(self.day), 'Lunes')

    def test_schedule_str(self):
        self.assertIn('1 |', str(self.schedule))

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Belleza')

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Tijeras')

    def test_establishment_str(self):
        self.assertEqual(str(self.establishment), 'Peluquería Elite')

    def test_service_str(self):
        self.assertEqual(str(self.service), 'Corte Masculino')