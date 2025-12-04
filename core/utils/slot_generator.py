"""
BARBERB - Sistema de Generación de Slots para Citas
=================================================

Este módulo contiene las funciones auxiliares para generar, validar y gestionar
slots de tiempo para el sistema de agendamiento de la barbería.

Autor: Equipo BarberB
Fecha: Noviembre 2025
Versión: 1.0

FUNCIONES PRINCIPALES:
- generate_time_slots(): Genera slots disponibles para una fecha específica
- get_available_barbers_for_slot(): Obtiene barberos libres para un slot
- find_consecutive_slots(): Encuentra slots consecutivos para servicios largos
- check_slot_conflicts(): Valida conflictos de horarios
"""

from datetime import datetime, timedelta, time, date
from typing import List, Dict, Tuple, Optional
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q

# Importar modelos necesarios
from admin_module.models import (
    EstablishmentSchedule, 
    BarberAvailability, 
    Service
)
from admin_module.slot_config_models import (
    EstablishmentSlotConfiguration
)
from services_module.models import ServiceDate
from establishment.models import Establishment

import logging
logger = logging.getLogger(__name__)


class SlotGenerator:
    """
    Clase principal para la generación y gestión de slots de tiempo.
    Centraliza toda la lógica de horarios y disponibilidad.
    """
    
    def __init__(self, establishment: Establishment):
        self.establishment = establishment
        # Cargar configuración avanzada (o usar defaults)
        self.config = EstablishmentSlotConfiguration.get_config(establishment)
    
    def generate_time_slots(self, target_date: date, interval_minutes: int = None) -> List[Dict]:
        """
        Genera todos los slots de tiempo disponibles para una fecha específica.
        
        Args:
            target_date (date): Fecha para la cual generar slots (ej: 2024-11-20)
            interval_minutes (int): Intervalo entre slots en minutos (None = usar config)
            
        Returns:
            List[Dict]: Lista de slots disponibles con formato:
            [
                {
                    'start_time': time(9, 0),
                    'end_time': time(9, 30),
                    'available_barbers': [user1, user2],
                    'slot_id': 'slot_09:00_09:30',
                    'is_available': True
                },
                ...
            ]
            
        Example:
            >>> generator = SlotGenerator(establishment)
            >>> slots = generator.generate_time_slots(date(2024, 11, 20))
            >>> print(f"Slots disponibles: {len(slots)}")
        """
        try:
            # Usar configuración o default
            if interval_minutes is None:
                interval_minutes = self.config.default_slot_duration
            
            # 1. Verificar si es día festivo/cerrado
            if self._is_holiday(target_date):
                logger.info(f"Fecha {target_date} es día festivo/cerrado en {self.establishment.name_est}")
                return []
            
            # 2. Verificar límites de agendamiento
            if not self._is_within_booking_limits(target_date):
                logger.info(f"Fecha {target_date} fuera de límites de agendamiento")
                return []
            # 1. Obtener horarios del establecimiento para el día de la semana
            day_of_week = target_date.isoweekday()  # 1=Lunes, 7=Domingo
            
            establishment_schedule = EstablishmentSchedule.objects.filter(
                establishment=self.establishment,
                day_of_week=day_of_week,
                is_open=True
            ).first()
            
            if not establishment_schedule:
                logger.warning(f"Establecimiento {self.establishment.name_est} cerrado el {target_date}")
                return []
            
            # 2. Generar slots base según horarios del establecimiento
            opening_time = establishment_schedule.opening_time
            closing_time = establishment_schedule.closing_time
            
            base_slots = self._generate_base_slots(
                opening_time, 
                closing_time, 
                interval_minutes
            )
            
            # 3. Aplicar filtros de configuración
            base_slots = self._apply_lunch_break(base_slots)
            base_slots = self._apply_buffer_time(base_slots)
            
            # 4. Para cada slot, determinar barberos disponibles
            available_slots = []
            
            for slot_start, slot_end in base_slots:
                available_barbers = self.get_available_barbers_for_slot(
                    target_date, 
                    slot_start, 
                    slot_end
                )
                
                if available_barbers:  # Solo incluir slots con al menos 1 barbero
                    slot_dict = {
                        'start_time': slot_start,
                        'end_time': slot_end,
                        'available_barbers': available_barbers,
                        'slot_id': f"slot_{slot_start.strftime('%H:%M')}_{slot_end.strftime('%H:%M')}",
                        'is_available': True,
                        'barber_count': len(available_barbers),
                        'date': target_date
                    }
                    available_slots.append(slot_dict)
            
            logger.info(f"Generados {len(available_slots)} slots para {target_date} en {self.establishment.name_est}")
            return available_slots
            
        except Exception as e:
            logger.error(f"Error generando slots para {target_date}: {str(e)}")
            return []
    
    def get_available_barbers_for_slot(self, target_date: date, start_time: time, end_time: time) -> List[User]:
        """
        Obtiene la lista de barberos disponibles para un slot específico.
        
        Args:
            target_date (date): Fecha del slot
            start_time (time): Hora de inicio del slot
            end_time (time): Hora de fin del slot
            
        Returns:
            List[User]: Lista de barberos (usuarios) disponibles
            
        Lógica:
            1. Barberos con BarberAvailability para ese día
            2. Que NO tengan BarberTimeOff en esa fecha/hora
            3. Que NO tengan ServiceDate existente en ese horario
        """
        try:
            day_of_week = target_date.isoweekday()
            
            # 1. Barberos con disponibilidad general para ese día
            barber_availabilities = BarberAvailability.objects.filter(
                establishment=self.establishment,
                day_of_week=day_of_week,
                is_available=True,
                start_time__lte=start_time,
                end_time__gte=end_time
            ).select_related('barber')
            
            available_barbers = []
            
            for availability in barber_availabilities:
                barber = availability.barber
                
                # 2. Verificar que no tenga ausencias (BarberTimeOff)
                if self._barber_has_time_off(barber, target_date, start_time, end_time):
                    continue
                
                # 3. Verificar que no tenga citas existentes en ese horario
                if self._barber_has_conflict(barber, target_date, start_time, end_time):
                    continue
                
                available_barbers.append(barber)
            
            return available_barbers
            
        except Exception as e:
            logger.error(f"Error obteniendo barberos disponibles: {str(e)}")
            return []
    
    def find_consecutive_slots(self, barber: User, target_date: date, duration_minutes: int) -> List[Tuple[time, time]]:
        """
        Encuentra slots consecutivos para servicios que requieren más tiempo.
        
        Args:
            barber (User): Barbero específico
            target_date (date): Fecha objetivo
            duration_minutes (int): Duración total requerida en minutos
            
        Returns:
            List[Tuple[time, time]]: Lista de rangos de tiempo consecutivos disponibles
            
        Example:
            >>> # Para un servicio de 90 minutos (3 slots de 30min)
            >>> consecutive = generator.find_consecutive_slots(barber, date(2024, 11, 20), 90)
            >>> # Resultado: [(time(9,0), time(10,30)), (time(14,0), time(15,30))]
        """
        try:
            # Generar todos los slots del día
            all_slots = self.generate_time_slots(target_date)
            
            # Filtrar slots donde este barbero específico está disponible
            barber_slots = [
                slot for slot in all_slots 
                if barber in slot['available_barbers']
            ]
            
            if not barber_slots:
                return []
            
            # Ordenar por hora de inicio
            barber_slots.sort(key=lambda x: x['start_time'])
            
            # Buscar secuencias consecutivas que cubran la duración requerida
            consecutive_ranges = []
            
            for i, start_slot in enumerate(barber_slots):
                current_time = start_slot['start_time']
                accumulated_duration = 0
                slot_sequence = [start_slot]
                
                # Intentar construir secuencia consecutiva
                for j in range(i + 1, len(barber_slots)):
                    next_slot = barber_slots[j]
                    
                    # Verificar que el siguiente slot sea inmediatamente consecutivo
                    if slot_sequence[-1]['end_time'] == next_slot['start_time']:
                        slot_sequence.append(next_slot)
                        accumulated_duration = self._calculate_duration(
                            start_slot['start_time'], 
                            next_slot['end_time']
                        )
                        
                        # Si hemos acumulado suficiente duración
                        if accumulated_duration >= duration_minutes:
                            end_time = next_slot['end_time']
                            consecutive_ranges.append((current_time, end_time))
                            break
                    else:
                        break  # Secuencia rota
            
            return consecutive_ranges
            
        except Exception as e:
            logger.error(f"Error buscando slots consecutivos: {str(e)}")
            return []
    
    def check_slot_conflicts(self, barber: User, target_date: date, start_time: time, end_time: time) -> bool:
        """
        Valida si hay conflictos para un slot específico antes de guardarlo.
        
        Args:
            barber (User): Barbero a verificar
            target_date (date): Fecha del slot
            start_time (time): Hora de inicio
            end_time (time): Hora de fin
            
        Returns:
            bool: True si HAY conflictos, False si está libre
            
        Validaciones:
            1. Barbero tiene disponibilidad general
            2. Barbero no tiene ausencias
            3. Barbero no tiene citas existentes
            4. Slot está dentro del horario del establecimiento
        """
        try:
            # 1. Verificar horarios del establecimiento
            day_of_week = target_date.isoweekday()
            establishment_schedule = EstablishmentSchedule.objects.filter(
                establishment=self.establishment,
                day_of_week=day_of_week,
                is_open=True
            ).first()
            
            if not establishment_schedule:
                return True  # Establecimiento cerrado = conflicto
            
            if (start_time < establishment_schedule.opening_time or 
                end_time > establishment_schedule.closing_time):
                return True  # Fuera del horario = conflicto
            
            # 2. Verificar disponibilidad del barbero
            barber_availability = BarberAvailability.objects.filter(
                barber=barber,
                establishment=self.establishment,
                day_of_week=day_of_week,
                is_available=True,
                start_time__lte=start_time,
                end_time__gte=end_time
            ).exists()
            
            if not barber_availability:
                return True  # Barbero no disponible = conflicto
            
            # 3. Verificar ausencias
            if self._barber_has_time_off(barber, target_date, start_time, end_time):
                return True  # Barbero con ausencia = conflicto
            
            # 4. Verificar citas existentes
            if self._barber_has_conflict(barber, target_date, start_time, end_time):
                return True  # Barbero con cita = conflicto
            
            return False  # Sin conflictos
            
        except Exception as e:
            logger.error(f"Error verificando conflictos: {str(e)}")
            return True  # En caso de error, asumir conflicto por seguridad
    
    # =========================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # =========================================================================
    
    def _generate_base_slots(self, opening_time: time, closing_time: time, interval_minutes: int) -> List[Tuple[time, time]]:
        """
        Genera la lista base de slots entre horarios de apertura y cierre.
        
        Args:
            opening_time (time): Hora de apertura
            closing_time (time): Hora de cierre  
            interval_minutes (int): Intervalo en minutos
            
        Returns:
            List[Tuple[time, time]]: Lista de tuplas (inicio, fin) para cada slot
        """
        slots = []
        current_time = opening_time
        
        while current_time < closing_time:
            # Calcular hora de fin del slot
            current_datetime = datetime.combine(date.today(), current_time)
            end_datetime = current_datetime + timedelta(minutes=interval_minutes)
            end_time = end_datetime.time()
            
            # Solo agregar si el slot completo cabe antes del cierre
            if end_time <= closing_time:
                slots.append((current_time, end_time))
            
            # Avanzar al siguiente slot
            current_time = end_time
        
        return slots
    
    """ def _barber_has_time_off(self, barber: User, target_date: date, start_time: time, end_time: time) -> bool:
      
        #Verifica si el barbero tiene ausencias en la fecha/hora especificada.
        
        #verificar si tiene solicitudes de permisos para ese dia o dias
        try:
            # Aquí se asume que existe un modelo BarberTimeOff similar a BarberAvailability
            time_off_exists = BarberTimeOff.objects.filter(
                barber=barber,
                start_date__lte=target_date,
                end_date__gte=target_date,
                Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
            ).exists()
            return time_off_exists
        except:
        
        
        return False
     """
    def _barber_has_conflict(self, barber: User, target_date: date, start_time: time, end_time: time) -> bool:
        """
        Verifica si el barbero tiene citas existentes en conflicto.
        """
        # Convertir a datetime para comparación
        start_datetime = datetime.combine(target_date, start_time)
        end_datetime = datetime.combine(target_date, end_time)
        
        # Buscar citas existentes que se superpongan
        conflicting_appointments = ServiceDate.objects.filter(
            barber=barber,
            date__date=target_date,
            date__lt=end_datetime,
            # Asumimos que cada cita dura según el servicio
        ).exists()
        
        return conflicting_appointments
    
    def _calculate_duration(self, start_time: time, end_time: time) -> int:
        """
        Calcula la duración en minutos entre dos horas.
        """
        start_datetime = datetime.combine(date.today(), start_time)
        end_datetime = datetime.combine(date.today(), end_time)
        duration = end_datetime - start_datetime
        return int(duration.total_seconds() / 60)
    
    def _is_holiday(self, target_date: date) -> bool:
        """
        Verifica si la fecha es un día festivo/cerrado.
        """
        try:
            return 
            #se obtendra de los dias que tiene abierto o no el local
            #      

        except:
            return False
    
    def _is_within_booking_limits(self, target_date: date) -> bool:
        """
        Verifica si la fecha está dentro de los límites de agendamiento.
        """
        today = date.today()
        
        # Verificar fecha mínima (min_advance_booking_hours)
        min_datetime = datetime.now() + timedelta(hours=self.config.min_advance_booking_hours)
        if target_date < min_datetime.date():
            return False
        
        # Verificar fecha máxima (advance_booking_days)
        max_date = today + timedelta(days=self.config.advance_booking_days)
        if target_date > max_date:
            return False
        
        # Verificar si permite agendamiento el mismo día
        if target_date == today and not self.config.allow_same_day_booking:
            return False
        
        return True
    
    def _apply_lunch_break(self, slots: List[Tuple[time, time]]) -> List[Tuple[time, time]]:
        """
        Filtra slots que se superponen con horario de almuerzo.
        """
        if not (self.config.lunch_break_start and self.config.lunch_break_end):
            return slots
        
        filtered_slots = []
        lunch_start = self.config.lunch_break_start
        lunch_end = self.config.lunch_break_end
        
        for slot_start, slot_end in slots:
            # Si el slot NO se superpone con el almuerzo, mantenerlo
            if slot_end <= lunch_start or slot_start >= lunch_end:
                filtered_slots.append((slot_start, slot_end))
        
        return filtered_slots
    
    def _apply_buffer_time(self, slots: List[Tuple[time, time]]) -> List[Tuple[time, time]]:
        """
        Aplica tiempo de buffer entre slots si está configurado.
        """
        buffer_minutes = self.config.buffer_time_between_appointments
        if buffer_minutes == 0:
            return slots
        
        # Recalcular slots con buffer
        buffered_slots = []
        for slot_start, slot_end in slots:
            # Reducir duración del slot para incluir buffer
            buffered_end = (datetime.combine(date.today(), slot_end) - 
                          timedelta(minutes=buffer_minutes)).time()
            
            # Solo incluir si el slot sigue siendo válido después del buffer
            if buffered_end > slot_start:
                buffered_slots.append((slot_start, buffered_end))
        
        return buffered_slots


# =========================================================================
# FUNCIONES DE UTILIDAD INDEPENDIENTES
# =========================================================================

def get_service_duration(service_id: int) -> int:
    """
    Obtiene la duración de un servicio específico.
    
    Args:
        service_id (int): ID del servicio
        
    Returns:
        int: Duración en minutos
    """
    try:
        service = Service.objects.get(id=service_id)
        return service.duration
    except Service.DoesNotExist:
        logger.warning(f"Servicio {service_id} no encontrado")
        return 30  # Duración por defecto


def validate_slot_booking(establishment_id: int, barber_id: int, service_id: int, 
                         target_date: date, start_time: time) -> Dict[str, any]:
    """
    Función de validación completa antes de crear una cita.
    
    Args:
        establishment_id (int): ID del establecimiento
        barber_id (int): ID del barbero
        service_id (int): ID del servicio
        target_date (date): Fecha de la cita
        start_time (time): Hora de inicio
        
    Returns:
        Dict: Resultado de validación con estructura:
        {
            'is_valid': bool,
            'errors': List[str],
            'slot_info': Dict,
            'end_time': time
        }
    """
    try:
        # Obtener objetos
        establishment = Establishment.objects.get(id=establishment_id)
        barber = User.objects.get(id=barber_id)
        service_duration = get_service_duration(service_id)
        
        # Calcular hora de fin
        start_datetime = datetime.combine(target_date, start_time)
        end_datetime = start_datetime + timedelta(minutes=service_duration)
        end_time = end_datetime.time()
        
        # Crear generador y validar
        generator = SlotGenerator(establishment)
        has_conflicts = generator.check_slot_conflicts(
            barber, target_date, start_time, end_time
        )
        
        # Preparar respuesta
        result = {
            'is_valid': not has_conflicts,
            'errors': [],
            'slot_info': {
                'start_time': start_time,
                'end_time': end_time,
                'duration_minutes': service_duration
            },
            'end_time': end_time
        }
        
        if has_conflicts:
            result['errors'].append("El slot seleccionado no está disponible")
        
        return result
        
    except Exception as e:
        logger.error(f"Error validando slot: {str(e)}")
        return {
            'is_valid': False,
            'errors': [f"Error interno: {str(e)}"],
            'slot_info': {},
            'end_time': None
        }


# =========================================================================
# FUNCIONES DE INTEGRACIÓN PARA VISTAS
# =========================================================================

def get_available_slots_for_date(establishment_id: int, target_date: date, 
                                service_id: Optional[int] = None) -> List[Dict]:
    """
    Función principal para obtener slots disponibles desde las vistas.
    
    Args:
        establishment_id (int): ID del establecimiento
        target_date (date): Fecha objetivo
        service_id (int, optional): ID del servicio (para filtrar por duración)
        
    Returns:
        List[Dict]: Slots disponibles formateados para el frontend
    """
    try:
        establishment = Establishment.objects.get(id=establishment_id)
        generator = SlotGenerator(establishment)
        
        # Obtener duración del servicio si se especifica
        service_duration = None
        if service_id:
            service_duration = get_service_duration(service_id)
        
        slots = generator.generate_time_slots(target_date)
        
        # Formatear para el frontend
        formatted_slots = []
        for slot in slots:
            formatted_slot = {
                'slot_id': slot['slot_id'],
                'start_time': slot['start_time'].strftime('%H:%M'),
                'end_time': slot['end_time'].strftime('%H:%M'),
                'barber_count': slot['barber_count'],
                'available_barbers': [
                    {
                        'id': barber.id,
                        'name': f"{barber.first_name} {barber.last_name}",
                        'username': barber.username
                    }
                    for barber in slot['available_barbers']
                ],
                'is_available': slot['is_available']
            }
            formatted_slots.append(formatted_slot)
        
        return formatted_slots
        
    except Exception as e:
        logger.error(f"Error obteniendo slots para frontend: {str(e)}")
        return []