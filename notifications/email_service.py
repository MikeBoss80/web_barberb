"""
Servicio centralizado para envío de emails
Uso simple desde cualquier vista:
    from notifications.email_service import send_email_notification
    send_email_notification(user, 'solicitud_creada', context_data)
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import EmailNotification
import logging

logger = logging.getLogger(__name__)


# Configuración de tipos de email con sus templates y asuntos
EMAIL_TYPES = {
    # 🔐 LOGIN & SEGURIDAD
    'profile_update_confirmation': {
        'subject': '✅ Perfil Actualizado - BarberB',
        'template': 'notifications/emails/profile_update_confirmation.html',
    },
    
    # 📅 CITAS – CLIENTE
    'appointment_created_client': {
        'subject': '📅 ¡Tu cita ha sido confirmada! - BarberB',
        'template': 'notifications/emails/appointment_created_client.html',
    },
    'appointment_updated_client': {
        'subject': '📝 Tu cita ha sido actualizada - BarberB',
        'template': 'notifications/emails/appointment_updated_client.html',
    },
    'appointment_cancelled_by_client': {
        'subject': '🚫 Cita cancelada - BarberB',
        'template': 'notifications/emails/appointment_cancelled_by_client.html',
    },
    'appointment_cancelled_by_admin': {
        'subject': '⚠️ Tu cita ha sido cancelada - BarberB',
        'template': 'notifications/emails/appointment_cancelled_by_admin.html',
    },
    'appointment_reminder_24h': {
        'subject': '⏰ Recordatorio: Tu cita es mañana - BarberB',
        'template': 'notifications/emails/appointment_reminder_24h.html',
    },
    'appointment_reminder_2h': {
        'subject': '🕐 ¡Tu cita es en 2 horas! - BarberB',
        'template': 'notifications/emails/appointment_reminder_2h.html',
    },
    'appointment_rate_request': {
        'subject': '⭐ ¿Cómo estuvo tu experiencia? - BarberB',
        'template': 'notifications/emails/appointment_rate_request.html',
    },
    
    # 💈 CITAS – BARBERO
    'appointment_updated_barber': {
        'subject': '� Cita actualizada en tu agenda - BarberB',
        'template': 'notifications/emails/appointment_updated_barber.html',
    },
    'appointment_cancelled_barber': {
        'subject': '🚫 Cita cancelada en tu agenda - BarberB',
        'template': 'notifications/emails/appointment_cancelled_barber.html',
    },
    'barber_daily_schedule': {
        'subject': '📋 Tu agenda de hoy - BarberB',
        'template': 'notifications/emails/barber_daily_schedule.html',
    },
    'barber_daily_alert': {
        'subject': '� Alerta de agenda - BarberB',
        'template': 'notifications/emails/barber_daily_alert.html',
    },
    
    # 🏢 CITAS – ADMINISTRADOR
    'daily_appointments_report': {
        'subject': '� Resumen diario de citas - BarberB',
        'template': 'notifications/emails/daily_appointments_report.html',
    },
    'appointment_conflict_warning': {
        'subject': '⚠️ Conflicto de agenda detectado - BarberB',
        'template': 'notifications/emails/appointment_conflict_warning.html',
    },
    
    # 🧑‍🔧 SOLICITUDES DE BARBERO
    'request_submitted_barber': {
        'subject': '✅ Tu solicitud ha sido enviada - BarberB',
        'template': 'notifications/emails/request_submitted_barber.html',
    },
    'request_status_update': {
        'subject': '📬 Actualización de tu solicitud - BarberB',
        'template': 'notifications/emails/request_status_update.html',
    },
    'pending_requests_reminder': {
        'subject': '📋 Solicitudes pendientes por revisar - BarberB',
        'template': 'notifications/emails/pending_requests_reminder.html',
    },
    'new_request_admin': {
        'subject': '📩 Nueva solicitud de barbero recibida - BarberB',
        'template': 'notifications/emails/new_request_admin.html',
    },
    
    # 🤝 VINCULACIÓN BARBERO ↔ ADMINISTRADOR
    'link_request_submitted': {
        'subject': '🔗 Solicitud de vinculación enviada - BarberB',
        'template': 'notifications/emails/link_request_submitted.html',
    },
    'link_request_approved': {
        'subject': '🎉 ¡Vinculación aprobada! - BarberB',
        'template': 'notifications/emails/link_request_approved.html',
    },
    'link_request_rejected': {
        'subject': '❌ Vinculación rechazada - BarberB',
        'template': 'notifications/emails/link_request_rejected.html',
    },
    
    # 📦 INVENTARIO
    'inventory_low_stock': {
        'subject': '⚠️ Stock bajo en inventario - BarberB',
        'template': 'notifications/emails/inventory_low_stock.html',
    },
    'inventory_out_of_stock': {
        'subject': '🚫 Producto agotado - BarberB',
        'template': 'notifications/emails/inventory_out_of_stock.html',
    },
    'inventory_new_product': {
        'subject': '📦 Nuevo producto agregado - BarberB',
        'template': 'notifications/emails/inventory_new_product.html',
    },
    'inventory_expiration_warning': {
        'subject': '⏰ Producto próximo a vencer - BarberB',
        'template': 'notifications/emails/inventory_expiration_warning.html',
    },
    'inventory_update_confirmation': {
        'subject': '✅ Inventario actualizado - BarberB',
        'template': 'notifications/emails/inventory_update_confirmation.html',
    },
    
    # ⚙️ CONFIGURACIÓN DEL ESTABLECIMIENTO
    'establishment_info_updated': {
        'subject': '🏢 Información del establecimiento actualizada - BarberB',
        'template': 'notifications/emails/establishment_info_updated.html',
    },
}


def send_email_notification(user, email_type, context=None, recipient_email=None):
    """
    Función principal para enviar emails
    
    Args:
        user: Usuario que recibirá el email (User instance)
        email_type: Tipo de email (debe estar en EMAIL_TYPES)
        context: Diccionario con datos para el template
        recipient_email: Email específico (opcional, usa user.email por default)
    
    Returns:
        bool: True si se envió exitosamente, False si falló
    
    Ejemplo de uso:
        send_email_notification(
            user=admin_user,
            email_type='solicitud_creada',
            context={
                'barbero_nombre': 'Juan Pérez',
                'establecimiento': 'Kennedy',
                'fecha': '2025-11-06',
            }
        )
    """
    
    # Validar que el tipo de email existe
    if email_type not in EMAIL_TYPES:
        logger.error(f"Tipo de email '{email_type}' no existe en EMAIL_TYPES")
        return False
    
    # Obtener configuración del email
    email_config = EMAIL_TYPES[email_type]
    subject = email_config['subject']
    template_path = email_config['template']
    
    # Email del destinatario
    to_email = recipient_email or user.email
    
    if not to_email:
        logger.warning(f"Usuario {user.username} no tiene email configurado")
        return False
    
    # Crear registro en base de datos
    email_record = EmailNotification.objects.create(
        recipient=user,
        email_type=email_type,
        subject=subject,
        status='pending'
    )
    
    try:
        # Preparar contexto para el template
        email_context = context or {}
        email_context['user'] = user
        email_context['user_name'] = user.get_full_name() or user.username
        email_context['site_name'] = 'BarberB'
        email_context['site_url'] = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
        
        # Renderizar HTML del email
        html_content = render_to_string(template_path, email_context)
        
        # Crear email
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Ver este email en un navegador compatible con HTML.",  # Texto plano fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        
        # Enviar
        email.send(fail_silently=False)
        
        # Marcar como enviado
        email_record.mark_as_sent()
        logger.info(f"Email '{email_type}' enviado exitosamente a {to_email}")
        
        return True
        
    except Exception as e:
        # Marcar como fallido
        email_record.mark_as_failed(str(e))
        logger.error(f"Error enviando email '{email_type}' a {to_email}: {str(e)}")
        
        return False


def send_bulk_email_notification(users, email_type, context=None):
    """
    Enviar el mismo email a múltiples usuarios
    
    Args:
        users: Lista o QuerySet de usuarios
        email_type: Tipo de email
        context: Contexto compartido (se puede personalizar por usuario si es función)
    
    Returns:
        dict: {'sent': int, 'failed': int}
    """
    results = {'sent': 0, 'failed': 0}
    
    for user in users:
        # Si context es una función, llamarla para cada usuario
        user_context = context(user) if callable(context) else context
        
        success = send_email_notification(user, email_type, user_context)
        
        if success:
            results['sent'] += 1
        else:
            results['failed'] += 1
    
    logger.info(f"Email masivo '{email_type}': {results['sent']} enviados, {results['failed']} fallidos")
    
    return results


def get_email_stats(user=None, days=30):
    """
    Obtener estadísticas de emails enviados
    
    Args:
        user: Usuario específico (opcional)
        days: Últimos N días (default 30)
    
    Returns:
        dict: Estadísticas
    """
    from django.utils import timezone
    from datetime import timedelta
    
    start_date = timezone.now() - timedelta(days=days)
    
    queryset = EmailNotification.objects.filter(created_at__gte=start_date)
    
    if user:
        queryset = queryset.filter(recipient=user)
    
    stats = {
        'total': queryset.count(),
        'sent': queryset.filter(status='sent').count(),
        'failed': queryset.filter(status='failed').count(),
        'pending': queryset.filter(status='pending').count(),
    }
    
    return stats
