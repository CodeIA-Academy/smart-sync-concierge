#!/bin/bash

################################################################################
# Smart-Sync Concierge - n8n Integration Setup Script
#
# Este script automatiza el setup completo de integración con n8n
#
# Uso:
#   ./scripts/n8n/setup.sh
#
# Requisitos:
#   - Python 3.7+
#   - Django corriendo o preparado
#   - API key de n8n
#   - ngrok (si estás en desarrollo local)
################################################################################

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "================================================================================"
echo "🚀  SMART-SYNC CONCIERGE - N8N INTEGRATION SETUP"
echo "================================================================================"
echo -e "${NC}\n"

# Paso 1: Verificar directorios
echo -e "${YELLOW}[1/5] Verificando configuración...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    echo "Por favor copia .env.example a .env y completa las variables"
    exit 1
fi

if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ No estamos en el directorio raíz del proyecto${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Configuración OK${NC}\n"

# Paso 2: Verificar variables
echo -e "${YELLOW}[2/5] Verificando variables de entorno...${NC}"

N8N_API_KEY=$(grep "N8N_API_KEY=" .env | cut -d= -f2)
DJANGO_API_TOKEN=$(grep "DJANGO_API_TOKEN=" .env | cut -d= -f2)
DJANGO_API_URL=$(grep "DJANGO_API_URL=" .env | cut -d= -f2)

if [ -z "$N8N_API_KEY" ]; then
    echo -e "${RED}❌ N8N_API_KEY no configurada en .env${NC}"
    exit 1
fi

if [ -z "$DJANGO_API_TOKEN" ]; then
    echo -e "${YELLOW}⚠  DJANGO_API_TOKEN no configurada${NC}"
    echo "Generando token Django..."
    python3 manage.py drf_create_token admin || {
        echo -e "${RED}❌ Error al generar token${NC}"
        exit 1
    }
    exit 1
fi

echo -e "${GREEN}✓ Variables configuradas${NC}\n"

# Paso 3: Información
echo -e "${YELLOW}[3/5] Información del setup:${NC}"
echo "   N8N API URL: $(grep 'N8N_API_URL=' .env | cut -d= -f2)"
echo "   Django API URL: $DJANGO_API_URL"
echo "   Django Token: ${DJANGO_API_TOKEN:0:20}..."
echo ""

# Paso 4: Pedir confirmación de URL
echo -e "${YELLOW}[4/5] Configuración de Django API URL...${NC}"

if [ "$DJANGO_API_URL" = "http://localhost:8000" ]; then
    echo -e "${YELLOW}⚠  Detectado: localhost:8000${NC}"
    echo "¿Estás en desarrollo con ngrok?"
    read -p "Ingresa URL de ngrok (ej: https://abc123.ngrok.io) o presiona Enter para localhost: " NGROK_URL

    if [ ! -z "$NGROK_URL" ]; then
        # Actualizar .env
        sed -i '' "s|DJANGO_API_URL=.*|DJANGO_API_URL=$NGROK_URL|" .env
        DJANGO_API_URL=$NGROK_URL
        echo -e "${GREEN}✓ Actualizado a: $DJANGO_API_URL${NC}"
    fi
fi

echo ""

# Paso 5: Ejecutar comando setup
echo -e "${YELLOW}[5/5] Ejecutando setup n8n...${NC}\n"

python3 manage.py setup_n8n_workflow \
    --django-url "$DJANGO_API_URL" \
    --activate

echo ""
echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}✅ SETUP COMPLETADO EXITOSAMENTE${NC}"
echo -e "${GREEN}================================================================================${NC}\n"

echo -e "📚 Documentación:"
echo "   - Guía completa: docs/N8N_WORKFLOW_SETUP.md"
echo "   - Arquitectura: docs/MCP_ARCHITECTURE.md"
echo "   - App: apps/mcp_integration/README.md"
echo ""

echo -e "🧪 Próximo paso: Prueba el webhook con curl"
echo "   curl -X POST https://n8n.codeia.dev/webhook/appointments/process \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"prompt\": \"cita mañana 10am\"}'"
echo ""
