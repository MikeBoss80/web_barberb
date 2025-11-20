"""
============================================
EJEMPLOS DE USO - SISTEMA DE NOTIFICACIONES BARBERB
============================================

Este archivo muestra cómo usar el sistema de notificaciones por email
actualizado con todos los tipos específicos del proyecto BarberB.
"""

from notifications.email_service import send_email_notification
from django.urls import reverse


# ============================================
# 📅 EJEMPLOS DE CITAS - CLIENTE
# ============================================

# EJEMPLO 1: Cita creada por cliente
def crear_cita_cliente(request, form):
    cita = form.instance
    
    send_email_notification(
        user=cita.cliente,
        email_type='appointment_created_client',
        context={
            'servicio_nombre': cita.servicio.nombre,
            'barbero_nombre': cita.barbero.get_full_name(),
            'fecha_cita': cita.fecha.strftime('%d/%m/%Y'),
            'hora_cita': cita.fecha.strftime('%I:%M %p'),
            'duracion': cita.servicio.duracion,
            'precio': cita.precio_total,
            'establecimiento_nombre': cita.establecimiento.nombre,
            'establecimiento_direccion': cita.establecimiento.direccion,
            'establecimiento_telefono': cita.establecimiento.telefono,
            'url_detalle_cita': request.build_absolute_uri(
                reverse('citas:detalle', kwargs={'pk': cita.id})
            ),
        }
    )

# EJEMPLO 2: Recordatorio 24 horas antes
def enviar_recordatorio_24h():
    from django.core.management.base import BaseCommand
    from datetime import datetime, timedelta
    
    manana = datetime.now() + timedelta(days=1)
    citas = Cita.objects.filter(fecha__date=manana.date(), estado='confirmada')
    
    for cita in citas:
        send_email_notification(
            user=cita.cliente,
            email_type='appointment_reminder_24h',
            context={
                'servicio_nombre': cita.servicio.nombre,
                'barbero_nombre': cita.barbero.get_full_name(),
                'fecha_cita': cita.fecha.strftime('%d/%m/%Y'),
                'hora_cita': cita.fecha.strftime('%I:%M %p'),
                'establecimiento_nombre': cita.establecimiento.nombre,
                'establecimiento_direccion': cita.establecimiento.direccion,
                'establecimiento_telefono': cita.establecimiento.telefono,
                'url_confirmar_asistencia': f"/citas/{cita.id}/confirmar/",
                'url_cancelar_cita': f"/citas/{cita.id}/cancelar/",
            }
        )

# EJEMPLO 3: Solicitud de calificación post-servicio
def solicitar_calificacion_cliente(cita_id):
    cita = Cita.objects.get(id=cita_id)
    
    send_email_notification(
        user=cita.cliente,
        email_type='appointment_rate_request',
        context={
            'servicio_nombre': cita.servicio.nombre,
            'barbero_nombre': cita.barbero.get_full_name(),
            'fecha_cita': cita.fecha.strftime('%d/%m/%Y'),
            'establecimiento_nombre': cita.establecimiento.nombre,
            'url_calificar_servicio': f"/citas/{cita.id}/calificar/",
            'url_agendar_nueva_cita': "/citas/nueva/",
            # Opcional: código de descuento para próxima cita
            'codigo_descuento': 'FIDELIDAD10',
            'descuento_porcentaje': 10,
        }
    )


# ============================================
# 💈 EJEMPLOS DE BARBERO
# ============================================

# EJEMPLO 4: Agenda diaria del barbero (enviado cada mañana a las 7 AM)
def enviar_agenda_diaria_barbero(barbero):
    from datetime import datetime
    
    hoy = datetime.now().date()
    citas_hoy = Cita.objects.filter(
        barbero=barbero, 
        fecha__date=hoy, 
        estado='confirmada'
    ).order_by('fecha')
    
    ingresos_estimados = sum(cita.precio_total for cita in citas_hoy)
    
    send_email_notification(
        user=barbero,
        email_type='barber_daily_schedule',
        context={
            'barbero_nombre': barbero.get_full_name(),
            'fecha_hoy': hoy.strftime('%d/%m/%Y'),
            'citas_hoy': [{
                'hora': cita.fecha.strftime('%I:%M %p'),
                'cliente_nombre': cita.cliente.get_full_name(),
                'servicio': cita.servicio.nombre,
                'duracion': f"{cita.servicio.duracion}",
                'precio': cita.precio_total,
                'notas': cita.notas_especiales,
            } for cita in citas_hoy],
            'total_citas': citas_hoy.count(),
            'ingresos_estimados': ingresos_estimados,
            'horas_trabajo': '8 horas',
            'tiempo_libre': '2 horas',
            'recordatorios': [
                'Revisar herramientas antes de empezar',
                'Actualizar inventario de productos',
            ],
            'url_agenda_completa': '/barbero/agenda/',
            'url_reportar_llegada': '/barbero/llegada/',
        }
    )


# ============================================
# 🧑‍🔧 EJEMPLOS DE SOLICITUDES
# ============================================

# EJEMPLO 5: Nueva solicitud recibida por admin
def notificar_nueva_solicitud_admin(request, solicitud):
    send_email_notification(
        user=solicitud.establecimiento.administrador,
        email_type='new_request_admin',
        context={
            'barbero_nombre': solicitud.barbero.get_full_name(),
            'barbero_email': solicitud.barbero.email,
            'barbero_telefono': getattr(solicitud.barbero.profile, 'telefono', ''),
            'barbero_experiencia': getattr(solicitud.barbero.profile, 'anos_experiencia', ''),
            'establecimiento_nombre': solicitud.establecimiento.nombre,
            'fecha_solicitud': solicitud.fecha_creacion.strftime('%d/%m/%Y'),
            'mensaje_barbero': solicitud.mensaje,
            'especialidades': solicitud.especialidades.all() if hasattr(solicitud, 'especialidades') else [],
            'url_detalle_solicitud': request.build_absolute_uri(
                reverse('admin:solicitud_detalle', kwargs={'pk': solicitud.id})
            ),
            'url_aprobar_solicitud': request.build_absolute_uri(
                reverse('admin:solicitud_aprobar', kwargs={'pk': solicitud.id})
            ),
            'url_rechazar_solicitud': request.build_absolute_uri(
                reverse('admin:solicitud_rechazar', kwargs={'pk': solicitud.id})
            ),
        }
    )

# EJEMPLO 6: Confirmación de solicitud enviada al barbero
def confirmar_solicitud_enviada(solicitud):
    send_email_notification(
        user=solicitud.barbero,
        email_type='request_submitted_barber',
        context={
            'establecimiento_nombre': solicitud.establecimiento.nombre,
            'establecimiento_direccion': solicitud.establecimiento.direccion,
            'fecha_solicitud': solicitud.fecha_creacion.strftime('%d/%m/%Y'),
            'solicitud_id': solicitud.id,
            'mensaje_enviado': solicitud.mensaje,
            'url_mis_solicitudes': '/barbero/mis-solicitudes/',
            'url_buscar_establecimientos': '/establecimientos/',
        }
    )


# ============================================
# 🤝 EJEMPLOS DE VINCULACIÓN
# ============================================

# EJEMPLO 7: Vinculación aprobada
def notificar_vinculacion_aprobada(vinculacion, mensaje_admin=None):
    send_email_notification(
        user=vinculacion.barbero,
        email_type='link_request_approved',
        context={
            'establecimiento_nombre': vinculacion.establecimiento.nombre,
            'establecimiento_direccion': vinculacion.establecimiento.direccion,
            'admin_nombre': vinculacion.establecimiento.administrador.get_full_name(),
            'fecha_aprobacion': timezone.now().strftime('%d/%m/%Y'),
            'mensaje_admin': mensaje_admin,
            'informacion_establecimiento': [
                'Horario de trabajo: Lunes a Sábado 9:00 AM - 7:00 PM',
                'Comisión por servicio: 60%',
                'Pago semanal todos los viernes',
                'Capacitación inicial incluida',
            ],
            'url_panel_barbero': '/barbero/panel/',
            'url_configurar_horarios': '/barbero/horarios/',
            'url_contactar_admin': f'/admin/contacto/{vinculacion.establecimiento.id}/',
        }
    )


# ============================================
# 📦 EJEMPLOS DE INVENTARIO
# ============================================

# EJEMPLO 8: Stock bajo en inventario
def alertar_stock_bajo(producto):
    send_email_notification(
        user=producto.establecimiento.administrador,
        email_type='inventory_low_stock',
        context={
            'producto_nombre': producto.nombre,
            'producto_categoria': producto.categoria.nombre,
            'stock_actual': producto.stock_actual,
            'stock_minimo': producto.stock_minimo,
            'codigo_producto': producto.codigo,
            'consumo_promedio': producto.consumo_promedio_semanal,
            'dias_duracion': producto.dias_estimados_duracion,
            'ultimo_pedido': producto.ultimo_pedido.strftime('%d/%m/%Y') if producto.ultimo_pedido else None,
            'proveedor_nombre': producto.proveedor.nombre if producto.proveedor else None,
            'proveedor_telefono': producto.proveedor.telefono if producto.proveedor else None,
            'proveedor_email': producto.proveedor.email if producto.proveedor else None,
            'precio_unitario': producto.precio_compra,
            'url_actualizar_inventario': f'/inventario/producto/{producto.id}/editar/',
            'url_pedido_rapido': f'/inventario/pedido/{producto.id}/',
            'url_inventario_completo': '/inventario/',
        }
    )


# ============================================
# 🔐 EJEMPLOS DE SEGURIDAD Y PERFIL
# ============================================

# EJEMPLO 9: Confirmación de actualización de perfil
def confirmar_actualizacion_perfil(user, campos_actualizados):
    send_email_notification(
        user=user,
        email_type='profile_update_confirmation',
        context={
            'fecha_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M'),
            'campos_actualizados': campos_actualizados,
            'cambios_importantes': [
                {'campo': 'Email', 'descripcion': 'Se requiere verificación'},
                {'campo': 'Teléfono', 'descripcion': 'Se envió código de verificación'},
            ] if 'email' in campos_actualizados or 'telefono' in campos_actualizados else [],
            'url_ver_perfil': '/perfil/',
            'url_soporte': '/soporte/',
        }
    )


# ============================================
# COMANDOS DE MANAGEMENT PARA AUTOMATIZACIÓN
# ============================================

# EJEMPLO 10: Comando para enviar agenda diaria (ejecutar con cron a las 7 AM)
"""
# Archivo: management/commands/enviar_agenda_diaria.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Envía la agenda diaria a todos los barberos activos'
    
    def handle(self, *args, **options):
        barberos = User.objects.filter(
            groups__name='Barbero',
            is_active=True,
            profile__establecimiento__isnull=False
        )
        
        for barbero in barberos:
            enviar_agenda_diaria_barbero(barbero)
        
        self.stdout.write(
            self.style.SUCCESS(f'Agendas enviadas a {barberos.count()} barberos')
        )
"""

# EJEMPLO 11: Comando para recordatorios 24h (ejecutar diariamente a las 6 PM)
"""
# Archivo: management/commands/enviar_recordatorios_24h.py

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Envía recordatorios de citas 24 horas antes'
    
    def handle(self, *args, **options):
        enviar_recordatorio_24h()
        self.stdout.write(
            self.style.SUCCESS('Recordatorios 24h enviados')
        )
"""


# ============================================
# INTEGRACIONES EN VISTAS EXISTENTES
# ============================================

"""
INTEGRACIÓN RECOMENDADA EN TUS VISTAS:

1. En CreateCitaView.form_valid():
   crear_cita_cliente(self.request, form)

2. En CancelarCitaView.post():
   send_email_notification(user=cita.cliente, email_type='appointment_cancelled_by_client', context={...})

3. En AprobarSolicitudView.post():
   notificar_nueva_solicitud_admin(self.request, solicitud)

4. En ActualizarInventarioView.form_valid():
   if producto.stock_actual <= producto.stock_minimo:
       alertar_stock_bajo(producto)

5. En UpdateProfileView.form_valid():
   confirmar_actualizacion_perfil(self.request.user, ['nombre', 'telefono'])
"""


# ============================================
# CONFIGURACIÓN DE CRON JOBS (LINUX/MAC)
# ============================================

"""
# Agregar al crontab (crontab -e):

# Agenda diaria a las 7:00 AM
0 7 * * * cd /path/to/project && python manage.py enviar_agenda_diaria

# Recordatorios 24h a las 6:00 PM  
0 18 * * * cd /path/to/project && python manage.py enviar_recordatorios_24h

# Recordatorios 2h cada hora de 8 AM a 8 PM
0 8-20 * * * cd /path/to/project && python manage.py enviar_recordatorios_2h

# Revisión de stock bajo todos los lunes a las 9 AM
0 9 * * 1 cd /path/to/project && python manage.py revisar_inventario_bajo
"""