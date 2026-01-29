# 🚀 Smart-Sync Concierge v0.2.0 - LISTO PARA EASYPANEL

**Estado:** Completamente configurado para producción
**Fecha:** 29 de Enero, 2026
**Última actualización:** Configuración de PostgreSQL y Docker completa

---

## ✅ COMPLETADO

### 1. Infraestructura Docker
- ✅ `Dockerfile` - Multi-stage build (builder + runtime)
- ✅ `docker-compose.yml` - PostgreSQL 15 + Django con health checks
- ✅ `docker-entrypoint.sh` - Inicialización automática (migrate, collectstatic, superuser)
- ✅ `.dockerignore` - Exclusiones optimizadas
- ✅ `Makefile` - Comandos de desarrollo

### 2. Configuración de Producción
- ✅ `config/settings/production.py` - PostgreSQL con dj-database-url
- ✅ `config/settings/base.py` - INSTALLED_APPS actualizado
- ✅ `requirements.txt` - Dependencias incluyen psycopg2, gunicorn, whitenoise, dj-database-url
- ✅ `.env.production.example` - Template completo con todas las variables

### 3. Modelos Django & Migraciones
- ✅ `apps/appointments/models.py` - Modelo Appointment
- ✅ `apps/contacts/models.py` - Modelo Contact
- ✅ `apps/services/models.py` - Modelo Service
- ✅ `apps/traces/models.py` - Modelo Trace
- ✅ Migraciones ejecutadas localmente (`migrate --run-syncdb`)

### 4. Script de Migración de Datos
- ✅ `data/migrate_to_db.py` - Migración JSON → PostgreSQL con --dry-run

### 5. Seguridad & Performance
- ✅ WhiteNoise configurado para static files
- ✅ IsAuthenticated permissions restauradas
- ✅ SSL/HTTPS configurado en production
- ✅ HSTS headers habilitados
- ✅ CORS configurado para tu dominio

---

## 📋 PASOS SIGUIENTES EN EASYPANEL

### 1. Crear App en EasyPanel
```
App Name: smartsync-concierge
Repository: https://github.com/CodeIA-Academy/smart-sync-concierge
Branch: main
Build Method: Dockerfile
Port: 9000
Domain: smartsync.codeia.dev
```

### 2. Configurar Variables de Entorno
En EasyPanel → Environment Variables, agregar:

```env
# CRÍTICO: Estos valores DEBEN ser especificados en EasyPanel
SECRET_KEY=django-insecure-YOUR-SECRET-KEY-HERE-CHANGE-THIS
DEBUG=False
ALLOWED_HOSTS=smartsync.codeia.dev,www.smartsync.codeia.dev
DJANGO_SETTINGS_MODULE=config.settings.production

# Base de datos - TU NEON CONNECTION STRING
DATABASE_URL=postgresql://neondb_owner:npg_pNMxGiXL0CZ5@ep-nameless-recipe-aga8q8eu-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# IA Configuration
QWEN_API_KEY=YOUR-API-KEY-HERE
QWEN_MODEL=qwen-2.5
QWEN_TEMPERATURA=0.3
QWEN_MAX_TOKENS=500

# Security
ENABLE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# CORS
CORS_ALLOWED_ORIGINS=https://smartsync.codeia.dev

# Timezone
TIMEZONE=America/Mexico_City
LANGUAGE=es

# Superuser (Crear en primer despliegue)
CREATE_SUPERUSER=true
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@smartsync.dev
DJANGO_SUPERUSER_PASSWORD=YOUR-STRONG-PASSWORD-HERE
```

### 3. Desplegar
- Click en **Deploy** en EasyPanel
- EasyPanel automáticamente:
  1. Clonará el repositorio
  2. Construirá la imagen Docker
  3. Ejecutará `docker-entrypoint.sh` que:
     - Esperará a PostgreSQL (Neon)
     - Ejecutará migraciones Django
     - Recolectará archivos estáticos
     - Creará superuser
  4. Iniciará Gunicorn en puerto 9000
  5. Configurará SSL automáticamente

### 4. Verificar Post-Despliegue
```bash
# Health check
curl https://smartsync.codeia.dev/api/v1/health/
# Esperado: {"status": "healthy", "message": "...", "version": "0.2.0"}

# Admin panel
open https://smartsync.codeia.dev/admin/
# Login con las credenciales del superuser

# API Root
curl https://smartsync.codeia.dev/api/v1/

# Endpoints
curl https://smartsync.codeia.dev/api/v1/contacts/
curl https://smartsync.codeia.dev/api/v1/services/
curl https://smartsync.codeia.dev/api/v1/appointments/
```

---

## 🔧 TESTING LOCAL (OPCIONAL)

Antes de desplegar a EasyPanel, puedes probar localmente:

```bash
# Build imagen Docker
make build

# Iniciar servicios (PostgreSQL local + Django)
make up

# Esperar 15 segundos, luego:

# Health check
make healthcheck

# Ver logs
make logs

# Ejecutar tests
make test

# Detener
make down
```

---

## 📊 CHECKLIST FINAL ANTES DE DESPLEGAR

- [ ] Generaste un SECRET_KEY único (no uses el del template)
- [ ] DATABASE_URL es correcto (tu Neon connection string)
- [ ] QWEN_API_KEY está configurado
- [ ] CORS_ALLOWED_ORIGINS incluye tu dominio
- [ ] CREATE_SUPERUSER=true en EasyPanel
- [ ] DJANGO_SUPERUSER_PASSWORD es una contraseña segura
- [ ] DJANGO_SETTINGS_MODULE=config.settings.production
- [ ] Todos los archivos Docker existen en el repo (git push exitoso)

---

## 🚀 URLS POST-DESPLIEGUE

| Recurso | URL |
|---------|-----|
| API Root | https://smartsync.codeia.dev/api/v1/ |
| Health | https://smartsync.codeia.dev/api/v1/health/ |
| Admin Panel | https://smartsync.codeia.dev/admin/ |

---

## 🆘 SI ALGO FALLA

### Error: "Dockerfile no encontrado"
- Verifica que los archivos Docker estén en el repo
- Ejecuta: `git push origin main`
- Intenta rebuild en EasyPanel

### Error: "relation does not exist"
- En EasyPanel, ve a Logs y busca el error específico
- Posible causa: migraciones no se ejecutaron
- EasyPanel ejecutará `docker-entrypoint.sh` automáticamente, que corre las migraciones

### Error: "could not connect to server"
- Verifica DATABASE_URL es correcta
- Comprueba que Neon está activo
- Prueba conexión localmente: `psql 'tu-database-url'`

### Error: "DisallowedHost"
- Verifica ALLOWED_HOSTS en variables de entorno
- Debe incluir: `smartsync.codeia.dev,www.smartsync.codeia.dev`

---

## 📦 MIGRACIÓN DE DATOS (OPCIONAL)

Si quieres migrar datos de JSON a PostgreSQL después del despliegue:

```bash
# Via EasyPanel shell o docker exec:
python data/migrate_to_db.py --dry-run   # Ver qué se migrará
python data/migrate_to_db.py              # Ejecutar migración
```

---

## 🔄 ROLLBACK (Si necesitas revertir)

En EasyPanel:
1. **Deployments** → Selecciona versión anterior
2. Click **Rollback**
3. Espera ~2 minutos

Tiempo de rollback total: < 5 minutos

---

## 📝 GIT LOG - Cambios realizados

```
commit 0d6639a - Update production settings for PostgreSQL and WhiteNoise
commit f7d9d90 - Add Docker infrastructure for EasyPanel deployment
```

---

**Próximo paso:** Vete a EasyPanel y crea la app con las variables de entorno especificadas arriba.

¿Tienes preguntas o necesitas ayuda con algo específico?
