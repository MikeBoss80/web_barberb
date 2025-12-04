# ============================================
# CONFIGURACIÓN DE EMAIL - BARBERB
# ============================================
# Agrega estas líneas a tu barberb/settings.py

# Configuración de Email Backend
# Para desarrollo (muestra emails en consola):
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Para producción (Gmail):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu-email@gmail.com'  # Usa variable de entorno
# EMAIL_HOST_PASSWORD = 'tu-app-password'  # Usa variable de entorno (NO tu contraseña real)

# Para producción (SendGrid):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = 'tu-sendgrid-api-key'  # Usa variable de entorno

# Email por defecto del remitente
DEFAULT_FROM_EMAIL = 'BarberB <noreply@barberb.com>'

# URL base del sitio (para enlaces en emails)
SITE_URL = 'http://localhost:8000'  # Cambiar en producción

# Logging para emails
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/email_notifications.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'notifications.email_service': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================
# IMPORTANTE: Configuración de Gmail
# ============================================
# Si usas Gmail, debes:
# 1. Activar "Verificación en 2 pasos" en tu cuenta Google
# 2. Generar una "Contraseña de aplicación" en:
#    https://myaccount.google.com/apppasswords
# 3. Usar esa contraseña (NO tu contraseña de Gmail)
# 4. NUNCA subir las credenciales a GitHub (usar variables de entorno)

# Ejemplo con variables de entorno (.env):
# import os
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
