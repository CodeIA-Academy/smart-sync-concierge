# Smart-Sync Concierge - Referencia Completa de Endpoints de API

## 🚀 Quick Reference

**Base URL (desarrollo)**: `http://localhost:9001/api/v1/`
**Autenticación**: Token Authentication
**Formato**: JSON
**Paginación**: Automática (20 items por defecto, máx 100)

---

## 📌 ENDPOINTS GLOBALES

### Health Check (Sin Autenticación)
```bash
GET /api/v1/health/

# Response
{
  "status": "healthy",
  "message": "Smart-Sync Concierge API is running",
  "version": "0.1.0"
}
```

### Obtener Token
```bash
POST /api/v1/token-auth/

# Request
{
  "username": "admin",
  "password": "admin123456"
}

# Response
{
  "status": "success",
  "token": "a75267088f61b319d75ffef873ac095e93558a37",
  "user": {
    "id": 2,
    "username": "admin",
    "email": "admin@smartsync.dev"
  }
}
```

### Documentación de API
```bash
GET /docs/swagger/     # Swagger UI
GET /docs/redoc/       # ReDoc
GET /api/v1/docs/schema/  # OpenAPI Schema
```

---

## 👥 ENDPOINTS DE CONTACTOS

### Listar Contactos
```bash
GET /api/v1/contacts/

# Query Parameters
?tipo=prestador              # Filtrar por tipo
?buscar=juan                 # Búsqueda en nombre/titulo
?activo=true                 # Filtrar por estado activo
?page=1                      # Número de página
?page_size=20                # Items por página (máx 100)

# Response
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "dr_juan_perez",
      "nombre": "Dr. Juan Pérez",
      "tipo": "prestador",
      "titulo": "Médico General",
      "email": "juan.perez@hospital.com",
      "telefono": "+34912345678",
      "especialidades": ["consulta_general", "pediatria"],
      "activo": true,
      "created_at": "2026-01-30T09:14:54.820385Z",
      "updated_at": "2026-01-30T09:14:54.820403Z"
    }
  ]
}
```

### Obtener Detalle de Contacto
```bash
GET /api/v1/contacts/{id}/
```

### Crear Contacto
```bash
POST /api/v1/contacts/

# Request
{
  "nombre": "Dr. New Doctor",
  "tipo": "prestador",
  "titulo": "Médico Especialista",
  "email": "new@hospital.com",
  "telefono": "+34900000000",
  "especialidades": ["especialidad1", "especialidad2"]
}
```

### Actualizar Contacto
```bash
PUT /api/v1/contacts/{id}/         # Actualización completa
PATCH /api/v1/contacts/{id}/       # Actualización parcial
```

### Eliminar Contacto
```bash
DELETE /api/v1/contacts/{id}/
```

### Verificar Disponibilidad de Contacto
```bash
POST /api/v1/contacts/{id}/availability/

# Request
{
  "fecha": "2026-02-10",
  "hora_inicio": "14:00",
  "hora_fin": "15:00"
}

# Response
{
  "status": "success",
  "data": {
    "disponible": true,
    "slots_disponibles": []
  }
}
```

### Obtener Citas de un Contacto
```bash
GET /api/v1/contacts/{id}/appointments/

# Query Parameters
?status=confirmed
?fecha_inicio=2026-01-31
?fecha_fin=2026-02-28
```

---

## 📅 ENDPOINTS DE CITAS

### Listar Citas
```bash
GET /api/v1/appointments/

# Query Parameters (CORRECTOS)
?status=confirmed              # pending, confirmed, cancelled, completed, no_show
?fecha_inicio=2026-01-31       # Filtrar desde fecha
?fecha_fin=2026-02-28          # Filtrar hasta fecha
?page=1
?page_size=20

# ⚠️ INCORRECTO
?status=confirmed              # ❌ NO USAR /by_status/confirmed/
```

### Obtener Detalle de Cita
```bash
GET /api/v1/appointments/{id}/

# Response
{
  "status": "success",
  "data": {
    "id": "apt_20260131_001",
    "fecha": "2026-01-31",
    "hora_inicio": "10:00:00",
    "hora_fin": "10:30:00",
    "duracion_minutos": 30,
    "status": "confirmed",
    "tipo": {
      "id": "consulta_general",
      "nombre": "Consulta General",
      "categoria": "medica"
    },
    "participantes": [
      {
        "id": "dr_juan_perez",
        "nombre": "Dr. Juan Pérez",
        "rol": "prestador"
      }
    ],
    "usuario_id": "user_001",
    "prompt_original": "cita mañana 10am con Dr. Pérez",
    "notas": {
      "cliente": "Primera consulta",
      "interna": "Paciente nuevo"
    },
    "created_at": "2026-01-30T15:14:55.933887Z",
    "updated_at": "2026-01-30T15:14:55.933897Z"
  }
}
```

### Crear Cita (Con IA)
```bash
POST /api/v1/appointments/

# Request
{
  "prompt": "cita con Dr. Pérez mañana a las 10am",
  "user_timezone": "America/Mexico_City"
}

# Response (201 - Created)
{
  "status": "success",
  "data": { /* details */ },
  "message": "Appointment created successfully"
}

# Response (409 - Conflict)
{
  "status": "error",
  "code": "CONFLICT",
  "message": "No disponibilidad en el horario solicitado",
  "suggestions": [
    {
      "fecha": "2026-02-01",
      "hora_inicio": "14:00",
      "confidence": 0.95
    }
  ]
}
```

### Actualizar Cita
```bash
PUT /api/v1/appointments/{id}/         # Actualización completa
PATCH /api/v1/appointments/{id}/       # Actualización parcial

# Request
{
  "status": "confirmed",
  "notas": {
    "cliente": "Actualización",
    "interna": "Nota interna"
  }
}
```

### Reprogramar Cita
```bash
POST /api/v1/appointments/{id}/reschedule/

# Request
{
  "fecha": "2026-02-01",
  "hora_inicio": "15:00",
  "hora_fin": "15:30"
}

# Response
{
  "status": "success",
  "data": { /* updated appointment */ },
  "message": "Appointment rescheduled successfully"
}
```

### Verificar Disponibilidad para Reprogramar
```bash
GET /api/v1/appointments/{id}/availability/?dias_adelante=14

# Response
{
  "status": "success",
  "data": {
    "appointment_id": "apt_20260131_001",
    "available_slots": [
      {
        "fecha": "2026-02-01",
        "hora_inicio": "09:00",
        "hora_fin": "10:00",
        "disponible": true
      }
    ]
  }
}
```

### Cancelar Cita
```bash
DELETE /api/v1/appointments/{id}/

# Response: 204 No Content
```

---

## 🏥 ENDPOINTS DE SERVICIOS

### Listar Servicios
```bash
GET /api/v1/services/

# Query Parameters
?categoria=medica
?activo=true
?buscar=general
?page=1
?page_size=20

# Response
{
  "count": 4,
  "results": [
    {
      "id": "consulta_general",
      "nombre": "Consulta General",
      "categoria": "medica",
      "descripcion": "Consulta médica general",
      "duracion_minutos": 30,
      "activo": true,
      "created_at": "2026-01-30T09:14:55.218891Z",
      "updated_at": "2026-01-30T09:14:55.218903Z"
    }
  ]
}
```

### Obtener Detalle de Servicio
```bash
GET /api/v1/services/{id}/
```

### Crear Servicio
```bash
POST /api/v1/services/

# Request
{
  "id": "consulta_nueva",
  "nombre": "Nueva Consulta",
  "categoria": "medica",
  "descripcion": "Descripción del servicio",
  "duracion_minutos": 45
}
```

### Actualizar Servicio
```bash
PUT /api/v1/services/{id}/         # Completa
PATCH /api/v1/services/{id}/       # Parcial
```

### Eliminar Servicio
```bash
DELETE /api/v1/services/{id}/
```

---

## 📍 ENDPOINTS DE DISPONIBILIDAD

### Verificar Disponibilidad
```bash
POST /api/v1/availability/check/

# Request
{
  "contacto_id": "dr_juan_perez",
  "servicio_id": "consulta_general",
  "fecha": "2026-02-10",
  "hora_inicio": "14:00",
  "hora_fin": "15:00"
}

# Response
{
  "status": "success",
  "data": {
    "disponible": true,
    "conflictos": [],
    "slots_disponibles": [...]
  }
}
```

### Obtener Sugerencias de Horarios
```bash
POST /api/v1/availability/suggest/

# Request
{
  "contacto_id": "dr_juan_perez",
  "servicio_id": "consulta_general",
  "fecha_preferida": "2026-02-10",
  "dias_adelante": 7,
  "duracion_minutos": 30
}

# Response
{
  "status": "success",
  "data": {
    "slots_sugeridos": [
      {
        "fecha": "2026-02-10",
        "hora_inicio": "09:00",
        "hora_fin": "09:30",
        "confianza": 0.95
      }
    ]
  }
}
```

### Obtener Horario de Contacto
```bash
GET /api/v1/availability/schedule/{contacto_id}/

# Response
{
  "status": "success",
  "data": {
    "contacto_id": "dr_juan_perez",
    "nombre": "Dr. Juan Pérez",
    "tipo": "prestador",
    "ubicaciones": [
      {
        "id": "loc_consultorio_1",
        "nombre": "Consultorio 1",
        "horarios": [...]
      }
    ]
  }
}
```

---

## 🔍 ENDPOINTS DE TRAZAS

### Listar Trazas
```bash
GET /api/v1/traces/

# Query Parameters
?status=success              # success, error, conflict
?user_id=user_123
?page=1

# Response
{
  "count": 4,
  "results": [
    {
      "trace_id": "trace_20260128_020003_595478bc",
      "timestamp": "2026-01-28T02:00:03.057987",
      "user_id": "test_user",
      "final_status": "success",
      "total_duration_ms": 750,
      "num_agents": 6
    }
  ]
}
```

### Obtener Detalle de Traza
```bash
GET /api/v1/traces/{id}/
```

### Obtener Decisiones de Agentes
```bash
GET /api/v1/traces/{id}/agents/

# Response
{
  "status": "success",
  "trace_id": "trace_123",
  "agents": [
    {
      "agent": "ParsingAgent",
      "status": "success",
      "duration_ms": 150,
      "confidence": 0.98,
      "output": {...}
    },
    {
      "agent": "TemporalReasoningAgent",
      "status": "success",
      "duration_ms": 200,
      "confidence": 0.95,
      "output": {...}
    }
  ]
}
```

### Obtener Métricas de Traza
```bash
GET /api/v1/traces/{id}/metrics/

# Response
{
  "status": "success",
  "trace_id": "trace_123",
  "total_duration_ms": 750,
  "agents": [
    {
      "agent": "ParsingAgent",
      "duration_ms": 150,
      "status": "success"
    }
  ]
}
```

### Filtrar Trazas por Status
```bash
GET /api/v1/traces/by_status/?status=success

# ✅ CORRECTO - Usa query parameter
# ❌ INCORRECTO - /by_status/success/
```

### Filtrar Trazas por Usuario
```bash
GET /api/v1/traces/by_user/?user_id=user_123

# ✅ CORRECTO - Usa query parameter
```

---

## 🔐 AUTENTICACIÓN

Todos los endpoints (excepto `/health/` y `/token-auth/`) requieren token:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" http://localhost:9001/api/v1/contacts/
```

---

## 📊 TABLA DE REFERENCIA RÁPIDA

| Recurso | GET | POST | PUT | PATCH | DELETE |
|---------|-----|------|-----|-------|--------|
| `/contacts/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/contacts/{id}/` | ✅ | - | ✅ | ✅ | ✅ |
| `/contacts/{id}/availability/` | - | ✅ | - | - | - |
| `/contacts/{id}/appointments/` | ✅ | - | - | - | - |
| `/appointments/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/appointments/{id}/` | ✅ | - | ✅ | ✅ | ✅ |
| `/appointments/{id}/reschedule/` | - | ✅ | - | - | - |
| `/appointments/{id}/availability/` | ✅ | - | - | - | - |
| `/services/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/services/{id}/` | ✅ | - | ✅ | ✅ | ✅ |
| `/availability/check/` | - | ✅ | - | - | - |
| `/availability/suggest/` | - | ✅ | - | - | - |
| `/availability/schedule/{id}/` | ✅ | - | - | - | - |
| `/traces/` | ✅ | - | - | - | - |
| `/traces/{id}/` | ✅ | - | - | - | - |
| `/traces/{id}/agents/` | ✅ | - | - | - | - |
| `/traces/{id}/metrics/` | ✅ | - | - | - | - |

---

## ⚠️ ERRORES COMUNES

### 1. Endpoint no encontrado (404)
```
GET /api/v1/appointments/by_status/confirmed/  ❌ INCORRECTO

# Usar en su lugar:
GET /api/v1/appointments/?status=confirmed     ✅ CORRECTO
```

### 2. Sin autenticación (401)
```json
{
  "status": "error",
  "code": "UNAUTHORIZED",
  "message": "No autorizado. Se requiere autenticación."
}

# Solución: Incluir token en header
-H "Authorization: Token YOUR_TOKEN"
```

### 3. Conflicto de disponibilidad (409)
```json
{
  "status": "error",
  "code": "CONFLICT",
  "message": "No disponibilidad en el horario solicitado",
  "suggestions": [...]
}

# Solución: Usar slots sugeridos o verificar con /availability/
```

### 4. Validación fallida (400)
```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Datos inválidos",
  "details": {...}
}

# Solución: Revisar formato del request
```

---

## 🧪 Ejemplos de Uso Completo

### Crear Cita desde Cero
```bash
# 1. Obtener token
TOKEN=$(curl -s -X POST http://localhost:9001/api/v1/token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123456"}' \
  | jq -r '.token')

# 2. Crear cita con IA
curl -X POST http://localhost:9001/api/v1/appointments/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Agendar cita con Dr. Pérez mañana a las 10am",
    "user_timezone": "America/Mexico_City"
  }' | jq .

# 3. Ver trazas de decisión
TRACE_ID="<trace_id_from_response>"
curl http://localhost:9001/api/v1/traces/$TRACE_ID/agents/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### Listar Citas Confirmadas
```bash
curl "http://localhost:9001/api/v1/appointments/?status=confirmed" \
  -H "Authorization: Token $TOKEN" | jq .
```

### Reprogramar Cita
```bash
curl -X POST http://localhost:9001/api/v1/appointments/apt_20260131_001/reschedule/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2026-02-01",
    "hora_inicio": "15:00",
    "hora_fin": "15:30"
  }' | jq .
```

---

## 📚 Referencias Adicionales

- [Database Migration](./DATABASE_MIGRATION.md) - Detalles de modelos y migraciones
- [Setup Local](./SETUP_LOCAL.md) - Guía de instalación local
- Swagger UI: http://localhost:9001/docs/swagger/
- ReDoc: http://localhost:9001/docs/redoc/

---

**Última actualización**: 2026-01-30
**Versión API**: 0.1.0
**Status**: ✅ Completamente Implementada
