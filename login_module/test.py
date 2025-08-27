from django.test import TestCase
from django.contrib.auth.models import User
from login_module.models import Profile
import datetime

class ProfileModelTest(TestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(username='johann', password='testpass')

        # Obtener o crear el perfil
        self.profile, created = Profile.objects.get_or_create(user=self.user)

        # Forzar actualización de los campos que quieres probar
        self.profile.phone = 3001234567
        self.profile.address = 'Calle 456'
        self.profile.birth_date = datetime.date(1995, 5, 10)
        self.profile.document = '123456789'
        self.profile.data_complete = True
        self.profile.establishment = None
        self.profile.qa_average = 4.5
        self.profile.save()

    def test_profile_str(self):
        self.assertEqual(str(self.profile), 'johann')

    def test_profile_data(self):
        self.assertEqual(self.profile.phone, 3001234567)
        self.assertEqual(self.profile.address, 'Calle 456')
        self.assertEqual(self.profile.birth_date, datetime.date(1995, 5, 10))
        self.assertEqual(self.profile.document, '123456789')
        self.assertTrue(self.profile.data_complete)
        self.assertIsNone(self.profile.establishment)
        self.assertEqual(self.profile.qa_average, 4.5)