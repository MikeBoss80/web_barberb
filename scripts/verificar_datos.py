"""
Script de verificación de datos iniciales
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberb.settings')
django.setup()

from django.contrib.auth.models import User, Group
from establishment.models import Establishment
from login_module.models import Profile
from workflows.models import FlowStatus
from admin_module.models import (
    Category, Service, EstablishmentService,
    Product, Inventory, Day
)

print("=" * 60)
print("🔍 VERIFICACIÓN DE DATOS INICIALES - BarberB")
print("=" * 60)
print()

# Grupos
print("👥 GRUPOS DE USUARIOS:")
grupos = Group.objects.all()
print(f"   Total: {grupos.count()}")
for grupo in grupos:
    usuarios_count = grupo.user_set.count()
    print(f"   ✅ {grupo.name} ({usuarios_count} usuarios)")
print()

# Usuarios
print("👤 USUARIOS CREADOS:")
usuarios = User.objects.all().order_by('groups__name', 'username')
print(f"   Total: {usuarios.count()}")
for user in usuarios:
    grupo = user.groups.first().name if user.groups.exists() else "Sin grupo"
    print(f"   ✅ {user.username:15} - {user.first_name} {user.last_name:15} ({grupo})")
print()

# Establecimientos
print("🏢 ESTABLECIMIENTOS:")
establecimientos = Establishment.objects.all()
print(f"   Total: {establecimientos.count()}")
for est in establecimientos:
    barberos = Profile.objects.filter(establishment=est).count()
    print(f"   ✅ {est.name_est:25} - Admin: {est.id_admin.username:10} - Barberos: {barberos}")
print()

# Estados de flujo
print("🔄 ESTADOS DE FLUJO:")
estados = FlowStatus.objects.all()
print(f"   Total: {estados.count()}")
for estado in estados:
    final = "✔️ Final" if estado.final else "⏳ Activo"
    print(f"   ✅ {estado.name:15} - {final}")
print()

# Perfiles
print("📋 PERFILES:")
perfiles = Profile.objects.select_related('user', 'establishment').all()
print(f"   Total: {perfiles.count()}")
for perfil in perfiles:
    est = perfil.establishment.name_est if perfil.establishment else "Sin establecimiento"
    print(f"   ✅ {perfil.user.username:15} - {est}")
print()

# Categorías
print("📂 CATEGORÍAS:")
categorias = Category.objects.all()
print(f"   Total: {categorias.count()}")
for cat in categorias:
    servicios = Service.objects.filter(category=cat).count()
    productos = Product.objects.filter(category=cat).count()
    print(f"   ✅ {cat.name:25} - Servicios: {servicios}, Productos: {productos}")
print()

# Servicios
print("✂️  SERVICIOS:")
servicios = Service.objects.all()
print(f"   Total: {servicios.count()}")
for serv in servicios[:5]:
    establecimientos = EstablishmentService.objects.filter(service=serv).count()
    print(f"   ✅ {serv.name_service:30} - ${serv.price_service:>10,} - {serv.duration}min - {establecimientos} est.")
if servicios.count() > 5:
    print(f"   ... y {servicios.count() - 5} servicios más")
print()

# Productos
print("📦 PRODUCTOS EN INVENTARIO:")
productos = Product.objects.all()
print(f"   Total: {productos.count()}")
for prod in productos[:5]:
    print(f"   ✅ {prod.name_product:30} - Stock: {prod.amount:3} - Min: {prod.minimum_stock:2} - ${prod.price_product:>10,}")
if productos.count() > 5:
    print(f"   ... y {productos.count() - 5} productos más")
print()

# Inventarios por establecimiento
print("📊 INVENTARIOS POR ESTABLECIMIENTO:")
for est in Establishment.objects.all():
    inv_count = Inventory.objects.filter(establishment=est).count()
    print(f"   ✅ {est.name_est:30} - {inv_count} productos")
print()

# Días
print("📅 DÍAS DE LA SEMANA:")
dias = Day.objects.all()
print(f"   Total: {dias.count()}")
print(f"   ✅ {', '.join([d.name for d in dias])}")
print()

print("=" * 60)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 60)
print()
print("🔐 CREDENCIALES DE ACCESO:")
print()
print("   SUPERUSUARIO (Django Admin):")
print("   → superadmin / super1234")
print("   → http://localhost:8000/admin/")
print()
print("   ADMINISTRADORES:")
print("   → admin1 / admin1234 (BarberShop Kennedy)")
print("   → admin2 / admin1234 (BarberShop Timiza)")
print()
print("   BARBEROS:")
print("   → josequintero / barbero1234 (Kennedy)")
print("   → danielperez / barbero1234 (Kennedy)")
print("   → marcogomez / barbero1234 (Timiza)")
print("   → andreslopez / barbero1234 (Timiza)")
print()
print("   CLIENTES:")
print("   → lauratorres / cliente1234")
print()
print("=" * 60)
