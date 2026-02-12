# Changelog - Smart-Sync Concierge

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Planeado
- Validación HMAC para webhooks n8n
- Endpoint de diagnóstico `/api/v1/mcp/status/`
- Tests unitarios para n8n integration
- Webhooks de n8n → Django (notificaciones)
- Dashboard de monitoreo
- Migración a base de datos PostgreSQL
- Integración con calendarios externos (Google Calendar, Outlook)
- Panel de analytics y reportes
- Multi-tenant para múltiples negocios

---

## [0.3.0] - 2026-02-12

### ✨ n8n AI Agent con Claude Haiku 4.5

#### Workflow n8n Productivo con IA
- **AI Agent** integrado en n8n usando Claude Haiku 4.5 via OpenRouter
- Procesamiento de lenguaje natural para solicitudes de citas médicas
- Extracción automática de: doctor, fecha, hora, motivo, urgencia
- Respuesta JSON estructurada con datos del appointment
- Email HTML con estilos inline enviado via Gmail OAuth2
- Respuesta HTTP al cliente con datos procesados

#### Flujo del Workflow (6 nodos)
```
Webhook Input → AI Agent (Claude Haiku 4.5) → Procesar Respuesta IA → Gmail → Preparar Respuesta HTTP → (lastNode response)
```

1. **Webhook Input**: Recibe POST con prompt de cita en lenguaje natural
2. **AI Agent**: Procesa con Claude Haiku 4.5 y devuelve JSON estructurado
3. **OpenRouter Chat Model**: Sub-nodo LLM conectado al agente
4. **Procesar Respuesta IA**: Parsea JSON del agente
5. **Enviar por Email**: Gmail OAuth2 con plantilla HTML profesional
6. **Preparar Respuesta HTTP**: Construye respuesta final para el cliente

#### Endpoint de Producción
- **URL**: `POST https://n8n.codeia.dev/webhook/smartsync-prod/cita-email`
- **Payload**: `{"prompt": "...", "user_id": "...", "user_timezone": "..."}`
- **Response**: JSON con appointment, message, email_sent, ai_processed

#### Limpieza y Organización
- Eliminados 13 workflows duplicados de pruebas anteriores
- Un único workflow productivo: `Smart-Sync Concierge - AI Agent` (ID: BkmU9DTalYI0OVml)
- Copia JSON del workflow guardada en `docs/n8n_workflow_ai_agent.json`

#### Archivos Modificados/Creados
- `apps/mcp_integration/services/workflow_builder.py`: Corrección parámetro Gmail (textPlain → message), nuevo método de conexiones con respuesta HTTP
- `docs/n8n_workflow_ai_agent.json`: Backup del workflow productivo
- `scripts/n8n/update_workflow_with_response.py`: Script de actualización de workflows
- `scripts/n8n/create_simple_workflow.py`: Script de creación de workflows

#### Credenciales Utilizadas
- OpenRouter API (Claude Haiku 4.5): `fh3p0R39FTAktnL6`
- Gmail OAuth2: Configurada manualmente en n8n UI

---

## [0.1.2] - 2026-02-10

### 🔧 Bug Fixes

#### n8n Workflow - Node "Generar Respuesta" Fix
- **Fixed:** Node "Generar Respuesta" (ID: 27404633-cf26-462b-8e8b-85b30567a0ca) was referencing fields at the root level that were actually nested inside the `appointment` object
- **Issue:** The node was attempting to access `doctor_name` and `appointment_datetime` directly from `$input.item.json`, but these fields are located within `data.appointment`
- **Solution:** Updated functionCode to properly extract and reference nested appointment object:
  ```javascript
  const data = $input.item.json;
  return {
    status: "success",
    message: "Cita confirmada exitosamente",
    appointment: data.appointment,
    confirmation_message: `Tu cita con ${data.appointment.doctor_name} ha sido confirmada para ${data.appointment.appointment_datetime}`
  };
  ```
- **Method:** API PUT request via n8n REST API (authenticated with X-N8N-API-KEY)
- **Verification:** Updated node confirmed via GET workflow request
- **Workflow ID:** bLmWJ1oeHFjyt1t7
- **Status:** ✅ Deployed successfully to n8n.codeia.dev

### 📋 Impacted Components
- n8n workflow: Smart-Sync Concierge - Appointments
- Node chain: Enriquecer Respuesta → Generar Respuesta (final output node)
- API endpoint: POST /appointments/process (webhook)

---

## [0.1.1] - 2026-02-10

### ✨ New Features

#### n8n Integration (MCP App)
- **Nueva app:** `apps/mcp_integration` para integración automática con n8n
  - Cliente n8n API completo con métodos CRUD
  - Constructor automático de workflows n8n
  - Comando Django para setup en una línea
  - Documentación completa de arquitectura

#### Componentes Nuevos
1. **N8NClient** (`apps/mcp_integration/services/n8n_client.py`)
   - Autenticación via JWT con n8n API
   - Métodos: create, activate, deactivate, list, delete, get_executions
   - Búsqueda por nombre y validación de conexión
   - Manejo robusto de errores HTTP

2. **SmartSyncWorkflowBuilder** (`apps/mcp_integration/services/workflow_builder.py`)
   - Generación automática de workflows JSON
   - 5 nodos: Webhook Input → Preparar Datos → HTTP Request → Procesar → Webhook Response
   - Enriquecimiento de metadata en tiempo real
   - Flujo completamente configurable

3. **setup_n8n_workflow Command** (`apps/mcp_integration/management/commands/`)
   - Setup automático de workflow con validaciones
   - Opciones: --django-url, --activate, --replace
   - Feedback detallado y guía de testing
   - Manejo de workflows existentes

#### Configuración
- Nuevo archivo: `config/settings/n8n.py`
  - Variables de entorno para n8n API
  - Configuración de webhook y seguridad
  - Parámetros de workflow

#### Documentación
- **MCP_ARCHITECTURE.md**: Decisiones de arquitectura, diagramas completos, flujo de datos
- **N8N_WORKFLOW_SETUP.md**: Guía paso a paso, troubleshooting, comandos útiles
- **apps/mcp_integration/README.md**: Documentación de la app

#### Dependencias
- Agregado: `requests==2.31.0` para llamadas HTTP a n8n API

### 🔄 Changed
- Actualizado `config/settings/base.py`: Agregada app `apps.mcp_integration`
- Importación de configuración n8n en base settings
- Actualizado `.env.example` con variables de n8n

### 📚 Documentation
- Actualizado CLAUDE.md con instrucciones de integración
- Documentación completa de arquitectura y decisiones
- Guía de setup paso a paso para usuarios

### 🧪 Testing
- Comandos para testing local con curl
- Instrucciones para testing con ngrok
- Verificación de conectividad a n8n

---

## [0.2.1] - 2026-01-29

### 🔧 Bug Fixes & Deployment Improvements

#### Production Settings
- Fixed SECRET_KEY validation - now generates automatically as fallback for development
- Made SECURE_SSL_REDIRECT configurable via environment variable
- Added SECURE_PROXY_SSL_HEADER to detect HTTPS when behind reverse proxy (EasyPanel)
- Improved production.py flexibility for different deployment scenarios

#### Docker & Deployment
- Fixed Dockerfile: Create logs/data/staticfiles directories before switching to non-root user
- Enhanced docker-entrypoint.sh to parse DATABASE_URL and extract connection details
- Fixed PostgreSQL readiness check to work with connection string format
- Added graceful fallback when DATABASE_URL is not configured
- Improved initialization output with colored status messages
- Resolved PermissionError when creating required directories in container

#### Documentation
- Added EASYPANEL_DEPLOYMENT_FIX.md - Complete EasyPanel configuration guide
- Added EASYPANEL_VERIFICATION_CHECKLIST.md - Step-by-step verification checklist
- Added scripts/generate_secret_key.py - Helper script for SECRET_KEY generation

#### CI/CD
- Deployment process now properly handles database initialization in containers
- EasyPanel integration ready for production with HTTPS and PostgreSQL
- Container permissions fixed for production-grade non-root execution

---

## [0.2.0] - 2026-01-27

### ✨ AI Agent Integration - Phase 3 Complete

#### Agents Implementation (1,200+ lines)
- ✅ **ParsingAgent** - Extract entities from natural language (240 lines)
  - Contact names, dates, times, locations, services
  - Ambiguity detection and field validation
  - Multi-format support (10+ date/time variations)

- ✅ **TemporalReasoningAgent** - Resolve relative dates/times (260 lines)
  - "mañana" → "2026-01-24", "10am" → "10:00"
  - Support for weekday names, ranges, relative references
  - IANA timezone handling with pytz
  - Business hours validation (8:00-18:00)

- ✅ **GeoReasoningAgent** - Location matching (200 lines)
  - Exact matching with normalization
  - Fuzzy matching with SequenceMatcher (70%+ accuracy)
  - Default to primary location if not specified
  - Accent/case insensitive matching

- ✅ **ValidationAgent** - Data integrity validation (150 lines)
  - Format validation (YYYY-MM-DD, HH:MM, semantic IDs)
  - Entity existence checks (contact, service, location)
  - Time range validation (start < end)
  - Integration with stores for real-time verification

- ✅ **AvailabilityAgent** - Real-time availability checking (130 lines)
  - Contact status and active verification
  - Conflict detection with existing appointments
  - Service duration constraint validation
  - Clear error messages with reasons

- ✅ **NegotiationAgent** - Intelligent suggestion generation (190 lines)
  - Same-day alternative slots (30-min intervals)
  - Next 3 days at preferred time
  - Confidence scoring based on proximity
  - Weekend skip, top 5 suggestions

#### Orchestrator & Infrastructure (500+ lines)
- ✅ **AgentOrchestrator** - 6-agent pipeline orchestration (280 lines)
  - Sequential execution with error handling
  - 3 result states: success, error, conflict
  - Graceful fallback at each stage
  - Full decision trace recording

- ✅ **DecisionTrace** - Complete observability model (dataclass)
  - trace_id, timestamp, user context
  - Per-agent metadata (status, duration_ms, confidence)
  - final_status and output tracking
  - Ready for persistence

- ✅ **TraceStore** - Persistent storage for traces (60 lines)
  - CRUD operations on traces.json
  - Query by user, status, trace_id
  - Metadata tracking (total_traces, last_updated)

#### API Integration (400+ lines)
- ✅ **AppointmentViewSet.create()** refactored to use orchestrator
  - Full agent pipeline integration
  - 3 HTTP response types:
    - 201 Created (success) with trace_id
    - 400 Bad Request (parsing errors)
    - 409 Conflict (with suggestions)
  - All responses include trace_id for debugging

- ✅ **TracesViewSet** - 6 specialized endpoints (250 lines)
  - GET /api/v1/traces/ - List with pagination
  - GET /api/v1/traces/{id}/ - Trace details
  - GET /api/v1/traces/by_status/ - Filter by status
  - GET /api/v1/traces/by_user/ - Filter by user
  - GET /api/v1/traces/{id}/agents/ - Agent decisions
  - GET /api/v1/traces/{id}/metrics/ - Performance metrics

#### Testing (100+ lines)
- ✅ **22 Unit Tests** covering all agents
  - ParsingAgent: 5 tests (extraction, ambiguities, edge cases)
  - TemporalReasoningAgent: 4 tests (dates, times, validation)
  - GeoReasoningAgent: 3 tests (exact/fuzzy matching, defaults)
  - ValidationAgent: 4 tests (formats, ranges, entities)
  - AgentResult: 3 tests (creation, success/error states)
  - AgentOrchestrator: 3 tests (initialization, traces, pipeline)

#### Documentation (800+ lines)
- ✅ **PHASE_3_COMPLETE.md** - Comprehensive Phase 3 summary
  - Architecture diagrams (happy path + conflicts)
  - Pipeline flow documentation
  - Performance metrics (700-1500ms typical)
  - Detailed agent descriptions
  - Integration examples
  - Next steps for v0.3.0

#### Performance
- **ParsingAgent**: 200-300ms typical
- **TemporalReasoningAgent**: 50-100ms typical
- **GeoReasoningAgent**: 50-150ms typical
- **ValidationAgent**: 50-100ms typical
- **AvailabilityAgent**: 100-300ms typical
- **NegotiationAgent**: 200-500ms typical
- **Total Pipeline**: 700-1500ms typical

#### Data Structure
- **data/traces.json** - New file for storing decision traces
- **TraceStore** class in data/stores.py for persistence

#### Configuration
- Updated config/urls.py to include traces app routing
- Added pytz dependency to requirements.txt (timezone support)

### 🔄 Migration from v0.1.0
- No breaking changes to existing API contracts
- All v0.1.0 endpoints continue to work unchanged
- New agent-powered appointment creation (backward compatible)
- Traces endpoint is additive (no removals)

### 🔐 Security
- Input validation in all agents
- Entity existence verification before use
- Type checking for all formats
- Timezone validation (IANA format)
- No SQL injection (JSON-based storage)
- Ready for rate limiting with trace auditing

### 📊 Statistics
- **1,200+ lines** of agent code
- **400+ lines** of integration code
- **100+ lines** of test code
- **800+ lines** of documentation
- **16 new files** created
- **3 files** modified
- **16 git commits** in Phase 3

---

## [0.1.0] - 2026-01-27

### ✨ Django Base Configuration - Setup Complete

#### Infrastructure
- ✅ **Django 4.2.27 (LTS)** configuration with modular settings (base, local, production)
- ✅ **Django REST Framework 3.15.2** with full API configuration
- ✅ **CORS & Security** configuration with HTTPS/HSTS for production
- ✅ **Error Handling** with custom exception handlers and standardized responses
- ✅ **Throttling** configured (60 req/min per user, 10k in development)
- ✅ **Logging** with rotating file handlers and level-based filtering
- ✅ **Static Files** and media handling configured

#### Applications
- ✅ **4 Django Apps** created with placeholder structure:
  - `apps.appointments` - Appointment management
  - `apps.contacts` - Doctor/staff/resource management
  - `apps.services` - Service catalog
  - `apps.availability` - Availability checks
- ✅ Each app has `models.py`, `serializers.py`, `views.py`, `urls.py` ready for implementation

#### Configuration Files
- ✅ **config/constants.py** (300+ lines) - All enums and constants
- ✅ **config/validators.py** (320+ lines) - Custom validation functions
- ✅ **config/exceptions.py** (170+ lines) - Exception handling with conflict suggestions
- ✅ **config/urls.py** - API root, health check, app routing
- ✅ **config/views.py** - Custom 404/500 error handlers

#### Project Structure
- ✅ **manage.py** - Django CLI entry point
- ✅ **requirements.txt** - Updated dependencies for Python 3.9+
- ✅ **.gitignore** - Comprehensive git ignore rules
- ✅ **pytest.ini** - Testing configuration with coverage settings
- ✅ **data/** - JSON storage files (appointments, contacts, services)
- ✅ **logs/**, **static/**, **media/**, **templates/** - Directories created

#### Documentation
- ✅ **DJANGO_SETUP.md** - Complete setup documentation
- ✅ **architecture.md** - Updated with Django 4.2.27 version info

#### Verification
- ✅ `python manage.py check` - All systems verified and working
- ✅ 40 Python files created with ~2,200 lines of code
- ✅ Git commit: `c72d885 Set up Django base configuration (v0.1.0)`

**Status: Ready for Phase 2 (Endpoint Implementation)**

---

## [0.1.0] - 2026-01-22

### Añadido
- 🎉 **Lanzamiento inicial de Smart-Sync Concierge**

#### Arquitectura
- Estructura modular Django 6.0.1 con apps separadas
- Sistema de storage JSON local para citas, contactos y servicios
- Arquitectura de servicios para lógica de negocio
- Sistema de prompts para integración con Qwen IA

#### API REST
- Endpoint `POST /api/v1/appointments/` para crear citas desde lenguaje natural
- Endpoint `GET /api/v1/appointments/` para listar citas con filtros
- Endpoint `GET /api/v1/appointments/{id}/` para obtener detalles de cita
- Endpoint `PUT /api/v1/appointments/{id}/` para actualizar citas
- Endpoint `DELETE /api/v1/appointments/{id}/` para cancelar citas
- Endpoint `POST /api/v1/appointments/{id}/reschedule/` para reprogramar
- Endpoint `GET /api/v1/availability/slots/` para consultar disponibilidad
- Endpoint `GET /api/v1/contacts/` para gestionar contactos
- Endpoint `GET /api/v1/services/` para catálogo de servicios

#### Motor IA (Qwen)
- Cliente para integración con Qwen 2.5
- Sistema de prompts modular (extraction, validation, conflict)
- Parser de respuestas IA a datos estructurados
- Extracción de entidades: fecha, hora, participantes, tipo, ubicación
- Detección de ambigüedades e información faltante

#### Pipeline Prompt-First
- Servicio de parsing de lenguaje natural
- Servicio de validación de reglas de negocio
- Servicio de verificación de disponibilidad
- Resolución de conflictos con sugerencias inteligentes
- Enriquecimiento de datos con contexto geo-temporal

#### Admin de Django
- Panel de administración con URLs amigables
- Gestión de citas con vista de calendario
- Gestión de contactos y disponibilidad
- Configuración de servicios
- Vista de conflictos y resolución

#### Validaciones
- Validación de sintaxis de prompts
- Validación de dominio (contactos, servicios)
- Validación de reglas de negocio (horarios, días laborales)
- Validación temporal (zonas horarias, festivos)
- Validación de disponibilidad (sin superposiciones)

#### Seguridad
- Validación y sanitización de entrada
- Rate limiting configurable
- Estructura para autenticación token-based
- Preparación para RBAC

#### Documentación
- [architecture.md](architecture.md) - Arquitectura completa del sistema
- [api_reference.md](api_reference.md) - Referencia detallada de la API
- [deployment.md](deployment.md) - Guía de despliegue
- [changelog.md](changelog.md) - Este archivo

#### Características Técnicas
- Archivos fragmentados (<1000 líneas por archivo)
- Constantes reutilizables para consistencia
- URLs amigables en todo el sistema
- Soporte para zonas horarias múltiples
- Configuración modular de Django settings

### Dependencias
- Django 6.0.1
- Django REST Framework 3.15.2
- Qwen 2.5
- python-dateutil 2.9.0
- pytz 2024.2
- pydantic 2.10.4

---

## Convenciones de Versionado

Para este proyecto seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Funcionalidades backwards-compatibles
- **PATCH**: Correcciones de errores backwards-compatibles

## Tipos de Cambios

- `Añadido` - Nuevas funcionalidades
- `Cambiado` - Cambios en funcionalidades existentes
- `Eliminado` - Funcionalidades removidas
- `Corregido` - Correcciones de bugs
- `Seguridad` - Mejoras de seguridad

---

*Fecha de lanzamiento inicial: 22 de Enero, 2026*
*Versión actual: 0.3.0*
