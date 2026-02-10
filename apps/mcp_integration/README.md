# MCP Integration (n8n)

App Django para integración automática con n8n.

## Descripción

Esta app proporciona herramientas para conectar n8n (self-hosted) con la API Django:

- **Cliente n8n**: Interacción programática con n8n API
- **Constructor de workflows**: Generación automática de workflows JSON
- **Comando Django**: Setup automático en una línea

## Estructura

```
mcp_integration/
├── services/
│   ├── n8n_client.py        # Cliente para n8n API
│   └── workflow_builder.py   # Constructor de workflows
├── management/
│   └── commands/
│       └── setup_n8n_workflow.py  # Comando Django de setup
└── README.md                 # Este archivo
```

## Configuración

### Variables de Entorno

Agregar a `.env`:

```bash
# n8n API
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=<tu_api_key>

# Django API (para que n8n lo llame)
DJANGO_API_URL=http://localhost:8000  # o ngrok URL en desarrollo
DJANGO_API_TOKEN=<tu_token_django>

# Webhook (opcional)
WEBHOOK_SECRET=<opcional>
WEBHOOK_VERIFY_SIGNATURE=False
```

### Obtener API Key de n8n

1. Ir a https://n8n.codeia.dev/
2. Settings → API
3. Crear nueva API key
4. Copiar a `.env`

### Obtener Token Django

```bash
python manage.py drf_create_token admin
```

## Uso

### Setup Automático

```bash
# Crear y activar workflow
python manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io \
  --activate

# Crear sin activar
python manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io

# Reemplazar workflow existente
python manage.py setup_n8n_workflow \
  --django-url https://abc123.ngrok.io \
  --activate \
  --replace
```

### Cliente n8n Directo

```python
from apps.mcp_integration.services.n8n_client import N8NClient

client = N8NClient()

# Verificar conexión
client.test_connection()  # → True/False

# Crear workflow
workflow = client.create_workflow({...})

# Listar workflows
workflows = client.list_workflows()

# Activar workflow
client.activate_workflow(workflow_id)

# Ver ejecuciones
executions = client.get_executions(workflow_id)

# Eliminar workflow
client.delete_workflow(workflow_id)
```

### Constructor de Workflow

```python
from apps.mcp_integration.services.workflow_builder import SmartSyncWorkflowBuilder

builder = SmartSyncWorkflowBuilder(
    django_api_url="https://abc123.ngrok.io",
    django_api_token="<token>"
)

workflow_json = builder.build()

# Crear en n8n
client.create_workflow(workflow_json)
```

## Flujo Completo

```
Usuario → n8n Webhook → Django API → 6 Agentes → Respuesta
```

### Pasos

1. Usuario envía solicitud al webhook n8n
2. n8n prepara datos y enriquece metadata
3. n8n hace HTTP POST a Django API
4. Django procesa con AgentOrchestrator
5. Los 6 agentes procesan el prompt
6. Django retorna respuesta estruturada
7. n8n procesa respuesta y la devuelve al usuario

## Testing

### Test Local (sin n8n)

```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

### Con ngrok

```bash
# Terminal 1: Django
python manage.py runserver 0.0.0.0:8000

# Terminal 2: ngrok
ngrok http 8000

# Terminal 3: Test
curl -X POST https://abc123.ngrok.io/api/v1/appointments/ \
  -H "Authorization: Token <token>" \
  -d '{"prompt": "cita mañana 10am"}'
```

### Con n8n

```bash
# Test webhook n8n
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

## Troubleshooting

### Error: "No se puede conectar a n8n"

```bash
# Verificar URL y API key
echo $N8N_API_URL
echo $N8N_API_KEY

# Test manual
curl -X GET https://n8n.codeia.dev/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY"
```

### Error: "Unauthorized al llamar Django"

```bash
# Crear nuevo token Django
python manage.py drf_create_token admin

# Actualizar DJANGO_API_TOKEN en .env
```

### Error: "Django API no responde"

```bash
# Verificar Django está corriendo
curl http://localhost:8000/api/v1/health/

# Verificar ngrok está activo
curl https://abc123.ngrok.io/api/v1/health/

# Reiniciar ngrok y actualizar DJANGO_API_URL en .env
```

## Logging

Los logs de la integración aparecen en:

```bash
tail -f logs/django.log | grep "mcp_integration"
```

## Referencias

- [docs/N8N_CLOUD_INTEGRATION.md](../../docs/N8N_CLOUD_INTEGRATION.md)
- [docs/MCP_ARCHITECTURE.md](../../docs/MCP_ARCHITECTURE.md)
- [n8n API Docs](https://docs.n8n.io/api/)

## Versionado

- v0.1.0: Setup automático de workflow
- Futuro: Tests, validación HMAC, endpoint diagnóstico
