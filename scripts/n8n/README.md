# Scripts de n8n Integration

Herramientas para facilitar la integración con n8n.

## setup.sh

Script interactivo para configurar la integración n8n automáticamente.

### Uso

```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge

./scripts/n8n/setup.sh
```

### Qué Hace

1. **Verifica configuración**: Valida que `.env` existe y está completo
2. **Valida variables**: Verifica N8N_API_KEY, DJANGO_API_TOKEN
3. **Detecta entorno**: Identifica si estás en desarrollo o producción
4. **Pregunta por ngrok**: Si estás en localhost, te pide URL de ngrok
5. **Ejecuta setup**: Corre el comando Django para crear el workflow

### Requisitos

- Python 3.7+
- `.env` configurado con:
  - `N8N_API_KEY`: Tu API key de n8n
  - `DJANGO_API_TOKEN`: Token Django (se genera si no existe)
  - `DJANGO_API_URL`: URL de tu API Django

### Ejemplo

```bash
# Terminal 1: Iniciar Django
python3 manage.py runserver 0.0.0.0:8000

# Terminal 2: Iniciar ngrok
ngrok http 8000
# Output: https://abc123.ngrok.io

# Terminal 3: Ejecutar setup
./scripts/n8n/setup.sh

# Ingresa URL ngrok cuando se pida: https://abc123.ngrok.io
```

### Output Esperado

```
================================================================================
🚀  SMART-SYNC CONCIERGE - N8N INTEGRATION SETUP
================================================================================

[1/5] Verificando configuración...
✓ Configuración OK

[2/5] Verificando variables de entorno...
✓ Variables configuradas

[3/5] Información del setup:
   N8N API URL: https://n8n.codeia.dev
   Django API URL: https://abc123.ngrok.io
   Django Token: a75267088f61b319...

[4/5] Configuración de Django API URL...
⚠  Detectado: localhost:8000
¿Estás en desarrollo con ngrok?
Ingresa URL de ngrok (ej: https://abc123.ngrok.io) o presiona Enter para localhost: https://abc123.ngrok.io
✓ Actualizado a: https://abc123.ngrok.io

[5/5] Ejecutando setup n8n...

📡 [1/5] Conectando a n8n...
✓ Conectado a n8n

... [resto del output del comando Django] ...

================================================================================
✅ SETUP COMPLETADO EXITOSAMENTE
================================================================================

📚 Documentación:
   - Guía completa: docs/N8N_WORKFLOW_SETUP.md
   - Arquitectura: docs/MCP_ARCHITECTURE.md
   - App: apps/mcp_integration/README.md

🧪 Próximo paso: Prueba el webhook con curl
   curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "cita mañana 10am"}'
```

## test_webhook.sh

Script para probar el webhook n8n (próxima versión).

## deploy_workflow.py

Script Python para deployment completo (próxima versión).

## Troubleshooting

### Error: "Command not found: setup.sh"

Asegúrate de estar en el directorio raíz del proyecto:

```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge
./scripts/n8n/setup.sh
```

### Error: ".env not found"

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Luego completa las variables requeridas en `.env`.

### Error: "DJANGO_API_TOKEN not configured"

Genera el token Django:

```bash
python3 manage.py drf_create_token admin
```

Luego agrega el token generado a `.env`:

```bash
DJANGO_API_TOKEN=<el_token_generado>
```

## Referencias

- [N8N_WORKFLOW_SETUP.md](../../docs/N8N_WORKFLOW_SETUP.md) - Guía de setup
- [MCP_ARCHITECTURE.md](../../docs/MCP_ARCHITECTURE.md) - Arquitectura
- [apps/mcp_integration/README.md](../../apps/mcp_integration/README.md) - App documentation
