# Arquitectura MCP - Integración n8n

## Descripción General

Este documento describe la arquitectura de integración entre n8n (self-hosted) y Smart-Sync Concierge API mediante la app MCP de Django.

**Versión:** 0.1.0
**Estado:** ✅ Implementado
**Última actualización:** 2026-02-10

## Decisiones de Arquitectura

### 1. Ubicación del MCP Server

**Decisión:** Django app en lugar de servidor FastAPI separado

**Justificación:**
- ✅ Reutiliza 6 agentes existentes (no duplica lógica)
- ✅ Acceso directo a stores (AppointmentStore, ContactStore)
- ✅ Un solo proceso (menor overhead)
- ✅ Deployment simplificado
- ✅ Endpoint `/api/v1/appointments/` YA procesa prompts correctamente

**Alternativas consideradas:**
- ❌ Servidor FastAPI en puerto 8001 → Duplica lógica, complejidad operacional
- ❌ Función serverless (Lambda) → Mayor latencia, costo

### 2. Integración con Agentes Existentes

**Decisión:** n8n llama directamente a API Django existente

**Flujo:**
```
Usuario → n8n Webhook → Django API (/api/v1/appointments/)
                            ↓
                      AgentOrchestrator
                            ↓
                    6 Agentes IA
                            ↓
                    Respuesta Estructurada
```

**Justificación:**
- ✅ Los agentes YA están implementados
- ✅ Reutiliza validaciones, cálculos de disponibilidad
- ✅ Trazabilidad completa (DecisionTrace)
- ✅ No necesita Openrouter directo

### 3. Creación del Workflow

**Decisión:** Cliente Python + Comando Django

**Beneficios:**
- ✅ Creación automática (no manual)
- ✅ Garantiza configuración correcta
- ✅ Parametrizable (URLs, tokens)
- ✅ Facilitaretesting y re-despliegue

## Arquitectura de Componentes

```
┌──────────────────────────────────────────────────────────────┐
│                    USUARIO FINAL                             │
│            (Postman / Frontend / Bot)                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    HTTP POST
                    JSON body:
                    {
                      "prompt": "...",
                      "user_timezone": "..."
                    }
                         │
                         ↓
┌──────────────────────────────────────────────────────────────┐
│             N8N CLOUD (https://n8n.codeia.dev)              │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [1] Webhook Input Node                                  │ │
│  │     POST /webhook/appointments/process                  │ │
│  │     Recibe: prompt, user_timezone, user_id             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                      ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [2] Preparar Datos (Function Node)                      │ │
│  │     - Extrae body del webhook                           │ │
│  │     - Enriquece con metadata:                           │ │
│  │       * n8n_execution_id                                │ │
│  │       * timestamp                                        │ │
│  │       * source                                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                      ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [3] HTTP Request Node                                   │ │
│  │     POST Django API                                     │ │
│  │     URL: /api/v1/appointments/                          │ │
│  │     Headers: Authorization: Token <django_token>        │ │
│  │     Body: { prompt, user_timezone, user_id }           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                      ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [4] Procesar Respuesta (Function Node)                 │ │
│  │     - Extrae status, data, suggestions                 │ │
│  │     - Estructura respuesta estándar                    │ │
│  │     - Agrega timestamp de respuesta                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                      ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [5] Webhook Response Node                               │ │
│  │     Devuelve respuesta al usuario                       │ │
│  │     Status: 201 Created / 400 Bad Request / etc         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    HTTPS
              (https://abc123.ngrok.io)
                         │
                         ↓
┌──────────────────────────────────────────────────────────────┐
│     NGROK TUNNEL (Desarrollo) / Dominio (Producción)        │
│                                                               │
│     https://abc123.ngrok.io → localhost:8000                 │
│     o                                                         │
│     https://api.smartsync.dev → AWS/Railway                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────┐
│         DJANGO REST API (localhost:8000)                     │
│                                                               │
│  POST /api/v1/appointments/                                  │
│  ├─ Autenticación: Token Django                              │
│  └─ Body: { prompt, user_timezone, user_id }               │
│           ↓                                                  │
│       AppointmentViewSet.create()                            │
│           ↓                                                  │
│       AgentOrchestrator.process_appointment_prompt()         │
│           ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │             PIPELINE DE 6 AGENTES                       │ │
│  │                                                          │ │
│  │ [1] ParsingAgent                                         │ │
│  │     Input: "cita mañana 10am con Dr. Pérez"             │ │
│  │     Output: {fecha_raw, hora_raw, contacto_nombre, ...} │ │
│  │           ↓                                              │ │
│  │ [2] TemporalReasoningAgent                              │ │
│  │     Input: {fecha_raw, hora_raw, ...}                   │ │
│  │     Output: {fecha, hora_inicio, hora_fin, ...}         │ │
│  │           ↓                                              │ │
│  │ [3] GeoReasoningAgent                                    │ │
│  │     Input: {contacto_nombre, ubicacion_raw, ...}        │ │
│  │     Output: {contacto_id, ubicacion_id, ...}            │ │
│  │           ↓                                              │ │
│  │ [4] ValidationAgent                                      │ │
│  │     Input: {fecha, hora, contacto_id, ...}              │ │
│  │     Output: {valid: true/false, errors, warnings}       │ │
│  │           ↓                                              │ │
│  │ [5] AvailabilityAgent                                    │ │
│  │     Input: {contacto_id, fecha, hora_inicio, ...}       │ │
│  │     Output: {disponible, conflicts}                     │ │
│  │           ↓                                              │ │
│  │ [6] NegotiationAgent (si hay conflicto)                │ │
│  │     Input: {conflicts, preferred_date, ...}             │ │
│  │     Output: {suggestions}                               │ │
│  │                                                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│           ↓                                                  │
│       Success / Conflict / Error                             │
│           ↓                                                  │
│       Django responde:                                       │
│       {                                                      │
│         "status": "success|conflict|error",                 │
│         "data": {...appointment...},                         │
│         "message": "...",                                    │
│         "suggestions": [...],                               │
│         "trace_id": "trace_20260210_abc123",               │
│         "metadata": {...}                                   │
│       }                                                      │
│           ↓                                                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    HTTPS Response
                         │
                         ↓
┌──────────────────────────────────────────────────────────────┐
│             N8N (Nodo [5] procesa respuesta)                 │
│                                                               │
│     - Extrae status, data, suggestions                       │
│     - Estructura formato final                              │
│     - Devuelve al usuario via Webhook Response             │
│                                                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                    USUARIO FINAL                             │
│                                                               │
│  HTTP 201 Created                                            │
│  {                                                           │
│    "status": "success",                                      │
│    "message": "Appointment created successfully",            │
│    "data": {                                                 │
│      "id": "apt_20260211_abc123",                            │
│      "contacto_nombre": "Dr. Pérez",                         │
│      "fecha": "2026-02-11",                                  │
│      "hora_inicio": "10:00",                                 │
│      "hora_fin": "11:00",                                    │
│      ...                                                     │
│    },                                                        │
│    "trace_id": "trace_20260210_abc123"                      │
│  }                                                           │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Flujo de Datos Completo (Ejemplo Real)

### Paso 1: Usuario envía solicitud

```
POST https://n8n.codeia.dev/webhook/appointments/process
Content-Type: application/json

{
  "prompt": "cita mañana 10am con Dr. Pérez para consulta general",
  "user_timezone": "America/Mexico_City",
  "user_id": "user_001"
}
```

### Paso 2: n8n recibe y prepara

```json
{
  "prompt": "cita mañana 10am con Dr. Pérez para consulta general",
  "user_timezone": "America/Mexico_City",
  "user_id": "user_001",
  "metadata": {
    "n8n_execution_id": "exec_abc123def456",
    "timestamp": "2026-02-10T20:15:30.123Z",
    "source": "n8n_webhook"
  }
}
```

### Paso 3: n8n envía a Django

```bash
POST https://abc123.ngrok.io/api/v1/appointments/
Authorization: Token django_token_abc123
Content-Type: application/json

{
  "prompt": "cita mañana 10am con Dr. Pérez para consulta general",
  "user_timezone": "America/Mexico_City",
  "user_id": "user_001",
  "metadata": {...}
}
```

### Paso 4: Django procesa con 6 agentes

**ParsingAgent:** Extrae entidades
```json
{
  "fecha_raw": "mañana",
  "hora_raw": "10am",
  "contacto_nombre": "Dr. Pérez",
  "servicio_raw": "consulta general"
}
```

**TemporalReasoningAgent:** Resuelve fecha/hora
```json
{
  "fecha": "2026-02-11",
  "hora_inicio": "10:00:00",
  "hora_fin": "11:00:00",
  "duracion_minutos": 60
}
```

**GeoReasoningAgent:** Mapea contacto
```json
{
  "contacto_id": "dr_perez_001",
  "contacto_nombre": "Dr. Juan Pérez",
  "especialidades": ["consulta_general", "pediatria"],
  "ubicacion_id": "hosp_cdmx_consultorios"
}
```

**ValidationAgent:** Valida reglas
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

**AvailabilityAgent:** Verifica disponibilidad
```json
{
  "disponible": true,
  "conflicts": []
}
```

**Result:** Appointment creada exitosamente

### Paso 5: Django devuelve respuesta

```json
HTTP 201 Created

{
  "status": "success",
  "data": {
    "id": "apt_20260211_abc123",
    "fecha": "2026-02-11",
    "hora_inicio": "10:00:00",
    "hora_fin": "11:00:00",
    "duracion_minutos": 60,
    "tipo": {
      "id": "consulta_general",
      "nombre": "Consulta General"
    },
    "participantes": [
      {
        "id": "dr_perez_001",
        "nombre": "Dr. Juan Pérez",
        "rol": "prestador"
      }
    ],
    "status": "confirmed",
    "user_id": "user_001",
    "prompt_original": "cita mañana 10am con Dr. Pérez para consulta general",
    "created_at": "2026-02-10T20:15:45.678Z",
    "updated_at": "2026-02-10T20:15:45.678Z"
  },
  "message": "Appointment created successfully",
  "trace_id": "trace_20260210_20_15_30_abc123",
  "timestamp": "2026-02-10T20:15:45.678Z"
}
```

### Paso 6: n8n procesa respuesta

Extrae campos y estructura respuesta final

### Paso 7: Usuario recibe respuesta

```json
HTTP 201 Created

{
  "status": "success",
  "message": "Appointment created successfully",
  "data": {
    "id": "apt_20260211_abc123",
    "contacto_nombre": "Dr. Juan Pérez",
    "fecha": "2026-02-11",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "tipo_servicio": "Consulta General"
  },
  "trace_id": "trace_20260210_20_15_30_abc123"
}
```

## Componentes Principales

### 1. N8NClient (`apps/mcp_integration/services/n8n_client.py`)

Cliente Python para interactuar con n8n API.

**Métodos:**
- `test_connection()`: Verifica conectividad
- `create_workflow(workflow_data)`: Crea workflow
- `activate_workflow(workflow_id)`: Activa workflow
- `deactivate_workflow(workflow_id)`: Desactiva workflow
- `get_workflow(workflow_id)`: Obtiene detalles
- `list_workflows()`: Lista todos
- `delete_workflow(workflow_id)`: Elimina
- `get_executions(workflow_id)`: Ver historial
- `find_workflow_by_name(name)`: Busca por nombre

**Autenticación:**
```python
headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json"
}
```

### 2. SmartSyncWorkflowBuilder (`apps/mcp_integration/services/workflow_builder.py`)

Constructor automático de workflows JSON.

**Nodos generados:**
1. **Webhook Input**: Recibe POST
2. **Preparar Datos**: Function node que enriquece
3. **HTTP Request**: POST a Django API
4. **Procesar Respuesta**: Function node que extrae
5. **Webhook Response**: Devuelve respuesta

**Conexiones:** `[1] → [2] → [3] → [4] → [5]`

### 3. Comando Django (`apps/mcp_integration/management/commands/setup_n8n_workflow.py`)

Setup automático del workflow.

**Uso:**
```bash
python manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io \
  --activate
```

**Pasos:**
1. Verifica conectividad a n8n
2. Busca workflow existente
3. Construye JSON del workflow
4. Crea en n8n
5. Activa (opcional)

## Variables de Entorno

```bash
# n8n API
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=<jwt_token>

# Django API (para que n8n lo llame)
DJANGO_API_URL=http://localhost:8000  # ngrok en dev
DJANGO_API_TOKEN=<token_drf>

# Webhook Security
WEBHOOK_SECRET=<optional>
WEBHOOK_VERIFY_SIGNATURE=False
```

## Conectividad: n8n Cloud ↔ Django Local/Cloud

### Desarrollo: ngrok

```bash
# Terminal 1: Django
python manage.py runserver 0.0.0.0:8000

# Terminal 2: ngrok
ngrok http 8000
# Output: https://abc123.ngrok.io

# Configurar DJANGO_API_URL=https://abc123.ngrok.io
```

### Producción: Dominio público

```bash
# Deploy Django a Railway, Render, AWS
# Configurar dominio: api.smartsync.dev
# n8n llama a: https://api.smartsync.dev/api/v1/appointments/
```

## Seguridad

### Autenticación n8n → Django

Token Django en header:
```
Authorization: Token <django_token>
```

Generar con:
```bash
python manage.py drf_create_token admin
```

### Rate Limiting

Configurado en Django REST Framework:
```python
'DEFAULT_THROTTLE_RATES': {
    'anon': '60/minute',
    'user': '60/minute',
}
```

### Validación HMAC (Producción)

Opcional: Validar firma HMAC de webhooks en middleware.

## Testing

### Unit Tests

```bash
python manage.py test apps.mcp_integration
```

### Integration Tests

```bash
# Test endpoint Django directo
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Token <token>" \
  -d '{"prompt": "cita mañana"}'

# Test con ngrok
curl -X POST https://abc123.ngrok.io/api/v1/appointments/ \
  -H "Authorization: Token <token>" \
  -d '{"prompt": "cita mañana"}'

# Test webhook n8n
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -d '{"prompt": "cita mañana"}'
```

## Monitoreo

### Logs Django

```bash
tail -f logs/django.log | grep "mcp_integration"
```

### Executions n8n

```
https://n8n.codeia.dev/workflow/<workflow_id>/executions
```

### Traces Django

```bash
curl http://localhost:8000/api/v1/traces/
```

## Ventajas de esta Arquitectura

✅ **Reutilización:** 6 agentes ya implementados
✅ **Simplicidad:** Un solo proceso (Django)
✅ **Automatización:** Setup en una línea
✅ **Trazabilidad:** DecisionTrace completo
✅ **Escalabilidad:** Fácil de escalar a producción
✅ **Mantenibilidad:** Código modular y documentado

## Limitaciones y Futuros

- [ ] Validación HMAC de webhooks
- [ ] Endpoint diagnóstico `/api/v1/mcp/status/`
- [ ] Tests unitarios completos
- [ ] Soporte para múltiples workflows
- [ ] Webhooks de n8n → Django (notificaciones)
- [ ] Dashboard de monitoreo

## Referencias

- [N8N_CLOUD_INTEGRATION.md](N8N_CLOUD_INTEGRATION.md)
- [apps/agents/orchestrator.py](../apps/agents/orchestrator.py)
- [apps/mcp_integration/README.md](../apps/mcp_integration/README.md)
