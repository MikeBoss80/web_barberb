"""
SETUP: Configuración de Horarios de Establecimientos y Barberos
================================================================

Este script configura los horarios de operación de los establecimientos
y la disponibilidad de los barberos.

Uso:
    python scripts/setup_schedules.py

Requisitos previos:
    - Ejecutar migraciones: python manage.py migrate
    - Ejecutar setup_initial_data.py para crear establecimientos y usuarios

Autor: BarberB Development Team
Fecha: Octubre 2025
"""

import os
import sys
import django
from datetime import time

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberb.settings')
django.setup()

from django.contrib.auth.models import User
from establishment.models import Establishment
from admin_module.models import EstablishmentSchedule, BarberAvailability


class ScheduleSetup:
    """Clase para gestionar la configuración de horarios."""
    
    def __init__(self):
        self.establishments = {}
        self.barbers = {}
        
    def load_data(self):
        """Carga los datos necesarios desde la base de datos."""
        try:
            self.establishments['kennedy'] = Establishment.objects.get(name_est__icontains="Kennedy")
            self.establishments['timiza'] = Establishment.objects.get(name_est__icontains="Timiza")
            
            self.barbers['jose'] = User.objects.get(username='josequintero')
            self.barbers['daniel'] = User.objects.get(username='danielperez')
            self.barbers['marco'] = User.objects.get(username='marcogomez')
            self.barbers['andres'] = User.objects.get(username='andreslopez')
            
            return True
        except (Establishment.DoesNotExist, User.DoesNotExist) as e:
            print(f"\n❌ ERROR: {e}")
            print("   Ejecuta primero: python scripts/setup_initial_data.py")
            return False
    
    def setup_establishment_schedules(self):
        """Configura los horarios de operación de los establecimientos."""
        print("\n" + "="*70)
        print("📅 CONFIGURANDO HORARIOS DE ESTABLECIMIENTOS")
        print("="*70)
        
        schedules_config = {
            'kennedy': {
                'name': 'BarberShop Kennedy',
                'description': 'Horarios premium con servicio extendido',
                'schedules': [
                    {'day': 1, 'open': time(9, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 2, 'open': time(9, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 3, 'open': time(9, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 4, 'open': time(9, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 5, 'open': time(9, 0), 'close': time(20, 0), 'is_open': True},
                    {'day': 6, 'open': time(8, 0), 'close': time(18, 0), 'is_open': True},
                    {'day': 7, 'open': time(9, 0), 'close': time(14, 0), 'is_open': True},
                ]
            },
            'timiza': {
                'name': 'BarberShop Timiza',
                'description': 'Horarios estándar, domingos cerrado',
                'schedules': [
                    {'day': 1, 'open': time(10, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 2, 'open': time(10, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 3, 'open': time(10, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 4, 'open': time(10, 0), 'close': time(19, 0), 'is_open': True},
                    {'day': 5, 'open': time(10, 0), 'close': time(20, 0), 'is_open': True},
                    {'day': 6, 'open': time(9, 0), 'close': time(17, 0), 'is_open': True},
                    {'day': 7, 'open': time(10, 0), 'close': time(14, 0), 'is_open': False},
                ]
            }
        }
        
        created_count = 0
        for key, config in schedules_config.items():
            establishment = self.establishments[key]
            print(f"\n📍 {config['name']}")
            print(f"   {config['description']}")
            
            for schedule_data in config['schedules']:
                schedule, created = EstablishmentSchedule.objects.get_or_create(
                    establishment=establishment,
                    day_of_week=schedule_data['day'],
                    defaults={
                        'opening_time': schedule_data['open'],
                        'closing_time': schedule_data['close'],
                        'is_open': schedule_data['is_open']
                    }
                )
                
                day_name = dict(EstablishmentSchedule.DAYS_OF_WEEK)[schedule_data['day']]
                
                if created:
                    created_count += 1
                    if schedule_data['is_open']:
                        print(f"   ✅ {day_name:10} → {schedule_data['open'].strftime('%H:%M')} - {schedule_data['close'].strftime('%H:%M')}")
                    else:
                        print(f"   ✅ {day_name:10} → CERRADO")
                else:
                    print(f"   ⚠️  {day_name:10} → Ya existía (sin cambios)")
        
        print(f"\n✅ Horarios creados: {created_count}")
        print(f"📊 Total en base de datos: {EstablishmentSchedule.objects.count()}")
    
    def setup_barber_availability(self):
        """Configura la disponibilidad de cada barbero."""
        print("\n" + "="*70)
        print("💈 CONFIGURANDO DISPONIBILIDAD DE BARBEROS")
        print("="*70)
        
        barber_configs = {
            'jose': {
                'name': 'Jose Quintero',
                'establishment': 'kennedy',
                'description': 'Turno completo (Lunes-Sábado)',
                'schedules': [
                    {'day': 1, 'start': time(9, 0), 'end': time(19, 0), 'available': True},
                    {'day': 2, 'start': time(9, 0), 'end': time(19, 0), 'available': True},
                    {'day': 3, 'start': time(9, 0), 'end': time(19, 0), 'available': True},
                    {'day': 4, 'start': time(9, 0), 'end': time(19, 0), 'available': True},
                    {'day': 5, 'start': time(9, 0), 'end': time(20, 0), 'available': True},
                    {'day': 6, 'start': time(8, 0), 'end': time(18, 0), 'available': True},
                    {'day': 7, 'start': time(9, 0), 'end': time(14, 0), 'available': False},
                ]
            },
            'daniel': {
                'name': 'Daniel Pérez',
                'establishment': 'kennedy',
                'description': 'Turno tarde (L-V), completo fines de semana',
                'schedules': [
                    {'day': 1, 'start': time(14, 0), 'end': time(19, 0), 'available': True},
                    {'day': 2, 'start': time(14, 0), 'end': time(19, 0), 'available': True},
                    {'day': 3, 'start': time(14, 0), 'end': time(19, 0), 'available': True},
                    {'day': 4, 'start': time(14, 0), 'end': time(19, 0), 'available': True},
                    {'day': 5, 'start': time(14, 0), 'end': time(20, 0), 'available': True},
                    {'day': 6, 'start': time(8, 0), 'end': time(18, 0), 'available': True},
                    {'day': 7, 'start': time(9, 0), 'end': time(14, 0), 'available': True},
                ]
            },
            'marco': {
                'name': 'Marco Gómez',
                'establishment': 'timiza',
                'description': 'Turno completo (Lunes-Sábado)',
                'schedules': [
                    {'day': 1, 'start': time(10, 0), 'end': time(19, 0), 'available': True},
                    {'day': 2, 'start': time(10, 0), 'end': time(19, 0), 'available': True},
                    {'day': 3, 'start': time(10, 0), 'end': time(19, 0), 'available': True},
                    {'day': 4, 'start': time(10, 0), 'end': time(19, 0), 'available': True},
                    {'day': 5, 'start': time(10, 0), 'end': time(20, 0), 'available': True},
                    {'day': 6, 'start': time(9, 0), 'end': time(17, 0), 'available': True},
                    {'day': 7, 'start': time(10, 0), 'end': time(14, 0), 'available': False},
                ]
            },
            'andres': {
                'name': 'Andrés López',
                'establishment': 'timiza',
                'description': 'Turno mañana (L-J), completo (V-S)',
                'schedules': [
                    {'day': 1, 'start': time(10, 0), 'end': time(15, 0), 'available': True},
                    {'day': 2, 'start': time(10, 0), 'end': time(15, 0), 'available': True},
                    {'day': 3, 'start': time(10, 0), 'end': time(15, 0), 'available': True},
                    {'day': 4, 'start': time(10, 0), 'end': time(15, 0), 'available': True},
                    {'day': 5, 'start': time(10, 0), 'end': time(20, 0), 'available': True},
                    {'day': 6, 'start': time(9, 0), 'end': time(17, 0), 'available': True},
                    {'day': 7, 'start': time(10, 0), 'end': time(14, 0), 'available': False},
                ]
            }
        }
        
        created_count = 0
        for key, config in barber_configs.items():
            barber = self.barbers[key]
            establishment = self.establishments[config['establishment']]
            
            print(f"\n💈 {config['name']} - {establishment.name_est}")
            print(f"   {config['description']}")
            
            for avail_data in config['schedules']:
                availability, created = BarberAvailability.objects.get_or_create(
                    barber=barber,
                    establishment=establishment,
                    day_of_week=avail_data['day'],
                    defaults={
                        'start_time': avail_data['start'],
                        'end_time': avail_data['end'],
                        'is_available': avail_data['available']
                    }
                )
                
                day_name = dict(BarberAvailability.DAYS_OF_WEEK)[avail_data['day']]
                
                if created:
                    created_count += 1
                    if avail_data['available']:
                        print(f"   ✅ {day_name:10} → {avail_data['start'].strftime('%H:%M')} - {avail_data['end'].strftime('%H:%M')}")
                    else:
                        print(f"   ✅ {day_name:10} → NO DISPONIBLE")
                else:
                    print(f"   ⚠️  {day_name:10} → Ya existía (sin cambios)")
        
        print(f"\n✅ Disponibilidades creadas: {created_count}")
        print(f"📊 Total en base de datos: {BarberAvailability.objects.count()}")
    
    def show_summary(self):
        """Muestra un resumen de la configuración."""
        print("\n" + "="*70)
        print("📊 RESUMEN DE CONFIGURACIÓN")
        print("="*70)
        
        establishments_count = Establishment.objects.count()
        schedules_count = EstablishmentSchedule.objects.count()
        barbers_count = User.objects.filter(groups__name='Barbero').count()
        availability_count = BarberAvailability.objects.count()
        
        print(f"\n✅ Establecimientos: {establishments_count}")
        print(f"✅ Horarios de establecimientos: {schedules_count}")
        print(f"✅ Barberos activos: {barbers_count}")
        print(f"✅ Disponibilidades configuradas: {availability_count}")
        
        print("\n🎯 Estado del sistema:")
        print("   ✅ Modelos de horarios creados")
        print("   ✅ Migraciones aplicadas")
        print("   ✅ Horarios de establecimientos configurados")
        print("   ✅ Disponibilidad de barberos configurada")
        
        print("\n📝 Próximos pasos:")
        print("   1. Crear funciones auxiliares para generar slots")
        print("   2. Integrar sistema de slots en las vistas")
        print("   3. Actualizar interfaz de reservas")
        print("   4. Agregar panel de administración")
        
        print("\n" + "="*70)
    
    def run(self):
        """Ejecuta la configuración completa."""
        print("\n🚀 CONFIGURACIÓN DE HORARIOS - BARBERB")
        print("="*70)
        print("Este script configurará:")
        print("  • Horarios de operación de establecimientos")
        print("  • Disponibilidad de barberos por día")
        print("="*70)
        
        # Cargar datos
        if not self.load_data():
            return False
        
        # Configurar horarios de establecimientos
        self.setup_establishment_schedules()
        
        # Configurar disponibilidad de barberos
        self.setup_barber_availability()
        
        # Mostrar resumen
        self.show_summary()
        
        print("\n✅ ¡Configuración completada exitosamente!\n")
        return True


if __name__ == '__main__':
    setup = ScheduleSetup()
    success = setup.run()
    sys.exit(0 if success else 1)
