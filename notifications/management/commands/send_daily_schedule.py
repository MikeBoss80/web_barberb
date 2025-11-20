"""
Comando de gestión para enviar agenda diaria a todos los barberos activos.

Uso:
    python manage.py send_daily_schedule
    python manage.py send_daily_schedule --barbero=juan@email.com
    python manage.py send_daily_schedule --dry-run
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from notifications.email_service import send_email_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''
    Envía la agenda diaria a todos los barberos activos.
    Ejecutar diariamente a las 7:00 AM con cron job.
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--barbero',
            type=str,
            help='Email específico de barbero para enviar solo a él',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular envío sin enviar emails realmente',
        )
        
        parser.add_argument(
            '--fecha',
            type=str,
            help='Fecha específica para la agenda (formato: YYYY-MM-DD). Por defecto es hoy.',
        )

    def handle(self, *args, **options):
        try:
            dry_run = options['dry_run']
            
            # Determinar fecha objetivo
            if options['fecha']:
                try:
                    fecha_objetivo = datetime.strptime(options['fecha'], '%Y-%m-%d').date()
                except ValueError:
                    raise CommandError('Formato de fecha inválido. Use YYYY-MM-DD')
            else:
                fecha_objetivo = timezone.now().date()
            
            if options['barbero']:
                # Enviar solo a un barbero específico
                self.send_to_barbero(options['barbero'], fecha_objetivo, dry_run)
            else:
                # Enviar a todos los barberos activos
                self.send_to_all_barberos(fecha_objetivo, dry_run)
                
        except Exception as e:
            logger.error(f"Error en comando send_daily_schedule: {e}")
            raise CommandError(f"Error ejecutando comando: {e}")

    def send_to_all_barberos(self, fecha_objetivo, dry_run=False):
        """Enviar agenda a todos los barberos activos"""
        try:
            # Obtener barberos activos
            barberos = User.objects.filter(
                groups__name='Barbero',
                is_active=True,
                email__isnull=False,
                email__gt=''
            )
            
            sent_count = 0
            failed_count = 0
            
            for barbero in barberos:
                try:
                    agenda_data = self.get_agenda_barbero(barbero, fecha_objetivo)
                    
                    if not dry_run:
                        send_email_notification(
                            user=barbero,
                            email_type='barber_daily_schedule',
                            context=agenda_data
                        )
                    
                    sent_count += 1
                    self.stdout.write(f"  ✓ {barbero.get_full_name()} ({barbero.email})")
                    
                except Exception as e:
                    logger.error(f"Error enviando agenda a {barbero.email}: {e}")
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"  ✗ {barbero.get_full_name()}: {e}")
                    )
            
            status = "[DRY RUN] " if dry_run else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n{status}Agendas enviadas: {sent_count} exitosas, {failed_count} fallidas'
                )
            )
            
        except Exception as e:
            logger.error(f"Error en send_to_all_barberos: {e}")
            raise CommandError(f"Error enviando a barberos: {e}")

    def send_to_barbero(self, email_barbero, fecha_objetivo, dry_run=False):
        """Enviar agenda a un barbero específico"""
        try:
            barbero = User.objects.get(
                email=email_barbero,
                groups__name='Barbero',
                is_active=True
            )
            
            agenda_data = self.get_agenda_barbero(barbero, fecha_objetivo)
            
            if not dry_run:
                send_email_notification(
                    user=barbero,
                    email_type='barber_daily_schedule',
                    context=agenda_data
                )
            
            status = "[DRY RUN] " if dry_run else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f'{status}Agenda enviada a {barbero.get_full_name()} ({email_barbero})'
                )
            )
            
        except User.DoesNotExist:
            raise CommandError(f'Barbero no encontrado: {email_barbero}')
        except Exception as e:
            logger.error(f"Error enviando agenda a {email_barbero}: {e}")
            raise CommandError(f"Error: {e}")

    def get_agenda_barbero(self, barbero, fecha_objetivo):
        """Obtener datos de agenda para un barbero específico"""
        try:
            # CAMBIAR: Ajustar según tus modelos
            # from services_module.models import ServiceDate
            
            # SIMULACIÓN - Reemplazar con queries reales
            # citas_hoy = ServiceDate.objects.filter(
            #     barber=barbero,
            #     date__date=fecha_objetivo,
            #     status='confirmada'
            # ).order_by('date')
            
            citas_hoy = []  # Reemplazar con query real
            
            # Calcular estadísticas
            total_citas = len(citas_hoy)
            ingresos_estimados = sum(getattr(cita, 'price_total', 0) for cita in citas_hoy)
            
            # Preparar lista de citas formateada
            citas_formateadas = []
            for cita in citas_hoy:
                citas_formateadas.append({
                    'hora': cita.date.strftime('%I:%M %p'),
                    'cliente_nombre': cita.customer.get_full_name(),
                    'servicio': cita.service.name,
                    'duracion': f"{cita.service.duration_minutes} min",
                    'precio': cita.price_total,
                    'notas': getattr(cita, 'notas_especiales', ''),
                })
            
            # Calcular horas de trabajo estimadas
            if citas_hoy:
                primera_cita = min(cita.date for cita in citas_hoy)
                ultima_cita = max(cita.date for cita in citas_hoy)
                horas_trabajo = (ultima_cita - primera_cita).total_seconds() / 3600
                horas_trabajo_str = f"{int(horas_trabajo)}h {int((horas_trabajo % 1) * 60)}min"
            else:
                horas_trabajo_str = "Sin citas programadas"
            
            # Generar recordatorios personalizados
            recordatorios = [
                'Revisar herramientas antes de empezar',
                'Actualizar inventario de productos después de cada cliente',
            ]
            
            if total_citas > 5:
                recordatorios.append('Día ocupado: tomar descansos entre citas')
            
            if total_citas == 0:
                recordatorios = [
                    'Día libre: revisar equipos y herramientas',
                    'Actualizar perfil y servicios disponibles',
                ]
            
            return {
                'barbero_nombre': barbero.get_full_name(),
                'fecha_hoy': fecha_objetivo.strftime('%d/%m/%Y'),
                'citas_hoy': citas_formateadas,
                'total_citas': total_citas,
                'ingresos_estimados': ingresos_estimados,
                'horas_trabajo': horas_trabajo_str,
                'tiempo_libre': self.calculate_tiempo_libre(citas_hoy),
                'recordatorios': recordatorios,
                'url_agenda_completa': '/barbero/agenda/',
                'url_reportar_llegada': '/barbero/llegada/',
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo agenda para {barbero.email}: {e}")
            # Retornar agenda vacía en caso de error
            return {
                'barbero_nombre': barbero.get_full_name(),
                'fecha_hoy': fecha_objetivo.strftime('%d/%m/%Y'),
                'citas_hoy': [],
                'total_citas': 0,
                'ingresos_estimados': 0,
                'horas_trabajo': 'Sin citas',
                'tiempo_libre': '8 horas',
                'recordatorios': ['Error cargando agenda - contactar soporte'],
                'url_agenda_completa': '/barbero/agenda/',
                'url_reportar_llegada': '/barbero/llegada/',
            }

    def calculate_tiempo_libre(self, citas):
        """Calcular tiempo libre entre citas"""
        if not citas or len(citas) < 2:
            return "8 horas"
        
        # Ordenar citas por hora
        citas_ordenadas = sorted(citas, key=lambda x: x.date)
        
        tiempo_libre_total = 0
        for i in range(len(citas_ordenadas) - 1):
            cita_actual = citas_ordenadas[i]
            cita_siguiente = citas_ordenadas[i + 1]
            
            # Calcular tiempo entre el final de una cita y el inicio de la siguiente
            fin_cita_actual = cita_actual.date + timedelta(minutes=cita_actual.service.duration_minutes)
            tiempo_libre = (cita_siguiente.date - fin_cita_actual).total_seconds() / 60
            
            if tiempo_libre > 0:
                tiempo_libre_total += tiempo_libre
        
        if tiempo_libre_total >= 60:
            horas = int(tiempo_libre_total // 60)
            minutos = int(tiempo_libre_total % 60)
            return f"{horas}h {minutos}min"
        else:
            return f"{int(tiempo_libre_total)} min"