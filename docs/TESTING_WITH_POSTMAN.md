# Testing Smart-Sync Concierge con Postman

**Guía completa para testear la integración Phase 3 en local**

---

## 1. Requisitos Previos

- ✅ Postman instalado (https://www.postman.com/downloads/)
- ✅ Django server corriendo en `http://localhost:9000`
- ✅ Colección de Postman importada

---

## 2. Iniciar el Servidor Django

### Terminal 1: Iniciar servidor
```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge

python3 manage.py runserver 0.0.0.0:9000
```

**Esperado:**
```
Starting development server at http://0.0.0.0:9000/
Quit the server with CONTROL-C.
```

### Verificar que funciona
```bash
curl http://localhost:9000/api/v1/health/
```

Debería retornar:
```json
{
  "status": "healthy",
  "message": "Smart-Sync Concierge API is running",
  "version": "0.1.0",
  "timestamp": null
}
```

---

## 3. Importar Colección en Postman

### Opción A: Importar desde archivo JSON

1. Abre Postman
2. Click en **Import** (arriba a la izquierda)
3. Selecciona **Upload Files**
4. Navega a: `docs/POSTMAN_COLLECTION.json`
5. Click en **Import**

### Opción B: Crear manualmente

Si prefieres crear las requests manualmente, sigue los pasos del Paso 4.

---

## 4. Testear Endpoints Uno por Uno

### 4.1 Health Check (GET)

**URL:** `http://localhost:9000/api/v1/health/`

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "status": "healthy",
  "message": "Smart-Sync Concierge API is running",
  "version": "0.1.0"
}
```

---

### 4.2 API Root (GET)

**URL:** `http://localhost:9000/api/v1/`

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "status": "success",
  "message": "Smart-Sync Concierge API v1",
  "version": "0.1.0",
  "endpoints": {
    "appointments": "http://localhost:9000/api/v1/appointments/",
    "contacts": "http://localhost:9000/api/v1/contacts/",
    "services": "http://localhost:9000/api/v1/services/",
    "traces": "http://localhost:9000/api/v1/traces/"
  }
}
```

---

### 4.3 List Appointments (GET)

**URL:** `http://localhost:9000/api/v1/appointments/`

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "results": [],
  "count": 0
}
```

---

### 4.4 Create Appointment - Test 1: Prompt Simple

**URL:** `http://localhost:9000/api/v1/appointments/`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "prompt": "cita mañana 9am con Dr. García",
  "user_timezone": "America/Mexico_City",
  "user_id": "user_001"
}
```

**Expected:** Uno de estos resultados:

#### Caso 1: Success (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": "apt_20260128_020030_xxxx",
    "contacto_id": "contact_07255ac6",
    "contacto_nombre": "Dr. Juan García",
    "fecha": "2026-01-29",
    "hora_inicio": "09:00",
    "hora_fin": "09:30",
    "status": "confirmed",
    "created_via_agent": true,
    "trace_id": "trace_20260128_020003_xxxx"
  },
  "message": "Appointment created successfully",
  "trace_id": "trace_20260128_020003_xxxx",
  "_links": {
    "self": "/api/v1/appointments/apt_20260128_020030_xxxx/",
    "reschedule": "/api/v1/appointments/apt_20260128_020030_xxxx/reschedule/",
    "contact": "/api/v1/contacts/contact_07255ac6/",
    "trace": "/api/v1/traces/trace_20260128_020003_xxxx/"
  }
}
```

**✓ Lo importante:** Anotate el `trace_id` para usarlo en los siguientes tests

#### Caso 2: Conflict (409 Conflict)
```json
{
  "status": "error",
  "code": "CONFLICT",
  "message": "Requested time is not available",
  "error_detail": "Time slot conflict with existing appointment",
  "suggestions": [
    {
      "fecha": "2026-01-29",
      "hora_inicio": "11:00",
      "confidence": 0.9
    },
    {
      "fecha": "2026-01-30",
      "hora_inicio": "09:00",
      "confidence": 0.85
    }
  ],
  "trace_id": "trace_20260128_015941_140730d9"
}
```

#### Caso 3: Error (400 Bad Request)
```json
{
  "status": "error",
  "code": "PROCESSING_ERROR",
  "message": "Could not parse prompt: Missing required entities",
  "trace_id": "trace_20260128_015951_54f10bd6"
}
```

---

### 4.5 View Trace Details (GET)

**URL:** `http://localhost:9000/api/v1/traces/{trace_id}/`

Reemplaza `{trace_id}` con el trace_id del paso anterior.

**Ejemplo:**
```
http://localhost:9000/api/v1/traces/trace_20260128_020003_xxxx/
```

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "trace_id": "trace_20260128_020003_xxxx",
  "timestamp": "2026-01-28T02:00:03.123456+00:00",
  "input_prompt": "cita mañana 9am con Dr. García",
  "user_timezone": "America/Mexico_City",
  "user_id": "user_001",
  "agents": [
    {
      "agent": "parsing",
      "status": "success",
      "message": "Extracted entities",
      "duration_ms": 2,
      "confidence": 0.8
    },
    {
      "agent": "temporal_reasoning",
      "status": "success",
      "message": "Resolved 2026-01-29 09:00",
      "duration_ms": 5,
      "confidence": 0.95
    },
    ...
  ],
  "final_status": "success",
  "total_duration_ms": 17
}
```

---

### 4.6 List All Traces (GET)

**URL:** `http://localhost:9000/api/v1/traces/`

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "trace_id": "trace_20260128_020003_xxxx",
      "timestamp": "2026-01-28T02:00:03.123456+00:00",
      "input_prompt": "cita mañana 9am con Dr. García",
      "final_status": "success",
      "total_duration_ms": 17
    },
    ...
  ]
}
```

---

### 4.7 Filter Traces by Status (GET)

**URL:** `http://localhost:9000/api/v1/traces/by_status/?status=success`

**Query Parameters:**
- status: `success` | `error` | `conflict`

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "count": 1,
  "results": [
    {
      "trace_id": "trace_20260128_020003_xxxx",
      "final_status": "success"
    }
  ]
}
```

---

### 4.8 Get Agent Decisions (GET)

**URL:** `http://localhost:9000/api/v1/traces/{trace_id}/agents/`

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "trace_id": "trace_20260128_020003_xxxx",
  "agents": [
    {
      "agent_name": "ParsingAgent",
      "status": "success",
      "message": "Extracted entities",
      "duration_ms": 2,
      "confidence": 0.8,
      "input": {...},
      "output": {...},
      "errors": [],
      "warnings": []
    },
    {
      "agent_name": "TemporalReasoningAgent",
      "status": "success",
      "message": "Resolved to 2026-01-29 09:00",
      "duration_ms": 5,
      "confidence": 0.95,
      ...
    },
    ...
  ]
}
```

---

### 4.9 Get Performance Metrics (GET)

**URL:** `http://localhost:9000/api/v1/traces/{trace_id}/metrics/`

**Headers:**
- Content-Type: application/json

**Body:** (vacío)

**Expected:** 200 OK
```json
{
  "trace_id": "trace_20260128_020003_xxxx",
  "total_duration_ms": 17,
  "agent_durations": {
    "ParsingAgent": 2,
    "TemporalReasoningAgent": 5,
    "GeoReasoningAgent": 1,
    "ValidationAgent": 2,
    "AvailabilityAgent": 4,
    "NegotiationAgent": 0
  },
  "orchestrator_overhead_ms": 3,
  "agents_total_ms": 14
}
```

---

## 5. Flujo Completo de Testing

### Paso 1: Crear Contact
```
POST /api/v1/contacts/
Body:
{
  "nombre": "Dr. García",
  "especialidad": "Medicina",
  "email": "garcia@clinic.com"
}
```

### Paso 2: Crear Service
```
POST /api/v1/services/
Body:
{
  "nombre": "Consulta",
  "descripcion": "Consulta médica",
  "duracion": 30
}
```

### Paso 3: Crear Appointment (con IA)
```
POST /api/v1/appointments/
Body:
{
  "prompt": "cita mañana 10am con Dr. García",
  "user_timezone": "America/Mexico_City"
}
```

### Paso 4: Recuperar Trace
```
GET /api/v1/traces/{trace_id}
```

### Paso 5: Analizar Decisiones
```
GET /api/v1/traces/{trace_id}/agents/
```

### Paso 6: Ver Métricas
```
GET /api/v1/traces/{trace_id}/metrics/
```

---

## 6. Test Cases Recomendados

### Test Case 1: Prompt Completo ✓
```
Prompt: "cita mañana 10am con Dr. García"
Expected: 201 Success o 409 Conflict
Agents: 6 ejecutados
```

### Test Case 2: Prompt Incompleto ✓
```
Prompt: "necesito una cita"
Expected: 400 Error
Agents: ParsingAgent falla
```

### Test Case 3: Prompt Ambiguo ✓
```
Prompt: "cita próxima semana con García"
Expected: 400 Error (no puede resolver "próxima semana")
Agents: TemporalReasoningAgent falla
```

### Test Case 4: Hora Fuera de Horario ✓
```
Prompt: "cita hoy 23:00 con Dr. García"
Expected: 400 Error o 409 Conflict
Agents: TemporalReasoningAgent warning
```

### Test Case 5: Múltiples Usuarios ✓
```
Crea 3 citas con diferente user_id
Filtra por user_id
Verifica que cada uno solo ve sus traces
```

---

## 7. Variables de Postman (Recomendado)

En Postman, crea estas variables en Environments:

```
base_url = http://localhost:9000
api_path = /api/v1

appointments_url = {{base_url}}{{api_path}}/appointments/
traces_url = {{base_url}}{{api_path}}/traces/
contacts_url = {{base_url}}{{api_path}}/contacts/

# Después de crear una cita, guarda:
trace_id = <valor del trace_id retornado>
appointment_id = <valor del appointment ID>
```

Luego usa en las requests:
```
GET {{traces_url}}{{trace_id}}/
```

---

## 8. Troubleshooting

### Error: Connection Refused
```
❌ error: connect ECONNREFUSED 127.0.0.1:9000
```

**Solución:**
```bash
# Verificar servidor está corriendo
ps aux | grep "manage.py runserver"

# Si no está, iniciarlo:
python3 manage.py runserver 0.0.0.0:9000
```

### Error: 404 Not Found
```
❌ 404 - El recurso solicitado no existe
```

**Solución:**
- Verifica la URL exacta
- Verifica que no hay espacios extra
- Verifica que reemplazaste {{trace_id}} con valor real

### Error: 401 Unauthorized
```
❌ 401 - Se requiere autenticación
```

**Solución:**
- Algunos endpoints (como /traces/) pueden requerir token
- Para ahora, prueba sin autenticación
- Si necesitas, crea un token en Django

### Error: 500 Internal Server Error
```
❌ 500 - Error interno del servidor
```

**Solución:**
```bash
# Ver logs del servidor:
tail -100 /tmp/django_server.log

# Reiniciar servidor:
python3 manage.py runserver 0.0.0.0:9000
```

---

## 9. Comandos Rápidos (sin Postman)

Si prefieres usar curl:

### Health Check
```bash
curl http://localhost:9000/api/v1/health/
```

### Create Appointment
```bash
curl -X POST http://localhost:9000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. García",
    "user_timezone": "America/Mexico_City"
  }'
```

### Get Trace
```bash
curl http://localhost:9000/api/v1/traces/{trace_id}/
```

### List Traces
```bash
curl http://localhost:9000/api/v1/traces/
```

---

## 10. Verificación Final

✅ **Todas las respuestas funcionan correctamente si:**
- ✓ Health check retorna status "healthy"
- ✓ Create appointment retorna 201 o 409
- ✓ Cada response incluye trace_id
- ✓ Los traces se pueden recuperar
- ✓ Los agentes se ejecutan (ver en /agents/)
- ✓ Las métricas se calculan correctamente

**Status:** 🟢 **Todo funcionando correctamente**

---

**Última actualización:** 28 de Enero, 2026
**Versión:** 0.2.0 (Phase 3)
