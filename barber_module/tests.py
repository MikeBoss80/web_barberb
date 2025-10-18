from django.test import TestCase
from django.contrib.auth.models import User
from establishment.models import Establishment
from barber_module.models import BarberRequest, TIPO_SOLICITUD_CHOICES, ESTADO_SOLICITUD_CHOICES
from datetime import date, timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

class BarberRequestModelTest(TestCase):

    def setUp(self):
        # Usuario de prueba
        self.user = User.objects.create_user(username='barbero1', password='12345', first_name='Juan', last_name='Pérez')

        # Imagen simulada para el establecimiento
        mock_image = SimpleUploadedFile(name='test.jpg', content=b'image_content', content_type='image/jpeg')

        # Establecimiento con todos los campos obligatorios
        self.establishment = Establishment.objects.create(
            name_est='Barbería Central',
            address_est='Calle 123',
            city_est='Bogotá',
            country_est='Colombia',
            phone_est='123456789',
            email_est='barberia@example.com',
            description='La mejor barbería',
            lat_est=4.6,
            lng_est=-74.0,
            img_est=mock_image,
            qa_average_est=5.0,
            id_admin=self.user
        )

    def test_crear_barber_request(self):
        solicitud = BarberRequest.objects.create(
            barber=self.user,
            establecimiento=self.establishment,
            tipo='vacaciones',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=5),
            comentario='Me voy de viaje',
            estado='pendiente',
            fecha_respuesta=None,
            respuesta_admin=''
        )

        self.assertEqual(solicitud.barber.username, 'barbero1')
        self.assertEqual(solicitud.establecimiento.name_est, 'Barbería Central')
        self.assertEqual(solicitud.tipo, 'vacaciones')
        self.assertEqual(solicitud.estado, 'pendiente')
        self.assertIsNone(solicitud.fecha_respuesta)
        self.assertEqual(str(solicitud), f"Solicitud de Juan Pérez - Vacaciones (Pendiente)")

    def test_opciones_tipo_y_estado(self):
        tipos = [t[0] for t in TIPO_SOLICITUD_CHOICES]
        estados = [e[0] for e in ESTADO_SOLICITUD_CHOICES]

        self.assertIn('vacaciones', tipos)
        self.assertIn('aprobada', estados)
        self.assertIn('rechazada', estados)

    def test_ordenamiento_por_fecha(self):
        hoy = timezone.now()
        solicitud1 = BarberRequest.objects.create(
            barber=self.user,
            establecimiento=self.establishment,
            tipo='permiso',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            estado='pendiente',
            fecha_solicitud=hoy - timedelta(days=1)
        )
        solicitud2 = BarberRequest.objects.create(
            barber=self.user,
            establecimiento=self.establishment,
            tipo='licencia',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            estado='aprobada',
            fecha_solicitud=hoy
        )

        solicitudes = BarberRequest.objects.all().order_by('-fecha_solicitud')
        self.assertEqual(solicitudes[0], solicitud2)
        self.assertEqual(solicitudes[1], solicitud1)