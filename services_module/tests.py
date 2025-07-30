from django.test import TestCase
from django.contrib.auth.models import User
from admin_module.models import (
    Day, Establishment, Service, Category, EstablishmentService
)
from services_module.models import ServiceDate, ServiceDateDay
from datetime import datetime, timedelta
from decimal import Decimal

class ServiceDateModelTest(TestCase):

    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='pass123')
        self.barber = User.objects.create_user(username='barber', password='pass123')

        self.category = Category.objects.create(
            name='Corte',
            description='Servicios de corte de cabello'
        )

        self.service = Service.objects.create(
            name_service='Corte clásico',
            description_service='Un corte clásico y limpio',
            price_service=Decimal('30000.00'),
            duration=30,
            active=True,
            category=self.category
        )

        self.establishment = Establishment.objects.create(
            name_est='Barbería Centro',
            address_est='Calle Falsa 123',
            city_est='Bogotá',
            country_est='Colombia',
            phone_est='3001234567',
            email_est='contacto@barberia.com',
            description='Corte y estilo',
            lat_est=4.60971,
            lng_est=-74.08175,
            img_est='establishments/foto.jpg',
            qa_average_est=4.5,
            id_admin=self.customer
        )

        self.est_service = EstablishmentService.objects.create(
            establishment=self.establishment,
            service=self.service
        )

        self.service_date = ServiceDate.objects.create(
            service=self.est_service,
            date=datetime.now() + timedelta(days=1),
            customer=self.customer,
            barber=self.barber,
            status='pending',
            comments='Por favor ser puntual',
            price_total=Decimal('30000.00')
        )

    def test_service_date_creation(self):
        self.assertEqual(ServiceDate.objects.count(), 1)
        self.assertEqual(self.service_date.customer.username, 'customer')
        self.assertEqual(self.service_date.barber.username, 'barber')
        self.assertEqual(self.service_date.status, 'pending')
        self.assertEqual(self.service_date.price_total, Decimal('30000.00'))

    def test_service_date_str(self):
        expected = f"{self.est_service} on {self.service_date.date}"
        self.assertEqual(str(self.service_date), expected)


class ServiceDateDayModelTest(TestCase):

    def setUp(self):
        self.customer = User.objects.create_user(username='cliente', password='pass')
        self.barber = User.objects.create_user(username='barbero', password='pass')

        self.category = Category.objects.create(
            name='Afeitado',
            description='Servicios de afeitado'
        )

        self.service = Service.objects.create(
            name_service='Afeitado Premium',
            description_service='Afeitado con espuma y toalla caliente',
            price_service=Decimal('25000.00'),
            duration=20,
            active=True,
            category=self.category
        )

        self.establishment = Establishment.objects.create(
            name_est='Barbería Norte',
            address_est='Avenida Siempre Viva 742',
            city_est='Medellín',
            country_est='Colombia',
            phone_est='3011234567',
            email_est='info@nortebarber.com',
            description='Los mejores barberos',
            lat_est=6.25184,
            lng_est=-75.56359,
            img_est='establishments/foto2.jpg',
            qa_average_est=4.8,
            id_admin=self.customer
        )

        self.est_service = EstablishmentService.objects.create(
            establishment=self.establishment,
            service=self.service
        )

        self.service_date = ServiceDate.objects.create(
            service=self.est_service,
            date=datetime.now() + timedelta(days=3),
            customer=self.customer,
            barber=self.barber,
            status='confirmed',
            comments='Sin comentarios',
            price_total=Decimal('25000.00')
        )

        self.day = Day.objects.create(name="Lunes")

        self.service_date_day = ServiceDateDay.objects.create(
            service_date=self.service_date,
            day=self.day
        )

    def test_service_date_day_creation(self):
        self.assertEqual(ServiceDateDay.objects.count(), 1)
        self.assertEqual(self.service_date_day.day.name, "Lunes")
        self.assertEqual(self.service_date_day.service_date, self.service_date)