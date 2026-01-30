# Resumen de Endpoints - Smart-Sync Concierge API v1

**Base URL:** `https://smartsync.codeia.dev/api/v1/`

**Autenticación:** `Authorization: Token {token}` (obtener en `/token-auth/`)

---

## 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/token-auth/` | Obtener token con username y password |
| `GET` | `/health/` | Verificar estado de la API |

---

## 📅 Citas (Appointments)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/appointments/` | Crear cita (desde prompt o datos directos) |
| `GET` | `/appointments/` | Listar citas (con filtros: fecha, estado, contacto) |
| `GET` | `/appointments/{id}/` | Obtener detalles de cita |
| `PUT` | `/appointments/{id}/` | Actualizar cita |
| `POST` | `/appointments/{id}/cancel/` | Cancelar cita |
| `POST` | `/appointments/{id}/reschedule/` | Reprogramar cita |
| `GET` | `/appointments/by_status/{status}/` | Listar citas por estado |
| `GET` | `/appointments/by_user/{user_id}/` | Listar citas de un usuario |

---

## 👥 Contactos (Doctors/Staff/Resources)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/contacts/` | Crear contacto (prestador/cliente/recurso) |
| `GET` | `/contacts/` | Listar contactos (filtrar por tipo) |
| `GET` | `/contacts/{id}/` | Obtener detalles de contacto |
| `PUT` | `/contacts/{id}/` | Actualizar contacto |
| `DELETE` | `/contacts/{id}/` | Eliminar contacto |
| `GET` | `/contacts/{id}/availability/` | Ver disponibilidad del contacto |

---

## 📋 Servicios (Services)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/services/` | Crear servicio médico |
| `GET` | `/services/` | Listar servicios (filtrar por categoría) |
| `GET` | `/services/{id}/` | Obtener detalles de servicio |
| `PUT` | `/services/{id}/` | Actualizar servicio |
| `DELETE` | `/services/{id}/` | Eliminar servicio |

---

## ⏰ Disponibilidad (Availability)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/availability/` | Consultar disponibilidad general por fecha |
| `GET` | `/availability/slots/` | Obtener lista de horarios disponibles |
| `GET` | `/availability/contacts/{contact_id}/` | Ver disponibilidad de un contacto |

---

## 📊 Trazas/Historial (Traces)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/traces/` | Listar eventos/trazas del sistema |
| `GET` | `/traces/{id}/` | Obtener detalle de una traza |
| `GET` | `/traces/by_status/{status}/` | Filtrar trazas por estado |
| `GET` | `/traces/by_user/{user_id}/` | Trazas de un usuario específico |
| `GET` | `/traces/agents/` | Listar actividades de agentes IA |
| `GET` | `/traces/metrics/` | Obtener métricas del sistema |

---

## 📖 Documentación Interactiva

- **Swagger UI:** `https://smartsync.codeia.dev/docs/swagger/`
- **ReDoc:** `https://smartsync.codeia.dev/docs/redoc/`
- **OpenAPI Schema:** `https://smartsync.codeia.dev/api/v1/docs/schema/`

---

## ⚡ Parámetros Comunes

**Query Parameters:**
- `page` - Número de página (default: 1)
- `page_size` - Elementos por página (default: 20, max: 100)
- `search` - Búsqueda por nombre/contenido
- `fecha` - Filtrar por fecha (YYYY-MM-DD)
- `estado` - Filtrar por estado
- `activo` - Filtrar por estado activo (true/false)

**Rate Limit:** 60 req/min por IP

**Respuesta Exitosa:**
```json
{
  "status": "success",
  "data": {...}
}
```

**Respuesta Error:**
```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Descripción del error"
}
```

---

*Última actualización: 2026-01-29 | Versión API: 0.1.0*
