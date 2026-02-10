# Estrategia de Deployment - n8n Integration

**Estado:** Listo para despliegue a producción
**Enfoque:** Production-first (sin desarrollo local con ngrok)
**Fecha:** 2026-02-10

---

## 📊 Estado Actual

✅ **Implementación completada:**
- App Django `mcp_integration` funcional
- Cliente n8n con 11 métodos
- Constructor automático de workflows
- Documentación completa
- Tests básicos incluidos
- Variables de entorno configuradas

✅ **Configuración lista:**
- N8N_API_KEY: Configurada
- DJANGO_API_TOKEN: Generado
- WEBHOOK_SECRET: Listo para producción
- Validación HMAC: Disponible

⏳ **Próximo paso:** Desplegar a producción

---

## 🚀 Plan de Deployment

### Fase 1: Elección de Proveedor (Elige uno)

| Proveedor | Dificultad | Costo | Tiempo | Recomendación |
|-----------|-----------|-------|--------|--------------|
| **Railway** | ⭐ Muy fácil | $5/mes | 10 min | ✅ **RECOMENDADO** |
| **Render** | ⭐⭐ Fácil | $7/mes | 15 min | ✅ Buena alternativa |
| **AWS** | ⭐⭐⭐ Medio | Variable | 45 min | Para máximo control |
| **Heroku** | ⭐ Muy fácil | $7+/mes | 10 min | ❌ Menos cost-effective |

### Fase 2: Railway.app (Ruta Rápida - 10 minutos)

**1. Preparar código**
```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge
git push origin main
```

**2. Crear proyecto en Railway**
- Ir a https://railway.app
- Conectar GitHub
- Seleccionar repositorio Smart-Sync-Concierge
- Railway automáticamente:
  - Detecta que es Django
  - Provee PostgreSQL
  - Genera DATABASE_URL
  - Crea dominio temporal

**3. Configurar variables en Railway Dashboard**
```bash
DEBUG=False
SECRET_KEY=<tu_secret_key>
ALLOWED_HOSTS=api.smartsync.dev,*.railway.app
DATABASE_URL=<generada_automáticamente>

# N8N Integration
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DJANGO_API_URL=https://api.smartsync.dev  # O tu dominio en Railway
DJANGO_API_TOKEN=a75267088f61b319d75ffef873ac095e93558a37
WEBHOOK_SECRET=<generar_uno_nuevo>
WEBHOOK_VERIFY_SIGNATURE=True
```

**4. Agregar dominio personalizado** (opcional)
- Railway Dashboard → Domains
- Agregar: `api.smartsync.dev`
- Apuntar DNS

**5. Deploy automático**
- Cada push a main = deployment automático
- Ver logs en Railway dashboard

### Fase 3: Ejecutar Setup n8n en Producción

```bash
# Opción A: SSH a Railway (si da acceso)
# Opción B: Usar Django management command remotamente

# Una vez que el sitio está disponible:
python3 manage.py setup_n8n_workflow \
  --django-url https://api.smartsync.dev \
  --activate
```

### Fase 4: Testing del Flujo Completo

```bash
# Test 1: Verificar que Django responde
curl https://api.smartsync.dev/api/v1/health/

# Test 2: Crear una cita directamente
curl -X POST https://api.smartsync.dev/api/v1/appointments/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am",
    "user_timezone": "America/Mexico_City"
  }'

# Test 3: Activar webhook n8n
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

---

## 📋 Checklist Pre-Deployment

### Configuración
- [ ] `requirements.txt` incluye `requests==2.31.0`
- [ ] `.env` tiene N8N_API_KEY y DJANGO_API_TOKEN
- [ ] `config/settings/n8n.py` existe y está importado
- [ ] App `mcp_integration` está en INSTALLED_APPS
- [ ] Base de datos PostgreSQL lista

### Código
- [ ] Todos los cambios están en git
- [ ] Tests locales pasan (si existen)
- [ ] No hay errores de Django check: `manage.py check`
- [ ] Documentación está actualizada

### Producción
- [ ] Dominio configurado (api.smartsync.dev)
- [ ] SSL/HTTPS activo
- [ ] DEBUG=False
- [ ] SECRET_KEY único en producción
- [ ] ALLOWED_HOSTS correcto
- [ ] WEBHOOK_VERIFY_SIGNATURE=True

### n8n
- [ ] N8N_API_KEY válida y activa
- [ ] DJANGO_API_TOKEN generado
- [ ] URL de Django pública y accesible
- [ ] Webhook testeado

---

## 🔄 Proceso de Deployment Step-by-Step

### Opción A: Railway (Recomendado)

```
1. git push origin main
   ↓
2. Railway detecta cambio
   ↓
3. Railway hace build y deploy
   ↓
4. Django migrations se ejecutan
   ↓
5. Sitio está live en api.smartsync.dev
   ↓
6. python manage.py setup_n8n_workflow --django-url https://api.smartsync.dev --activate
   ↓
7. Workflow activado en n8n
   ↓
8. Sistema listo
```

### Opción B: Render.com

Similar a Railway pero con pasos manuales adicionales.

### Opción C: AWS

Más control pero más configuración manual.

---

## 🧪 Testing Post-Deployment

### Test 1: Django está respondiendo

```bash
curl -I https://api.smartsync.dev/api/v1/health/
# Expected: HTTP 200
```

### Test 2: Base de datos funciona

```bash
curl https://api.smartsync.dev/api/v1/contacts/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37"
# Expected: JSON list
```

### Test 3: n8n puede conectar

```bash
# En n8n: Settings → Credentials → Test

# O manualmente
curl -X POST https://api.smartsync.dev/api/v1/appointments/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37" \
  -d '{"prompt": "test"}'
```

### Test 4: Webhook completo

```bash
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am",
    "user_timezone": "America/Mexico_City"
  }'
```

---

## 📊 Monitoreo Post-Deployment

### Railway Dashboard
- https://railway.app → Project → Deployments
- Ver logs en tiempo real
- Métricas de CPU/Memoria

### Logs en Producción
```bash
# Ver último deployment
curl https://api.smartsync.dev/api/v1/traces/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37" | jq '.results[-1]'
```

### Alertas Recomendadas
- [ ] Configurar alertas de error 5xx
- [ ] Configurar alertas de base de datos
- [ ] Configurar alertas de API timeout

---

## 🔐 Seguridad Post-Deployment

✅ **Ya implementado:**
- Token-based authentication
- Rate limiting
- CORS configurado
- SECRET_KEY único

🔒 **Recomendaciones para producción:**
- [ ] Activar WEBHOOK_VERIFY_SIGNATURE=True
- [ ] Generar nuevo WEBHOOK_SECRET
- [ ] Usar HTTPS only (SECURE_SSL_REDIRECT=True)
- [ ] Configurar HSTS headers
- [ ] Agregar IP whitelist para n8n (opcional)

---

## 📈 Escala de Resultados Esperados

Después del deployment:

✅ **Usuarios pueden:**
- Enviar solicitudes al webhook n8n
- Recibir respuestas estructuradas
- Ver trazas de decisiones de agentes
- Consultar citas en base de datos

✅ **Monitoreo disponible:**
- Logs de Django
- Trazas de decisiones
- Executions en n8n

✅ **Escalabilidad:**
- Railway puede escalar automáticamente
- Database PostgreSQL soporta miles de citas
- n8n puede procesar miles de requests

---

## 🎯 Timeline

| Tarea | Tiempo | Requerimientos |
|-------|--------|----------------|
| Crear cuenta Railway | 5 min | Email |
| Conectar GitHub | 2 min | GitHub token |
| Configurar variables | 3 min | Valores de .env |
| Deploy | 1 min | Push a main |
| Setup n8n | 2 min | Ejecutar comando |
| Testing | 5 min | curl |
| **TOTAL** | **~18 minutos** | - |

---

## 📞 Soporte y Referencias

**Si algo falla:**

1. Verificar logs en Railway/Render
2. Consultar: `docs/N8N_PRODUCTION_DEPLOYMENT.md`
3. Revisar: `docs/N8N_WORKFLOW_SETUP.md`
4. Troubleshooting: `docs/MCP_ARCHITECTURE.md`

**Documentación clave:**
- [Railway Docs](https://docs.railway.app/)
- [Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [n8n API Docs](https://docs.n8n.io/api/)

---

## ✅ Resumen

**Estado:** ✅ Listo para desplegar

**Próximo paso:** Elegir proveedor (Railway recomendado) y ejecutar deployment

**Tiempo estimado:** 20 minutos

**Equipo:** Solo necesitas tener:
- GitHub conectado
- Railway/Render account
- Tu n8n API key

---

**¿Necesitas ayuda con el deployment?** Lee `docs/N8N_PRODUCTION_DEPLOYMENT.md` para guía detallada de tu proveedor preferido.
