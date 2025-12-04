# 📧 Sistema de Notificaciones por Email - BarberB

Sistema centralizado, simple y profesional para envío de emails en la aplicación BarberB.

---

## 🎯 Características

- ✅ **Super simple de usar**: Una sola función para todo
- ✅ **Totalmente centralizado**: Todo en la app `notifications`
- ✅ **Templates profesionales**: 10+ templates HTML responsive
- ✅ **Tracking automático**: Registra todos los emails enviados
- ✅ **A prueba de fallos**: Si falla el email, no afecta el proceso principal
- ✅ **Listo para producción**: Compatible con Gmail, SendGrid, AWS SES

---

## 📁 Estructura

```
notifications/
├── models.py                    # Modelo EmailNotification
├── email_service.py             # Servicio principal ⭐
├── admin.py                     # Admin para ver emails enviados
├── EMAIL_CONFIG.py              # Configuración de settings
├── EJEMPLOS_USO.py              # Ejemplos prácticos
└── templates/
    └── notifications/
        └── emails/
            ├── base_email.html           # Template base
            ├── solicitud_creada.html     # Email al admin
            ├── solicitud_aprobada.html   # Email al barbero
            ├── solicitud_rechazada.html  # Email al barbero
            ├── cita_confirmada.html      # Email al cliente
            ├── cita_recordatorio.html    # Recordatorio
            ├── cita_cancelada.html       # Cancelación
            ├── cita_reagendada.html      # Reagendamiento
            ├── pago_confirmado.html      # Confirmación de pago
            ├── pago_fallido.html         # Error en pago
            ├── nueva_calificacion.html   # Calificación recibida
            └── bienvenida.html           # Email de bienvenida
```

---

## 🚀 Uso Rápido

### 1. Importar la función

```python
from notifications.email_service import send_email_notification
```

### 2. Llamar en cualquier vista

```python
def form_valid(self, form):
    # Guardar en BD primero
    response = super().form_valid(form)
    
    # Enviar email
    send_email_notification(
        user=admin_user,
        email_type='solicitud_creada',
        context={
            'barbero_nombre': 'Juan Pérez',
            'establecimiento_nombre': 'Kennedy',
            'fecha_solicitud': '06/11/2025',
            'url_detalle_solicitud': 'http://localhost:8000/solicitudes/1/',
        }
    )
    
    return response
```

### ¡Eso es todo! 🎉

---

## 📧 Tipos de Email Disponibles

| Tipo de Email | Cuándo usar | Destinatario |
|--------------|-------------|--------------|
| `solicitud_creada` | Cuando un barbero crea una solicitud | Admin del establecimiento |
| `solicitud_aprobada` | Cuando admin aprueba solicitud | Barbero |
| `solicitud_rechazada` | Cuando admin rechaza solicitud | Barbero |
| `cita_confirmada` | Cuando se crea una cita | Cliente |
| `cita_recordatorio` | 24h antes de la cita | Cliente |
| `cita_cancelada` | Cuando se cancela una cita | Cliente |
| `cita_reagendada` | Cuando se reagenda una cita | Cliente |
| `pago_confirmado` | Cuando se confirma un pago | Cliente |
| `pago_fallido` | Cuando falla un pago | Cliente |
| `nueva_calificacion` | Cuando un barbero recibe calificación | Barbero |
| `bienvenida` | Cuando se registra un nuevo usuario | Nuevo usuario |

---

## ⚙️ Configuración

### 1. Configurar `settings.py`

Ya está configurado en `barberb/settings.py`:

```python
# Para desarrollo (emails en consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Para producción (descomentar y configurar)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = 'BarberB <noreply@barberb.com>'
SITE_URL = 'http://localhost:8000'
```

### 2. Para usar Gmail en producción

1. Activa "Verificación en 2 pasos" en tu cuenta Google
2. Genera una "Contraseña de aplicación": https://myaccount.google.com/apppasswords
3. Crea archivo `.env` en la raíz:

```env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-generada
```

4. Descomenta las líneas de producción en `settings.py`

---

## 📝 Ejemplos Implementados

### ✅ Ya Integrado en tu Código

**1. Solicitud Creada** (`admin_module/views.py` línea 361)
```python
class BarberRequestCreateView:
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Envía email al admin automáticamente ✅
        send_email_notification(
            user=solicitud.establecimiento.id_admin,
            email_type='solicitud_creada',
            context={...}
        )
        
        return response
```

**2. Solicitud Aprobada/Rechazada** (`admin_module/views.py` línea 755)
```python
class AdminSolicitudesDetailView:
    def form_valid(self, form):
        if estado_nuevo == 'aprobada':
            # Envía email al barbero automáticamente ✅
            send_email_notification(
                user=barbero,
                email_type='solicitud_aprobada',
                context={...}
            )
```

---

## 🔍 Ver Emails Enviados

### En el Admin de Django

1. Ve a: http://localhost:8000/admin/
2. Busca: **Email notifications**
3. Verás todos los emails con su estado:
   - ✅ Enviado (sent)
   - ⏳ Pendiente (pending)
   - ❌ Fallido (failed)

### En el Código

```python
from notifications.email_service import get_email_stats

# Estadísticas generales
stats = get_email_stats()
print(f"Total: {stats['total']}")
print(f"Enviados: {stats['sent']}")
print(f"Fallidos: {stats['failed']}")

# Estadísticas de un usuario
user_stats = get_email_stats(user=mi_usuario, days=7)
```

---

## 🎨 Personalizar Templates

Todos los templates están en: `notifications/templates/notifications/emails/`

Para personalizar:

1. Abre el template que quieras modificar
2. Edita el HTML dentro del bloque `{% block content %}`
3. Usa las variables del contexto (ej: `{{ barbero_nombre }}`)

**Variables siempre disponibles:**
- `user` - Usuario destinatario
- `user_name` - Nombre completo del usuario
- `site_name` - Nombre del sitio ("BarberB")
- `site_url` - URL base del sitio

---

## ➕ Agregar Nuevo Tipo de Email

### 1. Agregar en `email_service.py`

```python
EMAIL_TYPES = {
    # ... tipos existentes ...
    
    'nuevo_tipo': {
        'subject': '📢 Título del Email',
        'template': 'notifications/emails/nuevo_tipo.html',
    },
}
```

### 2. Crear template HTML

Crea `notifications/templates/notifications/emails/nuevo_tipo.html`:

```html
{% extends "notifications/emails/base_email.html" %}

{% block content %}
<div class="alert alert-info">
    <strong>Tu mensaje aquí</strong>
</div>

<div class="content">
    <p>Contenido del email con {{ variables_dinamicas }}</p>
</div>
{% endblock %}
```

### 3. Usar en tu código

```python
send_email_notification(
    user=usuario,
    email_type='nuevo_tipo',
    context={
        'variables_dinamicas': 'Datos personalizados',
    }
)
```

---

## 🧪 Probar el Sistema

### Modo Desarrollo (Consola)

Los emails se muestran en la terminal donde corre `python manage.py runserver`:

```bash
python manage.py runserver

# Verás algo como:
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: ✅ Nueva Solicitud de Vinculación Recibida
From: BarberB <noreply@barberb.com>
To: admin@example.com
Date: Wed, 06 Nov 2025 15:30:00 -0000
Message-ID: <...>

[HTML del email]
```

### Probar Envío Real

```python
# En shell de Django
python manage.py shell

from django.contrib.auth.models import User
from notifications.email_service import send_email_notification

user = User.objects.first()
send_email_notification(
    user=user,
    email_type='bienvenida',
    context={}
)
```

---

## 🚨 Manejo de Errores

El sistema **NO FALLA** si hay error en el email:

```python
try:
    send_email_notification(...)
except Exception as e:
    print(f"Error: {e}")
    # El proceso principal continúa normalmente
```

Los errores se registran en:
- Base de datos (campo `error_message`)
- Logs (si configuraste logging)

---

## 📊 Estadísticas y Monitoreo

```python
from notifications.models import EmailNotification

# Todos los emails enviados hoy
from django.utils import timezone
hoy = timezone.now().date()
enviados_hoy = EmailNotification.objects.filter(
    sent_at__date=hoy,
    status='sent'
).count()

# Emails fallidos
fallidos = EmailNotification.objects.filter(status='failed')
for email in fallidos:
    print(f"Falló: {email.email_type} - Error: {email.error_message}")
```

---

## 🎯 Próximos Pasos

- [ ] Configurar Gmail/SendGrid para producción
- [ ] Agregar más tipos de email según necesites
- [ ] Implementar Celery para envío asíncrono (opcional)
- [ ] Agregar preferencias de usuario (activar/desactivar emails)

---

## 💡 Tips y Mejores Prácticas

1. **Siempre guardar en BD primero**, luego enviar email
2. **Usar try/except** para no romper el flujo principal
3. **URLs absolutas** con `build_absolute_uri()`
4. **Formatear fechas** legibles: `strftime('%d/%m/%Y')`
5. **Validar que el usuario tenga email** antes de enviar

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa `EJEMPLOS_USO.py` - hay 8+ ejemplos
2. Revisa los logs en el admin de Django
3. Verifica la configuración en `settings.py`
4. Asegúrate que el usuario tenga email configurado

---

**Creado para BarberB** 🚀  
Sistema simple, profesional y escalable.
