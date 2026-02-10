#!/bin/bash
# Script de deployment para Smart-Sync n8n Integration

set -e

echo "=========================================="
echo "🚀 DEPLOYMENT: Smart-Sync n8n Integration"
echo "=========================================="

# 1. Verificar que Django está corriendo
echo -e "\n1️⃣  Verificando Django..."
if ! curl -s http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "❌ Django no está corriendo en localhost:8000"
    echo "   Inicia Django: python manage.py runserver"
    exit 1
fi
echo "✅ Django disponible en localhost:8000"

# 2. Crear/actualizar token Django
echo -e "\n2️⃣  Generando token Django..."
TOKEN=$(python manage.py drf_create_token admin 2>&1 | grep "Token:" | awk '{print $NF}' || echo "")
if [ -z "$TOKEN" ]; then
    echo "⚠️  No se pudo crear token, usando el del .env"
    TOKEN=$(grep DJANGO_API_TOKEN .env | cut -d= -f2)
fi
echo "✓ Token: ${TOKEN:0:20}..."

# 3. Actualizar .env si es necesario
echo -e "\n3️⃣  Actualizando .env..."
if ! grep -q "DJANGO_API_URL=https://smartsync.codeia.dev" .env 2>/dev/null; then
    sed -i '' 's|DJANGO_API_URL=.*|DJANGO_API_URL=https://smartsync.codeia.dev|g' .env
    echo "✓ URL actualizada a smartsync.codeia.dev"
fi

# 4. Iniciar ngrok para exponer Django
echo -e "\n4️⃣  Iniciando ngrok..."
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no instalado. Instalalo con: brew install ngrok"
    exit 1
fi

# Detener ngrok anterior si existe
pkill -f "ngrok.*8000" 2>/dev/null || true
sleep 1

# Iniciar ngrok en background
ngrok http 8000 -log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
echo "✓ ngrok iniciado (PID: $NGROK_PID)"

# Esperar a que ngrok inicie
sleep 3

# Obtener URL de ngrok
NGROK_URL=$(grep "url=" /tmp/ngrok.log 2>/dev/null | tail -1 | grep -oE 'https://[^"]+' || echo "")
if [ -z "$NGROK_URL" ]; then
    # Intentar via API
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -oE 'https://[^"]+' | head -1 || echo "")
fi

if [ -z "$NGROK_URL" ]; then
    echo "❌ No se pudo obtener URL de ngrok"
    kill $NGROK_PID
    exit 1
fi

echo "✓ URL ngrok: $NGROK_URL"

# 5. Actualizar workflow_builder con la URL de ngrok
echo -e "\n5️⃣  Actualizando workflow_builder.py..."
python3 << PYTHON_EOF
import sys
sys.path.insert(0, '.')
from apps.mcp_integration.services.workflow_builder import SmartSyncWorkflowBuilder
import json

builder = SmartSyncWorkflowBuilder(
    django_api_url="$NGROK_URL",
    django_api_token="$TOKEN"
)

workflow = builder.build()
with open('docs/workflow_current.json', 'w') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("✓ Workflow actualizado con URL: $NGROK_URL")
PYTHON_EOF

# 6. Instrucciones finales
echo -e "\n=========================================="
echo "✅ DEPLOYMENT COMPLETADO"
echo "=========================================="
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1. Ve a n8n: https://n8n.codeia.dev/"
echo "2. Copia el JSON de: docs/workflow_current.json"
echo "3. Importa el workflow en n8n"
echo "4. Activa el workflow (botón verde arriba a la derecha)"
echo ""
echo "5. Prueba con curl:"
echo "   curl -X POST https://n8n.codeia.dev/webhook-test/default/WORKFLOW_ID/appointments/process \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"prompt\": \"cita urgente\", \"user_timezone\": \"America/Mexico_City\"}'"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - ngrok sigue corriendo en background (PID: $NGROK_PID)"
echo "   - Django debe estar activo en localhost:8000"
echo "   - Mantén esta terminal abierta"
echo ""
echo "Para detener:"
echo "   kill $NGROK_PID"
echo ""
