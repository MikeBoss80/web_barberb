from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import ListView,TemplateView, UpdateView,CreateView,DeleteView, DetailView
from datetime import date, time, datetime, timedelta
from django.utils import timezone
from django.views import View
from .utils.mixins import BreadcrumbMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Sum, Count
from .models import Service, Category, EstablishmentSchedule
from establishment.models import Establishment
import calendar
from workflows.models import FlowInstance
from services_module.models import ServiceDate
from django.contrib.auth.models import User, Group
from barber_module.models import BarberRequest
from login_module.models import Profile
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import CreateEstablishmentForm,ServiceDateForm,EditarBarberoEstadoForm,BarberRequestAdminResponseForm, CreateServiceForm, VinculationForm, BarberRequestForm
from django.views.generic.edit import FormView
from collections import defaultdict
from admin_module.models import Category, EstablishmentSchedule
from admin_module.slot_config_models import EstablishmentSlotConfiguration 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from workflows.models import FlowInstance, FlowStatus
from admin_module.utils.mixins import CitasQuerysetMixin
from login_module.forms import ProfileEditForm,UserEditForm


class HomeadminView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    """Vista Principal Modulo Admin"""
    template_name = 'admin_module/main.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [{'label': 'Inicio', 'url': reverse('admin_module:main'), 'icon': 'house-door'}]

    #DATPS TEMPORALES
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el establecimiento donde el usuario es administrador
        establecimiento = Establishment.objects.filter(id_admin=self.request.user).first()
        
        if not establecimiento:
            # Si el usuario no es admin de ningún establecimiento, retornar contexto vacío
            context.update({
                'today': timezone.now().date(),
                'citas_hoy': 0,
                'barberos_activos': 0,
                'bajo_stock': 0,
                'ingresos_hoy': 0,
                'proximas_citas': [],
                'notificaciones': ['No tienes un establecimiento asignado.'],
            })
            return context

        today=timezone.now().date()

        #Citas del dia
        citas_hoy=ServiceDate.objects.filter(
            date=today,
            establishment=establecimiento
        ).count()

        #Barberos activos
        barberos_activos = Profile.objects.filter(
            establishment=establecimiento,
            user__is_active=True,
            user__groups__name='Barbero'  
        ).count()

        #Productos bajo stock
        # bajo_stock= Inventory.objects.filter(
        #     establishment=establecimiento,
        #     product=5
        # #Revisar aca quedamos  
        # ).count()

        # Ingresos del día
        ingresos_hoy = ServiceDate.objects.filter(
            date=today,
            establishment=establecimiento
        ).aggregate(total=Sum('price_total'))['total'] or 0

        # Próximas citas (de hoy en adelante)
        proximas_citas = ServiceDate.objects.filter(
            date__gte=today,
            establishment=establecimiento
        ).order_by('date', 'date')[:5]

        # Notificaciones del sistema (ejemplo: solicitudes pendientes)
        solicitudes_pendientes = BarberRequest.objects.filter(
            establecimiento=establecimiento,
            estado='pendiente'
        ).count()

        notificaciones = []
        if solicitudes_pendientes:
            notificaciones.append(f"Tienes {solicitudes_pendientes} solicitudes de barberos pendientes por revisar.")

        context.update({
            'today': today,
            'citas_hoy': citas_hoy,
            'barberos_activos': barberos_activos,
            # 'bajo_stock': bajo_stock,
            'ingresos_hoy': ingresos_hoy,
            'proximas_citas': proximas_citas,
            'notificaciones': notificaciones,
        })

        return context

class CitasView(UserPassesTestMixin, BreadcrumbMixin, TemplateView, CitasQuerysetMixin):
    template_name = 'citas/citas.html'

    # Validación: solo los usuarios en el grupo 'Administrador' pueden acceder
    def test_func(self):
        User = self.request.user
        return (
            User.groups.filter(name='Administrador').exists() or
            User.groups.filter(name='Barbero').exists() or 
            User.groups.filter(name='Cliente').exists()
        )       

    # Redirección si no tiene permiso
    def handle_no_permission(self):
        return redirect('not_in_group')
    
    # Breadcrumb (navegación)
    def get_breadcrumb(self):
        return [{'label': 'Citas', 'url': reverse('admin_module:citas'), 'icon': 'calendar-check'}]

    # Contexto que se pasa a la plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener el usuario actual
        user = self.request.user
        establishment = None
        rol = self.request.session.get('current_role')


        # ADMINISTRADOR
        # Buscar el establecimiento que administra este usuario
          # ADMINISTRADOR
        if rol == 'Administrador':
            try:
                establecimiento = Establishment.objects.get(id_admin=user)
                citas = ServiceDate.objects.select_related(
                    'product', 'establishment', 'barber', 'customer'
                ).filter(establishment=establecimiento)
            except Establishment.DoesNotExist:
                pass

        # BARBERO
        elif rol == 'Barbero':
            establecimiento = getattr(user.profile, 'establishment_id', None)
            if establecimiento:
                citas = ServiceDate.objects.select_related(
                    'product', 'establishment', 'barber', 'customer'
                ).filter(establishment=establecimiento, barber=user)

        # CLIENTE
        elif rol == 'Cliente':
            citas = ServiceDate.objects.select_related(
                'product', 'establishment', 'barber', 'customer'
            ).filter(customer=user)

        # Agregar citas al contexto
        context['dates'] = citas

        # Mostrar barberos si es administrador con establecimiento
        if rol == 'Administrador' and establecimiento:
            context['barberos'] = User.objects.filter(
                groups__name='Barbero',
                profile__establishment=establecimiento
            )
        else:
            context['barberos'] = None

        # Resumen de citas
        context['resumen'] = {
            'total_dates': citas.count(),
            'completadas': citas.filter(status='Completada').count(),
            'agendadas': citas.filter(status='Agendada').count(),
            'canceladas': citas.filter(status='Cancelada').count(),
        }

        context['fecha_actual'] = date.today()
        return context

def cancelar_cita(request):
    if request.method == "POST":
        date_id = request.POST.get("date_id")
        date = get_object_or_404(ServiceDate, id=date_id)
        date.status = 'Cancelada'
        date.save()
    return redirect('admin_module:citas')

class EditarBarberoEstadoView(LoginRequiredMixin, UpdateView):
    model = ServiceDate
    form_class = EditarBarberoEstadoForm
    template_name = 'partials/form_editar_barbero_estado.html'
    success_url = reverse_lazy('admin_module:citas')
    login_url = '/login_module/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CrearCitaRapidaView(LoginRequiredMixin, CreateView):
    model = ServiceDate
    form_class = ServiceDateForm
    template_name = 'partials/form_crear_cita.html'
    success_url = reverse_lazy('admin_module:citas')
    login_url = '/login_module/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date, timedelta
        context['today'] = date.today().isoformat()
        context['max_date'] = (date.today() + timedelta(days=60)).isoformat()
        return context

    def form_valid(self, form):
        # Asignar precio automático desde el producto/servicio
        form.instance.price_total = form.instance.product.sale_price
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request # Pasar el request al formulario    
        return kwargs
    
class CollapsView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):  
     template_name= 'collabs/collabs.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Colaboradores', 'url': reverse('admin_module:collabs'), 'icon': 'people'}]

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instances = FlowInstance.objects.filter(workflow_type_id=1)
        context['requests'] = instances
        estab_ids = self.request.user.admin_est.all().values_list('id', flat=True)
        users_team = User.objects.filter(profile__establishment_id__in=estab_ids)
        context['team'] = users_team

        return context

class CreateVinculationView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'collabs/solicitudes_barbero.html'
    form_class = VinculationForm
    success_url = reverse_lazy('admin_module:collabs')
    login_url = '/login_module/login/'

    def form_valid(self, form):
        documento = form.cleaned_data.get('document')
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.updated_by = self.request.user

        try:
            colaborator = User.objects.filter(profile__document=documento).last()
            # TODO: Esto debe cambiarse, no deberia existir usuarios con el mismo documento 
            # o si no, realizar la validacion por algun id unico
            instance.status_id = 4
            instance.recipient = colaborator  # lo vinculamos si existe
        except User.DoesNotExist:
            instance.status_id = 4
            instance.recipient = self.request.user  # o dejar el campo nulo
        
        # Guardar la instancia
        instance.save()
        
        # 🚀 ENVIAR EMAIL AL COLABORADOR (opcional)
        try:
            if instance.recipient and instance.recipient != self.request.user:
                from notifications.email_service import send_email_notification
                
                send_email_notification(
                    user=instance.recipient,
                    email_type='vinculacion_aprobada',
                    context={
                        'establecimiento_nombre': self.request.user.profile.establishment.name_est if hasattr(self.request.user, 'profile') and self.request.user.profile.establishment else 'Establecimiento',
                        'establecimiento_direccion': self.request.user.profile.establishment.address_est if hasattr(self.request.user, 'profile') and self.request.user.profile.establishment else '',
                        'fecha_aprobacion': timezone.now().strftime('%d/%m/%Y'),
                        'url_panel_barbero': self.request.build_absolute_uri(
                            reverse('barber_module:barber_main')
                        ),
                    }
                )
        except Exception as e:
            # Si falla el email, no afectar el proceso principal
            print(f"Error enviando email de vinculación: {e}")
        
        # IMPORTANTE: Retornar la respuesta
        return super().form_valid(form)

    
class VinculationDeleteView(LoginRequiredMixin, DeleteView):
    model = FlowInstance
    success_url = reverse_lazy('admin_module:barberos')
    login_url = '/login_module/login/'
     
class BarberRequestListView(LoginRequiredMixin,BreadcrumbMixin, ListView):
    model = BarberRequest
    template_name ='requets/solicitudes_list.html' #plantilla html
    success_url = reverse_lazy('admin_module:barber_solicitudes_list')  # Redirección tras guardar
    context_object_name = 'solicitudes' #nombre variable en el template
    paginate_by = 10 #paginar de 10

    def get_breadcrumb(self):
        return [{'label': 'Solicitudes', 'url': reverse('admin_module:barber_solicitudes_list'), 'icon': 'file-earmark-text'}]
    
    def get_queryset(self):
        #Filtra las solicitudes para que el barbero solo vea las suyas,
        #ordenadas por fecha descendente.
        return BarberRequest.objects.filter(barber=self.request.user).order_by('-fecha_solicitud')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_vinculation = FlowInstance.objects.filter(workflow_type_id=1,recipient=self.request.user).order_by('-created_at')
        context['requests'] = request_vinculation

        return context

class BarberValidateVinculation(View):
    """
    Vista para que el barbero acepte o rechace una solicitud de vinculación
    """
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        value = int(self.kwargs['value'])
        
        try:
            # Obtener la solicitud
            solicitud = get_object_or_404(FlowInstance, pk=pk)
            
            # Verificar que el usuario sea el destinatario de la solicitud
            if solicitud.recipient != request.user:
                messages.error(request, 'No tienes permiso para validar esta solicitud.')
                return redirect('admin_module:barber_solicitudes_list')
            
            # Verificar que la solicitud esté en estado "En espera"
            if solicitud.status.name != "En espera":
                messages.warning(request, 'Esta solicitud ya fue procesada.')
                return redirect('admin_module:barber_solicitudes_list')
            
            if value == 1:  # ACEPTAR
                # Cambiar estado a "Confirmada"
                new_status = get_object_or_404(FlowStatus, name='Confirmada')
                
                # Vincular al establecimiento
                vinculation_est = solicitud.created_by.admin_est.first()
                
                if vinculation_est:
                    profile = request.user.profile
                    profile.establishment = vinculation_est
                    profile.save()
                    
                    messages.success(
                        request, 
                        f'¡Vinculación aceptada! Ahora perteneces al establecimiento {vinculation_est.name_est}'
                    )
                    
                    # 🚀 ENVIAR EMAIL AL ADMIN QUE CREÓ LA SOLICITUD
                    try:
                        from notifications.email_service import send_email_notification
                        
                        send_email_notification(
                            user=solicitud.created_by,
                            email_type='vinculacion_aprobada',
                            context={
                                'barbero_nombre': request.user.get_full_name() or request.user.username,
                                'establecimiento_nombre': vinculation_est.name_est,
                                'establecimiento_direccion': vinculation_est.address_est,
                                'fecha_aprobacion': timezone.now().strftime('%d/%m/%Y'),
                                'url_panel_barbero': request.build_absolute_uri(
                                    reverse('admin_module:collabs')
                                ),
                            }
                        )
                    except Exception as e:
                        print(f"Error enviando email de confirmación: {e}")
                else:
                    messages.error(request, 'No se pudo vincular al establecimiento.')
                    
            else:  # RECHAZAR (value == 0)
                # Cambiar estado a "Cancelada"
                new_status = get_object_or_404(FlowStatus, name='Cancelada')
                
                messages.info(request, 'Solicitud de vinculación rechazada.')
                
                # 🚀 ENVIAR EMAIL AL ADMIN QUE CREÓ LA SOLICITUD
                try:
                    from notifications.email_service import send_email_notification
                    
                    vinculation_est = solicitud.created_by.admin_est.first()
                    
                    send_email_notification(
                        user=solicitud.created_by,
                        email_type='vinculacion_rechazada',
                        context={
                            'barbero_nombre': request.user.get_full_name() or request.user.username,
                            'establecimiento_nombre': vinculation_est.name_est if vinculation_est else 'Establecimiento',
                            'fecha_rechazo': timezone.now().strftime('%d/%m/%Y'),
                            'motivo': 'El barbero rechazó la solicitud',
                            'url_establecimientos': request.build_absolute_uri(
                                reverse('core:home')
                            ),
                        }
                    )
                except Exception as e:
                    print(f"Error enviando email de rechazo: {e}")
            
            # Guardar el nuevo estado
            solicitud.status = new_status
            solicitud.save()
            
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            print(f"Error en BarberValidateVinculation: {e}")
        
        return redirect('admin_module:barber_solicitudes_list')


class BarberRequestDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = BarberRequest
    template_name = 'requets/solicitudes_detail.html'
    context_object_name = 'solicitud'

    
    def get_queryset(self):
        """
        Asegura que el barbero solo pueda ver sus propias solicitudes.
        """
        return BarberRequest.objects.filter(barber=self.request.user)

class BarberRequestCreateView(LoginRequiredMixin, BreadcrumbMixin, CreateView):

    model = BarberRequest  # Modelo a crear
    form_class = BarberRequestForm  # Formulario personalizado
    template_name = 'requets/barber_request_form.html'  # HTML a renderizar
    success_url = reverse_lazy('admin_module:barber_solicitudes_list')  # Redirección tras guardar

    def get_breadcrumb(self):
        return [{'label': 'Solicitudes', 'url': reverse('admin_module:solicitud_barbero')}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener el establecimiento y su administrador
        try:
            perfil = Profile.objects.get(user=user)
            if perfil.establishment:
                context['establecimiento'] = perfil.establishment
                context['administrador'] = perfil.establishment.id_admin
        except Profile.DoesNotExist:
            context['establecimiento'] = None
            context['administrador'] = None
        
        return context

    def form_valid(self, form):
        """
        Este método se ejecuta si el formulario es válido.
        Aquí se asignan automáticamente el barbero y el establecimiento.
        """
        user = self.request.user  # Barbero autenticado
        form.instance.barber = user  # Asigna el barbero automáticamente

        # Asignar el establecimiento al que pertenece este barbero
        try:
            perfil = Profile.objects.get(user=user)
            if perfil.establishment:
                form.instance.establecimiento = perfil.establishment
        except Profile.DoesNotExist:
            pass

        # Guardar la solicitud en la base de datos
        response = super().form_valid(form)

        # 🚀 ENVIAR EMAIL AL ADMIN (si la solicitud se guardó exitosamente)
        try:
            from notifications.email_service import send_email_notification
            from django.urls import reverse
            
            solicitud = self.object
            
            if solicitud.establecimiento and solicitud.establecimiento.id_admin:
                send_email_notification(
                    user=solicitud.establecimiento.id_admin,
                    email_type='solicitud_creada',
                    context={
                        'barbero_nombre': user.get_full_name() or user.username,
                        'barbero_email': user.email,
                        'establecimiento_nombre': solicitud.establecimiento.name_est,
                        'fecha_solicitud': solicitud.created_at.strftime('%d/%m/%Y'),
                        'mensaje': getattr(solicitud, 'message', ''),
                        'url_detalle_solicitud': self.request.build_absolute_uri(
                            reverse('admin_module:admin_solicitudes_detail', kwargs={'pk': solicitud.id})
                        ),
                    }
                )
        except Exception as e:
            # Si falla el email, no afectar el proceso principal
            print(f"Error enviando email: {e}")

        return response
    
class CalendarioBarberoView(LoginRequiredMixin, View):
    """
    Vista principal del calendario del barbero.
    Carga datos reales del barbero y renderiza el template base.
    """
    login_url = '/login_module/login/'
    
    def get(self, request, barbero_id):
        # Obtener barbero real de la BD
        barbero = get_object_or_404(User, id=barbero_id, groups__name='Barbero')
        
        # Construir nombre completo
        nombre_completo = f"{barbero.first_name} {barbero.last_name}".strip()
        if not nombre_completo:
            nombre_completo = barbero.username
        
        context = {
            'barbero_id': barbero_id,
            'nombre_barbero': nombre_completo,
            'fecha_actual': timezone.now().date(),
        }
        return render(request, 'admin_module/calendario_barbero.html', context)


class CalendarioBarberMesAPIView(LoginRequiredMixin, View):
    """
    API para obtener datos del calendario mensual de un barbero.
    Retorna JSON con días que tienen citas agendadas.
    
    GET /admin/calendario/barbero/<id>/mes/?year=2025&month=12
    """
    login_url = '/login_module/login/'
    
    def get(self, request, barbero_id):
        # Validar que el barbero existe
        barbero = get_object_or_404(User, id=barbero_id, groups__name='Barbero')
        
        # Obtener parámetros de año y mes
        try:
            year = int(request.GET.get('year', timezone.now().year))
            month = int(request.GET.get('month', timezone.now().month))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Año o mes inválido'}, status=400)
        
        # Validar mes
        if not (1 <= month <= 12):
            return JsonResponse({'error': 'Mes debe estar entre 1 y 12'}, status=400)
        
        # Calcular primer y último día del mes
        first_day = datetime(year, month, 1).date()
        last_day_num = calendar.monthrange(year, month)[1]
        last_day = datetime(year, month, last_day_num).date()
        
        # Consultar citas del mes (excluir canceladas)
        citas_mes = ServiceDate.objects.filter(
            barber=barbero,
            date__date__gte=first_day,
            date__date__lte=last_day
        ).exclude(
            status='Cancelada'
        ).values('date__date').annotate(
            count=Count('id')
        ).order_by('date__date')
        
        # Construir diccionario de días con citas
        dias_con_citas = {
            cita['date__date'].isoformat(): cita['count']
            for cita in citas_mes
        }
        
        # Construir respuesta con todos los días del mes
        days = []
        for day_num in range(1, last_day_num + 1):
            day_date = datetime(year, month, day_num).date()
            day_iso = day_date.isoformat()
            
            days.append({
                'date': day_iso,
                'day': day_num,
                'has_appointments': day_iso in dias_con_citas,
                'appointment_count': dias_con_citas.get(day_iso, 0)
            })
        
        return JsonResponse({
            'year': year,
            'month': month,
            'barber_id': barbero_id,
            'barber_name': f"{barbero.first_name} {barbero.last_name}".strip() or barbero.username,
            'days': days
        })


class CalendarioBarberoDiaAPIView(LoginRequiredMixin, View):
    """
    API para obtener slots de un día específico del barbero.
    Genera slots basados en horario del establecimiento y marca ocupados según ServiceDate.
    
    GET /admin/calendario/barbero/<id>/dia/?date=2025-12-15
    """
    login_url = '/login_module/login/'
    
    def get(self, request, barbero_id):
        # Validar barbero
        barbero = get_object_or_404(User, id=barbero_id, groups__name='Barbero')
        
        # Obtener fecha del query param
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Parámetro date requerido (formato: YYYY-MM-DD)'}, status=400)
        
        try:
            fecha = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha inválido (debe ser YYYY-MM-DD)'}, status=400)
        
        # Obtener establecimiento del barbero
        try:
            establecimiento = barbero.profile.establishment
        except (Profile.DoesNotExist, AttributeError):
            return JsonResponse({'error': 'Barbero sin establecimiento asignado'}, status=400)
        
        if not establecimiento:
            return JsonResponse({'error': 'Barbero sin establecimiento asignado'}, status=400)
        
        # Generar slots del día
        slots = self._generar_slots_dia(barbero, establecimiento, fecha)
        
        return JsonResponse({
            'date': fecha.isoformat(),
            'barber_id': barbero_id,
            'barber_name': f"{barbero.first_name} {barbero.last_name}".strip() or barbero.username,
            'slots': slots
        })
    
    def _generar_slots_dia(self, barbero, establecimiento, fecha):
        """
        Genera lista de slots para un día específico.
        Basado en horario del establecimiento + duración de slot configurada.
        Marca ocupado si hay cita en ServiceDate.
        """
        # Obtener día de la semana (1=Lunes, 7=Domingo)
        dia_semana = fecha.isoweekday()
        
        # Obtener horario del establecimiento para ese día
        try:
            horario_est = EstablishmentSchedule.objects.get(
                establishment=establecimiento,
                day_of_week=dia_semana,
                is_open=True
            )
            hora_inicio = horario_est.opening_time
            hora_fin = horario_est.closing_time
        except EstablishmentSchedule.DoesNotExist:
            # No hay horario configurado, retornar vacío
            return []
        
        # Obtener duración de slot desde configuración del establecimiento
        try:
            slot_config = EstablishmentSlotConfiguration.objects.get(establishment=establecimiento)
            duracion_slot = slot_config.default_slot_duration
        except EstablishmentSlotConfiguration.DoesNotExist:
            duracion_slot = 30  # Por defecto 30 minutos
        
        # Obtener todas las citas del barbero en ese día (excluir canceladas)
        citas_dia = ServiceDate.objects.filter(
            barber=barbero,
            date__date=fecha
        ).exclude(
            status='Cancelada'
        ).select_related('product', 'customer')
        
        # Crear diccionario de citas por hora (redondear a minutos exactos)
        citas_por_hora = {}
        for cita in citas_dia:
            hora_cita = cita.date.time().replace(second=0, microsecond=0)
            citas_por_hora[hora_cita] = {
                'id': cita.id,
                'customer': f"{cita.customer.first_name} {cita.customer.last_name}".strip() or cita.customer.username,
                'service': cita.product.name if cita.product else 'Sin servicio',
                'status': cita.status,
                'price': float(cita.price_total)
            }
        
        # Generar todos los slots del día
        slots = []
        hora_actual = datetime.combine(fecha, hora_inicio)
        hora_limite = datetime.combine(fecha, hora_fin)
        
        while hora_actual < hora_limite:
            hora_slot = hora_actual.time().replace(second=0, microsecond=0)
            
            # Verificar si hay cita en este slot
            if hora_slot in citas_por_hora:
                slots.append({
                    'time': hora_slot.strftime('%H:%M'),
                    'status': 'occupied',
                    'appointment': citas_por_hora[hora_slot]
                })
            else:
                slots.append({
                    'time': hora_slot.strftime('%H:%M'),
                    'status': 'available'
                })
            
            # Avanzar al siguiente slot
            hora_actual += timedelta(minutes=duracion_slot)
        
        return slots


# Vista para mostrar servicios
class ServiciosView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'admin_module/servicios.html'
    login_url = '/login_module/login/'

    def get_breadcrumb(self):
        return [{'label': 'Productos & Servicios', 'url': reverse('admin_module:servicios'), 'icon': 'grid'}]
    
    
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Traer solo los servicios relacionados al establecimiento
        try:
            # Primero intentar obtener el establecimiento donde el usuario es admin
            establecimiento = Establishment.objects.filter(id_admin=user).first()
            
            # Si no es admin, intentar obtenerlo desde el perfil (para barberos)
            if not establecimiento:
                perfil = Profile.objects.get(user=user)
                establecimiento = perfil.establishment
            
            if establecimiento:
                servicios = (
                    Service.objects.filter(establishmentservice__establishment=establecimiento)
                    .select_related('category')
                    .distinct()
                )
            else:
                servicios = Service.objects.none()
        except (Establishment.DoesNotExist, Profile.DoesNotExist):
            servicios = Service.objects.none()

        context['servicios'] = servicios
        return context

# Agregar servicio
def agregar_servicio(request):
    if request.method == 'POST':
        form = CreateServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_module:servicios')
        else:
            # Aquí se imprime en consola si hay errores
            print("⚠️ Errores del formulario:", form.errors)
    else:
        form = CreateServiceForm()
    
    return render(request, 'admin_module/form_servicio.html', {
    'form': form,
    'action_url': reverse('admin_module:agregar_servicio')
})# Editar servicio
def editar_servicio(request, id):
    servicio = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        form = CreateServiceForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('admin_module:servicios')
    else:
        form = CreateServiceForm(instance=servicio)
        return render(request, 'admin_module/form_servicio.html', {
    'form': form,
    'action_url': reverse('admin_module:editar_servicio', args=[servicio.id])
})

# Eliminar servicio
def eliminar_servicio(request, id):
    servicio = get_object_or_404(Service, id=id)
    servicio.delete()
    return redirect('admin_module:servicios')

class ContenidosView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name= 'establecimiento/contenidos.html'
    login_url = '/login_module/login/'
    
    def get_breadcrumb(self):
        return [{'label': 'Establecimiento', 'url': reverse('admin_module:establecimiento'), 'icon': 'building'}]
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Cargar todos los establecimientos (o el actual del admin, si aplica)
        context['establecimientos'] = self.request.user.admin_est.all()

        # Si se quiere pasar un formulario vacío para registrar o editar desde modal
        context['form'] = CreateEstablishmentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        # Captura del establecimiento a editar (por ejemplo, con un input hidden)
        establishment_id = request.POST.get('establishment_id')
        if establishment_id:
            # Es edición
            establishment = get_object_or_404(Establishment, pk=establishment_id)
            form = CreateEstablishmentForm(request.POST, instance=establishment)
        else:
            # Es creación
            form = CreateEstablishmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('/admin_module/establecimiento/')  # o el name de tu url para esta vista

     
# class InventarioView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
#     template_name= 'inventario/inventario.html'
#     login_url = '/login_module/login/'
    
#     def get_breadcrumb(self):
#         return [{'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'}]
        
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context['products'] = Product.objects.all()
#         return context

# class InventarioListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
#     template_name = 'inventario/inventario.html'
#     login_url = '/login_module/login/'
    
#     def get_breadcrumb(self):
#         return [{'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'}]
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         context['products'] = Product.objects.all()
#         return context

# class ProductCreateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, CreateView):
#     template_name = 'inventario/form_product.html'
#     form_class = CreateProductForm
#     success_url = reverse_lazy('admin_module:inventario')
#     login_url = '/login_module/login/'

#     def get_breadcrumb(self):
#         return [
#             {'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'},
#             {'label': 'Crear Producto', 'url': '', 'icon': 'plus-circle'}
#         ]

#     def form_valid(self, form):
#         product=form.save(commit=False)
#         form.instance.created_by = self.request.user
#         form.instance.updated_by = self.request.user
#         product.save()
#         return super().form_valid(form)

# class ProductUpdateView(LoginRequiredMixin, BreadcrumbMixin, SuccessMessageMixin, UpdateView):
#     model = Product
#     template_name = 'inventario/form_product.html'
#     form_class = CreateProductForm
#     success_url = reverse_lazy('admin_module:inventario')
#     login_url = '/login_module/login/'

#     def get_breadcrumb(self):
#         return [
#             {'label': 'Inventario', 'url': reverse('admin_module:inventario'), 'icon': 'box-seam'},
#             {'label': 'Editar Producto', 'url': '', 'icon': 'pencil-square'}
#         ]

#     def form_valid(self, form):
#         form.instance.updated_by = self.request.user
#         return super().form_valid(form)

# class ProductDeleteView(LoginRequiredMixin, DeleteView):
#     model = Product
#     success_url = reverse_lazy('admin_module:inventario')
#     login_url = '/login_module/login/'
    
     
class ReportesView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
     template_name= 'reportes/reportes.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Reportes', 'url': reverse('admin_module:reportes'), 'icon': 'graph-up'}]

class SeguridadView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
     template_name= 'perfil/seguridad.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Seguridad', 'url': reverse('admin_module:seguridad'), 'icon': 'shield-lock'}]

class SoporteView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
     template_name= 'perfil/soporte.html'
     login_url = '/login_module/login/'
     
     def get_breadcrumb(self):
        return [{'label': 'Soporte', 'url': reverse('admin_module:soporte'), 'icon': 'headset'}]

class PerfilUsuarioView(BreadcrumbMixin, TemplateView):
    template_name = 'perfil/perfil_usuario.html'

    def get_breadcrumb(self):
        return [{'label': 'Perfil', 'url': reverse('admin_module:perfil_usuario'), 'icon': 'person-circle'}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        profile = Profile.objects.get(user=usuario)

        context['usuario'] = usuario
        context['profile'] = profile    
        context['profile_form'] = ProfileEditForm(instance=profile)
        context["user_form"] = UserEditForm(instance=usuario)

        return context

    #
    def post(self, request, *args, **kwargs):
        """ Maneja la actualización del perfil desde el formulario """
        usuario = request.user
        profile = Profile.objects.get(user=usuario)
        user_form = UserEditForm(request.POST, instance=usuario)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        # Validar y guardar el formulario
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('admin_module:perfil_usuario')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

        context = self.get_context_data(**kwargs)
        context["user_form"] = user_form
        context['profile_form'] = profile_form
        return self.render_to_response(context)
  

""" # Editar perfil 
class EditarPerfilView(LoginRequiredMixin, UpdateView):
#    model = usuario
    fields = ['first_name', 'last_name', 'email', 'username', 'profile__phone', 'profile__address', 'profile__birth_date', 'profile__document']
    template_name = 'perfil/editar_perfil.html'
    success_url = reverse_lazy('perfil:perfil_usuario')

    def get_object(self):
        return self.request.user
 """

class CreateEstablishmentView(BreadcrumbMixin,UserPassesTestMixin, FormView):
    template_name = 'establecimiento/registro_est.html'
    form_class = CreateEstablishmentForm

    def get_success_url(self):
        return '/admin_module/establecimiento/'

    def form_valid(self, form):
        from datetime import time
        from django.db import transaction
        
        # Guardar establecimiento
        establishment = form.save(commit=False)
        establishment.id_admin_id = self.request.user.id
        establishment.save()
        
        # Crear horarios por defecto en una transacción
        with transaction.atomic():
            # Crear horarios estándar: Lun-Vie 9:00-18:00, Sáb 9:00-14:00, Dom cerrado
            default_schedules = [
                {'day': 1, 'open': time(9, 0), 'close': time(18, 0), 'is_open': True},  # Lunes
                {'day': 2, 'open': time(9, 0), 'close': time(18, 0), 'is_open': True},  # Martes
                {'day': 3, 'open': time(9, 0), 'close': time(18, 0), 'is_open': True},  # Miércoles
                {'day': 4, 'open': time(9, 0), 'close': time(18, 0), 'is_open': True},  # Jueves
                {'day': 5, 'open': time(9, 0), 'close': time(18, 0), 'is_open': True},  # Viernes
                {'day': 6, 'open': time(9, 0), 'close': time(14, 0), 'is_open': True},  # Sábado
                {'day': 7, 'open': time(9, 0), 'close': time(18, 0), 'is_open': False}, # Domingo cerrado
            ]
            
            for schedule_data in default_schedules:
                EstablishmentSchedule.objects.create(
                    establishment=establishment,
                    day_of_week=schedule_data['day'],
                    opening_time=schedule_data['open'],
                    closing_time=schedule_data['close'],
                    is_open=schedule_data['is_open']
                )
            
            # Crear configuración de slots por defecto
            EstablishmentSlotConfiguration.objects.create(
                establishment=establishment,
                default_slot_duration=30,
                advance_booking_days=30,
                min_advance_booking_hours=2,
                allow_same_day_booking=True,
                business_type='traditional'
            )
        
        # Mensaje de éxito con link a configuración
        messages.success(
            self.request, 
            f'Establecimiento "{establishment.name_est}" creado exitosamente con horarios por defecto. '
            f'<a href="/admin_module/horarios/configurar/" class="btn btn-sm btn-outline-primary ms-2">'
            f'<i class="fas fa-clock me-1"></i>Configurar Horarios</a>',
            extra_tags='safe'
        )
        
        return super().form_valid(form)


    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()
        
    def handle_no_permission(self):
        return redirect('not_in_group')
    
    def get_breadcrumb(self):
        return [{'label': 'Registro Establecimiento', 'url': reverse('admin_module:registro_est'), 'icon': 'building-add'}]

class DeleteEstablishmentView(DeleteView):
    
    def get_success_url(self):
        return '/admin_module/establecimiento/'
    
    def get_queryset(self):
        return Establishment.objects.filter(id_admin_id=self.request.user.id)
    
#Solicitudes Barberos
class AdminSolicitudesListView(LoginRequiredMixin,BreadcrumbMixin, ListView):
    model = BarberRequest
    template_name = 'admin_module/solicitudes_list.html'
    context_object_name = 'solicitudes'

    # Breadcrumb (navegación)
    def get_breadcrumb(self):
        return [{'label': 'Solicitudes', 'url': reverse('admin_module:admin_solicitudes_list'), 'icon': 'file-earmark-text'}]

    def get_queryset(self):
        """
        Muestra solo las solicitudes de barberos que pertenecen
        al establecimiento del administrador actual.
        """
        user = self.request.user
        # Obtener el establecimiento donde el usuario es administrador
        establecimiento = Establishment.objects.filter(id_admin=user).first()
        if establecimiento:
            return BarberRequest.objects.filter(establecimiento=establecimiento).order_by('-fecha_solicitud')
        return BarberRequest.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        # Contadores por estado
        context['pendientes_count'] = queryset.filter(estado='pendiente').count()
        context['aprobadas_count'] = queryset.filter(estado='aprobada').count()
        context['rechazadas_count'] = queryset.filter(estado='rechazada').count()
        
        return context
    
class AdminSolicitudesDetailView(LoginRequiredMixin, BreadcrumbMixin, UpdateView):
    model = BarberRequest
    form_class = BarberRequestAdminResponseForm
    template_name = 'admin_module/solicitudes_detail.html'
    context_object_name = 'solicitud'

    def get_breadcrumb(self):
        return [
            {'label': 'Solicitudes', 'url': reverse('admin_module:admin_solicitudes_list'), 'icon': 'file-earmark-text'},
            {'label': 'Detalle', 'url': '', 'icon': 'eye'}
        ]

    def dispatch(self, request, *args, **kwargs):
        # Obtener la solicitud
        solicitud = self.get_object()
        
        # Si la solicitud ya fue procesada (aprobada o rechazada), no permitir modificaciones
        if solicitud.estado != 'pendiente' and request.method == 'POST':
            from django.contrib import messages
            messages.warning(request, 'Esta solicitud ya ha sido procesada y no puede ser modificada.')
            return redirect('admin_module:admin_solicitudes_list')
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Estado enviado en POST (desde los botones)
        estado_nuevo = self.request.POST.get('accion_estado')

        if estado_nuevo in ['aprobada', 'rechazada']:
            form.instance.estado = estado_nuevo
            
            # Guardar primero
            response = super().form_valid(form)
            
            # 🚀 ENVIAR EMAIL AL BARBERO
            try:
                from notifications.email_service import send_email_notification
                from django.utils import timezone
                
                solicitud = form.instance
                barbero = solicitud.user
                
                if estado_nuevo == 'aprobada':
                    send_email_notification(
                        user=barbero,
                        email_type='solicitud_aprobada',
                        context={
                            'establecimiento_nombre': solicitud.establecimiento.name_est,
                            'establecimiento_direccion': f"{solicitud.establecimiento.address_est}, {solicitud.establecimiento.city_est}",
                            'fecha_aprobacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
                            'url_panel_barbero': self.request.build_absolute_uri(
                                reverse('barber_module:main')
                            ),
                        }
                    )
                
                elif estado_nuevo == 'rechazada':
                    send_email_notification(
                        user=barbero,
                        email_type='solicitud_rechazada',
                        context={
                            'establecimiento_nombre': solicitud.establecimiento.name_est,
                            'fecha_rechazo': timezone.now().strftime('%d/%m/%Y %H:%M'),
                            'motivo': self.request.POST.get('motivo_rechazo', 'No especificado'),
                            'url_establecimientos': self.request.build_absolute_uri(
                                reverse('core:home')
                            ),
                        }
                    )
            except Exception as e:
                # Si falla el email, no afectar el proceso principal
                print(f"Error enviando email: {e}")
            
            return response

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('admin_module:admin_solicitudes_list')

class SelecGrupoView(LoginRequiredMixin, TemplateView):
    """Vista para visualizar y modificar los roles activos del usuario en el sistema"""
    template_name = 'perfil/seleccionar_rol.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Permitir que esta vista se cargue en un iframe"""
        response = super().dispatch(request, *args, **kwargs)
        # Eliminar la restricción X-Frame-Options para permitir iframe
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener grupos actuales del usuario
        user_groups = user.groups.values_list('name', flat=True)
        
        context['user_groups'] = list(user_groups)
        context['has_role'] = user.groups.exists()
        
        # Información de cada rol
        context['roles_info'] = {
            'Cliente': {
                'icon': 'person',
                'description': 'Acceso como cliente de la barbería',
                'features': ['Reservar citas', 'Ver servicios disponibles', 'Historial de citas', 'Calificar servicios']
            },
            'Barbero': {
                'icon': 'scissors',
                'description': 'Acceso como barbero profesional',
                'features': ['Gestionar agenda', 'Atender clientes', 'Ver solicitudes', 'Vincularse a establecimientos']
            },
            'Administrador': {
                'icon': 'gear',
                'description': 'Gestión completa del establecimiento',
                'features': ['Crear establecimientos', 'Gestionar barberos', 'Aprobar solicitudes', 'Ver reportes']
            }
        }
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Manejar la modificación de roles del usuario"""
        user = request.user
        selected_roles = request.POST.getlist('roles')  # Lista de roles seleccionados
        
        # Roles válidos en el sistema
        valid_roles = ['Cliente', 'Barbero', 'Administrador']
        
        # Validar que al menos se seleccionó un rol
        if not selected_roles:
            messages.warning(request, 'Debes seleccionar al menos un rol.')
            return redirect('admin_module:seleccionar_rol')
        
        # Validar que todos los roles seleccionados sean válidos
        for role in selected_roles:
            if role not in valid_roles:
                messages.error(request, f'El rol "{role}" no es válido.')
                return redirect('admin_module:seleccionar_rol')
        
        try:
            # Limpiar todos los grupos actuales del usuario
            user.groups.clear()
            
            # Agregar los nuevos grupos seleccionados
            for role_name in selected_roles:
                group, created = Group.objects.get_or_create(name=role_name)
                user.groups.add(group)
            
            messages.success(request, 'Tus roles se han actualizado correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar roles: {str(e)}')
        
        return redirect('admin_module:seleccionar_rol')


# ==========================================
# ENDPOINTS API PARA DASHBOARD EN TIEMPO REAL
# ==========================================

class DashboardCitasHoyAPIView(LoginRequiredMixin, View):
    """
    Endpoint API que devuelve el número de citas programadas para hoy
    en el establecimiento del administrador
    """
    login_url = '/login_module/login/'
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el establecimiento del usuario administrador
            establecimiento = Establishment.objects.filter(id_admin=request.user).first()
            
            if not establecimiento:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes un establecimiento asignado',
                    'data': {'citas_hoy': 0, 'comparacion': 0}
                })
            
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)
            
            # Citas de hoy
            citas_hoy = ServiceDate.objects.filter(
                date__date=today,
                establishment=establecimiento
            ).count()
            
            # Citas de ayer para comparación
            citas_ayer = ServiceDate.objects.filter(
                date__date=yesterday,
                establishment=establecimiento
            ).count()
            
            # Calcular porcentaje de cambio
            if citas_ayer > 0:
                cambio_porcentaje = ((citas_hoy - citas_ayer) / citas_ayer) * 100
            else:
                cambio_porcentaje = 100 if citas_hoy > 0 else 0
            
            return JsonResponse({
                'success': True,
                'data': {
                    'citas_hoy': citas_hoy,
                    'citas_ayer': citas_ayer,
                    'cambio_porcentaje': round(cambio_porcentaje, 1),
                    'tendencia': 'up' if cambio_porcentaje > 0 else 'down' if cambio_porcentaje < 0 else 'neutral'
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener las citas: {str(e)}',
                'data': {'citas_hoy': 0}
            }, status=500)


class DashboardIngresosAPIView(LoginRequiredMixin, View):
    """
    Endpoint API que devuelve el ingreso estimado del día
    basado en las citas programadas y completadas
    """
    login_url = '/login_module/login/'
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el establecimiento del usuario administrador
            establecimiento = Establishment.objects.filter(id_admin=request.user).first()
            
            if not establecimiento:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes un establecimiento asignado',
                    'data': {'ingresos_hoy': 0}
                })
            
            today = timezone.now().date()
            
            # Ingresos del día (citas completadas + agendadas)
            ingresos_result = ServiceDate.objects.filter(
                date__date=today,
                establishment=establecimiento
            ).exclude(
                status='Cancelada'
            ).aggregate(
                total=Sum('price_total')
            )
            
            ingresos_hoy = float(ingresos_result['total'] or 0)
            
            # Ingresos confirmados (solo completadas)
            ingresos_confirmados = ServiceDate.objects.filter(
                date__date=today,
                establishment=establecimiento,
                status='Completada'
            ).aggregate(
                total=Sum('price_total')
            )['total'] or 0
            
            # Calcular promedio semanal para comparación
            hace_7_dias = today - timedelta(days=7)
            promedio_semanal = ServiceDate.objects.filter(
                date__date__gte=hace_7_dias,
                date__date__lt=today,
                establishment=establecimiento
            ).exclude(
                status='Cancelada'
            ).aggregate(
                total=Sum('price_total')
            )['total'] or 0
            
            promedio_diario = float(promedio_semanal) / 7 if promedio_semanal > 0 else 0
            
            # Calcular porcentaje vs promedio
            if promedio_diario > 0:
                cambio_vs_promedio = ((ingresos_hoy - promedio_diario) / promedio_diario) * 100
            else:
                cambio_vs_promedio = 100 if ingresos_hoy > 0 else 0
            
            return JsonResponse({
                'success': True,
                'data': {
                    'ingresos_hoy': round(ingresos_hoy, 2),
                    'ingresos_confirmados': round(float(ingresos_confirmados), 2),
                    'promedio_diario': round(promedio_diario, 2),
                    'cambio_vs_promedio': round(cambio_vs_promedio, 1),
                    'tendencia': 'up' if cambio_vs_promedio > 0 else 'down' if cambio_vs_promedio < 0 else 'neutral'
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al calcular ingresos: {str(e)}',
                'data': {'ingresos_hoy': 0}
            }, status=500)


class DashboardBarberosActivosAPIView(LoginRequiredMixin, View):
    """
    Endpoint API que devuelve el número de barberos activos
    en el establecimiento
    """
    login_url = '/login_module/login/'
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el establecimiento del usuario administrador
            establecimiento = Establishment.objects.filter(id_admin=request.user).first()
            
            if not establecimiento:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes un establecimiento asignado',
                    'data': {'barberos_activos': 0}
                })
            
            # Barberos activos (usuarios activos del grupo Barbero)
            barberos_activos = Profile.objects.filter(
                establishment=establecimiento,
                user__is_active=True,
                user__groups__name='Barbero'
            ).count()
            
            # Total de barberos (incluyendo inactivos)
            total_barberos = Profile.objects.filter(
                establishment=establecimiento,
                user__groups__name='Barbero'
            ).count()
            
            # Barberos con citas hoy
            today = timezone.now().date()
            barberos_con_citas_hoy = ServiceDate.objects.filter(
                date__date=today,
                establishment=establecimiento
            ).values('barber').distinct().count()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'barberos_activos': barberos_activos,
                    'total_barberos': total_barberos,
                    'barberos_con_citas_hoy': barberos_con_citas_hoy,
                    'porcentaje_ocupados': round((barberos_con_citas_hoy / barberos_activos * 100), 1) if barberos_activos > 0 else 0
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener barberos activos: {str(e)}',
                'data': {'barberos_activos': 0}
            }, status=500)


class DashboardIngresosSemanalesAPIView(LoginRequiredMixin, View):
    """
    Endpoint API que devuelve los ingresos de los últimos 7 días
    para la gráfica de ingresos semanales
    """
    login_url = '/login_module/login/'
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el establecimiento del usuario administrador
            establecimiento = Establishment.objects.filter(id_admin=request.user).first()
            
            if not establecimiento:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes un establecimiento asignado',
                    'data': {}
                })
            
            today = timezone.now().date()
            
            # Obtener ingresos de los últimos 7 días (semana actual)
            ingresos_semana_actual = []
            labels = []
            dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
            
            for i in range(6, -1, -1):
                dia = today - timedelta(days=i)
                ingresos_dia = ServiceDate.objects.filter(
                    date__date=dia,
                    establishment=establecimiento
                ).exclude(
                    status='Cancelada'
                ).aggregate(
                    total=Sum('price_total')
                )['total'] or 0
                
                ingresos_semana_actual.append(float(ingresos_dia))
                # Obtener nombre del día de la semana
                dia_semana = dias_semana[dia.weekday()]
                labels.append(dia_semana)
            
            # Obtener ingresos de la semana anterior (hace 7-13 días) para comparación
            ingresos_semana_anterior = []
            for i in range(13, 6, -1):
                dia = today - timedelta(days=i)
                ingresos_dia = ServiceDate.objects.filter(
                    date__date=dia,
                    establishment=establecimiento
                ).exclude(
                    status='Cancelada'
                ).aggregate(
                    total=Sum('price_total')
                )['total'] or 0
                
                ingresos_semana_anterior.append(float(ingresos_dia))
            
            return JsonResponse({
                'success': True,
                'data': {
                    'labels': labels,
                    'semana_actual': ingresos_semana_actual,
                    'semana_anterior': ingresos_semana_anterior,
                    'total_actual': sum(ingresos_semana_actual),
                    'total_anterior': sum(ingresos_semana_anterior)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener ingresos semanales: {str(e)}',
                'data': {}
            }, status=500)


class DashboardServiciosPopularesAPIView(LoginRequiredMixin, View):
    """
    Endpoint API que devuelve los servicios más solicitados
    para la gráfica de servicios populares
    """
    login_url = '/login_module/login/'
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el establecimiento del usuario administrador
            establecimiento = Establishment.objects.filter(id_admin=request.user).first()
            
            if not establecimiento:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes un establecimiento asignado',
                    'data': {}
                })
            
            # Obtener el parámetro de periodo (por defecto: mes actual)
            periodo = request.GET.get('periodo', 'mes')
            today = timezone.now().date()
            
            # Calcular fecha de inicio según el periodo
            if periodo == 'mes':
                fecha_inicio = today.replace(day=1)
            elif periodo == '3meses':
                fecha_inicio = (today - timedelta(days=90))
            elif periodo == 'anio':
                fecha_inicio = today.replace(month=1, day=1)
            else:
                fecha_inicio = today.replace(day=1)
            
            # Obtener los servicios más solicitados con su cantidad
            servicios_populares = ServiceDate.objects.filter(
                date__date__gte=fecha_inicio,
                date__date__lte=today,
                establishment=establecimiento
            ).exclude(
                status='Cancelada'
            ).values(
                'product__name'
            ).annotate(
                cantidad=Count('id'),
                ingresos=Sum('price_total')
            ).order_by('-cantidad')[:10]  # Top 10 servicios
            
            # Preparar datos para la gráfica
            labels = []
            cantidades = []
            ingresos = []
            
            for servicio in servicios_populares:
                labels.append(servicio['product__name'] or 'Sin nombre')
                cantidades.append(servicio['cantidad'])
                ingresos.append(float(servicio['ingresos'] or 0))
            
            return JsonResponse({
                'success': True,
                'data': {
                    'labels': labels,
                    'cantidades': cantidades,
                    'ingresos': ingresos,
                    'periodo': periodo,
                    'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                    'fecha_fin': today.strftime('%Y-%m-%d')
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener servicios populares: {str(e)}',
                'data': {}
            }, status=500)
