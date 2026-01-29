# Changelog - Smart-Sync Concierge

Todos los cambios importantes de este proyecto están documentados en este archivo.

## [0.2.0] - 2026-01-29

### Agregado

#### Infraestructura Docker
- Dockerfile multi-stage optimizado (builder + runtime stages)
- docker-compose.yml para desarrollo local con PostgreSQL 15 Alpine
- docker-entrypoint.sh para inicialización automática (migrations, collectstatic, superuser)
- .dockerignore con exclusiones apropiadas
- Makefile con comandos de desarrollo (build, up, down, migrate, test, etc)

#### Migración a PostgreSQL
- Modelos Django ORM para 4 entidades:
  - `apps/appointments/models.py` - Citas con JSONField para datos complejos
  - `apps/contacts/models.py` - Contactos (doctores, staff, recursos)
  - `apps/services/models.py` - Servicios y catálogo
  - `apps/traces/models.py` - Trazas de decisiones IA
- Script de migración `data/migrate_to_db.py` para migrar JSON → PostgreSQL con modo --dry-run
- dj-database-url para configuración basada en DATABASE_URL

#### Configuración de Producción
- `config/settings/production.py` actualizado para PostgreSQL
- WhiteNoise middleware para servir static files en producción
- Restauradas permisos IsAuthenticated para endpoints API
- STATICFILES_STORAGE con compresión de archivos estáticos
- Variables de entorno `.env.production.example` completas

#### Documentación de Despliegue
- `DEPLOYMENT_READY.md` - Guía rápida para EasyPanel
- `DEPLOYMENT_EASYPANEL.md` - Guía completa de despliegue
- `FASE2_RESUMEN.md` - Resumen de avances de Phase 2

### Cambios

- `config/settings/base.py` - INSTALLED_APPS incluye apps.traces y apps.agents
- `requirements.txt` - Actualizadas dependencias:
  - psycopg2-binary==2.9.9 (PostgreSQL driver)
  - dj-database-url==2.2.0 (database URL parsing)
  - gunicorn==21.2.0 (production WSGI server)
  - whitenoise==6.6.0 (static file serving)

### Seguridad

- Permisos IsAuthenticated restaurados (endpoints requieren autenticación)
- SSL/HTTPS forzado en producción
- HSTS headers habilitados (31536000 segundos = 1 año)
- CORS configurado para dominio específico
- CSP headers implementados
- XFrame options seteadas a DENY

### Testing & Quality

- Health check endpoint implementado
- Docker health checks configurados para web y database
- Makefile con targets para test (pytest)
- Docker-compose setup para testing local

---

## [0.1.0] - 2026-01-22

### Agregado

#### Funcionalidad Core
- 6 agentes IA integrados (appointments, contacts, services, availability, traces, qwen)
- AppointmentViewSet con CUD completo
- Sistema de trazas para decisiones IA
- Almacenamiento en SQLite + JSON files

#### API
- DRF REST API con endpoints v1
- Health check endpoint
- Autenticación por Token
- CORS configurado

#### Documentación
- README.md con setup local
- POSTMAN_COLLECTION.json para testing

---

## Próximas Versiones Planeadas

### [0.3.0] - Monitoreo y Analytics
- Integration con Sentry para error tracking
- Logging centralizado
- Métricas de uso y performance
- Dashboard de monitoring

### [0.4.0] - Optimizaciones
- Caching con Redis
- Compresión de responses
- Rate limiting mejorado
- Índices de base de datos optimizados

### [0.5.0] - Escalabilidad
- Celery para tareas asincrónicas
- Message queue (RabbitMQ/Redis)
- Multi-worker deployment
- Load balancing

---

## Versionado

Este proyecto sigue [Semantic Versioning](https://semver.org/):
- MAJOR version (1.0.0) para cambios incompatibles
- MINOR version (0.1.0) para nuevas funcionalidades
- PATCH version (0.0.1) para bug fixes

---

## Despliegues

### v0.2.0
- **Estado:** Listo para producción en EasyPanel
- **Base de datos:** PostgreSQL (Neon)
- **Container:** Docker + Gunicorn
- **Fecha de despliegue:** 2026-01-29

### v0.1.0
- **Estado:** MVP completado
- **Base de datos:** SQLite + JSON files
- **Server:** Django development server
- **Fecha de despliegue:** 2026-01-22
