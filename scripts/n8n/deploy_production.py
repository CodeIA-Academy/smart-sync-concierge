#!/usr/bin/env python3
"""
Script de deployment para flujo n8n en producción.
Sin ngrok, directamente con URL pública de Django.

Uso:
    python3 scripts/n8n/deploy_production.py --django-url https://api.smartsync.dev
"""
import os
import sys
import argparse
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

import django
django.setup()

from apps.mcp_integration.services.n8n_client import N8NClient
from apps.mcp_integration.services.workflow_builder import SmartSyncWorkflowBuilder
from django.conf import settings


def print_header(title):
    """Imprime un encabezado bonito."""
    print("\n" + "=" * 80)
    print(f"  🚀 {title}")
    print("=" * 80 + "\n")


def print_success(msg):
    """Imprime un mensaje de éxito."""
    print(f"✅ {msg}")


def print_error(msg):
    """Imprime un mensaje de error."""
    print(f"❌ {msg}")


def print_info(msg):
    """Imprime un mensaje de información."""
    print(f"ℹ️  {msg}")


def validate_config(django_url):
    """Valida que la configuración sea correcta."""
    print_header("Validando Configuración")

    # Verificar variables de entorno
    if not settings.N8N_API_KEY:
        print_error("N8N_API_KEY no configurada en .env")
        return False
    print_success("N8N_API_KEY configurada")

    if not settings.DJANGO_API_TOKEN:
        print_error("DJANGO_API_TOKEN no configurada en .env")
        return False
    print_success("DJANGO_API_TOKEN configurada")

    print_success(f"Django URL: {django_url}")
    print_success(f"N8N URL: {settings.N8N_API_URL}")

    return True


def test_connectivity():
    """Prueba la conectividad con n8n."""
    print_header("Probando Conectividad")

    client = N8NClient()
    if client.test_connection():
        print_success("Conexión con n8n establecida")
        return True
    else:
        print_error("No se pudo conectar a n8n")
        return False


def deploy_workflow(django_url, replace=False, activate=True):
    """Crea e implementa el workflow."""
    print_header("Creando Workflow")

    client = N8NClient()
    builder = SmartSyncWorkflowBuilder(
        django_api_url=django_url,
        django_api_token=settings.DJANGO_API_TOKEN,
        openrouter_api_key=os.environ.get('OPENROUTER_API_KEY', '')
    )

    workflow_json = builder.build()

    # Buscar si ya existe
    existing = client.find_workflow_by_name(workflow_json['name'])

    if existing and replace:
        print_info(f"Eliminando workflow anterior (ID: {existing['id']})")
        if client.delete_workflow(existing['id']):
            print_success("Workflow anterior eliminado")
        else:
            print_error("No se pudo eliminar workflow anterior")
            return None

    elif existing:
        print_info(f"Workflow ya existe (ID: {existing['id']})")
        print_info("Usa --replace para reemplazarlo")
        return existing

    # Crear workflow
    print_info("Enviando workflow a n8n...")
    result = client.create_workflow(workflow_json)

    if not result:
        print_error("No se pudo crear el workflow")
        return None

    workflow_id = result.get('id')
    print_success(f"Workflow creado (ID: {workflow_id})")

    # Activar si se solicita
    if activate:
        print_info("Activando workflow...")
        if client.activate_workflow(workflow_id):
            print_success("Workflow activado")
        else:
            print_error("No se pudo activar el workflow (puede hacerse manualmente)")

    return result


def show_webhook_info(workflow_id):
    """Muestra información del webhook para testing."""
    print_header("Información del Webhook")

    webhook_url = f"{settings.N8N_API_URL}/webhook/appointments/process"
    dashboard_url = f"{settings.N8N_API_URL}/workflow/{workflow_id}"

    print_info(f"Webhook URL: {webhook_url}")
    print_info(f"Dashboard: {dashboard_url}")

    print("\n📝 Comando de prueba:")
    print(f"""
curl -X POST {webhook_url} \\
  -H "Content-Type: application/json" \\
  -d '{{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }}'
    """.strip())

    print("\n📊 Ver executions:")
    print(f"   Dashboard: {dashboard_url}/executions")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Deploy n8n workflow para Smart-Sync Concierge'
    )
    parser.add_argument(
        '--django-url',
        required=True,
        help='URL pública de Django API (ej: https://api.smartsync.dev)'
    )
    parser.add_argument(
        '--replace',
        action='store_true',
        help='Reemplazar workflow si ya existe'
    )
    parser.add_argument(
        '--no-activate',
        action='store_true',
        help='No activar workflow automáticamente'
    )

    args = parser.parse_args()

    # Validar configuración
    if not validate_config(args.django_url):
        sys.exit(1)

    # Probar conectividad
    if not test_connectivity():
        sys.exit(1)

    # Crear workflow
    result = deploy_workflow(
        django_url=args.django_url,
        replace=args.replace,
        activate=not args.no_activate
    )

    if not result:
        sys.exit(1)

    # Mostrar información
    show_webhook_info(result.get('id'))

    print_header("✨ ¡Deployment Completado!")
    print_info("Próximo paso: Configura la credencial de Openrouter en n8n")
    print_info("  1. Abre el dashboard del workflow")
    print_info("  2. Haz clic en el nodo 'Llamar Openrouter (Haiku)'")
    print_info("  3. Selecciona la credencial de Openrouter del dropdown")
    print_info("  4. Si no está, agrégala en Settings → Credentials → Add")


if __name__ == '__main__':
    main()
