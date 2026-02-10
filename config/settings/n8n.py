"""
Configuración para integración con n8n.
Archivo separado para mantener modularidad.
"""
import os

# ============================================================================
# N8N API CONFIGURATION
# ============================================================================

# URL base de n8n API
N8N_API_URL = os.environ.get('N8N_API_URL', 'https://n8n.codeia.dev')

# API key JWT para autenticarse con n8n
N8N_API_KEY = os.environ.get('N8N_API_KEY', '')

# ============================================================================
# DJANGO API CONFIGURATION (para que n8n lo llame)
# ============================================================================

# URL pública de la API Django (para n8n llamarla)
# Desarrollo: usar ngrok URL (https://abc123.ngrok.io)
# Producción: usar dominio real (https://api.smartsync.dev)
DJANGO_API_URL = os.environ.get('DJANGO_API_URL', 'http://localhost:8000')

# Token de autenticación Django para que n8n se autentique
# Generar con: python manage.py drf_create_token admin
DJANGO_API_TOKEN = os.environ.get('DJANGO_API_TOKEN', '')

# ============================================================================
# WEBHOOK SECURITY (Opcional, para producción)
# ============================================================================

# Secreto para validar firma HMAC de webhooks
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')

# Habilitar verificación de firma HMAC
WEBHOOK_VERIFY_SIGNATURE = os.environ.get('WEBHOOK_VERIFY_SIGNATURE', 'False') == 'True'

# ============================================================================
# WORKFLOW SETTINGS
# ============================================================================

# Nombre del workflow en n8n
N8N_WORKFLOW_NAME = "Smart-Sync Concierge - Appointments"

# Timeout máximo para ejecución de workflow (segundos)
N8N_WORKFLOW_TIMEOUT = 60

# Ruta del webhook en n8n
N8N_WEBHOOK_PATH = "appointments/process"
