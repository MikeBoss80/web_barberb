"""
Comando de gestión para enviar recordatorios automáticos de citas.

Uso:
    python manage.py send_appointment_reminders --type=24h
    python manage.py send_appointment_reminders --type=2h
    python manage.py send_appointment_reminders --all
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
from notifications.email_service import send_email_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''
    Envía recordatorios automáticos de citas:
    - Recordatorios de 24 horas (ejecutar a las 6 PM diariamente)
    - Recordatorios de 2 horas (ejecutar cada hora de 8 AM a 8 PM)
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['24h', '2h'],
            help='Tipo de recordatorio: 24h (24 horas antes) o 2h (2 horas antes)',
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Enviar todos los tipos de recordatorio',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular envío sin enviar emails realmente',
        )

    def handle(self, *args, **options):
        try:
            # Importar modelos aquí para evitar errores de Django
            from django.contrib.auth.models import User
            
            # Ajustar según tus modelos reales
            # Ejemplo: desde services_module.models import ServiceDate as Cita
            
            dry_run = options['dry_run']
            
            if options['all']:
                self.send_24h_reminders(dry_run)
                self.send_2h_reminders(dry_run)
            elif options['type'] == '24h':
                self.send_24h_reminders(dry_run)
            elif options['type'] == '2h':
                self.send_2h_reminders(dry_run)
            else:
                self.print_help('send_appointment_reminders', '')
                
        except Exception as e:
            logger.error(f"Error en comando send_appointment_reminders: {e}")
            raise CommandError(f"Error ejecutando comando: {e}")

    def send_24h_reminders(self, dry_run=False):
        """Enviar recordatorios 24 horas antes"""
        try:
            # CAMBIAR: Ajustar según tus modelos
            # from services_module.models import ServiceDate
            
            manana = timezone.now() + timedelta(days=1)
            
            # CAMBIAR: Ajustar query según tu modelo de citas
            # citas = ServiceDate.objects.filter(
            #     date__date=manana.date(),
            #     status='confirmada',
            #     customer__email__isnull=False,
            #     customer__is_active=True
            # )
            
            # SIMULACIÓN para demostrar funcionalidad
            citas = []  # Reemplazar con query real
            
            sent_count = 0
            failed_count = 0
            
            for cita in citas:
                try:
                    if not dry_run:
                        send_email_notification(
                            user=cita.customer,  # Cambiar según tu modelo
                            email_type='appointment_reminder_24h',
                            context={
                                'servicio_nombre': cita.service.name,
                                'barbero_nombre': cita.barber.get_full_name(),
                                'fecha_cita': cita.date.strftime('%d/%m/%Y'),
                                'hora_cita': cita.date.strftime('%I:%M %p'),
                                'establecimiento_nombre': cita.service.establishment.name_est,
                                'establecimiento_direccion': cita.service.establishment.address_est,
                                'establecimiento_telefono': cita.service.establishment.phone_est,
                                'url_confirmar_asistencia': f"/citas/{cita.id}/confirmar/",
                                'url_cancelar_cita': f"/citas/{cita.id}/cancelar/",
                            }
                        )
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Error enviando recordatorio 24h para cita {cita.id}: {e}")
                    failed_count += 1
            
            status = "[DRY RUN] " if dry_run else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f'{status}Recordatorios 24h: {sent_count} enviados, {failed_count} fallidos'
                )
            )
            
        except Exception as e:
            logger.error(f"Error en send_24h_reminders: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error enviando recordatorios 24h: {e}')
            )

    def send_2h_reminders(self, dry_run=False):
        """Enviar recordatorios 2 horas antes"""
        try:
            # CAMBIAR: Ajustar según tus modelos
            # from services_module.models import ServiceDate
            
            # Citas en las próximas 2 horas
            now = timezone.now()
            en_2_horas = now + timedelta(hours=2)
            
            # CAMBIAR: Ajustar query según tu modelo de citas
            # citas = ServiceDate.objects.filter(
            #     date__gte=now,
            #     date__lte=en_2_horas,
            #     status='confirmada',
            #     customer__email__isnull=False,
            #     customer__is_active=True
            # )
            
            # SIMULACIÓN
            citas = []  # Reemplazar con query real
            
            sent_count = 0
            failed_count = 0
            
            for cita in citas:
                try:
                    if not dry_run:
                        send_email_notification(
                            user=cita.customer,  # Cambiar según tu modelo
                            email_type='appointment_reminder_2h',
                            context={
                                'servicio_nombre': cita.service.name,
                                'barbero_nombre': cita.barber.get_full_name(),
                                'fecha_cita': cita.date.strftime('%d/%m/%Y'),
                                'hora_cita': cita.date.strftime('%I:%M %p'),
                                'establecimiento_nombre': cita.service.establishment.name_est,
                                'establecimiento_direccion': cita.service.establishment.address_est,
                                'establecimiento_telefono': cita.service.establishment.phone_est,
                                'tiempo_restante': self.calculate_time_remaining(cita.date),
                                'url_direcciones': f"/establecimiento/{cita.service.establishment.id}/direcciones/",
                                'url_contacto_barbero': f"/barbero/{cita.barber.id}/contacto/",
                            }
                        )
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Error enviando recordatorio 2h para cita {cita.id}: {e}")
                    failed_count += 1
            
            status = "[DRY RUN] " if dry_run else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f'{status}Recordatorios 2h: {sent_count} enviados, {failed_count} fallidos'
                )
            )
            
        except Exception as e:
            logger.error(f"Error en send_2h_reminders: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error enviando recordatorios 2h: {e}')
            )

    def calculate_time_remaining(self, cita_date):
        """Calcular tiempo restante hasta la cita"""
        now = timezone.now()
        diff = cita_date - now
        
        if diff.total_seconds() <= 0:
            return "La cita es ahora"
        
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes} minutos"