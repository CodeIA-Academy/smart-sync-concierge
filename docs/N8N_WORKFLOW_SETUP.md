# Guía de Setup: Integración n8n → Smart-Sync Concierge

Paso a paso para integrar Smart-Sync Concierge con n8n automáticamente.

**Tiempo estimado:** 10-15 minutos
**Requisitos previos:**
- Acceso a n8n.codeia.dev
- Django corriendo localmente o en servidor
- Token Django API

## Paso 1: Preparar Variables de Entorno

### 1a. Obtener API Key de n8n

1. Ir a https://n8n.codeia.dev/
2. Click en tu avatar (arriba a la derecha)
3. Settings → API
4. Click en "Create API Key"
5. Copiar la key (comienza con `eyJhb...`)

### 1b. Obtener Token Django

```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge

# Crear token (si no lo tienes)
python3 manage.py drf_create_token admin

# Output: Generated token abc123def456...
```

### 1c. Actualizar .env

Editar `.env` y agregar:

```bash
# N8N Integration
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=eyJhb...  # Tu API key de n8n
DJANGO_API_URL=http://localhost:8000  # O ngrok URL si estás en desarrollo
DJANGO_API_TOKEN=abc123def456...  # Tu token Django
WEBHOOK_SECRET=
WEBHOOK_VERIFY_SIGNATURE=False
```

## Paso 2: Instalar Dependencias

```bash
pip3 install requests==2.31.0
```

## Paso 3: Ejecutar Setup Automático

### 3a. Para Desarrollo (con ngrok)

Si estás en desarrollo local, necesitas ngrok para que n8n pueda llegar a tu Django:

```bash
# Terminal 1: Iniciar Django
python3 manage.py runserver 0.0.0.0:8000

# Terminal 2: Iniciar ngrok
ngrok http 8000

# Copiar URL ngrok (algo como https://abc123.ngrok.io)
```

Luego ejecutar el comando:

```bash
# Terminal 3: Setup
python3 manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io \
  --activate
```

### 3b. Para Producción (con dominio)

```bash
python3 manage.py setup_n8n_workflow \
  --django-url https://api.smartsync.dev \
  --activate
```

## Paso 4: Verificar Setup

Si el comando se ejecutó correctamente, verás:

```
======================================================================
🚀  SETUP DE WORKFLOW SMART-SYNC EN N8N
======================================================================

📡 [1/5] Conectando a n8n...
✓ Conectado a n8n

🔍 [2/5] Buscando workflow existente...
✓ No existe workflow previo

🔨 [3/5] Construyendo workflow...
✓ Workflow construido (5 nodos)

📤 [4/5] Creando workflow en n8n...
✓ Workflow creado: abc123def456

⚡ [5/5] Activando workflow...
✓ Workflow activado

======================================================================
✅ SETUP COMPLETADO EXITOSAMENTE
======================================================================

📋 INFORMACIÓN DEL WORKFLOW:
   ID: abc123def456
   Nombre: Smart-Sync Concierge - Appointments
   URL Webhook: https://n8n.codeia.dev/webhook/appointments/process
   Estado: ACTIVO ✓

🧪 TESTING DEL WORKFLOW:

curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'

📊 MONITOREO:
   Ver workflow en n8n: https://n8n.codeia.dev/workflow/abc123def456
   Ver traces Django: http://localhost:8000/api/v1/traces/
   Ver ejecuciones: https://n8n.codeia.dev/workflow/abc123def456/executions

======================================================================
```

## Paso 5: Probar el Webhook

Usa curl para probar que el workflow funciona:

```bash
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

**Respuesta esperada:**
```json
HTTP 201 Created

{
  "status": "success",
  "message": "Appointment created successfully",
  "data": {
    "id": "apt_20260211_abc123",
    "contacto_nombre": "Dr. Pérez",
    "fecha": "2026-02-11",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "tipo_servicio": "Consulta General"
  },
  "trace_id": "trace_20260210_abc123"
}
```

## Paso 6: Verificar Traces

Ver las trazas de decisiones de los agentes:

```bash
curl http://localhost:8000/api/v1/traces/ \
  -H "Authorization: Token <tu_token>" | jq '.' | head -50
```

## Troubleshooting

### Error: "No se puede conectar a n8n"

```bash
# Verificar variables
echo $N8N_API_URL
echo $N8N_API_KEY

# Test manual
curl -X GET https://n8n.codeia.dev/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY"

# Si falla, revisar:
# 1. ¿N8N_API_KEY es correcto?
# 2. ¿n8n.codeia.dev está disponible?
# 3. ¿Firewall permite acceso?
```

### Error: "Unauthorized al llamar Django"

```bash
# Crear nuevo token
python3 manage.py drf_create_token admin

# Actualizar .env con nuevo DJANGO_API_TOKEN
```

### Error: "Django API no responde"

```bash
# Verificar Django está corriendo
curl http://localhost:8000/api/v1/health/

# Si es con ngrok, verificar que está activo
curl https://abc123.ngrok.io/api/v1/health/

# Si falla, reiniciar:
# 1. Detener Django (Ctrl+C)
# 2. Detener ngrok (Ctrl+C)
# 3. Reiniciar ngrok
# 4. Actualizar DJANGO_API_URL en .env
# 5. Reiniciar Django
```

### Error: "Workflow ya existe"

```bash
# Opción 1: Reemplazar existente
python3 manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io \
  --activate \
  --replace

# Opción 2: Eliminar manual en n8n UI
# 1. Ir a https://n8n.codeia.dev/workflows
# 2. Buscar "Smart-Sync Concierge - Appointments"
# 3. Click en 3 puntos → Delete
```

## Comandos Útiles

### Ver estado del workflow

```bash
python3 manage.py shell

from apps.mcp_integration.services.n8n_client import N8NClient
client = N8NClient()

# Listar workflows
workflows = client.list_workflows()
for w in workflows:
    if "Smart-Sync" in w.get("name", ""):
        print(f"ID: {w['id']}")
        print(f"Nombre: {w['name']}")
        print(f"Activo: {w['active']}")
```

### Ver ejecuciones recientes

```python
# En Django shell
from apps.mcp_integration.services.n8n_client import N8NClient
client = N8NClient()

# Obtener workflow primero
workflow_id = "abc123..."  # Tu workflow ID

# Ver últimas ejecuciones
executions = client.get_executions(workflow_id, limit=5)
for exec in executions:
    print(f"Execution {exec['id']}: {exec['status']}")
```

### Desactivar workflow

```python
# En Django shell
client.deactivate_workflow("abc123...")
```

### Eliminar workflow

```python
# En Django shell
client.delete_workflow("abc123...")
```

## Monitoreo Continuo

### Dashboard n8n

Abre en el navegador:
```
https://n8n.codeia.dev/workflow/<workflow_id>/executions
```

### Logs Django

```bash
tail -f logs/django.log | grep "mcp_integration"
```

### Traces de Decisiones

```bash
# Terminal 1: Ver traces en tiempo real
cd "/Volumes/Externo/Proyectos/CodeIA Academy Projects/Sesion 15/Smart-Sync-Concierge"
python3 manage.py runserver

# Terminal 2: Hacer prueba
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -d '{"prompt": "cita hoy 2pm"}'

# Terminal 3: Ver traces
curl http://localhost:8000/api/v1/traces/ | jq '.results[-1]'
```

## Próximos Pasos

Ahora que tienes el workflow configurado:

1. **Integrar con frontend** → Llamar webhook desde tu app
2. **Agregar validación** → Implementar HMAC en producción
3. **Monitoreo** → Configurar alertas si workflow falla
4. **Documentación** → Documentar endpoints para clientes

## Referencias

- [MCP_ARCHITECTURE.md](MCP_ARCHITECTURE.md) - Arquitectura completa
- [apps/mcp_integration/README.md](../apps/mcp_integration/README.md) - Documentación de app
- [N8N_CLOUD_INTEGRATION.md](N8N_CLOUD_INTEGRATION.md) - Documentación original
