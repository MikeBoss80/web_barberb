"""
ESTE ARCHIVO NO ESTA EN USO, SE MANTENDRA PARA FUTURIAS INCORPORACIONES



























API Endpoint para validar disponibilidad de slots
==================================================

Este archivo contiene un endpoint opcional para validar qué slots están ocupados
en una fecha específica para un barbero determinado.

Uso: GET /api/barber/<barber_id>/occupied-slots/?date=YYYY-MM-DD
"""

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from services_module.models import ServiceDate
from product.models import ProductEstablishment
from establishment.models import Establishment
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import json


class BarberOccupiedSlotsView(View):
    """
    Vista API para obtener los slots ocupados de un barbero en una fecha específica.
    
    GET Parameters:
        - date: Fecha en formato YYYY-MM-DD
    
    Response:
        {
            "barber_id": 5,
            "date": "2024-12-15",
            "occupied_slots": [
                {
                    "time": "09:00",
                    "datetime": "2024-12-15 09:00:00",
                    "service": "Corte de cabello",
                    "customer": "Juan Pérez",
                    "status": "Agendada"
                },
                {
                    "time": "10:30",
                    "datetime": "2024-12-15 10:30:00",
                    "service": "Barba + Cabello",
                    "customer": "Carlos López",
                    "status": "Agendada"
                }
            ]
        }
    """
    
    def get(self, request, barber_id):
        try:
            # Obtener parámetros
            date_str = request.GET.get('date')
            
            if not date_str:
                return JsonResponse({
                    'error': 'El parámetro date es requerido'
                }, status=400)
            
            # Parsear fecha
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Validar que el barbero existe
            try:
                barber = User.objects.get(id=barber_id, groups__name='Barbero')
            except User.DoesNotExist:
                return JsonResponse({
                    'error': f'Barbero con id {barber_id} no encontrado'
                }, status=404)
            
            # Obtener citas del barbero para esa fecha
            # Rango: desde las 00:00:00 hasta las 23:59:59 de ese día
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            
            appointments = ServiceDate.objects.filter(
                barber=barber,
                date__gte=start_datetime,
                date__lte=end_datetime,
                status__in=['Agendada', 'agendada', 'confirmada', 'Confirmada']  # Solo citas activas
            ).select_related('product', 'customer')
            
            # Formatear datos
            occupied_slots = []
            for appointment in appointments:
                occupied_slots.append({
                    'time': appointment.date.strftime('%H:%M'),
                    'datetime': appointment.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'service': appointment.product.name if appointment.product else 'Servicio',
                    'customer': appointment.customer.get_full_name(),
                    'status': appointment.status
                })
            
            return JsonResponse({
                'barber_id': barber_id,
                'barber_name': barber.get_full_name(),
                'date': date_str,
                'occupied_slots': occupied_slots,
                'total_occupied': len(occupied_slots)
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Error interno: {str(e)}'
            }, status=500)


class CreateAppointmentView(LoginRequiredMixin, View):
    """
    Vista API para crear una nueva cita desde el frontend.
    
    POST Body (JSON):
        {
            "establishment_id": 1,
            "service_id": 5,
            "barber_id": 10,
            "date": "2025-12-15",
            "time": "09:30",
            "datetime": "2025-12-15 09:30:00",
            "customer_notes": "Opcional"
        }
    
    Response (éxito):
        {
            "success": true,
            "message": "Cita agendada exitosamente",
            "appointment_id": 123,
            "appointment": {
                "id": 123,
                "service": "Corte Premium",
                "barber": "Daniel Pérez",
                "date": "2025-12-15",
                "time": "09:30",
                "status": "Agendada",
                "price_total": "25000.00"
            }
        }
    
    Response (error):
        {
            "success": false,
            "error": "Mensaje de error",
            "errors": {...}
        }
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parsear datos JSON
            data = json.loads(request.body)
            
            # Validar campos requeridos
            required_fields = ['establishment_id', 'service_id', 'barber_id', 'datetime']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
                }, status=400)
            
            # Validar que el establecimiento existe
            try:
                establishment = Establishment.objects.get(id=data['establishment_id'], active=True)
            except Establishment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Establecimiento no encontrado o inactivo'
                }, status=404)
            
            # Validar que el servicio existe y pertenece al establecimiento
            try:
                # ProductEstablishment es la relación entre establecimiento y producto
                service = ProductEstablishment.objects.get(
                    id=data['service_id'],
                    establishment=establishment
                )
            except ProductEstablishment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Servicio no encontrado o no disponible en este establecimiento'
                }, status=404)
            
            # Validar que el barbero existe y es barbero
            try:
                barber = User.objects.get(id=data['barber_id'], groups__name='Barbero')
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Barbero no encontrado'
                }, status=404)
            
            # Parsear fecha y hora
            try:
                appointment_datetime = datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha/hora inválido. Use: YYYY-MM-DD HH:MM:SS'
                }, status=400)
            
            # Validar que no sea una fecha pasada
            if appointment_datetime < timezone.now():
                return JsonResponse({
                    'success': False,
                    'error': 'No puedes agendar citas en fechas pasadas'
                }, status=400)
            
            # Validar que el barbero esté disponible en ese horario
            # Obtener configuración de slots del establecimiento
            from admin_module.models import EstablishmentSlotConfiguration
            try:
                slot_config = EstablishmentSlotConfiguration.objects.get(establishment=establishment)
                slot_duration_minutes = slot_config.default_slot_duration
                buffer_minutes = slot_config.buffer_time_between_appointments
            except EstablishmentSlotConfiguration.DoesNotExist:
                slot_duration_minutes = 30  # Default
                buffer_minutes = 5  # Default
            
            # Calcular el rango de tiempo que ocupará esta cita
            appointment_end_time = appointment_datetime + timedelta(minutes=slot_duration_minutes + buffer_minutes)
            
            # Verificar si hay citas conflictivas (solapamiento de horarios)
            conflicting_appointments = ServiceDate.objects.filter(
                barber=barber,
                status__in=['Agendada', 'agendada', 'confirmada', 'Confirmada'],
                date__lt=appointment_end_time,  # Citas que terminan después del inicio de la nueva
                date__gte=appointment_datetime - timedelta(minutes=slot_duration_minutes + buffer_minutes)  # Citas que empiezan antes del fin de la nueva
            )
            
            if conflicting_appointments.exists():
                conflict = conflicting_appointments.first()
                conflict_time = conflict.date.strftime('%H:%M')
                return JsonResponse({
                    'success': False,
                    'error': f'Este horario ya está ocupado (conflicto con cita a las {conflict_time}). Por favor selecciona otro horario.'
                }, status=409)
            
            # Crear la cita
            appointment = ServiceDate.objects.create(
                product=service.product,
                establishment=establishment,
                date=appointment_datetime,
                customer=request.user,
                barber=barber,
                status='Agendada',
                comments=data.get('customer_notes', ''),
                price_total=service.product.sale_price  # Precio del producto/servicio
            )
            
            # Preparar respuesta
            response_data = {
                'success': True,
                'message': '¡Cita agendada exitosamente!',
                'appointment_id': appointment.id,
                'appointment': {
                    'id': appointment.id,
                    'service': service.product.name,
                    'service_price': str(service.product.sale_price),
                    'barber': barber.get_full_name(),
                    'barber_email': barber.email,
                    'establishment': establishment.name_est,
                    'date': appointment.date.strftime('%Y-%m-%d'),
                    'time': appointment.date.strftime('%H:%M'),
                    'datetime': appointment.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': appointment.status,
                    'price_total': str(appointment.price_total),
                    'comments': appointment.comments
                }
            }
            
            return JsonResponse(response_data, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Error al parsear JSON. Verifica el formato de los datos.'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)


# ============================================================================
# CONFIGURACIÓN DE URLS
# ============================================================================
"""
Agregar en services_module/urls.py:

from .api_views import BarberOccupiedSlotsView, CreateAppointmentView

urlpatterns = [
    # ... rutas existentes
    
    # API para slots ocupados
    path('api/barber/<int:barber_id>/occupied-slots/', 
         BarberOccupiedSlotsView.as_view(), 
         name='barber_occupied_slots'),
    
    # 🆕 API para crear cita
    path('api/appointments/create/', 
         CreateAppointmentView.as_view(), 
         name='create_appointment_api'),
]
"""
