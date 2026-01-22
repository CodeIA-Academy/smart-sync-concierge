# Primeros Pasos - Smart-Sync Concierge

Esta guía te lleva a través del proceso de configuración y primer uso de Smart-Sync Concierge.

## Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Editor de código (VS Code, PyCharm, etc.)
- API key de Qwen (obtener en https://qwen.readthedocs.io/)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/your-org/smart-sync-concierge.git
cd smart-sync-concierge
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv

# Activar (macOS/Linux)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias principales son:
- Django 6.0.1
- Django REST Framework 3.15.2
- Qwen 2.5.0
- python-dateutil 2.9.0
- pytz 2024.2
- pydantic 2.10.4

### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```bash
# Django
SECRET_KEY=genera-una-clave-segura-aquí
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# IA
QWEN_API_KEY=tu-api-key-de-qwen
QWEN_MODEL=qwen-2.5

# Zona Horaria
TIMEZONE=America/Mexico_City
LANGUAGE=es
```

### 5. Generar Clave Secreta de Django

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el output y pégalo en `SECRET_KEY` en `.env`.

### 6. Inicializar Datos

```bash
python manage.py init_data
```

Esto crea los archivos JSON iniciales:
- `data/appointments.json`
- `data/contacts.json`
- `data/services.json`
- `data/availability.json`
- `data/config.json`

### 7. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 8. Crear Superusuario (Admin)

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear usuario y contraseña.

### 9. Ejecutar Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en `http://localhost:8000`

## Primer Uso

### Crear una Cita desde Prompt

```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez"
  }'
```

**Respuesta Exitosa:**

```json
{
  "status": "confirmed",
  "appointment": {
    "id": "apt_20260123_abc123",
    "fecha": "2026-01-23",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "participantes": ["Dr. Pérez"],
    "tipo": "consulta_general"
  },
  "message": "Cita confirmada exitosamente"
}
```

### Verificar Cita Creada

```bash
curl http://localhost:8000/api/v1/appointments/apt_20260123_abc123/
```

### Listar Todas las Citas

```bash
curl http://localhost:8000/api/v1/appointments/
```

## Panel de Administración

### Acceder al Admin

Abre el navegador en `http://localhost:8000/admin/`

Inicia sesión con el superusuario que creaste.

### Navegación del Admin

```
/admin/
├── Citas
│   ├── Lista de citas
│   ├── Agregar cita
│   ├── Calendario
│   └── Conflictos
├── Contactos
│   └── Lista de contactos
└── Servicios
    └── Lista de servicios
```

## Estructura del Proyecto

```
smart_sync_concierge/
├── config/                     # Configuración Django
├── core/                       # Módulos core
│   ├── agents/                # Framework de agentes
│   ├── ai/                    # Abstracción IA
│   ├── geo_temporal/          # Validación geo-temporal
│   └── observability/         # Tracing y métricas
├── apps/
│   ├── appointments/          # Gestión de citas
│   ├── contacts/              # Gestión de contactos
│   ├── availability/          # Gestión de disponibilidad
│   └── ai_engine/             # Motor de IA
└── data/                      # JSON locales
```

## Próximos Pasos

### Aprendizaje

1. Lee [architecture.md](../architecture.md) para entender la arquitectura agentica
2. Lee [agent-development.md](./agent-development.md) para aprender a crear agentes
3. Lee [api_reference.md](../api_reference.md) para ver todos los endpoints

### Desarrollo

1. Revisa [checklists/mvp-checklist.md](../checklists/mvp-checklist.md) para ver el estado del MVP
2. Lee los ADRs en [adr/](../adr/) para entender decisiones arquitectónicas
3. Revisa contratos de agentes en [contracts/agents/](../contracts/agents/)

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'qwen'"

**Solución**: Asegúrate de haber activado el entorno virtual:

```bash
# Si no estás en el entorno
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Qwen API key not configured"

**Solución**: Configurar `QWEN_API_KEY` en `.env`:

```bash
# Editar .env
QWEN_API_KEY=tu-api-key-aquí
```

### Error: "Port 8000 already in use"

**Solución**: Usa un puerto diferente:

```bash
python manage.py runserver 8001
```

## Verificación de Instalación

### Test Básico

```bash
curl http://localhost:8000/api/v1/
```

Deberías ver:

```json
{
  "message": "Smart-Sync Concierge API v0.1.0",
  "version": "0.1.0",
  "_links": {...}
}
```

### Test de Creación de Cita

```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita hoy 3pm con contacto_prueba"
  }'
```

## Recursos Adicionales

### Documentación

- [Arquitectura](../architecture.md)
- [Referencia API](../api_reference.md)
- [Guía de Despliegue](../deployment.md)

### Comunidad

- [GitHub Issues](https://github.com/your-org/smart-sync-concierge/issues)
- [Discussions](https://github.com/your-org/smart-sync-concierge/discussions)

### Soporte

- Email: support@smart-sync.example.com
- Docs: [https://docs.smart-sync.example.com](https://docs.smart-sync.example.com)

---

**Última actualización**: Enero 22, 2026
**Versión**: 0.1.0
**Próxima revisión**: Cuando se lance v0.2.0
