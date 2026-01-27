# Smart-Sync Concierge API Contracts

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-green)
![Status](https://img.shields.io/badge/status-ready--for--implementation-brightgreen)

Especificaciones OpenAPI 3.0.3 completas para la API de Smart-Sync Concierge - Sistema de gestión de citas agentico con IA.

## 📋 Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [Contratos API](#contratos-api)
3. [Esquemas de Datos](#esquemas-de-datos)
4. [Visualización Interactiva](#visualización-interactiva)
5. [Autenticación](#autenticación)
6. [Rate Limiting](#rate-limiting)
7. [Códigos de Error](#códigos-de-error)
8. [Ejemplos de Uso](#ejemplos-de-uso)

## 🚀 Inicio Rápido

### Especificación Maestra

La especificación completa se encuentra en:

📄 **[openapi.yaml](./openapi.yaml)** - Consolidación de todos los endpoints

### Ver API en Tiempo Real

Puedes visualizar la API interactivamente usando:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📚 Contratos API

### 1. Appointments API (`appointments.yaml`)

**Base Path**: `/api/v1/appointments/`

Gestión completa del ciclo de vida de citas con procesamiento de lenguaje natural.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| **POST** | `/appointments/` | Crear cita desde prompt en lenguaje natural |
| **GET** | `/appointments/` | Listar citas con filtros y paginación |
| **GET** | `/appointments/{id}/` | Obtener detalle de cita |
| **PUT** | `/appointments/{id}/` | Actualizar cita |
| **DELETE** | `/appointments/{id}/` | Cancelar cita (soft delete) |
| **POST** | `/appointments/{id}/reschedule/` | Reprogramar cita |

**Características**:
- ✅ Creación desde prompt en lenguaje natural
- ✅ Detección automática de conflictos
- ✅ Generación de sugerencias cuando hay conflictos
- ✅ Validación geo-temporal multi-zona horaria
- ✅ Trazabilidad completa con DecisionTrace
- ✅ Ejemplos exhaustivos

👉 **Ver especificación completa**: [appointments.yaml](./appointments.yaml)

### 2. Contacts API (`contacts.yaml`)

**Base Path**: `/api/v1/contacts/`

Gestión de doctores, staff administrativo y recursos físicos.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| **GET** | `/contacts/` | Listar contactos con filtros |
| **POST** | `/contacts/` | Crear contacto (doctor, staff o recurso) |
| **GET** | `/contacts/{id}/` | Obtener detalle de contacto |
| **PUT** | `/contacts/{id}/` | Actualizar contacto |
| **DELETE** | `/contacts/{id}/` | Desactivar contacto |
| **GET** | `/contacts/{id}/availability/` | Obtener horarios disponibles |
| **PUT** | `/contacts/{id}/availability/` | Actualizar horarios |
| **GET** | `/contacts/{id}/appointments/` | Obtener citas del contacto |

**Características**:
- ✅ Soporte para múltiples tipos de contacto
- ✅ Ubicaciones múltiples por contacto
- ✅ Horarios complejos por ubicación
- ✅ Metadatos específicos por tipo (licencia, especialidad, etc.)
- ✅ Soft delete con recuperación

👉 **Ver especificación completa**: [contacts.yaml](./contacts.yaml)

### 3. Services API (`services.yaml`)

**Base Path**: `/api/v1/services/`

Catálogo de servicios/tipos de cita disponibles.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| **GET** | `/services/` | Listar servicios con filtros |
| **POST** | `/services/` | Crear servicio |
| **GET** | `/services/{id}/` | Obtener detalle de servicio |
| **PUT** | `/services/{id}/` | Actualizar servicio |
| **DELETE** | `/services/{id}/` | Desactivar servicio |

**Características**:
- ✅ Categorización (médica, odontología, laboratorio, imagen, terapia, otra)
- ✅ Configuración flexible de duración
- ✅ Políticas de cancelación y reprogramación
- ✅ Requerimientos de equipamiento
- ✅ Configuración de recordatorios automáticos

👉 **Ver especificación completa**: [services.yaml](./services.yaml)

### 4. Availability API

**Base Path**: `/api/v1/availability/`

Consulta de disponibilidad sin crear citas.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| **GET** | `/availability/` | Consultar disponibilidad general |
| **GET** | `/availability/slots/` | Buscar slots específicos |

**Características**:
- ✅ Consulta rápida de horarios disponibles
- ✅ Búsqueda por fecha, hora y duración
- ✅ Retorna alternativas cuando no hay disponibilidad

👉 **Ver especificación**: [appointments.yaml](./appointments.yaml#tag/availability)

### 5. Agents API (Interna) (`agents.yaml`)

**Base Path**: `/api/v1/internal/`

API interna para testing, debugging y observabilidad.

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| **GET** | `/internal/agents/` | Listar agentes disponibles |
| **POST** | `/internal/agents/{name}/execute` | Ejecutar agente individual |
| **GET** | `/internal/agents/{name}/config` | Obtener configuración de agente |
| **PUT** | `/internal/agents/{name}/config` | Actualizar configuración |
| **POST** | `/internal/agents/pipeline/execute` | Ejecutar pipeline completo |
| **GET** | `/internal/traces/` | Listar traces de decisiones |
| **GET** | `/internal/traces/{id}/` | Obtener trace completo |
| **GET** | `/internal/metrics/agents` | Obtener métricas de agentes |

**Características**:
- ✅ Testing individual de agentes
- ✅ Debugging con verbose output
- ✅ Trazabilidad completa de decisiones
- ✅ Métricas de rendimiento por agente
- ✅ Solo acceso interno/admin

👉 **Ver especificación completa**: [agents.yaml](./agents.yaml)

## 📦 Esquemas de Datos

Los esquemas JSON que definen la estructura de datos se encuentran en:

### Entidades Principales

| Esquema | Descripción | Archivo |
|---------|------------|---------|
| **Appointment** | Cita con todas sus propiedades | [`/schemas/appointment.json`](../schemas/appointment.json) |
| **Contact** | Doctor, staff o recurso | [`/schemas/contact.json`](../schemas/contact.json) |
| **Service** | Tipo de servicio/cita | [`/schemas/service.json`](../schemas/service.json) |
| **DecisionTrace** | Trazabilidad de decisiones de agentes | [`/schemas/decision-trace.json`](../schemas/decision-trace.json) |
| **SharedContext** | Contexto compartido entre agentes | [`/schemas/shared-context.json`](../schemas/shared-context.json) |

## 🔍 Visualización Interactiva

### Swagger UI

Interfaz interactiva para probar los endpoints:

```bash
# En desarrollo local
http://localhost:8000/docs

# Cargar especificación externa
curl -X GET http://localhost:8000/docs?url=/api/openapi.yaml
```

### ReDoc

Documentación elegante y responsiva:

```bash
# En desarrollo local
http://localhost:8000/redoc

# Con especificación externa
curl -X GET http://localhost:8000/redoc?url=/api/openapi.yaml
```

### Postman

Importar la colección OpenAPI:

1. Abre Postman
2. Click en "Import"
3. Selecciona "Link" y pega: `http://localhost:8000/api/openapi.yaml`
4. Automáticamente cargará todos los endpoints

## 🔐 Autenticación

### Esquema: Bearer Token (JWT)

Todos los endpoints (excepto health checks) requieren autenticación.

```bash
# Header requerido
Authorization: Bearer <your-jwt-token>

# Ejemplo con curl
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     http://localhost:8000/api/v1/appointments/
```

### Obtener Token

```bash
# Hacer login (endpoint no documentado en MVP)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password"
  }'

# Respuesta
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## ⏱️ Rate Limiting

### Límites por IP

**60 peticiones por minuto**

### Headers de Respuesta

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1706544000
```

### Qué Hacer Cuando se Alcanza el Límite

1. El servidor retorna **HTTP 429** (Too Many Requests)
2. Espera hasta el timestamp en `X-RateLimit-Reset`
3. O implementa retry con backoff exponencial

```python
import time
import requests

def call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code == 429:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            wait_time = reset_time - int(time.time())
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

## ❌ Códigos de Error

### Respuesta de Error Estándar

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Descripción legible del error",
  "details": {
    "field": "valor_invalido"
  },
  "ambiguities": [
    {
      "field": "contacto",
      "message": "No se especificó qué doctor",
      "suggestions": ["Dr. Pérez", "Dr. García"]
    }
  ]
}
```

### HTTP Status Codes

| Código | Significado | Ejemplo |
|--------|------------|---------|
| **200** | OK - Operación exitosa | GET /appointments/ |
| **201** | Created - Recurso creado | POST /appointments/ |
| **204** | No Content - Eliminación exitosa | DELETE /appointments/1/ |
| **400** | Bad Request - Solicitud inválida | Prompt ambiguo |
| **401** | Unauthorized - No autenticado | Token faltante o inválido |
| **403** | Forbidden - No autorizado | Usuario sin permisos |
| **404** | Not Found - Recurso no encontrado | Cita inexistente |
| **409** | Conflict - Conflicto de horario | Cita con solapamiento + sugerencias |
| **422** | Unprocessable Entity - No se pudieron extraer entidades | Parsing fallido |
| **429** | Too Many Requests - Rate limit excedido | Más de 60 req/min |
| **500** | Internal Server Error - Error del servidor | Error no controlado |

### Códigos de Error Específicos

| Código | HTTP | Descripción |
|--------|------|-------------|
| `VALIDATION_ERROR` | 400 | Error de validación de datos |
| `INSUFFICIENT_INFO` | 400 | Información insuficiente en el prompt |
| `CONTACT_NOT_FOUND` | 404 | Contacto no encontrado |
| `SERVICE_NOT_FOUND` | 404 | Servicio no encontrado |
| `APPOINTMENT_NOT_FOUND` | 404 | Cita no encontrada |
| `CONFLICT` | 409 | Conflicto de horario detectado |
| `OUTSIDE_BUSINESS_HOURS` | 409 | Fuera del horario laboral |
| `HOLIDAY` | 409 | Día festivo |
| `TOO_LATE` | 409 | Reserva muy tardía |
| `TOO_SOON` | 409 | Reserva con demasiada anticipación |
| `PARSING_FAILED` | 422 | No se pudieron extraer entidades |
| `RATE_LIMIT_EXCEEDED` | 429 | Límite de peticiones excedido |

## 💡 Ejemplos de Uso

### Crear Cita (Exitosa)

```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City",
    "user_id": "user123"
  }'
```

**Respuesta (201 Created)**:
```json
{
  "status": "success",
  "data": {
    "id": "apt_20260124_abc123",
    "fecha": "2026-01-24",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "contacto": {
      "id": "contact_dr_perez",
      "nombre": "Dr. Pérez"
    },
    "estado": "confirmed"
  },
  "_links": {
    "self": "/api/v1/appointments/apt_20260124_abc123/"
  }
}
```

### Crear Cita (Conflicto con Sugerencias)

```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita hoy 3pm con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

**Respuesta (409 Conflict)**:
```json
{
  "status": "error",
  "code": "CONFLICT",
  "message": "El horario solicitado no está disponible",
  "suggestions": [
    {
      "fecha": "2026-01-23",
      "hora_inicio": "16:00",
      "confidence": 0.95,
      "reason": "Mismo día, siguiente slot disponible"
    },
    {
      "fecha": "2026-01-24",
      "hora_inicio": "15:00",
      "confidence": 0.85,
      "reason": "Día siguiente, misma hora"
    }
  ]
}
```

### Consultar Disponibilidad

```bash
curl -X GET "http://localhost:8000/api/v1/availability/?contacto_id=contact_dr_perez&dias=7" \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta (200 OK)**:
```json
{
  "contacto_id": "contact_dr_perez",
  "slots_disponibles": [
    {
      "fecha": "2026-01-23",
      "slots": [
        {
          "hora_inicio": "09:00",
          "hora_fin": "10:00",
          "disponible": true
        },
        {
          "hora_inicio": "11:00",
          "hora_fin": "12:00",
          "disponible": true
        }
      ]
    }
  ]
}
```

### Listar Citas con Filtros

```bash
curl -X GET "http://localhost:8000/api/v1/appointments/?fecha_inicio=2026-01-01&fecha_fin=2026-01-31&estado=confirmed&page=1&page_size=20" \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta (200 OK)**:
```json
{
  "count": 45,
  "next": "/api/v1/appointments/?page=2",
  "previous": null,
  "results": [
    {
      "id": "apt_20260123_abc123",
      "fecha": "2026-01-23",
      "hora_inicio": "10:00",
      "estado": "confirmed",
      "contacto": {
        "id": "contact_dr_perez",
        "nombre": "Dr. Pérez"
      }
    }
  ]
}
```

### Crear Contacto

```bash
curl -X POST http://localhost:8000/api/v1/contacts/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Dr. Juan Pérez",
    "tipo": "doctor",
    "especialidad": "Cardiología",
    "email": "juan.perez@clinica.example.com",
    "telefono": "+525512345678",
    "ubicaciones": [
      {
        "nombre": "Consultorio Principal",
        "direccion": "Av. Reforma 123, CDMX",
        "timezone": "America/Mexico_City",
        "horario": {
          "inicio": "09:00",
          "fin": "18:00",
          "dias_laborales": [1, 2, 3, 4, 5]
        }
      }
    ]
  }'
```

**Respuesta (201 Created)**:
```json
{
  "id": "contact_dr_perez",
  "nombre": "Dr. Juan Pérez",
  "tipo": "doctor",
  "especialidad": "Cardiología",
  "email": "juan.perez@clinica.example.com",
  "activo": true,
  "created_at": "2026-01-22T10:00:00Z"
}
```

## 📖 Documentación Adicional

- [Arquitectura del Sistema](../../architecture.md)
- [Decision Records (ADRs)](../../adr/)
- [Changelog](../../CHANGELOG.md)
- [Roadmap](../../ROADMAP.md)

## 🛠️ Herramientas Recomendadas

- **Postman**: Colección de endpoints con ejemplos
- **Swagger Editor**: Validación y edición de OpenAPI
- **Thunder Client**: Extensión de VS Code para testing
- **Bruno**: Cliente HTTP open-source
- **Insomnia**: Cliente REST con soporte OpenAPI

## 📝 Notas

- Todos los datetimes están en formato ISO 8601 con timezone
- Los IDs siguen patrones específicos: `apt_`, `contact_`, `service_`, `trc_`
- Los soft deletes marcan registros como inactivos sin eliminarlos
- Los datos de ejemplo usan información ficticia de México

## 🔗 Referencias

- [OpenAPI 3.0.3 Specification](https://spec.openapis.org/oas/v3.0.3)
- [JSON Schema Draft 7](https://json-schema.org/draft-07/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html#status.codes)
- [RFC 3339 - Date and Time](https://tools.ietf.org/html/rfc3339)

---

**Versión**: 0.1.0 | **Estado**: Ready for Implementation | **Última actualización**: 2026-01-22
