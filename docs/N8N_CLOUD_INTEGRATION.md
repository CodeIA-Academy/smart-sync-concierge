# Integración N8N Cloud + MCP Server

## Descripción General

Este documento describe cómo conectar tu servidor N8N en la nube (https://n8n.codeia.dev/) con el servidor MCP local para procesar solicitudes de citas.

**Arquitectura:**
```
Postman/Cliente
    ↓
N8N Webhook (n8n.codeia.dev)
    ↓
MCP Server (localhost:8001)
    ↓
OpenRouter API (Haiku 4.5)
    ↓
Respuesta JSON estructurada
```

## Requisitos Previos

1. ✅ **Servidor MCP activo** en `http://localhost:8001`
   - Ver: [MCP_SERVER_SETUP.md](MCP_SERVER_SETUP.md)
   - Verificar: `curl http://localhost:8001/health`

2. ✅ **Acceso a N8N Cloud** en `https://n8n.codeia.dev/`
   - Usuario con permisos de administración
   - API key JWT configurada (tienes: eyJhbG...)

3. ✅ **OpenRouter API key** configurada
   - En variable de entorno: `OPENROUTER_API_KEY`
   - Verificar fondos en cuenta OpenRouter

## Pasos para Integración

### Paso 1: Importar el Flujo en N8N

#### Opción A: Importar desde JSON (Recomendado)

1. Accede a tu N8N cloud: https://n8n.codeia.dev/
2. Click en **"Workflows"** en el sidebar
3. Click en **"Create new"** → **"Import from file"**
4. Selecciona el archivo: `n8n/workflow_mcp_local.json`
5. Click **"Import"**

El flujo se importará con estos 5 nodos:
- **Webhook Input**: Recibe solicitudes POST
- **Preparar Datos**: Enriquece con metadata
- **Llamar MCP Local**: HTTP POST a http://localhost:8001/mcp/process-appointment
- **Procesar Respuesta MCP**: Valida y estructura respuesta
- **Webhook Response**: Devuelve respuesta HTTP

#### Opción B: Crear Manualmente

1. Nuevo Workflow en N8N
2. Seguir los pasos en: [MCP_LOCAL_WORKFLOW.md](../n8n/MCP_LOCAL_WORKFLOW.md) sección "Nodo 1-5"

### Paso 2: Configurar Webhook para Acceso Remoto

El MCP server está en tu máquina local (localhost:8001), pero N8N está en la nube. Necesitas conectividad.

#### Opción 1: Usar SSH Tunnel (Recomendado para desarrollo)

```bash
# Terminal 1: SSH Tunnel desde tu máquina local al servidor N8N
# Esto expone localhost:8001 en el servidor N8N
ssh -R 8001:localhost:8001 user@n8n-server
```

#### Opción 2: Abrir Firewall

Si tu MCP server está en un servidor propio:
- Abre puerto 8001 en tu firewall
- Usa IP pública en N8N: `http://<your_ip>:8001/mcp/process-appointment`

#### Opción 3: Proxy (Producción)

Usa un proxy como ngrok:
```bash
ngrok http 8001
# Outlet: https://xxxx-xxx-xxx.ngrok.io
# Usa esta URL en el nodo HTTP de N8N
```

### Paso 3: Configurar el Nodo "Llamar MCP Local"

En el flujo importado, el nodo **"Llamar MCP Local"** debe apuntar a tu MCP server:

1. En N8N, abre el flujo
2. Click en nodo **"Llamar MCP Local"**
3. **URL**: Configura según tu opción:
   - Local/Mismo servidor: `http://localhost:8001/mcp/process-appointment`
   - Remoto: `http://<ip_publica>:8001/mcp/process-appointment`
   - Via ngrok: `https://xxxx-xxx-xxx.ngrok.io/mcp/process-appointment`
4. **Headers**: Content-Type: application/json (ya configurado)
5. **Body**: Ya está correctamente configurado

### Paso 4: Activar el Flujo

1. En el flujo, click en **"Start"** (arriba derecha)
2. Debe mostrar: "Workflow active"
3. Busca el nodo "Webhook Input" y anota la URL del webhook

La URL será algo como:
```
https://n8n.codeia.dev/webhook/appointments/process
```

### Paso 5: Testear el Flujo

#### Test 1: Usar Postman

```bash
# 1. Importa esta colección en Postman:
POST https://n8n.codeia.dev/webhook/appointments/process
Content-Type: application/json

{
  "prompt": "cita mañana 10am con Dr. Pérez",
  "opciones": {
    "zona_horaria": "America/Mexico_City"
  }
}

# Respuesta esperada (200 OK):
{
  "status": "processed",
  "confidence": 1,
  "entities": {},
  "validation": {},
  "suggestions": [],
  "reasoning": "...",
  "trace_id": "mcp_1770764011",
  "cost_usd": 0.000968,
  "processing_time_ms": 5927.881,
  "timestamp": "2026-02-10T16:53:31.045732"
}
```

#### Test 2: Usar cURL

```bash
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "opciones": {"zona_horaria": "America/Mexico_City"}
  }' | jq .
```

#### Test 3: Usar Script Local

```bash
# Desde tu máquina donde está el MCP server:
cd Smart-Sync-Concierge
chmod +x n8n/test_mcp_flow.sh
./n8n/test_mcp_flow.sh

# Output:
# ✓ MCP Server is healthy
# ✓ MCP Server processed appointment
# ✓ All tests passed!
```

## Flujo Completo: Paso a Paso

### 1. Usuario envía solicitud de cita

**Postman:**
```json
POST https://n8n.codeia.dev/webhook/appointments/process
{
  "prompt": "cita mañana 10am con Dr. Pérez"
}
```

### 2. N8N recibe en Webhook Input

El nodo **"Webhook Input"** recibe el JSON

### 3. N8N Preparar Datos

El nodo **"Preparar Datos"** transforma:
```json
{
  "prompt": "cita mañana 10am con Dr. Pérez",
  "opciones": {},
  "metadata": {
    "n8n_execution_id": "abc123",
    "timestamp": "2026-02-10T...",
    "source": "n8n_mcp_local"
  }
}
```

### 4. N8N → MCP Server

El nodo **"Llamar MCP Local"** hace:
```bash
POST http://localhost:8001/mcp/process-appointment
{
  "prompt": "cita mañana 10am con Dr. Pérez",
  "max_tokens": 2000,
  "temperature": 0.3,
  "response_format": "json",
  "metadata": {...}
}
```

### 5. MCP Server → OpenRouter

El servidor MCP:
- Inicializa cliente OpenRouter
- Envía al modelo Haiku 4.5
- Parsea la respuesta
- Calcula costo
- Retorna con metadata

```json
{
  "status": "success",
  "data": {
    "status": "processed",
    "confidence": 0.95,
    "entities": {...},
    "reasoning": "..."
  },
  "trace_id": "mcp_...",
  "tokens_used": 179,
  "cost_usd": 0.00088,
  "processing_time_ms": 2341
}
```

### 6. N8N Procesa Respuesta

El nodo **"Procesar Respuesta MCP"** extrae los datos relevantes

### 7. N8N Webhook Response

El nodo **"Webhook Response"** devuelve al cliente:
```json
HTTP 200
{
  "status": "processed",
  "confidence": 1,
  "entities": {...},
  "trace_id": "mcp_...",
  "cost_usd": 0.00088,
  "processing_time_ms": 2341
}
```

## Monitoreo y Debugging

### Ver Executions en N8N

1. Abre tu flujo en N8N
2. Tab **"Executions"** (arriba)
3. Click en una ejecución específica
4. Ver logs detallados de cada nodo

### Logs del MCP Server

```bash
# En tu terminal local donde corre el MCP:
tail -f logs/mcp_server.log

# O en la misma terminal:
# Los logs aparecen en tiempo real
./start_mcp_server.sh 8001
```

### Verificar Conectividad

```bash
# Desde N8N (requiere ejecución del nodo HTTP):
# El nodo "Llamar MCP Local" mostrará en los logs si hay error

# Desde tu máquina local:
curl http://localhost:8001/health | jq .
curl http://localhost:8001/mcp/models | jq .
```

## Troubleshooting

### Error: "Connection refused"

**Problema:** N8N no puede conectar a localhost:8001

**Soluciones:**
1. Verificar que MCP server está corriendo: `curl http://localhost:8001/health`
2. Si N8N está remoto, usar SSH tunnel o ngrok (ver Paso 2)
3. Verificar firewall no bloquea puerto 8001

### Error: "Timeout after 30s"

**Problema:** MCP server toma demasiado tiempo (normal: 2-3 seg, pero OpenRouter a veces es lento)

**Soluciones:**
1. Aumentar timeout en nodo HTTP de N8N (Settings → Timeout)
2. Verificar conexión a internet en servidor MCP
3. Verificar fondos en OpenRouter
4. Usar temperatura más baja (0.1 en lugar de 0.3)

### Error: "Invalid JSON in response"

**Problema:** MCP retorna error

**Soluciones:**
1. Verificar logs del MCP server
2. El prompt puede ser ambiguo
3. Usar prompts más específicos

### Error: "OpenRouter API key not found"

**Problema:** MCP server no tiene API key

**Soluciones:**
```bash
# Exportar en tu terminal antes de iniciar MCP
export OPENROUTER_API_KEY="sk-or-v1-..."
./start_mcp_server.sh 8001
```

## Performance

| Métrica | Valor |
|---------|-------|
| Latencia promedio | 2-3 segundos |
| Tokens por solicitud | 150-500 |
| Costo por solicitud | $0.0008-0.001 USD |
| Throughput | Ilimitado (async) |

## Seguridad

⚠️ **IMPORTANTE:**
- ✅ NO expongas tu OPENROUTER_API_KEY en URLs o Postman
- ✅ El MCP server NO retorna la API key, solo la usa internamente
- ✅ Protege acceso a puerto 8001 en firewall
- ⚠️ Si usas SSH tunnel, asegura credenciales

## Arquitectura Completa

```
┌─────────────────────────────────────────────────┐
│  Cliente (Postman / Aplicación)                 │
│  POST /webhook/appointments/process             │
└──────────────────────┬──────────────────────────┘
                       │
                       ↓ HTTPS
        ┌──────────────────────────────────┐
        │  N8N Cloud (n8n.codeia.dev)      │
        │                                  │
        │  1. Webhook Input ───────────┐  │
        │  2. Preparar Datos          │   │
        │  3. HTTP POST a MCP ←────────┤  │
        │     (localhost:8001)        │   │
        │  4. Procesar Respuesta ←────┤  │
        │  5. Webhook Response ←──────┘  │
        │                                  │
        └──────────────────────────────────┘
                       │
                       ↓ HTTP
        ┌──────────────────────────────────┐
        │  MCP Server (localhost:8001)     │
        │  FastAPI + Uvicorn               │
        │  • Health check                  │
        │  • /mcp/process-appointment      │
        │  • /mcp/complete                 │
        └──────────────────┬───────────────┘
                           │
                           ↓ HTTPS
                ┌──────────────────────┐
                │  OpenRouter API      │
                │  Claude Haiku 4.5    │
                │  (async)             │
                └──────────────────────┘
```

## Próximos Pasos

1. ✅ Importar flujo en N8N
2. ✅ Configurar conectividad (SSH tunnel / ngrok / Firewall)
3. ✅ Activar flujo
4. ✅ Testear con Postman
5. 🔄 Agregar validación de base de datos
6. 🔄 Agregar notificaciones por email
7. 🔄 Integrar con Google Calendar

## Referencias

- [MCP_SERVER_SETUP.md](MCP_SERVER_SETUP.md) - Servidor MCP
- [MCP_LOCAL_WORKFLOW.md](../n8n/MCP_LOCAL_WORKFLOW.md) - Detalles del flujo
- [test_mcp_flow.sh](../n8n/test_mcp_flow.sh) - Script de testing

---

**Última actualización:** 2026-02-10
**Versión:** 0.1.0
**Estado:** ✅ Funcional
