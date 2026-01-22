# Changelog - Smart-Sync Concierge

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Planeado
- Migración a base de datos PostgreSQL
- Implementación de sistema de notificaciones (email, SMS)
- Integración con calendarios externos (Google Calendar, Outlook)
- Panel de analytics y reportes
- API webhooks para integraciones de terceros
- Multi-tenant para múltiples negocios

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
*Versión actual: 0.1.0*
