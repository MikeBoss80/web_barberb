"""
Comando de Django para configurar el objeto Site del framework Django Sites.

Este comando es necesario para resolver el problema de envío de emails de
restablecimiento de contraseña con dominios incorrectos (example.com).

Uso:
    python manage.py setup_site

Propósito:
    - Configura el dominio correcto para el entorno de desarrollo local
    - Permite que Django genere URLs correctas en los emails
    - Evita el uso del dominio por defecto 'example.com'

Autor: Sistema BarberB
Fecha: Octubre 2025
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    """
    Comando personalizado para configurar el Site de Django.
    
    Este comando maneja la configuración del objeto Site que Django utiliza
    para generar URLs absolutas en contextos como el envío de emails.
    """
    
    help = 'Configura el Site por defecto para el proyecto BarberB'

    def add_arguments(self, parser):
        """
        Argumentos opcionales del comando.
        """
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost:8000',
            help='Dominio a configurar (default: localhost:8000)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='BarberB Local Development',
            help='Nombre del sitio (default: BarberB Local Development)'
        )

    def handle(self, *args, **options):
        """
        Lógica principal del comando.
        
        Args:
            *args: Argumentos posicionales
            **options: Argumentos opcionales del comando
        """
        domain = options['domain']
        name = options['name']
        
        try:
            # Crear o actualizar el site con ID=1 (definido en SITE_ID)
            site, created = Site.objects.get_or_create(
                pk=settings.SITE_ID,
                defaults={
                    'domain': domain,
                    'name': name
                }
            )
            
            if not created:
                # Si ya existe, actualizar los valores
                site.domain = domain
                site.name = name
                site.save()
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Site existente actualizado: {site.domain} - {site.name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Site creado exitosamente: {site.domain} - {site.name}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error al configurar el Site: {str(e)}'
                )
            )
            raise