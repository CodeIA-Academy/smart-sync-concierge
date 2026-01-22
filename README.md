# Smart-Sync Concierge

> Una API de citas **prompt-first** donde el lenguaje natural se transforma en datos estructurados mediante un pipeline de IA, validación de negocio y contexto geo-temporal.

## 🎯 Características Principales

- **Prompt-First**: Crea citas desde lenguaje natural
  - *Ejemplo*: "cita mañana 10am con Dr. Pérez" → Cita confirmada

- **IA-Powered**: Extracción inteligente con Qwen
  - Reconoce fechas, horas, participantes, tipos de cita
  - Detección de ambigüedades e información faltante

- **Validación Inteligente**:
  - Verificación de disponibilidad en tiempo real
  - Detección de conflictos con sugerencias alternativas
  - Validación de reglas de negocio configurables

- **Contexto Geo-Temporal**:
  - Soporte multi-zona horaria
  - Cálculo automático de duración
  - Consideración de horarios laborales y festivos

## 🚀 Quick Start

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/your-org/smart-sync-concierge.git
cd smart-sync-concierge

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Inicializar datos
python manage.py init_data

# Ejecutar servidor
python manage.py runserver
```

### Primer Uso

```bash
# Crear cita desde lenguaje natural
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez"
  }'
```

**Respuesta:**

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

## 📚 Documentación

- [Arquitectura](docs/architecture.md) - Arquitectura completa del sistema
- [Referencia API](docs/api_reference.md) - Documentación detallada de endpoints
- [Guía de Despliegue](docs/deployment.md) - Instrucciones de instalación y producción
- [Changelog](docs/changelog.md) - Historial de cambios

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    API REST Layer                        │
│              Django REST Framework                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Parser     │  │  Validator   │  │  Scheduler   │  │
│  │   Prompt     │  │  Business    │  │  Engine      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    IA Engine                             │
│                       Qwen                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Storage Layer                         │
│                 JSON Local Files                         │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework | Django | 6.0.1 |
| API REST | Django REST Framework | 3.15.2 |
| Motor IA | Qwen | 2.5 |
| Storage | JSON Local | - |
| Arquitectura | Single-tenant | - |

## 📡 Endpoints Principales

### Citas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/appointments/` | Crear cita desde prompt |
| GET | `/api/v1/appointments/` | Listar citas |
| GET | `/api/v1/appointments/{id}/` | Obtener cita |
| PUT | `/api/v1/appointments/{id}/` | Actualizar cita |
| DELETE | `/api/v1/appointments/{id}/` | Cancelar cita |

### Disponibilidad

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/availability/slots/` | Slots disponibles |

### Recursos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/contacts/` | Listar contactos |
| GET | `/api/v1/services/` | Listar servicios |

Ver [Referencia API](docs/api_reference.md) para documentación completa.

## 🔧 Configuración

### Variables de Entorno

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# IA
QWEN_API_KEY=your-qwen-api-key
QWEN_MODEL=qwen-2.5

# Zona Horaria
TIMEZONE=America/Mexico_City

# Storage
DATA_DIR=data
```

Ver [`.env.example`](.env.example) para todas las opciones.

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=apps --cov-report=html

# Tests específicos
pytest tests/unit/test_parser.py
```

## 🚢 Despliegue

Ver [Guía de Despliegue](docs/deployment.md) para instrucciones detalladas.

### Resumen Rápido (Docker)

```bash
docker-compose build
docker-compose up -d
```

## 📈 Roadmap

### v0.2.0 (Próximo)
- [ ] Sistema de notificaciones (email, SMS)
- [ ] Integración con calendarios externos
- [ ] Panel de analytics

### v0.3.0
- [ ] Migración a PostgreSQL
- [ ] Redis para cache
- [ ] Colas de tareas asíncronas

### v1.0.0
- [ ] Multi-tenant
- [ ] API webhooks
- [ ] SDKs (JavaScript, Python)

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- **Tu Nombre** - *Trabajo inicial* - [Smart-Sync Concierge](https://github.com/your-org/smart-sync-concierge)

## 🙏 Agradecimientos

- Django y Django REST Framework communities
- Equipo de Qwen AI
- CodeIA Academy

---

**Versión**: 0.1.0
**Fecha**: Enero 22, 2026
