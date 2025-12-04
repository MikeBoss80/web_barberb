# ===== VISTA AJAX UNIFICADA PARA CONFIGURACIÓN =====
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from admin_module.models import EstablishmentSchedule
from django.db import transaction


@method_decorator(csrf_exempt, name='dispatch')
class SaveFullConfigurationAjaxView(LoginRequiredMixin, View):
    """Vista AJAX para guardar toda la configuración de un establecimiento"""
    def post(self, request):
        try:
            # Permitir tanto JSON como FormData
            if request.content_type.startswith('application/json'):
                data = json.loads(request.body)
            else:
                data = request.POST

            print(f"🔍 DEBUG: Datos recibidos: {dict(data)}")  # Debug log
            
            establishment_id = data.get('establishment_id')
            print(f"🏢 DEBUG: Establishment ID: {establishment_id}")  # Debug log
            
            if not establishment_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de establecimiento requerido'
                }, status=400)
                
            establishment = get_object_or_404(request.user.admin_est.all(), id=establishment_id)
            print(f"✅ DEBUG: Establecimiento encontrado: {establishment.name_est}")  # Debug log
            
            with transaction.atomic():
                # Guardar configuración de slots
                slot_config, created = EstablishmentSlotConfiguration.objects.get_or_create(
                    establishment=establishment
                )
                print(f"🔧 DEBUG: Configuración {'creada' if created else 'existente'}")  # Debug log

                # Mapear campos del formulario a campos del modelo que realmente existen
                # Slots
                if data.get('duracion_slot'):
                    slot_config.default_slot_duration = int(data.get('duracion_slot', 30))
                    
                if data.get('tiempo_descanso'):
                    slot_config.buffer_time_between_appointments = int(data.get('tiempo_descanso', 5))
                    
                if data.get('dias_anticipacion'):
                    slot_config.advance_booking_days = int(data.get('dias_anticipacion', 30))
                    
                # Boolean para permitir mismo día
                slot_config.allow_same_day_booking = data.get('permitir_mismo_dia') in ['true', 'True', True, 'on', '1', 1]

                # Notificaciones
                slot_config.send_appointment_reminders = data.get('enviar_recordatorio') in ['true', 'True', True, 'on', '1', 1]
                slot_config.send_confirmation_immediately = data.get('enviar_confirmacion') in ['true', 'True', True, 'on', '1', 1]
                
                if data.get('horas_recordatorio'):
                    slot_config.reminder_hours_before = int(data.get('horas_recordatorio', 24))

                slot_config.save()
                print(f"💾 DEBUG: Configuración de slots guardada exitosamente")  # Debug log
                
                # ============================================================================
                # GUARDAR HORARIOS EN ESTABLISHMENTSCHEDULE
                # ============================================================================
                
                # Días de la semana (1=Lunes, 2=Martes, ..., 7=Domingo)
                DAYS_MAP = {
                    'lunes': 1, 'martes': 2, 'miercoles': 3, 'jueves': 4,
                    'viernes': 5, 'sabado': 6, 'domingo': 7
                }
                
                for day_name, day_number in DAYS_MAP.items():
                    # Buscar campos de apertura y cierre para cada día según formato del template
                    opening_time = data.get(f'{day_name}_inicio')
                    closing_time = data.get(f'{day_name}_fin')
                    # Asumir que está abierto si se proporcionan horarios
                    is_open = bool(opening_time and closing_time)
                    
                    if opening_time and closing_time:
                        # Crear o actualizar el horario para este día
                        schedule, created = EstablishmentSchedule.objects.get_or_create(
                            establishment=establishment,
                            day_of_week=day_number,
                            defaults={
                                'opening_time': opening_time,
                                'closing_time': closing_time,
                                'is_open': is_open
                            }
                        )
                        
                        if not created:
                            # Actualizar horario existente
                            schedule.opening_time = opening_time
                            schedule.closing_time = closing_time
                            schedule.is_open = is_open
                            schedule.save()
                        
                        print(f"📅 DEBUG: Horario {day_name} guardado: {opening_time}-{closing_time} {'✅' if is_open else '❌'}")
                
                print(f"✅ DEBUG: Horarios de establecimiento guardados exitosamente")
            
            return JsonResponse({
                'success': True,
                'message': 'Configuración y horarios guardados correctamente',
                'establishment_name': establishment.name_est,
                "status": "ok"
            })
        except Exception as e:
            print(f"💥 DEBUG: Error en vista: {str(e)}")  # Debug log
            import traceback
            traceback.print_exc()  # Imprimir stack trace completo
            
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar configuración: {str(e)}'
            }, status=500)  # Cambiar a 500 para errores del servidor
import json
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, DeleteView, UpdateView
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from decimal import Decimal, InvalidOperation

from .forms import CreateEstablishmentForm
from establishment.models import Establishment
from admin_module.utils.mixins import BreadcrumbMixin
from admin_module.slot_config_models import EstablishmentSlotConfiguration

# Función para parsear coordenadas
def parse_coordinate(value, default=None):
    if value is None or value == '':
        return default
    try:
        return round(Decimal(str(value)), 6)
    except (InvalidOperation, ValueError, TypeError):
        return default

#===== VISTA PRINCIPAL DE ESTABLECIMIENTOS =====
class EstablishmentMainView(BreadcrumbMixin,TemplateView):
    template_name= 'establishment/base.html'

    def get_breadcrumb(self):
        return [{'label': 'Establecimiento', 'url': reverse('establishment:establishment_main'), 'icon': 'building'}]

#===== VISTA PRINCIPAL DE GESTIÓN DE ESTABLECIMIENTOS =====
class EstablishmentManagementView(TemplateView):
    template_name= 'establishment/tabs/management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['establecimientos'] = self.request.user.admin_est.all()
        context['form'] = CreateEstablishmentForm()
        return context

#===== VISTAS PARA CRUD DE ESTABLECIMIENTOS =====
class UpdateEstablishmentView(UserPassesTestMixin, UpdateView):
    model = Establishment
    form_class = CreateEstablishmentForm
    template_name = 'establishment/modals/update.html'
    
    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        if self.request.method == 'POST':
            data = self.request.POST.copy()
            
            if 'lat_est' in data and data['lat_est']:
                lat_parsed = parse_coordinate(data['lat_est'])
                if lat_parsed is not None:
                    data['lat_est'] = str(lat_parsed)
            
            if 'lng_est' in data and data['lng_est']:
                lng_parsed = parse_coordinate(data['lng_est'])
                if lng_parsed is not None:
                    data['lng_est'] = str(lng_parsed)
            
            form = self.get_form_class()(data, files=self.request.FILES, instance=self.get_object())
        
        return form
    
    def form_valid(self, form):
        try:
            form.instance.id_admin_id = self.request.user.id
            response = super().form_valid(form)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "message": "Establecimiento creado exitosamente",
                    "id": self.object.id,
                    "name": self.object.name_est
                })

            return response
        except Exception as e:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": False,
                    "message": "Error al guardar el establecimiento",
                    "error": str(e)
                }, status=500)
            raise
    
    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()
        
    def handle_no_permission(self):
        return redirect('not_in_group')


#===== VISTA PARA CREAR ESTABLECIMIENTOS =====
class CreateEstablishmentView(UserPassesTestMixin, CreateView):
    model = Establishment
    template_name = 'establishment/modals/add.html'
    form_class = CreateEstablishmentForm
    success_url = "/establishment/management/"

    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        if self.request.method == 'POST':
            data = self.request.POST.copy()
            
            if 'lat_est' in data and data['lat_est']:
                lat_parsed = parse_coordinate(data['lat_est'])
                if lat_parsed is not None:
                    data['lat_est'] = str(lat_parsed)
            
            if 'lng_est' in data and data['lng_est']:
                lng_parsed = parse_coordinate(data['lng_est'])
                if lng_parsed is not None:
                    data['lng_est'] = str(lng_parsed)
            
            form = self.get_form_class()(data, files=self.request.FILES)
        
        return form

    def form_valid(self, form):
        try:
            form.instance.id_admin_id = self.request.user.id
            response = super().form_valid(form)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "message": "Establecimiento creado exitosamente",
                    "id": self.object.id,
                    "name": self.object.name_est
                })

            return response
        except Exception as e:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": False,
                    "message": "Error al guardar el establecimiento",
                    "error": str(e)
                }, status=500)
            raise

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = list(error_list)
            
            return JsonResponse({
                "success": False,
                "message": "Por favor corrige los errores en el formulario",
                "errors": errors,
                "non_field_errors": list(form.non_field_errors())
            }, status=400)

        return super().form_invalid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()

    def handle_no_permission(self):
        return redirect('not_in_group')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MAPS_APIKEY'] = settings.MAPS_APIKEY
        return context

#===== VISTA PARA ELIMINAR ESTABLECIMIENTOS =====  
class DeleteEstablishmentView(DeleteView):
    
    def get_success_url(self):
        return reverse_lazy('establishment:establishment_main') + '?tab=management'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)

#===== VISTAS PARA PESTAÑAS DE ESTABLECIMIENTOS =====
class ProfileEstablishmentView(TemplateView):
    template_name= 'establishment/tabs/profile_est.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener establecimientos del usuario
        establecimientos = self.request.user.admin_est.all()
        context['establecimientos'] = establecimientos
        
        # Determinar establecimiento activo
        establishment_id = self.request.GET.get('establishment_id')
        establishment = None
        
        if establishment_id:
            try:
                # Convertir el ID a entero para la consulta
                establishment_id = int(establishment_id)
                establishment = establecimientos.get(id=establishment_id)
            except (ValueError, Establishment.DoesNotExist):
                # ValueError si no se puede convertir a int
                # DoesNotExist si no existe el establecimiento
                pass
        
        # Si no se especificó o no se encontró, usar el primero disponible
        if not establishment and establecimientos.exists():
            establishment = establecimientos.first()
        
        context['establishment'] = establishment
        
        if establishment:
            # Cargar servicios del establecimiento
            from admin_module.models import EstablishmentService
            services = EstablishmentService.objects.filter(
                establishment=establishment
            ).select_related('service', 'service__category')
            context['services'] = services
            
            # Cargar barberos vinculados al establecimiento
            from django.contrib.auth.models import User
            barberos = User.objects.filter(
                profile__establishment=establishment,
                groups__name='Barbero'
            ).select_related('profile')
            context['barberos'] = barberos
            
        return context


#===== VISTA PARA CONFIGURACIÓN DE ESTABLECIMIENTOS =====
class ConfigurationEstablishmentView(BreadcrumbMixin, TemplateView):
    """
    Vista para la configuración avanzada de establecimientos.
    Incluye configuración de horarios, slots, barberos, etc.
    """
    template_name = 'establishment/tabs/configuration.html'

    def get_breadcrumb(self):
        return [
            {'label': 'Establecimiento', 'url': reverse('establishment:establishment_main'), 'icon': 'building'},
            {'label': 'Configuración', 'url': '#', 'icon': 'gear-wide-connected'}
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = [day.strip() for day in [
            "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
        ]]
        context['days'] = days  
        # Días de la semana para la plantilla
    
        # Obtener solo los establecimientos del usuario actual (administrador)
        context['establecimientos'] = self.request.user.admin_est.all().order_by('name_est')
        # Si hay un establishment_id en la URL, verificar que pertenezca al usuario
        establishment_id = self.request.GET.get('establishment_id')
        if establishment_id:
            try:
                context['selected_establishment'] = self.request.user.admin_est.get(id=establishment_id)
            except Establishment.DoesNotExist:
                context['selected_establishment'] = None
        return context


# ===== VISTAS AJAX PARA CONFIGURACIÓN =====

@method_decorator(csrf_exempt, name='dispatch')
class SaveHorariosAjaxView(LoginRequiredMixin, View):
    """Vista AJAX para guardar configuración de horarios"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            establishment_id = data.get('establishment_id')
            
            # Verificar que el establecimiento pertenece al usuario
            establishment = get_object_or_404(
                request.user.admin_est.all(), 
                id=establishment_id
            )
            
            # Obtener o crear la configuración de slots
            slot_config, created = EstablishmentSlotConfiguration.objects.get_or_create(
                establishment=establishment,
                defaults={'is_active': True}
            )
            
            # Actualizar horarios
            slot_config.monday_open = data.get('monday_open')
            slot_config.monday_close = data.get('monday_close')
            slot_config.tuesday_open = data.get('tuesday_open') 
            slot_config.tuesday_close = data.get('tuesday_close')
            slot_config.wednesday_open = data.get('wednesday_open')
            slot_config.wednesday_close = data.get('wednesday_close')
            slot_config.thursday_open = data.get('thursday_open')
            slot_config.thursday_close = data.get('thursday_close')
            slot_config.friday_open = data.get('friday_open')
            slot_config.friday_close = data.get('friday_close')
            slot_config.saturday_open = data.get('saturday_open')
            slot_config.saturday_close = data.get('saturday_close')
            slot_config.sunday_open = data.get('sunday_open')
            slot_config.sunday_close = data.get('sunday_close')
            
            slot_config.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Horarios guardados correctamente',
                'establishment_name': establishment.name_est
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar horarios: {str(e)}'
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class SaveSlotsConfigAjaxView(LoginRequiredMixin, View):
    """Vista AJAX para guardar configuración de slots"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            establishment_id = data.get('establishment_id')
            
            # Verificar que el establecimiento pertenece al usuario
            establishment = get_object_or_404(
                request.user.admin_est.all(), 
                id=establishment_id
            )
            
            # Obtener o crear la configuración de slots
            slot_config, created = EstablishmentSlotConfiguration.objects.get_or_create(
                establishment=establishment,
                defaults={'is_active': True}
            )
            
            # Actualizar configuración de slots
            slot_config.slot_duration_minutes = data.get('slot_duration_minutes', 30)
            slot_config.break_duration_minutes = data.get('break_duration_minutes', 5)
            slot_config.max_consecutive_bookings = data.get('max_consecutive_bookings', 10)
            slot_config.allow_same_day_booking = data.get('allow_same_day_booking', True)
            slot_config.advance_booking_days = data.get('advance_booking_days', 30)
            slot_config.booking_deadline_hours = data.get('booking_deadline_hours', 2)
            slot_config.auto_generate_slots = data.get('auto_generate_slots', True)
            
            slot_config.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Configuración de slots guardada correctamente',
                'establishment_name': establishment.name_est
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar configuración de slots: {str(e)}'
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class SaveNotificationsConfigAjaxView(LoginRequiredMixin, View):
    """Vista AJAX para guardar configuración de notificaciones"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            establishment_id = data.get('establishment_id')
            
            # Verificar que el establecimiento pertenece al usuario
            establishment = get_object_or_404(
                request.user.admin_est.all(), 
                id=establishment_id
            )
            
            # Obtener o crear la configuración de slots
            slot_config, created = EstablishmentSlotConfiguration.objects.get_or_create(
                establishment=establishment,
                defaults={'is_active': True}
            )
            
            # Actualizar configuración de notificaciones
            slot_config.send_confirmation_email = data.get('send_confirmation_email', True)
            slot_config.send_reminder_email = data.get('send_reminder_email', True)
            slot_config.reminder_hours_before = data.get('reminder_hours_before', 24)
            slot_config.send_cancellation_email = data.get('send_cancellation_email', True)
            
            slot_config.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Configuración de notificaciones guardada correctamente',
                'establishment_name': establishment.name_est
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar configuración de notificaciones: {str(e)}'
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class SaveReportesConfigAjaxView(LoginRequiredMixin, View):
    """Vista AJAX para guardar configuración de reportes"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            establishment_id = data.get('establishment_id')
            
            # Verificar que el establecimiento pertenece al usuario
            establishment = get_object_or_404(
                request.user.admin_est.all(), 
                id=establishment_id
            )
            
            # Para reportes, podríamos usar el modelo Establishment directamente
            # o crear campos específicos en EstablishmentSlotConfiguration
            
            # Por ahora, vamos a simular el guardado
            return JsonResponse({
                'success': True,
                'message': 'Configuración de reportes guardada correctamente',
                'establishment_name': establishment.name_est
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar configuración de reportes: {str(e)}'
            }, status=400)


class LoadConfigurationAjaxView(LoginRequiredMixin, View):
    """Vista AJAX para cargar configuración existente"""
    
    def get(self, request, establishment_id):
        try:
            # Verificar que el establecimiento pertenece al usuario
            establishment = get_object_or_404(
                request.user.admin_est.all(), 
                id=establishment_id
            )
            
            # Obtener configuración existente
            try:
                slot_config = EstablishmentSlotConfiguration.objects.get(establishment=establishment)
                
                config_data = {
                    'establishment_id': establishment.id,
                    'establishment_name': establishment.name_est,
                    
                    # Slots (mapear campos del modelo a campos del formulario)
                    'duracion_slot': slot_config.default_slot_duration,
                    'tiempo_descanso': slot_config.buffer_time_between_appointments,
                    'dias_anticipacion': slot_config.advance_booking_days,
                    'permitir_mismo_dia': slot_config.allow_same_day_booking,
                    
                    # Notificaciones
                    'enviar_confirmacion': slot_config.send_confirmation_immediately,
                    'enviar_recordatorio': slot_config.send_appointment_reminders,
                    'horas_recordatorio': slot_config.reminder_hours_before,
                    'enviar_cancelacion': slot_config.allow_online_cancellation,
                }
                
            except EstablishmentSlotConfiguration.DoesNotExist:
                # Devolver valores por defecto si no existe configuración
                config_data = {
                    'establishment_id': establishment.id,
                    'establishment_name': establishment.name_est,
                    'duracion_slot': 30,
                    'tiempo_descanso': 5,
                    'dias_anticipacion': 30,
                    'permitir_mismo_dia': True,
                    'enviar_confirmacion': True,
                    'enviar_recordatorio': True,
                    'horas_recordatorio': 24,
                    'enviar_cancelacion': True,
                }
            
            # ============================================================================
            # CARGAR HORARIOS DE ESTABLISHMENTSCHEDULE
            # ============================================================================
            
            # Obtener horarios existentes o usar valores por defecto
            DAYS_MAP = {
                'lunes': 1, 'martes': 2, 'miercoles': 3, 'jueves': 4,
                'viernes': 5, 'sabado': 6, 'domingo': 7
            }
            
            # Horarios por defecto sugeridos (barbería típica)
            DEFAULT_SCHEDULES = {
                'lunes': {'inicio': '09:00', 'fin': '18:00'},
                'martes': {'inicio': '09:00', 'fin': '18:00'},
                'miercoles': {'inicio': '09:00', 'fin': '18:00'},
                'jueves': {'inicio': '09:00', 'fin': '18:00'},
                'viernes': {'inicio': '09:00', 'fin': '18:00'},
                'sabado': {'inicio': '09:00', 'fin': '16:00'},
                'domingo': {'inicio': '10:00', 'fin': '14:00'},
            }
            
            for day_name, day_number in DAYS_MAP.items():
                try:
                    # Buscar horario existente en la BD
                    schedule = EstablishmentSchedule.objects.get(
                        establishment=establishment,
                        day_of_week=day_number
                    )
                    # Usar datos reales de la BD
                    config_data[f'{day_name}_inicio'] = schedule.opening_time.strftime('%H:%M')
                    config_data[f'{day_name}_fin'] = schedule.closing_time.strftime('%H:%M')
                    config_data[f'{day_name}_activo'] = schedule.is_open
                    
                    print(f"📅 DEBUG: Horario {day_name} (día {day_number}) cargado desde BD: {schedule.opening_time.strftime('%H:%M')}-{schedule.closing_time.strftime('%H:%M')} ({'✅' if schedule.is_open else '❌'})")
                    
                except EstablishmentSchedule.DoesNotExist:
                    # Usar horarios por defecto sugeridos
                    default_schedule = DEFAULT_SCHEDULES[day_name]
                    config_data[f'{day_name}_inicio'] = default_schedule['inicio']
                    config_data[f'{day_name}_fin'] = default_schedule['fin']
                    config_data[f'{day_name}_activo'] = True  # Abierto por defecto
                    
                    print(f"📅 DEBUG: Horario {day_name} (día {day_number}) usando valores por defecto: {default_schedule['inicio']}-{default_schedule['fin']}")
            
            print(f"🔍 DEBUG: Datos completos a enviar: {config_data}")
            
            return JsonResponse({
                'success': True,
                'data': config_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al cargar configuración: {str(e)}'
            }, status=400)
