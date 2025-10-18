# 📁 Scripts de Utilidad - BarberB

Esta carpeta contiene scripts de utilidad para configuración, población de datos y mantenimiento del proyecto BarberB.

## 📋 Estructura de Scripts

```
scripts/
├── __init__.py                    # Documentación del paquete
├── setup_schedules.py             # ✅ Configuración de horarios
├── README.md                      # Este archivo
└── [futuros scripts]
```

## 🚀 Scripts Disponibles

### 1. **setup_schedules.py** - Configuración de Horarios
Configura los horarios de operación de establecimientos y disponibilidad de barberos.

**Uso:**
```bash
python scripts/setup_schedules.py
```

**Qué hace:**
- ✅ Crea horarios de operación para cada establecimiento
- ✅ Configura disponibilidad de barberos por día
- ✅ Valida que existan establecimientos y usuarios
- ✅ Muestra resumen detallado de la configuración

**Prerequisitos:**
- Migraciones aplicadas (`python manage.py migrate`)
- Datos iniciales creados (establecimientos y usuarios)

**Salida esperada:**
```
📅 CONFIGURANDO HORARIOS DE ESTABLECIMIENTOS
📍 BarberShop Kennedy
   ✅ Lunes      → 09:00 - 19:00
   ✅ Martes     → 09:00 - 19:00
   ...

💈 CONFIGURANDO DISPONIBILIDAD DE BARBEROS
💈 Jose Quintero - BarberShop Kennedy
   ✅ Lunes      → 09:00 - 19:00
   ...

✅ Configuración completada exitosamente!
```

---

## 🎯 Scripts en la Raíz (Legacy - En proceso de migración)

Estos scripts están en la raíz del proyecto y eventualmente se migrarán a `scripts/`:

### **poblar_datos_completos.py**
Puebla la base de datos con datos iniciales completos.
```bash
python poblar_datos_completos.py
```

### **verificar_datos.py**
Verifica el estado de la base de datos.
```bash
python verificar_datos.py
```

### **poblar_horarios.py** ⚠️ *Deprecated*
**Usar en su lugar:** `python scripts/setup_schedules.py`

---

## 📐 Convenciones y Buenas Prácticas

### ✅ Estructura de Scripts

Cada script debe seguir esta estructura:

```python
"""
NOMBRE DEL SCRIPT: Descripción breve
====================================

Descripción detallada de qué hace el script.

Uso:
    python scripts/nombre_script.py [opciones]

Requisitos previos:
    - Prerequisito 1
    - Prerequisito 2

Autor: BarberB Development Team
Fecha: [Fecha]
"""

import os
import sys
import django

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberb.settings')
django.setup()

# Imports de modelos de Django aquí
from django.contrib.auth.models import User
# ...

class MiScript:
    """Clase para encapsular la lógica del script."""
    
    def __init__(self):
        pass
    
    def run(self):
        """Método principal de ejecución."""
        pass

if __name__ == '__main__':
    script = MiScript()
    success = script.run()
    sys.exit(0 if success else 1)
```

### ✅ Principios de Diseño

1. **Clase contenedora**: Encapsular lógica en una clase
2. **Métodos pequeños**: Cada método hace una cosa específica
3. **Mensajes claros**: Usar emojis y formateo para feedback visual
4. **Validaciones**: Verificar prerequisitos antes de ejecutar
5. **Resumen final**: Mostrar estadísticas al terminar
6. **Exit codes**: Retornar 0 (éxito) o 1 (error)
7. **Idempotencia**: Se puede ejecutar múltiples veces sin duplicar datos (usar `get_or_create`)

### ✅ Estilo de Mensajes

```python
# Títulos de secciones
print("\n" + "="*70)
print("📅 TÍTULO DE LA SECCIÓN")
print("="*70)

# Items exitosos
print("   ✅ Operación completada")

# Advertencias
print("   ⚠️  Item ya existía (sin cambios)")

# Errores
print("   ❌ ERROR: Descripción del error")

# Información
print("   📊 Estadística: 123")
```

---

## 🔄 Orden de Ejecución Recomendado

Para configurar el proyecto desde cero:

```bash
# 1. Crear base de datos vacía en MySQL
# 2. Aplicar migraciones
python manage.py migrate

# 3. Poblar datos iniciales (usuarios, establecimientos, servicios)
python poblar_datos_completos.py

# 4. Configurar horarios
python scripts/setup_schedules.py

# 5. Verificar datos
python verificar_datos.py

# 6. Iniciar servidor
python manage.py runserver
```

---

## 🛠️ Desarrollo de Nuevos Scripts

### Template para nuevos scripts:

1. Crear archivo en `scripts/nuevo_script.py`
2. Copiar estructura del template de arriba
3. Implementar lógica en clase contenedora
4. Agregar validaciones y mensajes claros
5. Actualizar este README con documentación del script
6. Probar ejecución múltiple (idempotencia)

### Ejemplo de nuevo script:

```bash
# Crear el archivo
touch scripts/backup_database.py

# Editar y seguir el template
# ...

# Ejecutar
python scripts/backup_database.py
```

---

## 📚 Recursos Adicionales

- **Documentación Django**: https://docs.djangoproject.com/
- **Guía de migraciones**: Ver `MIGRACIONES_LIMPIAS_README.md`
- **Diseño de slots**: Ver `DISEÑO_SISTEMA_SLOTS.md`
- **Análisis de horarios**: Ver `ANALISIS_HORARIOS.md`

---

## 🤝 Contribuciones

Al agregar nuevos scripts:

1. ✅ Seguir la estructura documentada
2. ✅ Usar mensajes claros con emojis
3. ✅ Validar prerequisitos
4. ✅ Implementar idempotencia
5. ✅ Documentar en este README
6. ✅ Probar antes de commit

---

**Última actualización:** Octubre 2025  
**Mantenido por:** BarberB Development Team
