from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import CalendarEvent

User = get_user_model()

class CalendarEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_creacion_evento(self):
        evento = CalendarEvent.objects.create(
            user=self.user,
            title="Corte de cabello",
            description="Cliente regular",
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=1),
            event_type='other',
            approved=True
        )
        self.assertEqual(str(evento), f"Corte de cabello - {self.user.get_full_name()}")

    def test_evento_campos_requeridos(self):
        evento = CalendarEvent.objects.create(
            user=self.user,
            title="Evento importante",
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=2),
        )
        self.assertEqual(evento.event_type, "other")
        self.assertFalse(evento.approved)

    def test_evento_pasado_true(self):
        evento = CalendarEvent.objects.create(
            user=self.user,
            title="Evento pasado",
            start_datetime=timezone.now() - timedelta(days=2),
            end_datetime=timezone.now() - timedelta(days=1),
        )
        self.assertTrue(evento.is_past)

    def test_evento_pasado_false(self):
        evento = CalendarEvent.objects.create(
            user=self.user,
            title="Evento futuro",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=2),
        )
        self.assertFalse(evento.is_past)