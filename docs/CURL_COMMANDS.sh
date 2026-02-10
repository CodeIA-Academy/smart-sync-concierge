#!/bin/bash
# Comandos curl para probar el workflow n8n desde Postman o terminal

# Variables
N8N_WEBHOOK="https://n8n.codeia.dev/webhook/appointments/process"

# ========================================
# 1. Test Simple - Cardiología
# ========================================
echo "Test 1: Cardiología"
curl -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "necesito una cita con cardiólogo para la próxima semana",
    "user_timezone": "America/Mexico_City",
    "user_id": "patient_001"
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

# ========================================
# 2. Test - Medicina General
# ========================================
echo "Test 2: Medicina General"
curl -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "necesito un chequeo general para mañana",
    "user_timezone": "Europe/Madrid",
    "user_id": "patient_002"
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

# ========================================
# 3. Test - Urgencia
# ========================================
echo "Test 3: Urgencia"
curl -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita urgente hoy mismo si es posible",
    "user_timezone": "America/New_York",
    "user_id": "patient_003"
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

# ========================================
# 4. Test - Mínimal (solo prompt)
# ========================================
echo "Test 4: Mínimal"
curl -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am"
  }' \
  -w "\nHTTP Status: %{http_code}\n"
