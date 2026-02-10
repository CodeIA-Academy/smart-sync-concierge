# Próximos Pasos - Integración n8n

La implementación de integración n8n está **completada** ✅

Aquí están los pasos para activarla en tu entorno.

## 📋 Checklist de Setup

### Fase 1: Preparación Local (5 min)

- [x] API key de n8n obtenida
- [x] Token Django creado: `a75267088f61b319d75ffef873ac095e93558a37`
- [x] Variables en `.env` configuradas
- [ ] ngrok instalado (si estás en desarrollo)

### Fase 2: Testing Local (10 min)

1. **Iniciar Django en una terminal:**
```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge
python3 manage.py runserver 0.0.0.0:8000
```

2. **Iniciar ngrok en otra terminal (IMPORTANTE para desarrollo):**
```bash
ngrok http 8000
```
Copia la URL que aparece (ej: `https://abc123.ngrok.io`)

3. **Ejecutar setup en una tercera terminal:**
```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge

# Opción A: Script automático
./scripts/n8n/setup.sh

# Opción B: Comando Django directo
python3 manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io \
  --activate
```

Reemplaza `https://abc123.ngrok.io` con tu URL de ngrok.

### Fase 3: Testing del Webhook (5 min)

Una vez que el setup complete, prueba el webhook:

```bash
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

Respuesta esperada:
```json
HTTP 201 Created
{
  "status": "success",
  "message": "Appointment created successfully",
  "data": {
    "id": "apt_20260211_...",
    "contacto_nombre": "Dr. Pérez",
    "fecha": "2026-02-11",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "tipo_servicio": "Consulta General"
  },
  "trace_id": "trace_20260210_..."
}
```

## 📊 Variables Actuales

En tu `.env`:
```bash
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DJANGO_API_URL=http://localhost:8000  # O tu ngrok URL
DJANGO_API_TOKEN=a75267088f61b319d75ffef873ac095e93558a37
WEBHOOK_SECRET=
WEBHOOK_VERIFY_SIGNATURE=False
```

## 🔗 Arquitectura del Flujo

```
Usuario
  ↓
n8n Webhook
  ├─ Recibe POST
  ├─ Prepara datos
  ├─ Llama Django API
  └─ Devuelve respuesta
  ↓
Django API (/api/v1/appointments/)
  ├─ Autentica con Token
  ├─ Procesa con AgentOrchestrator
  ├─ Ejecuta 6 agentes
  └─ Devuelve respuesta
  ↓
Usuario recibe resultado
```

## 📚 Documentación

Consulta estos archivos para más información:

1. **[docs/N8N_WORKFLOW_SETUP.md](docs/N8N_WORKFLOW_SETUP.md)**
   - Guía detallada paso a paso
   - Troubleshooting completo
   - Comandos útiles

2. **[docs/MCP_ARCHITECTURE.md](docs/MCP_ARCHITECTURE.md)**
   - Decisiones de arquitectura
   - Diagramas de flujo
   - Componentes detallados

3. **[apps/mcp_integration/README.md](apps/mcp_integration/README.md)**
   - Documentación de la app Django
   - Uso programático
   - Testing

4. **[scripts/n8n/README.md](scripts/n8n/README.md)**
   - Scripts de automatización
   - Troubleshooting de scripts

## 🧪 Testing Completo

### Test 1: Endpoint Django directo

```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

### Test 2: Con ngrok

```bash
curl -X POST https://abc123.ngrok.io/api/v1/appointments/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37" \
  -d '{"prompt": "cita mañana"}'
```

### Test 3: Webhook n8n

```bash
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{"prompt": "cita mañana"}'
```

## 📊 Monitoreo

### Ver logs Django
```bash
tail -f logs/django.log | grep "mcp_integration"
```

### Ver traces de decisiones
```bash
curl http://localhost:8000/api/v1/traces/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37" | jq
```

### Dashboard n8n
Abre en navegador después de crear el workflow:
```
https://n8n.codeia.dev/workflow/<workflow_id>/executions
```

## ⚠️ Troubleshooting

### Problema: "No se puede conectar a n8n"

**Solución:**
```bash
# Verificar API key
echo "N8N_API_KEY: $(grep N8N_API_KEY .env | cut -d= -f2 | cut -c1-20)..."

# Test manual
curl -X GET https://n8n.codeia.dev/api/v1/workflows \
  -H "X-N8N-API-KEY: $(grep N8N_API_KEY .env | cut -d= -f2)"
```

### Problema: "Unauthorized al llamar Django"

**Solución:**
```bash
# Verificar token
echo "DJANGO_API_TOKEN: $(grep DJANGO_API_TOKEN .env | cut -d= -f2)"

# Generar nuevo si es necesario
python3 manage.py drf_create_token admin
```

### Problema: "Django API no responde"

**Solución:**
```bash
# Verificar Django está corriendo
curl http://localhost:8000/api/v1/health/

# Verificar ngrok está activo
curl https://abc123.ngrok.io/api/v1/health/

# Si falla, reiniciar ngrok y actualizar URL
```

### Problema: "Workflow ya existe"

**Solución:**
```bash
# Opción 1: Reemplazar
python3 manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io \
  --activate \
  --replace

# Opción 2: Eliminar manual en n8n UI
# https://n8n.codeia.dev/workflows → buscar "Smart-Sync" → Delete
```

## 📈 Próximas Mejoras (Roadmap)

- [ ] Agregar validación HMAC de webhooks
- [ ] Endpoint de diagnóstico `/api/v1/mcp/status/`
- [ ] Tests unitarios completos
- [ ] Soporte para múltiples workflows
- [ ] Webhooks de n8n → Django (notificaciones)
- [ ] Dashboard de monitoreo
- [ ] Integración CI/CD

## 📞 Contacto y Soporte

Para problemas específicos:

1. **Revisión de Logs:**
   - Django: `logs/django.log`
   - n8n: Dashboard → Executions

2. **Documentación:**
   - Ver archivos en `docs/`
   - Ver README en `apps/mcp_integration/`

3. **Comandos Útiles:**
   - Listar workflows: `python3 manage.py shell` → Usar N8NClient
   - Ver traces: `curl http://localhost:8000/api/v1/traces/`

## ✨ Resumen

✅ Implementación completada
✅ Variables configuradas
✅ Token Django generado
⏳ **Siguiente:** Ejecutar `./scripts/n8n/setup.sh` o comando Django

---

**¿Listo para comenzar?** Ejecuta el setup cuando tengas ngrok corriendo. 🚀
