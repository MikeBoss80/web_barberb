"""
Tests unitarios para el sistema de generación de slots
=====================================================

Cubre todas las funciones del slot_generator.py con casos de prueba
realistas y edge cases.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import date, time, timedelta
from unittest.mock import patch

from core.utils.slot_generator import (
    SlotGenerator,
    get_service_duration,
    validate_slot_booking,
    get_available_slots_for_date
)
from admin_module.models import (
    EstablishmentSchedule,
    BarberAvailability, 
    Service,
    Category
)
from establishment.models import Establishment
from login_module.models import Profile


class SlotGeneratorTestCase(TestCase):
    """
    Tests para la clase SlotGenerator y funciones relacionadas.
    """
    
    def setUp(self):
        """
        Configuración inicial para cada test.
        Crea establishment, barberos, horarios, etc.
        """
        # Crear grupos
        self.admin_group = Group.objects.create(name='Admin')
        self.barber_group = Group.objects.create(name='Barbero')
        self.client_group = Group.objects.create(name='Cliente')
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            first_name='Admin',
            last_name='Test'
        )
        self.admin_user.groups.add(self.admin_group)
        
        self.barber1 = User.objects.create_user(
            username='barber1',
            email='barber1@test.com',
            first_name='Juan',
            last_name='Pérez'
        )
        self.barber1.groups.add(self.barber_group)
        
        self.barber2 = User.objects.create_user(
            username='barber2', 
            email='barber2@test.com',
            first_name='Carlos',
            last_name='García'
        )
        self.barber2.groups.add(self.barber_group)
        
        # Crear establecimiento
        self.establishment = Establishment.objects.create(
            name_est='BarberB Test',
            address_est='Calle 123',
            city_est='Bogotá',
            country_est='Colombia',
            phone_est='123456789',
            email_est='test@barberb.com',
            description='Barbería de prueba',
            lat_est=4.6097,
            lng_est=-74.0817,
            id_admin=self.admin_user
        )
        
        # Crear perfiles
        Profile.objects.create(
            user=self.barber1,
            establishment=self.establishment,
            phone=123456789,
            address='Test Address 1',
            document='12345678'
        )
        
        Profile.objects.create(
            user=self.barber2,
            establishment=self.establishment,
            phone=987654321,
            address='Test Address 2', 
            document='87654321'
        )
        
        # Crear horarios del establecimiento (Lunes a Viernes 9:00-18:00)
        for day in range(1, 6):  # Lunes a Viernes
            EstablishmentSchedule.objects.create(
                establishment=self.establishment,
                day_of_week=day,
                opening_time=time(9, 0),
                closing_time=time(18, 0),
                is_open=True
            )
        
        # Sábados 9:00-14:00
        EstablishmentSchedule.objects.create(
            establishment=self.establishment,
            day_of_week=6,  # Sábado
            opening_time=time(9, 0),
            closing_time=time(14, 0),
            is_open=True
        )
        
        # Domingos cerrado
        EstablishmentSchedule.objects.create(
            establishment=self.establishment,
            day_of_week=7,  # Domingo
            opening_time=time(9, 0),
            closing_time=time(18, 0),
            is_open=False
        )
        
        # Crear disponibilidad de barberos
        # Barber1: Lunes a Viernes 9:00-17:00
        for day in range(1, 6):
            BarberAvailability.objects.create(
                barber=self.barber1,
                establishment=self.establishment,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_available=True
            )
        
        # Barber2: Martes a Sábado 10:00-18:00 
        for day in range(2, 7):  # Martes a Sábado
            BarberAvailability.objects.create(
                barber=self.barber2,
                establishment=self.establishment,
                day_of_week=day,
                start_time=time(10, 0),
                end_time=time(18, 0),
                is_available=True
            )
        
        # Crear categoría y servicios
        self.category = Category.objects.create(
            name='Cortes',
            description='Servicios de corte de cabello'
        )
        
        self.service_corte = Service.objects.create(
            name_service='Corte Básico',
            description_service='Corte de cabello básico',
            price_service=15000,
            duration=30,  # 30 minutos
            category=self.category
        )
        
        self.service_completo = Service.objects.create(
            name_service='Corte + Barba',
            description_service='Corte de cabello + arreglo de barba',
            price_service=25000,
            duration=60,  # 60 minutos
            category=self.category
        )
        
        # Crear generador de slots
        self.slot_generator = SlotGenerator(self.establishment)
    
    def test_generate_time_slots_normal_day(self):
        """
        Test: Generar slots para un día normal (Miércoles)
        """
        # Miércoles 20 de Noviembre 2024
        test_date = date(2024, 11, 20)  # Miércoles
        
        slots = self.slot_generator.generate_time_slots(test_date)
        
        # Verificaciones
        self.assertGreater(len(slots), 0, "Debe generar al menos un slot")
        
        # Verificar estructura de slots
        first_slot = slots[0]
        self.assertIn('start_time', first_slot)
        self.assertIn('end_time', first_slot)
        self.assertIn('available_barbers', first_slot)
        self.assertIn('slot_id', first_slot)
        self.assertIn('is_available', first_slot)
        
        # Verificar que los slots están dentro del horario
        opening_time = time(9, 0)
        closing_time = time(18, 0)
        
        for slot in slots:
            self.assertGreaterEqual(slot['start_time'], opening_time)
            self.assertLessEqual(slot['end_time'], closing_time)
        
        # Verificar que ambos barberos están disponibles en algún momento
        all_barbers = set()
        for slot in slots:
            all_barbers.update(slot['available_barbers'])
        
        barber_names = {barber.username for barber in all_barbers}
        self.assertIn('barber1', barber_names)
        self.assertIn('barber2', barber_names)
    
    def test_generate_time_slots_weekend(self):
        """
        Test: Generar slots para fin de semana
        """
        # Sábado (horario reducido)
        saturday = date(2024, 11, 23)  # Sábado
        slots_saturday = self.slot_generator.generate_time_slots(saturday)
        
        # Debe tener slots pero menos que un día normal
        self.assertGreater(len(slots_saturday), 0)
        
        # Último slot debe terminar a las 14:00 (horario sábado)
        last_slot = max(slots_saturday, key=lambda x: x['end_time'])
        self.assertLessEqual(last_slot['end_time'], time(14, 0))
        
        # Domingo (cerrado)
        sunday = date(2024, 11, 24)  # Domingo
        slots_sunday = self.slot_generator.generate_time_slots(sunday)
        
        # No debe generar slots (establecimiento cerrado)
        self.assertEqual(len(slots_sunday), 0, "Domingo debe estar sin slots")
    
    def test_get_available_barbers_for_slot(self):
        """
        Test: Obtener barberos disponibles para slot específico
        """
        test_date = date(2024, 11, 20)  # Miércoles
        start_time = time(10, 0)
        end_time = time(10, 30)
        
        barbers = self.slot_generator.get_available_barbers_for_slot(
            test_date, start_time, end_time
        )
        
        # Ambos barberos deben estar disponibles a las 10:00
        self.assertEqual(len(barbers), 2)
        barber_usernames = {barber.username for barber in barbers}
        self.assertEqual(barber_usernames, {'barber1', 'barber2'})
    
    def test_barber_time_off_blocks_slot(self):
        """
        Test: Las ausencias (BarberTimeOff) bloquean slots correctamente
        """
        test_date = date(2024, 11, 20)  # Miércoles
        
        # Crear ausencia para barber1 todo el día
        
        
        slots = self.slot_generator.generate_time_slots(test_date)
        
        # Verificar que barber1 NO aparece en ningún slot
        for slot in slots:
            barber_usernames = {barber.username for barber in slot['available_barbers']}
            self.assertNotIn('barber1', barber_usernames, 
                           f"Barber1 no debería estar disponible en slot {slot['slot_id']}")
            self.assertIn('barber2', barber_usernames,
                        f"Barber2 SÍ debería estar disponible en slot {slot['slot_id']}")
    
    def test_find_consecutive_slots(self):
        """
        Test: Encontrar slots consecutivos para servicios largos
        """
        test_date = date(2024, 11, 20)  # Miércoles
        duration_minutes = 90  # Servicio de 90 minutos (3 slots)
        
        consecutive_ranges = self.slot_generator.find_consecutive_slots(
            self.barber1, test_date, duration_minutes
        )
        
        # Debe encontrar al menos un rango consecutivo
        self.assertGreater(len(consecutive_ranges), 0)
        
        # Verificar que el primer rango tiene al menos 90 minutos
        first_range = consecutive_ranges[0]
        start_time, end_time = first_range
        
        # Calcular duración
        start_datetime = timezone.datetime.combine(test_date, start_time)
        end_datetime = timezone.datetime.combine(test_date, end_time)
        duration = (end_datetime - start_datetime).total_seconds() / 60
        
        self.assertGreaterEqual(duration, duration_minutes)
    
    def test_check_slot_conflicts(self):
        """
        Test: Verificar detección de conflictos
        """
        test_date = date(2024, 11, 20)
        start_time = time(10, 0)
        end_time = time(10, 30)
        
        # Sin conflictos inicialmente
        has_conflict = self.slot_generator.check_slot_conflicts(
            self.barber1, test_date, start_time, end_time
        )
        self.assertFalse(has_conflict, "No debería haber conflictos inicialmente")
        
        # Crear ausencia para generar conflicto
        
        
        # Ahora SÍ debe detectar conflicto
        has_conflict = self.slot_generator.check_slot_conflicts(
            self.barber1, test_date, start_time, end_time
        )
        self.assertTrue(has_conflict, "Debería detectar conflicto por ausencia")
    
    def test_get_service_duration(self):
        """
        Test: Obtener duración de servicios
        """
        duration = get_service_duration(self.service_corte.id)
        self.assertEqual(duration, 30)
        
        duration = get_service_duration(self.service_completo.id)
        self.assertEqual(duration, 60)
        
        # Servicio inexistente
        duration = get_service_duration(99999)
        self.assertEqual(duration, 30)  # Duración por defecto
    
    def test_validate_slot_booking(self):
        """
        Test: Validación completa de reserva de slot
        """
        test_date = date(2024, 11, 20)
        start_time = time(10, 0)
        
        result = validate_slot_booking(
            self.establishment.id,
            self.barber1.id,
            self.service_corte.id,
            test_date,
            start_time
        )
        
        # Debe ser válido
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['end_time'], time(10, 30))  # 30min después
    
    def test_get_available_slots_for_date_frontend(self):
        """
        Test: Función de integración para frontend
        """
        test_date = date(2024, 11, 20)
        
        slots = get_available_slots_for_date(
            self.establishment.id, 
            test_date,
            self.service_corte.id
        )
        
        # Verificar formato para frontend
        self.assertGreater(len(slots), 0)
        
        first_slot = slots[0]
        self.assertIn('slot_id', first_slot)
        self.assertIn('start_time', first_slot)  # String format
        self.assertIn('end_time', first_slot)    # String format
        self.assertIn('available_barbers', first_slot)
        self.assertIn('barber_count', first_slot)
        
        # Verificar formato de barberos
        if first_slot['available_barbers']:
            barber = first_slot['available_barbers'][0]
            self.assertIn('id', barber)
            self.assertIn('name', barber)
            self.assertIn('username', barber)


class SlotGeneratorEdgeCasesTestCase(TestCase):
    """
    Tests para casos extremos y edge cases.
    """
    
    def setUp(self):
        """Configuración mínima para edge cases"""
        self.admin_group = Group.objects.create(name='Admin')
        self.admin_user = User.objects.create_user(
            username='admin', email='admin@test.com'
        )
        self.admin_user.groups.add(self.admin_group)
        
        self.establishment = Establishment.objects.create(
            name_est='Test',
            address_est='Test',
            city_est='Test', 
            country_est='Test',
            phone_est='123',
            email_est='test@test.com',
            description='Test',
            lat_est=0,
            lng_est=0,
            id_admin=self.admin_user
        )
        
        self.generator = SlotGenerator(self.establishment)
    
    def test_no_establishment_schedule(self):
        """
        Test: Día sin horarios configurados
        """
        test_date = date(2024, 11, 20)  # Sin horarios configurados
        
        slots = self.generator.generate_time_slots(test_date)
        
        # No debe generar slots
        self.assertEqual(len(slots), 0)
    
    def test_no_barbers_available(self):
        """
        Test: Día con horarios pero sin barberos disponibles
        """
        test_date = date(2024, 11, 20)  # Miércoles
        
        # Crear horario del establecimiento pero sin barberos
        EstablishmentSchedule.objects.create(
            establishment=self.establishment,
            day_of_week=3,  # Miércoles
            opening_time=time(9, 0),
            closing_time=time(18, 0),
            is_open=True
        )
        
        slots = self.generator.generate_time_slots(test_date)
        
        # No debe generar slots (sin barberos)
        self.assertEqual(len(slots), 0)
    
    def test_very_short_intervals(self):
        """
        Test: Intervalos de tiempo muy cortos
        """
        test_date = date(2024, 11, 20)
        
        # Crear horario muy corto (1 hora)
        EstablishmentSchedule.objects.create(
            establishment=self.establishment,
            day_of_week=3,
            opening_time=time(9, 0),
            closing_time=time(10, 0),
            is_open=True
        )
        
        slots = self.generator.generate_time_slots(test_date, interval_minutes=15)
        
        # Debería generar exactamente 4 slots de 15min (9:00-9:15, 9:15-9:30, 9:30-9:45, 9:45-10:00)
        # Pero sin barberos = 0 slots
        self.assertEqual(len(slots), 0)


if __name__ == '__main__':
    import unittest
    unittest.main()