from django.db import migrations
import datetime
from django.contrib.auth.hashers import make_password


def create_initial_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    Profile = apps.get_model('login_module', 'Profile')
    Establishment = apps.get_model('admin_module', 'Establishment')

    # Grupos
    barbero_group, _ = Group.objects.get_or_create(name='Barbero')
    cliente_group, _ = Group.objects.get_or_create(name='Cliente')

    # Establecimientos
    est1 = Establishment.objects.get(name_est='Establecimiento 1')
    est2 = Establishment.objects.get(name_est='Establecimiento 2')

    # Barberos para Establecimiento 1
    barberos_est1 = [
        {
            'username': 'josequintero',
            'first_name': 'José',
            'last_name': 'Quintero',
            'email': 'jquintero@barber.com',
            'phone': 3011234567,
            'address': 'Calle 45 #12-34',
            'birth_date': datetime.date(1990, 6, 15),
            'document': 'CC12345678',
        },
        {
            'username': 'danielperez',
            'first_name': 'Daniel',
            'last_name': 'Pérez',
            'email': 'dperez@barber.com',
            'phone': 3019876543,
            'address': 'Carrera 23 #56-78',
            'birth_date': datetime.date(1992, 9, 21),
            'document': 'CC87654321',
        },
    ]

    # Barberos para Establecimiento 2
    barberos_est2 = [
        {
            'username': 'marcogomez',
            'first_name': 'Marco',
            'last_name': 'Gómez',
            'email': 'mgomez@barber.com',
            'phone': 3021234567,
            'address': 'Diagonal 10 #33-44',
            'birth_date': datetime.date(1988, 2, 10),
            'document': '56789012',
        },
        {
            'username': 'andreslopez',
            'first_name': 'Andrés',
            'last_name': 'López',
            'email': 'alopez@barber.com',
            'phone': 3029876543,
            'address': 'Transversal 8 #22-55',
            'birth_date': datetime.date(1993, 12, 5),
            'document': '21098765',
        },
    ]

    # Crear función auxiliar
    def crear_barbero(data, establecimiento):
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'is_staff': True,
                'is_superuser': False,
            }
        )
        if created:
            user.password = make_password('barbero1234')
            user.save()
        user.groups.add(barbero_group)

        Profile.objects.get_or_create(
            user=user,
            defaults={
                'phone': data['phone'],
                'address': data['address'],
                'birth_date': data['birth_date'],
                'document': data['document'],
                'data_complete': True,
                'establishment': establecimiento,
                'qa_average': 0.0,
            }
        )

    for b in barberos_est1:
        crear_barbero(b, est1)
    for b in barberos_est2:
        crear_barbero(b, est2)

    # Crear cliente
    cliente_user, created = User.objects.get_or_create(
        username='lauratorres',
        defaults={
            'email': 'ltorres@gmail.com',
            'first_name': 'Laura',
            'last_name': 'Torres',
            'is_staff': False,
            'is_superuser': False,
        }
    )
    if created:
        cliente_user.password = make_password('cliente1234')
        cliente_user.save()
    cliente_user.groups.add(cliente_group)

    Profile.objects.get_or_create(
        user=cliente_user,
        defaults={
            'phone': 3105556677,
            'address': 'Calle 100 #20-10',
            'birth_date': datetime.date(1995, 4, 18),
            'document': '11223344',
            'data_complete': True,
            'establishment': None,
            'qa_average': 0.0,
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('login_module', '0002_create_initial_users'),
        ('admin_module', '0002_create_initial_establishments'),
    ]

    operations = [
        migrations.RunPython(create_initial_profiles),
    ]
from django.db import migrations
import datetime

def create_barbers_and_client(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    Profile = apps.get_model('login_module', 'Profile')
    Establishment = apps.get_model('admin_module', 'Establishment')

    # Grupos
    barbero_group, _ = Group.objects.get_or_create(name='Barbero')
    cliente_group, _ = Group.objects.get_or_create(name='Cliente')

    # Establecimientos
    est1 = Establishment.objects.get(name_est='Establecimiento 1')
    est2 = Establishment.objects.get(name_est='Establecimiento 2')

    # Barberos para Establecimiento 1
    barberos_est1 = [
        {
            'username': 'josequintero',
            'first_name': 'José',
            'last_name': 'Quintero',
            'email': 'jquintero@barber.com',
            'phone': 3011234567,
            'address': 'Calle 45 #12-34',
            'birth_date': datetime.date(1990, 6, 15),
            'document': '12345678',
        },
        {
            'username': 'danielperez',
            'first_name': 'Daniel',
            'last_name': 'Pérez',
            'email': 'dperez@barber.com',
            'phone': 3019876543,
            'address': 'Carrera 23 #56-78',
            'birth_date': datetime.date(1992, 9, 21),
            'document': '87654321',
        },
    ]

    # Barberos para Establecimiento 2
    barberos_est2 = [
        {
            'username': 'marcogomez',
            'first_name': 'Marco',
            'last_name': 'Gómez',
            'email': 'mgomez@barber.com',
            'phone': 3021234567,
            'address': 'Diagonal 10 #33-44',
            'birth_date': datetime.date(1988, 2, 10),
            'document': '56789012',
        },
        {
            'username': 'andreslopez',
            'first_name': 'Andrés',
            'last_name': 'López',
            'email': 'alopez@barber.com',
            'phone': 3029876543,
            'address': 'Transversal 8 #22-55',
            'birth_date': datetime.date(1993, 12, 5),
            'document': '21098765',
        },
    ]

    # Crear función auxiliar
    def crear_barbero(data, establecimiento):
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'is_staff': True,
                'is_superuser': False,
            }
        )
        if created:
            user.password = make_password('barbero1234')
            user.save()
        user.groups.add(barbero_group)

        Profile.objects.get_or_create(
            user=user,
            defaults={
                'phone': data['phone'],
                'address': data['address'],
                'birth_date': data['birth_date'],
                'document': data['document'],
                'data_complete': True,
                'establishment': establecimiento,
                'qa_average': 5.0,
            }
        )

    for b in barberos_est1:
        crear_barbero(b, est1)
    for b in barberos_est2:
        crear_barbero(b, est2)

    # Crear cliente
    cliente_user, created = User.objects.get_or_create(
        username='lauratorres',
        defaults={
            'email': 'ltorres@gmail.com',
            'first_name': 'Laura',
            'last_name': 'Torres',
            'is_staff': False,
            'is_superuser': False,
        }
    )
    if created:
        cliente_user.password = make_password('cliente1234')
        cliente_user.save()
    cliente_user.groups.add(cliente_group)

    Profile.objects.get_or_create(
        user=cliente_user,
        defaults={
            'phone': 3105556677,
            'address': 'Calle 100 #20-10',
            'birth_date': datetime.date(1995, 4, 18),
            'document': '11223344',
            'data_complete': True,
            'establishment': None,
            'qa_average': 5.0,
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('login_module', '0002_create_initial_users'),
        ('admin_module', '0005_create_initial_establishments'),
    ]

    operations = [
        migrations.RunPython(create_barbers_and_client),
    ]
