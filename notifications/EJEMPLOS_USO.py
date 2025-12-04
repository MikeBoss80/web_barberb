"""
============================================
EJEMPLOS DE USO - SISTEMA DE NOTIFICACIONES BARBERB
============================================

Guía rápida para usar el sistema de notificaciones por email.
Simplemente importa la función y úsala en cualquier vista o función.
"""

from notifications.email_service import send_email_notification


# ============================================
# � USO BÁSICO
# ============================================

def ejemplo_basico():
    """Ejemplo más simple de envío de email"""
    
    # Obtener el usuario (desde request, base de datos, etc.)
    user = request.user  # o User.objects.get(id=123)
    
    # Enviar email
    send_email_notification(
        user=user,
        email_type='appointment_created_client',
        context={
            'servicio_nombre': 'Corte Premium',
            'barbero_nombre': 'Carlos García',
            'fecha_cita': '25/11/2025',
            'hora_cita': '10:30 AM',
            'establecimiento_nombre': 'Barbería Elite',
        }
    )


# ============================================
# 📅 EJEMPLOS POR CATEGORÍA
# ============================================

class CitasView:
    """Ejemplos en vistas de citas"""
    
    def form_valid(self, form):
        """Al crear una cita nueva"""
        cita = form.save()
        
        # ✅ Notificar al cliente
        send_email_notification(
            user=cita.customer,
            email_type='appointment_created_client',
            context={
                'servicio_nombre': cita.service.name,
                'barbero_nombre': cita.barber.get_full_name(),
                'fecha_cita': cita.date.strftime('%d/%m/%Y'),
                'hora_cita': cita.date.strftime('%I:%M %p'),
                'precio': cita.price,
                'establecimiento_nombre': cita.service.establishment.name_est,
                'establecimiento_direccion': cita.service.establishment.address_est,
                'url_detalle_cita': f'/citas/{cita.id}/',
            }
        )
        
        return super().form_valid(form)


class SolicitudesView:
    """Ejemplos en vistas de solicitudes"""
    
    def enviar_solicitud(self, solicitud):
        """Al recibir nueva solicitud de barbero"""
        
        # ✅ Notificar al admin
        send_email_notification(
            user=solicitud.establishment.id_admin,
            email_type='new_request_admin',
            context={
                'barbero_nombre': solicitud.user.get_full_name(),
                'barbero_email': solicitud.user.email,
                'establecimiento_nombre': solicitud.establishment.name_est,
                'fecha_solicitud': solicitud.created_at.strftime('%d/%m/%Y'),
                'mensaje_barbero': solicitud.message,
                'url_aprobar_solicitud': f'/admin/solicitudes/{solicitud.id}/aprobar/',
                'url_rechazar_solicitud': f'/admin/solicitudes/{solicitud.id}/rechazar/',
            }
        )


class InventarioView:
    """Ejemplos en vistas de inventario"""
    
    def verificar_stock(self, producto):
        """Al detectar stock bajo"""
        
        if producto.stock_actual <= producto.stock_minimo:
            # ✅ Alertar al admin
            send_email_notification(
                user=producto.establecimiento.administrador,
                email_type='inventory_low_stock',
                context={
                    'producto_nombre': producto.nombre,
                    'stock_actual': producto.stock_actual,
                    'stock_minimo': producto.stock_minimo,
                    'establecimiento_nombre': producto.establecimiento.nombre,
                    'url_pedido_rapido': f'/inventario/pedido/{producto.id}/',
                }
            )


# ============================================
# � AUTOMATIZACIÓN
# ============================================

def enviar_recordatorios_diarios():
    """Comando para enviar recordatorios (cron job)"""
    from datetime import datetime, timedelta
    from services_module.models import ServiceDate
    
    # Buscar citas de mañana
    manana = datetime.now() + timedelta(days=1)
    citas = ServiceDate.objects.filter(
        date__date=manana.date(),
        status='confirmada'
    )
    
    # Enviar recordatorio a cada cliente
    for cita in citas:
        send_email_notification(
            user=cita.customer,
            email_type='appointment_reminder_24h',
            context={
                'servicio_nombre': cita.service.name,
                'barbero_nombre': cita.barber.get_full_name(),
                'fecha_cita': cita.date.strftime('%d/%m/%Y'),
                'hora_cita': cita.date.strftime('%I:%M %p'),
                'establecimiento_nombre': cita.service.establishment.name_est,
                'url_confirmar_asistencia': f'/citas/{cita.id}/confirmar/',
                'url_cancelar_cita': f'/citas/{cita.id}/cancelar/',
            }
        )


def enviar_agenda_diaria_barberos():
    """Comando para agenda diaria de barberos (cron job)"""
    from django.contrib.auth.models import User
    from datetime import datetime
    
    # Obtener barberos activos
    barberos = User.objects.filter(groups__name='Barbero', is_active=True)
    hoy = datetime.now().date()
    
    for barbero in barberos:
        # Obtener citas del barbero para hoy
        citas_hoy = ServiceDate.objects.filter(
            barber=barbero,
            date__date=hoy,
            status='confirmada'
        )
        
        send_email_notification(
            user=barbero,
            email_type='barber_daily_schedule',
            context={
                'barbero_nombre': barbero.get_full_name(),
                'fecha_hoy': hoy.strftime('%d/%m/%Y'),
                'total_citas': citas_hoy.count(),
                'citas_hoy': [
                    {
                        'hora': cita.date.strftime('%I:%M %p'),
                        'cliente_nombre': cita.customer.get_full_name(),
                        'servicio': cita.service.name,
                        'precio': cita.price,
                    }
                    for cita in citas_hoy
                ],
                'url_agenda_completa': '/barbero/agenda/',
            }
        )


# ============================================
# � TIPOS DE EMAIL DISPONIBLES
# ============================================

"""
LISTA COMPLETA DE TIPOS DE EMAIL:

🔐 SEGURIDAD:
- profile_update_confirmation

📅 CITAS - CLIENTE:
- appointment_created_client
- appointment_updated_client
- appointment_cancelled_by_client
- appointment_cancelled_by_admin
- appointment_reminder_24h
- appointment_reminder_2h
- appointment_rate_request
- appointment_no_show_followup

💈 CITAS - BARBERO:
- appointment_updated_barber
- appointment_cancelled_barber
- barber_daily_schedule
- barber_daily_alert

🏢 ADMIN:
- daily_appointments_report
- appointment_conflict_warning

🧑‍🔧 SOLICITUDES:
- new_request_admin
- request_submitted_barber
- request_status_update
- pending_requests_reminder

🤝 VINCULACIÓN:
- link_request_submitted
- link_request_approved
- link_request_rejected

📦 INVENTARIO:
- inventory_low_stock
- inventory_out_of_stock
- inventory_new_product
- inventory_expiration_warning
- inventory_update_confirmation

⚙️ SISTEMA:
- establishment_info_updated
"""


# ============================================
# 🛠️ INTEGRACIÓN RÁPIDA
# ============================================

"""
CÓMO INTEGRAR EN TUS VISTAS EXISTENTES:

1. Importar la función:
   from notifications.email_service import send_email_notification

2. Agregar en el método donde quieres enviar email:
   send_email_notification(
       user=usuario_destinatario,
       email_type='tipo_email_de_la_lista_arriba',
       context={
           'variable1': 'valor1',
           'variable2': 'valor2',
           # ... todas las variables que usa el template
       }
   )

3. ¡Listo! El email se envía automáticamente.

TIPS:
- El user debe tener email válido
- El email_type debe existir en EMAIL_TYPES
- Las variables del context deben coincidir con el template
- Usa try/except para manejar errores si es crítico
"""


# ============================================
# 🔧 CONFIGURACIÓN CRON JOBS
# ============================================

"""
COMANDOS DISPONIBLES:

1. Recordatorios automáticos:
   python manage.py send_appointment_reminders --type=24h
   python manage.py send_appointment_reminders --type=2h

2. Agenda diaria barberos:
   python manage.py send_daily_schedule

CONFIGURACIÓN CRON (Linux/Mac):
# Editar crontab: crontab -e

# Agenda diaria a las 7:00 AM
0 7 * * * cd /ruta/proyecto && python manage.py send_daily_schedule

# Recordatorios 24h a las 6:00 PM
0 18 * * * cd /ruta/proyecto && python manage.py send_appointment_reminders --type=24h

# Recordatorios 2h cada hora de 8 AM a 8 PM
0 8-20 * * * cd /ruta/proyecto && python manage.py send_appointment_reminders --type=2h

WINDOWS (Task Scheduler):
- Crear tarea básica
- Trigger: Diario a la hora deseada  
- Action: Ejecutar programa
- Program: python
- Arguments: manage.py send_daily_schedule
- Start in: C:\ruta\a\tu\proyecto
"""