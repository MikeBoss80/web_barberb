#!/usr/bin/env python
"""
Script independiente para configurar el Site de Django.

Este script resuelve el problema de configuración del Site cuando:
- No se puede acceder al comando manage.py
- Se necesita configurar rápidamente el Site desde fuera de Django
- Hay problemas con el entorno virtual o dependencias

Problema que resuelve:
    Django usa el objeto Site para generar URLs absolutas en emails.
    Sin configurar correctamente, Django usa 'example.com' como dominio
    por defecto, causando enlaces rotos en emails de restablecimiento.

Uso:
    python fix_site.py
    
Requisitos:
    - Django instalado y configurado
    - Base de datos accesible
    - Variable DJANGO_SETTINGS_MODULE correcta
    
Alternativa preferida:
    python manage.py setup_site
    
Autor: Sistema BarberB
Fecha: Octubre 2025
Versión: 1.0
"""

import os
import sys
import django
from pathlib import Path


def main():
    """
    Función principal del script.
    
    Configura Django y actualiza el objeto Site con el dominio correcto
    para el entorno de desarrollo local.
    
    Raises:
        SystemExit: Si hay errores en la configuración
    """
    try:
        # Configurar Django antes de importar models
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberb.settings')
        django.setup()
        
        # Importar después de setup() para evitar errores
        from django.contrib.sites.models import Site
        from django.conf import settings
        
        print("🔧 Configurando Site de Django...")
        
        # Obtener configuración del Site
        site_id = getattr(settings, 'SITE_ID', 1)
        domain = 'localhost:8000'
        name = 'BarberB Local Development'
        
        # Crear o actualizar el site
        site, created = Site.objects.get_or_create(
            pk=site_id,
            defaults={
                'domain': domain,
                'name': name
            }
        )
        
        if not created:
            # Actualizar si ya existe
            site.domain = domain
            site.name = name
            site.save()
            print(f" Site actualizado: {site.domain} - {site.name}")
        else:
            print(f" Site creado: {site.domain} - {site.name}")
            
        print("\n Los emails de restablecimiento ahora usarán el dominio correcto.")
        
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Asegúrate de que Django esté instalado y el entorno virtual activado.")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error inesperado: {e}")
        print("Verifica la configuración de la base de datos y settings.py")
        sys.exit(1)


if __name__ == '__main__':
    main()