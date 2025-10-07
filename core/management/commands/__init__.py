"""
Paquete de comandos de gestión personalizados.

Contiene los comandos de Django personalizados para el proyecto BarberB.
Cada archivo .py en este directorio representa un comando disponible
a través de 'python manage.py <comando>'.

Comandos disponibles:
    - setup_site: Configura el dominio del Site para emails
    
Convención de nombres:
    - Usar snake_case para nombres de archivos/comandos
    - Heredar de BaseCommand
    - Implementar método handle()
    - Documentar con docstrings
"""