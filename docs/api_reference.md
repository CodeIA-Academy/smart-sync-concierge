# Referencia de API - Smart-Sync Concierge

## Base URL

```
Producción: https://api.smartsync.example.com
Desarrollo: http://localhost:8000
```

## Versionamiento

La API está versionada por URL: `/api/v1/`

## Autenticación

```
Authorization: Bearer {token}
```

## Respuestas Estándar

### Éxito (200-299)

```json
{
  "status": "success",
  "data": {...},
  "_links": {
    "self": "/api/v1/resource/1/"
  }
}
```

### Error (400-599)

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Descripción del error",
  "details": {...}
}
```

---

## Endpoints de Citas

### Crear Cita desde Prompt

`POST /api/v1/appointments/`

Convierte lenguaje natural en una cita estructurada.

**Request Body:**

```json
{
  "prompt": "cita mañana 10am con Dr. Pérez",
  "opciones": {
    "zona_horaria": "America/Mexico_City",
    "idioma": "es",
    "generar_alternativas": true
  }
}
```

**Response Exitoso (201 Created):**

```json
{
  "status": "confirmed",
  "appointment": {
    "id": "apt_20260123_abc123",
    "fecha": "2026-01-23",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "duracion_minutos": 60,
    "estado": "confirmed",
    "tipo": {
      "id": "consulta_general",
      "nombre": "Consulta General"
    },
    "participantes": [
      {
        "id": "contact_dr_perez",
        "nombre": "Dr. Juan Pérez",
        "rol": "prestador"
      }
    ],
    "prompt_original": "cita mañana 10am con Dr. Pérez"
  },
  "message": "Cita confirmada exitosamente",
  "_links": {
    "self": "/api/v1/appointments/apt_20260123_abc123/",
    "cancel": "/api/v1/appointments/apt_20260123_abc123/cancel/",
    "reschedule": "/api/v1/appointments/apt_20260123_abc123/reschedule/"
  }
}
```

**Response con Conflicto (409 Conflict):**

```json
{
  "status": "conflict",
  "reason": "El Dr. Pérez ya tiene cita a esa hora",
  "conflicting_appointments": [
    {
      "id": "apt_20260123_xyz789",
      "fecha": "2026-01-23",
      "hora_inicio": "10:00",
      "hora_fin": "11:00"
    }
  ],
  "suggestions": [
    {
      "fecha": "2026-01-23",
      "hora": "11:00",
      "motivo": "Disponible después de cita anterior",
      "prioridad": 1
    },
    {
      "fecha": "2026-01-24",
      "hora": "10:00",
      "motivo": "Disponible mañana mismo día",
      "prioridad": 2
    }
  ],
  "_links": {
    "create_with_suggestion": "/api/v1/appointments/?suggestion=0"
  }
}
```

**Error de Validación (400 Bad Request):**

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "No se pudo procesar el prompt",
  "details": {
    "contact_not_found": "Dr. Pérez",
    "similar_contacts": ["Dr. Pedro Pérez", "Dra. María Pérez"],
    "suggestion": "Por favor especifica el contacto completo"
  }
}
```

**Información Insuficiente (400 Bad Request):**

```json
{
  "status": "error",
  "code": "INSUFFICIENT_INFO",
  "message": "Información insuficiente para crear la cita",
  "details": {
    "missing_fields": ["fecha", "hora"],
    "suggestion": "Por favor especifica fecha y hora. Ejemplo: 'cita mañana 10am con Dr. Pérez'"
  }
}
```

---

### Listar Citas

`GET /api/v1/appointments/`

Obtiene lista de citas con filtros opcionales.

**Query Parameters:**

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `fecha` | string | Filtrar por fecha específica | `2026-01-23` |
| `fecha_desde` | string | Fecha inicio del rango | `2026-01-01` |
| `fecha_hasta` | string | Fecha fin del rango | `2026-01-31` |
| `contacto` | string | Filtrar por ID de contacto | `contact_dr_perez` |
| `estado` | string | Filtrar por estado | `confirmed` |
| `page` | integer | Número de página | `1` |
| `page_size` | integer | Tamaño de página (max 100) | `20` |

**Response (200 OK):**

```json
{
  "count": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "appointments": [
    {
      "id": "apt_20260123_abc123",
      "fecha": "2026-01-23",
      "hora_inicio": "10:00",
      "hora_fin": "11:00",
      "estado": "confirmed",
      "participantes": ["Dr. Pérez"],
      "tipo": "consulta_general"
    }
  ],
  "_links": {
    "self": "/api/v1/appointments/?page=1",
    "next": "/api/v1/appointments/?page=2",
    "prev": null
  }
}
```

---

### Obtener Cita Específica

`GET /api/v1/appointments/{id}/`

Obtiene detalles de una cita.

**Response (200 OK):**

```json
{
  "id": "apt_20260123_abc123",
  "status": "confirmed",
  "created_at": "2026-01-22T15:30:00Z",
  "updated_at": "2026-01-22T15:30:00Z",
  "prompt_original": "cita mañana 10am con Dr. Pérez",
  "fecha": "2026-01-23",
  "hora_inicio": "10:00",
  "hora_fin": "11:00",
  "duracion_minutos": 60,
  "zona_horaria": "America/Mexico_City",
  "tipo": {
    "id": "consulta_general",
    "nombre": "Consulta General",
    "categoria": "medica"
  },
  "participantes": [
    {
      "id": "contact_dr_perez",
      "nombre": "Dr. Juan Pérez",
      "rol": "prestador",
      "contacto": {
        "email": "drperez@example.com",
        "telefono": "+525512345678"
      }
    }
  ],
  "ubicacion": {
    "tipo": "presencial",
    "direccion": "Consultorio 301"
  },
  "notas": {
    "cliente": "Primera consulta",
    "interna": "Referencia: website",
    "ia_confidence": 0.95
  },
  "metadata_validacion": {
    "contacto_validado": true,
    "servicio_validado": true,
    "horario_validado": true,
    "conflictos_verificados": true,
    "conflictos_encontrados": 0
  }
}
```

---

### Actualizar Cita

`PUT /api/v1/appointments/{id}/`

Actualiza una cita existente.

**Request Body:**

```json
{
  "fecha": "2026-01-24",
  "hora_inicio": "11:00",
  "notas": {
    "cliente": "Cita reprogramada"
  }
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "appointment": {...},
  "message": "Cita actualizada exitosamente"
}
```

---

### Cancelar Cita

`POST /api/v1/appointments/{id}/cancel/`

Cancela una cita existente.

**Request Body (opcional):**

```json
{
  "razon": "El paciente no podrá asistir",
  "notificar": true
}
```

**Response (200 OK):**

```json
{
  "status": "cancelled",
  "appointment": {
    "id": "apt_20260123_abc123",
    "estado": "cancelled",
    "cancelled_at": "2026-01-22T16:00:00Z"
  },
  "message": "Cita cancelada exitosamente"
}
```

---

### Reprogramar Cita

`POST /api/v1/appointments/{id}/reschedule/`

Reprograma una cita a nueva fecha/hora.

**Request Body:**

```json
{
  "prompt": "reprogramar para el viernes a las 3pm",
  "opciones": {
    "verificar_disponibilidad": true,
    "generar_alternativas": true
  }
}
```

O con datos directos:

```json
{
  "nueva_fecha": "2026-01-24",
  "nueva_hora": "15:00",
  "razon": "Solicitud del paciente"
}
```

**Response Exitoso (200 OK):**

```json
{
  "status": "rescheduled",
  "appointment": {
    "id": "apt_20260123_abc123",
    "fecha": "2026-01-24",
    "hora_inicio": "15:00",
    "hora_fin": "16:00",
    "estado": "confirmed"
  },
  "message": "Cita reprogramada exitosamente"
}
```

**Response con Conflicto (409 Conflict):**

```json
{
  "status": "conflict",
  "suggestions": [
    {
      "fecha": "2026-01-24",
      "hora": "14:00",
      "motivo": "Horario disponible"
    },
    {
      "fecha": "2026-01-25",
      "hora": "15:00",
      "motivo": "Mismo día siguiente"
    }
  ]
}
```

---

## Endpoints de Disponibilidad

### Consultar Disponibilidad General

`GET /api/v1/availability/`

Obtiene disponibilidad general del sistema.

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `fecha` | string | Fecha a consultar (YYYY-MM-DD) |
| `contacto` | string | ID del contacto (opcional) |

**Response (200 OK):**

```json
{
  "fecha": "2026-01-23",
  "horario_operacion": {
    "inicio": "09:00",
    "fin": "18:00",
    "pausa": "12:00-14:00"
  },
  "slots_ocupados": [
    {
      "inicio": "10:00",
      "fin": "11:00",
      "cita_id": "apt_20260123_xyz789"
    }
  ],
  "slots_disponibles": 8,
  "total_slots": 9
}
```

---

### Obtener Slots Disponibles

`GET /api/v1/availability/slots/`

Obtiene lista de horarios disponibles.

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `fecha` | string | Fecha a consultar (requerido) |
| `contacto` | string | ID del contacto (opcional) |
| `servicio` | string | Tipo de servicio (opcional) |

**Response (200 OK):**

```json
{
  "fecha": "2026-01-23",
  "contacto": "Dr. Pérez",
  "servicio": "consulta_general",
  "slots": [
    {
      "inicio": "09:00",
      "fin": "10:00",
      "disponible": true
    },
    {
      "inicio": "10:00",
      "fin": "11:00",
      "disponible": false,
      "motivo": "Cita existente"
    },
    {
      "inicio": "11:00",
      "fin": "12:00",
      "disponible": true
    },
    {
      "inicio": "14:00",
      "fin": "15:00",
      "disponible": true
    }
  ],
  "resumen": {
    "total_slots": 8,
    "slots_disponibles": 6,
    "primer_disponible": "09:00",
    "ultimo_disponible": "17:00"
  }
}
```

---

## Endpoints de Contactos

### Listar Contactos

`GET /api/v1/contacts/`

Obtiene lista de contactos.

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `tipo` | string | Filtrar por tipo (prestador/cliente) |
| `activo` | boolean | Filtrar por estado activo |
| `search` | string | Búsqueda por nombre |

**Response (200 OK):**

```json
{
  "count": 5,
  "contacts": [
    {
      "id": "contact_dr_perez",
      "tipo": "prestador",
      "activo": true,
      "datos_personales": {
        "nombre": "Dr. Juan Pérez",
        "titulo": "Médico General",
        "email": "drperez@example.com",
        "telefono": "+525512345678"
      },
      "especialidades": ["consulta_general", "pediatria"]
    }
  ]
}
```

---

### Crear Contacto

`POST /api/v1/contacts/`

Crea un nuevo contacto.

**Request Body:**

```json
{
  "tipo": "prestador",
  "datos_personales": {
    "nombre": "Dra. María García",
    "titulo": "Médico Especialista",
    "email": "dra.garcia@example.com",
    "telefono": "+525598765432"
  },
  "especialidades": ["cardiologia"],
  "disponibilidad": {
    "horario_laboral": {
      "lunes": { "inicio": "09:00", "fin": "18:00" },
      "martes": { "inicio": "09:00", "fin": "18:00" }
    }
  }
}
```

**Response (201 Created):**

```json
{
  "id": "contact_dra_garcia",
  "status": "created",
  "contact": {...}
}
```

---

### Obtener Contacto

`GET /api/v1/contacts/{id}/`

Obtiene detalles de un contacto.

**Response (200 OK):**

```json
{
  "id": "contact_dr_perez",
  "tipo": "prestador",
  "activo": true,
  "created_at": "2026-01-22T10:00:00Z",
  "datos_personales": {
    "nombre": "Dr. Juan Pérez",
    "titulo": "Médico General",
    "email": "drperez@example.com",
    "telefono": "+525512345678",
    "idioma": "es"
  },
  "disponibilidad": {
    "horario_laboral": {
      "lunes": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
      "martes": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" }
    },
    "excepciones": []
  },
  "especialidades": ["consulta_general", "pediatria"],
  "duraciones_predeterminadas": {
    "consulta_general": 60,
    "pediatria": 45
  }
}
```

---

### Disponibilidad del Contacto

`GET /api/v1/contacts/{id}/availability/`

Obtiene configuración de disponibilidad de un contacto.

**Response (200 OK):**

```json
{
  "contacto_id": "contact_dr_perez",
  "contacto_nombre": "Dr. Juan Pérez",
  "horario_laboral": {
    "lunes": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
    "martes": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
    "miercoles": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
    "jueves": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
    "viernes": { "inicio": "09:00", "fin": "15:00", "pausa": null },
    "sabado": { "inicio": null, "fin": null, "pausa": null },
    "domingo": { "inicio": null, "fin": null, "pausa": null }
  },
  "excepciones": [
    {
      "fecha": "2026-01-25",
      "motivo": "Capacitación",
      "disponible": false
    }
  ],
  "preferencias": {
    "tiempo_entre_citas": 15,
    "anticipacion_reserva": 24,
    "max_citas_dia": 12
  }
}
```

---

## Endpoints de Servicios

### Listar Servicios

`GET /api/v1/services/`

Obtiene catálogo de servicios.

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `categoria` | string | Filtrar por categoría |
| `activo` | boolean | Solo servicios activos |

**Response (200 OK):**

```json
{
  "services": [
    {
      "id": "consulta_general",
      "nombre": "Consulta General",
      "categoria": "medica",
      "descripcion": "Consulta médica de rutina",
      "duracion_default": 60,
      "activo": true,
      "requiere_contacto": true
    },
    {
      "id": "consulta_seguimiento",
      "nombre": "Consulta de Seguimiento",
      "categoria": "medica",
      "descripcion": "Seguimiento de tratamiento",
      "duracion_default": 30,
      "activo": true,
      "requiere_contacto": true
    }
  ]
}
```

---

### Crear Servicio

`POST /api/v1/services/`

Crea un nuevo servicio.

**Request Body:**

```json
{
  "nombre": "Consulta Cardiología",
  "categoria": "medica",
  "descripcion": "Consulta especializada en cardiología",
  "duracion_default": 90,
  "activo": true,
  "requiere_contacto": true,
  "sinonimos_ia": ["cardiologia", "corazon", "consulta cardiovascular"]
}
```

**Response (201 Created):**

```json
{
  "id": "consulta_cardiologia",
  "status": "created",
  "service": {...}
}
```

---

## Códigos de Error

| Código | Descripción |
|-------|-------------|
| `VALIDATION_ERROR` | Error de validación de datos |
| `INSUFFICIENT_INFO` | Información insuficiente en el prompt |
| `CONTACT_NOT_FOUND` | Contacto no encontrado |
| `SERVICE_NOT_FOUND` | Servicio no encontrado |
| `CONFLICT` | Conflicto de horario |
| `OUTSIDE_BUSINESS_HOURS` | Fuera del horario laboral |
| `HOLIDAY` | Día festivo |
| `TOO_LATE` | Reserva muy tardía |
| `TOO_SOON` | Reserva con demasiada anticipación |
| `APPOINTMENT_NOT_FOUND` | Cita no encontrada |
| `APPOINTMENT_ALREADY_CANCELLED` | Cita ya cancelada |
| `RATE_LIMIT_EXCEEDED` | Límite de peticiones excedido |

## Rate Limiting

- **Límite**: 60 peticiones por minuto por IP
- **Headers response**:
  ```
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1706544000
  ```

## Paginación

Todas las endpoints de listado soportan paginación:

```json
{
  "count": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "_links": {
    "self": "?page=1",
    "next": "?page=2",
    "prev": null,
    "first": "?page=1",
    "last": "?page=8"
  }
}
```

---

*Última actualización: 2026-01-22*
*Versión: 0.1.0*
