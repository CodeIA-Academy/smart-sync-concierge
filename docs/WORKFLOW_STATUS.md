# Estado de Workflows n8n - Smart-Sync Concierge

## Resumen

Se han creado y testeado **3 workflows n8n** para procesar solicitudes de citas:

| ID | Nombre | Estado | Webhook URL | Descripción |
|:---|:-------|:-------|:------------|:-----------|
| `GfAyPHecDvmrmUZN` | Test Response (SIN deps) | ✅ **ACTIVO** | `https://n8n.codeia.dev/webhook/smartsync-prod/test-response` | Devuelve respuesta HTTP estructurada |
| `qpDB5VPnZg7NpzW0` | Con Gmail | ✅ **ACTIVO** | `https://n8n.codeia.dev/webhook/smartsync-prod/cita-email` | Envía email a yosnap@gmail.com |
| `E7CwON3Kaj33kp7i` | V3 (webhook_id custom) | ✅ **ACTIVO** | - | Versión anterior, no usar |

## ✅ Workflow Funcionando (COMPROBADO)

**Workflow ID:** `GfAyPHecDvmrmUZN`  
**Webhook URL:** https://n8n.codeia.dev/webhook/smartsync-prod/test-response

### Estructura

1. **Webhook Input** - Recibe POST con: `{prompt, user_timezone, user_id}`
2. **Generar Respuesta** - Function node que procesa datos y genera respuesta estructurada
3. **Webhook Response** - Devuelve respuesta al cliente HTTP 200

### Prueba

```bash
curl -X POST "https://n8n.codeia.dev/webhook/smartsync-prod/test-response" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita urgente mañana 10am",
    "user_timezone": "America/Mexico_City",
    "user_id": "user_123"
  }'
```

### Respuesta Exitosa (HTTP 200)

```json
{
  "appointment": {
    "prompt": "cita urgente mañana 10am",
    "timezone": "America/Mexico_City",
    "user_id": "user_123",
    "created_at": "2026-02-11T13:50:30.657Z",
    "status": "pendiente_confirmacion"
  },
  "message": "Solicitud de Cita Recibida...",
  "notification_needed": true
}
```

## 📧 Workflow Con Gmail

**Workflow ID:** `qpDB5VPnZg7NpzW0`  
**Webhook URL:** https://n8n.codeia.dev/webhook/smartsync-prod/cita-email  
**Estado:** Creado y activado, pero requiere credenciales Gmail

### Próximos Pasos

1. **Ve a n8n:** https://n8n.codeia.dev/workflow/qpDB5VPnZg7NpzW0
2. **Haz clic en el nodo "Enviar por Email"**
3. **Verifica credenciales Gmail:**
   - Si no están configuradas, haz clic en "Authenticate"
   - Se abrirá un formulario de OAuth de Google
   - Selecciona tu cuenta de Gmail
   - Autoriza el acceso
4. **Haz clic en "Execute Workflow"** para probar manualmente
5. **O prueba con curl:**
   ```bash
   curl -X POST "https://n8n.codeia.dev/webhook/smartsync-prod/cita-email" \
     -H "Content-Type: application/json" \
     -d '{"prompt":"cita test","user_timezone":"America/Mexico_City","user_id":"test123"}'
   ```
6. **Verifica** que el email llegue a yosnap@gmail.com

## 🔄 Integración Completa (Próximo Paso)

Una vez que Gmail esté configurado, el flujo será:

```
Usuario → POST a webhook → n8n:
  1. Recibe solicitud
  2. Procesa datos (Function node)
  3. Envía respuesta a email
  4. Devuelve respuesta HTTP al cliente
```

## 🤖 Próximo: Agregar AI Agent (Haiku 4.5)

Cuando Gmail esté funcionando, agregaremos:
- **AI Agent node** que use OpenRouter
- **Haiku 4.5 LLM** para generar respuestas personalizadas
- **Integración con Django API** para guardar citas en base de datos

## 📝 Notas Técnicas

- Los workflows utilizan `responseMode: "responseNode"` para devolver datos procesados
- El nodo `Webhook Response` maneja la respuesta HTTP final
- El nodo de Gmail requiere credenciales OAuth2 de Google
- Los workflows están en n8n cloud (https://n8n.codeia.dev)
- Todos los nodos usan JavaScript (n8n-nodes-base.function) para procesar datos

