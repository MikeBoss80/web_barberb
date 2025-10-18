"""
Script para poblar la base de datos con datos completos y realistas
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from establishment.models import Establishment
from admin_module.models import (
    Category, Service, EstablishmentService, 
    Product, Inventory, Day, Schedule
)

print("=" * 70)
print("🚀 POBLANDO BASE DE DATOS CON DATOS COMPLETOS")
print("=" * 70)
print()

# ==================== SUPERUSUARIO ====================
print("👑 Creando Superusuario...")
superuser, created = User.objects.get_or_create(
    username='superadmin',
    defaults={
        'email': 'superadmin@barberb.com',
        'first_name': 'Super',
        'last_name': 'Admin',
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    superuser.password = make_password('super1234')
    superuser.save()
    print(f"   ✅ Superusuario creado: superadmin / super1234")
else:
    print(f"   ℹ️  Superusuario ya existe: superadmin")
print()

# ==================== CATEGORÍAS ====================
print("📂 Creando Categorías...")
categorias_data = [
    {
        'name': 'Cortes',
        'description': 'Servicios de corte de cabello y barba'
    },
    {
        'name': 'Tratamientos',
        'description': 'Tratamientos capilares y faciales'
    },
    {
        'name': 'Peinados',
        'description': 'Peinados y estilos especiales'
    },
    {
        'name': 'Productos Capilares',
        'description': 'Productos para el cuidado del cabello'
    },
    {
        'name': 'Productos Faciales',
        'description': 'Productos para el cuidado de la barba y rostro'
    },
    {
        'name': 'Herramientas',
        'description': 'Herramientas profesionales de barbería'
    },
]

categorias_creadas = {}
for cat_data in categorias_data:
    categoria, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categorias_creadas[cat_data['name']] = categoria
    status = "✅ Creada" if created else "ℹ️  Ya existe"
    print(f"   {status}: {cat_data['name']}")
print()

# ==================== SERVICIOS ====================
print("✂️  Creando Servicios...")
servicios_data = [
    # Cortes
    {
        'name': 'Corte Clásico',
        'description': 'Corte tradicional de cabello con tijera y máquina',
        'price': Decimal('25000.00'),
        'duration': 30,
        'category': 'Cortes'
    },
    {
        'name': 'Corte Degradado',
        'description': 'Corte moderno con degradado (fade) personalizado',
        'price': Decimal('30000.00'),
        'duration': 45,
        'category': 'Cortes'
    },
    {
        'name': 'Corte y Barba',
        'description': 'Corte de cabello más arreglo y diseño de barba',
        'price': Decimal('40000.00'),
        'duration': 60,
        'category': 'Cortes'
    },
    {
        'name': 'Arreglo de Barba',
        'description': 'Perfilado, recorte y diseño de barba',
        'price': Decimal('15000.00'),
        'duration': 20,
        'category': 'Cortes'
    },
    {
        'name': 'Afeitado Clásico',
        'description': 'Afeitado tradicional con navaja y toallas calientes',
        'price': Decimal('20000.00'),
        'duration': 30,
        'category': 'Cortes'
    },
    # Tratamientos
    {
        'name': 'Tratamiento Capilar',
        'description': 'Hidratación profunda del cuero cabelludo',
        'price': Decimal('35000.00'),
        'duration': 40,
        'category': 'Tratamientos'
    },
    {
        'name': 'Mascarilla Facial',
        'description': 'Limpieza facial profunda con mascarilla revitalizante',
        'price': Decimal('25000.00'),
        'duration': 30,
        'category': 'Tratamientos'
    },
    # Peinados
    {
        'name': 'Peinado Express',
        'description': 'Peinado rápido para eventos',
        'price': Decimal('18000.00'),
        'duration': 20,
        'category': 'Peinados'
    },
    {
        'name': 'Peinado Premium',
        'description': 'Peinado elaborado con productos de alta gama',
        'price': Decimal('28000.00'),
        'duration': 35,
        'category': 'Peinados'
    },
]

servicios_creados = []
for serv_data in servicios_data:
    servicio, created = Service.objects.get_or_create(
        name_service=serv_data['name'],
        defaults={
            'description_service': serv_data['description'],
            'price_service': serv_data['price'],
            'duration': serv_data['duration'],
            'category': categorias_creadas[serv_data['category']],
            'active': True
        }
    )
    servicios_creados.append(servicio)
    status = "✅ Creado" if created else "ℹ️  Ya existe"
    print(f"   {status}: {serv_data['name']} - ${serv_data['price']:,}")
print()

# ==================== ASIGNAR SERVICIOS A ESTABLECIMIENTOS ====================
print("🏢 Asignando Servicios a Establecimientos...")
establecimientos = Establishment.objects.all()

# Servicios comunes a ambos establecimientos
servicios_comunes = Service.objects.filter(
    name_service__in=['Corte Clásico', 'Corte Degradado', 'Corte y Barba', 'Arreglo de Barba']
)

# Servicios especiales para Kennedy
servicios_kennedy = Service.objects.filter(
    name_service__in=['Afeitado Clásico', 'Tratamiento Capilar', 'Peinado Premium']
)

# Servicios especiales para Timiza
servicios_timiza = Service.objects.filter(
    name_service__in=['Mascarilla Facial', 'Peinado Express']
)

for est in establecimientos:
    # Asignar servicios comunes
    for servicio in servicios_comunes:
        est_serv, created = EstablishmentService.objects.get_or_create(
            establishment=est,
            service=servicio
        )
        if created:
            print(f"   ✅ {est.name_est}: {servicio.name_service}")
    
    # Asignar servicios especiales según establecimiento
    if 'Kennedy' in est.name_est:
        for servicio in servicios_kennedy:
            est_serv, created = EstablishmentService.objects.get_or_create(
                establishment=est,
                service=servicio
            )
            if created:
                print(f"   ✅ {est.name_est}: {servicio.name_service} (especial)")
    elif 'Timiza' in est.name_est:
        for servicio in servicios_timiza:
            est_serv, created = EstablishmentService.objects.get_or_create(
                establishment=est,
                service=servicio
            )
            if created:
                print(f"   ✅ {est.name_est}: {servicio.name_service} (especial)")
print()

# ==================== PRODUCTOS ====================
print("📦 Creando Productos...")
productos_data = [
    # Productos Capilares
    {
        'name': 'Shampoo Premium',
        'description': 'Shampoo profesional para todo tipo de cabello',
        'amount': 20,
        'minimum_stock': 5,
        'price': Decimal('45000.00'),
        'category': 'Productos Capilares'
    },
    {
        'name': 'Cera para Cabello',
        'description': 'Cera modeladora de fijación fuerte',
        'amount': 30,
        'minimum_stock': 8,
        'price': Decimal('32000.00'),
        'category': 'Productos Capilares'
    },
    {
        'name': 'Pomada Fijadora',
        'description': 'Pomada de alto brillo y fijación media',
        'amount': 25,
        'minimum_stock': 6,
        'price': Decimal('38000.00'),
        'category': 'Productos Capilares'
    },
    {
        'name': 'Gel Ultra Fuerte',
        'description': 'Gel de fijación extrema sin alcohol',
        'amount': 18,
        'minimum_stock': 5,
        'price': Decimal('28000.00'),
        'category': 'Productos Capilares'
    },
    # Productos Faciales
    {
        'name': 'Aceite para Barba',
        'description': 'Aceite nutritivo con aroma a madera de cedro',
        'amount': 15,
        'minimum_stock': 4,
        'price': Decimal('42000.00'),
        'category': 'Productos Faciales'
    },
    {
        'name': 'Bálsamo para Barba',
        'description': 'Bálsamo hidratante y acondicionador',
        'amount': 12,
        'minimum_stock': 3,
        'price': Decimal('48000.00'),
        'category': 'Productos Faciales'
    },
    {
        'name': 'Aftershave Clásico',
        'description': 'Loción aftershave con aloe vera',
        'amount': 22,
        'minimum_stock': 6,
        'price': Decimal('35000.00'),
        'category': 'Productos Faciales'
    },
    {
        'name': 'Crema de Afeitar',
        'description': 'Crema cremosa para afeitado perfecto',
        'amount': 16,
        'minimum_stock': 4,
        'price': Decimal('30000.00'),
        'category': 'Productos Faciales'
    },
    # Herramientas
    {
        'name': 'Tijeras Profesionales',
        'description': 'Tijeras de acero inoxidable de 6 pulgadas',
        'amount': 10,
        'minimum_stock': 2,
        'price': Decimal('85000.00'),
        'category': 'Herramientas'
    },
    {
        'name': 'Máquina Recortadora',
        'description': 'Recortadora profesional inalámbrica',
        'amount': 8,
        'minimum_stock': 2,
        'price': Decimal('250000.00'),
        'category': 'Herramientas'
    },
    {
        'name': 'Navaja de Barbero',
        'description': 'Navaja clásica con mango de madera',
        'amount': 6,
        'minimum_stock': 2,
        'price': Decimal('120000.00'),
        'category': 'Herramientas'
    },
    {
        'name': 'Brocha de Afeitar',
        'description': 'Brocha de cerdas naturales premium',
        'amount': 14,
        'minimum_stock': 3,
        'price': Decimal('55000.00'),
        'category': 'Herramientas'
    },
]

productos_creados = []
superadmin = User.objects.get(username='superadmin')

for prod_data in productos_data:
    producto, created = Product.objects.get_or_create(
        name_product=prod_data['name'],
        defaults={
            'description_product': prod_data['description'],
            'amount': prod_data['amount'],
            'minimum_stock': prod_data['minimum_stock'],
            'price_product': prod_data['price'],
            'category': categorias_creadas[prod_data['category']],
            'created_by': superadmin,
            'is_active': True
        }
    )
    productos_creados.append(producto)
    status = "✅ Creado" if created else "ℹ️  Ya existe"
    print(f"   {status}: {prod_data['name']:25} - Stock: {prod_data['amount']:3} - ${prod_data['price']:,}")
print()

# ==================== ASIGNAR PRODUCTOS A INVENTARIOS ====================
print("📊 Asignando Productos a Inventarios de Establecimientos...")
for est in establecimientos:
    count = 0
    for producto in productos_creados:
        inventario, created = Inventory.objects.get_or_create(
            establishment=est,
            product=producto
        )
        if created:
            count += 1
    print(f"   ✅ {est.name_est}: {count} productos asignados")
print()

# ==================== DÍAS DE LA SEMANA ====================
print("📅 Creando Días de la Semana...")
dias_semana = [
    'Lunes',
    'Martes',
    'Miércoles',
    'Jueves',
    'Viernes',
    'Sábado',
    'Domingo'
]

for dia_nombre in dias_semana:
    dia, created = Day.objects.get_or_create(name=dia_nombre)
    status = "✅ Creado" if created else "ℹ️  Ya existe"
    print(f"   {status}: {dia_nombre}")
print()

# ==================== RESUMEN ====================
print("=" * 70)
print("✅ POBLACIÓN DE DATOS COMPLETADA")
print("=" * 70)
print()
print(f"👑 Superusuario:     1 (superadmin / super1234)")
print(f"📂 Categorías:       {Category.objects.count()}")
print(f"✂️  Servicios:        {Service.objects.count()}")
print(f"🔗 Est-Servicios:    {EstablishmentService.objects.count()}")
print(f"📦 Productos:        {Product.objects.count()}")
print(f"📊 Inventarios:      {Inventory.objects.count()}")
print(f"📅 Días:             {Day.objects.count()}")
print()
print("=" * 70)
print("🎯 CREDENCIALES DE ACCESO")
print("=" * 70)
print()
print("🔐 SUPERUSUARIO (Django Admin):")
print("   → superadmin / super1234")
print("   → Acceso: http://localhost:8000/admin/")
print()
print("👥 ADMINISTRADORES:")
print("   → admin1 / admin1234 (BarberShop Kennedy)")
print("   → admin2 / admin1234 (BarberShop Timiza)")
print()
print("💈 BARBEROS:")
print("   → josequintero / barbero1234 (Kennedy)")
print("   → danielperez / barbero1234 (Kennedy)")
print("   → marcogomez / barbero1234 (Timiza)")
print("   → andreslopez / barbero1234 (Timiza)")
print()
print("👤 CLIENTES:")
print("   → lauratorres / cliente1234")
print()
print("=" * 70)
print("💡 PRÓXIMOS PASOS:")
print("=" * 70)
print()
print("1. Acceder al Django Admin: http://localhost:8000/admin/")
print("2. Iniciar sesión con superadmin / super1234")
print("3. Verificar todos los datos creados")
print("4. Probar funcionalidades del sistema")
print()
print("=" * 70)
