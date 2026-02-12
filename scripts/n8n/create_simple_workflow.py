#!/usr/bin/env python3
"""
Script para crear un nuevo workflow simple en n8n desde cero.
Evita los problemas de registro de webhooks con un flujo limpio.
"""
import os
import sys
import requests
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

def create_simple_workflow(
    n8n_api_url: str,
    n8n_api_key: str
) -> dict:
    """
    Crea un workflow simple desde cero.
    4 nodos: Webhook Input → Generar Respuesta → Enviar por Email → Webhook Response
    """
    headers = {
        "X-N8N-API-KEY": n8n_api_key,
        "Content-Type": "application/json"
    }

    workflow = {
        "name": "Smart-Sync Test - Complete Flow",
        "nodes": [
            {
                "id": "webhook_input",
                "name": "Webhook Input",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "smartsync-test",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "webhookId": "smartsync_test_simple"
            },
            {
                "id": "generar_respuesta",
                "name": "Generar Respuesta",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [450, 300],
                "parameters": {
                    "functionCode": '''const input = $input.item.json;
const data = input.body || input;

const appointment = {
  prompt: data.prompt || "Sin especificar",
  timezone: data.user_timezone || "Europe/Madrid",
  user_id: data.user_id || "anonymous",
  created_at: new Date().toISOString(),
  status: "pendiente_confirmacion"
};

const response_message = `
Solicitud de Cita Recibida
==========================

Detalles:
- Solicitud: ${appointment.prompt}
- Zona Horaria: ${appointment.timezone}
- Usuario ID: ${appointment.user_id}
- Fecha: ${appointment.created_at}
- Estado: ${appointment.status}

Pronto recibirás confirmación de tu cita.
`;

return {
  appointment: appointment,
  message: response_message,
  notification_needed: true
};'''
                }
            },
            {
                "id": "enviar_email",
                "name": "Enviar por Email",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [650, 300],
                "parameters": {
                    "toEmail": "yosnap@gmail.com",
                    "subject": "Solicitud de Cita Recibida - Smart-Sync",
                    "message": "={{$json.message}}",
                    "options": {}
                },
                "credentials": {
                    "gmailOAuth2": {
                        "id": "gmailOAuth2",
                        "name": "Gmail OAuth2"
                    }
                }
            },
            {
                "id": "webhook_response",
                "name": "Webhook Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [850, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{$json}}",
                    "statusCode": 200,
                    "options": {}
                }
            }
        ],
        "connections": {
            "Webhook Input": {
                "main": [[{"node": "Generar Respuesta", "type": "main", "index": 0}]]
            },
            "Generar Respuesta": {
                "main": [[{"node": "Enviar por Email", "type": "main", "index": 0}]]
            },
            "Enviar por Email": {
                "main": [[{"node": "Webhook Response", "type": "main", "index": 0}]]
            },
            "Webhook Response": {
                "main": [[]]
            }
        },
        "settings": {}
    }

    print(f"\n📝 Creando workflow nuevo...")

    # Crear workflow
    resp = requests.post(
        f"{n8n_api_url}/api/v1/workflows",
        json=workflow,
        headers=headers,
        timeout=30
    )

    if resp.status_code not in [200, 201]:
        print(f"❌ Error creando workflow: {resp.status_code}")
        print(resp.text)
        return {"status": "error", "message": f"HTTP {resp.status_code}"}

    result = resp.json()
    workflow_id = result['id']
    print(f"✓ Workflow creado: {workflow_id}")
    print(f"✓ Nombre: {result['name']}")
    print(f"✓ Nodos: {len(result['nodes'])}")

    # Listar nodos creados
    print("\nNodos creados:")
    for i, node in enumerate(result['nodes'], 1):
        print(f"  {i}. {node['name']} ({node['type']})")

    # Activar workflow
    print(f"\n🔄 Activando workflow...")
    resp = requests.post(
        f"{n8n_api_url}/api/v1/workflows/{workflow_id}/activate",
        headers=headers,
        timeout=30
    )

    if resp.status_code in [200, 400]:
        print(f"✓ Workflow activado")
    else:
        print(f"⚠ Status al activar: {resp.status_code}")

    # Construir webhook URL
    webhook_node = None
    for node in result['nodes']:
        if 'webhook' in node['type'].lower():
            webhook_node = node
            break

    webhook_url = None
    if webhook_node:
        webhook_id = webhook_node.get('webhookId', 'default')
        path = webhook_node['parameters'].get('path', '')
        webhook_url = f"{n8n_api_url}/webhook/{webhook_id}/{workflow_id}/{path}"

    return {
        "status": "success",
        "workflow_id": workflow_id,
        "workflow_name": result['name'],
        "nodes_count": len(result['nodes']),
        "active": result.get('active', False),
        "webhook_url": webhook_url,
        "n8n_url": f"{n8n_api_url}/workflow/{workflow_id}"
    }


if __name__ == "__main__":
    n8n_url = os.environ.get("N8N_API_URL", "https://n8n.codeia.dev")
    n8n_key = os.environ.get("N8N_API_KEY", "")

    if not n8n_key:
        print("❌ Error: N8N_API_KEY no configurada")
        sys.exit(1)

    print(f"""
╔════════════════════════════════════════╗
║    Crear Workflow Simple en n8n        ║
╚════════════════════════════════════════╝

n8n URL: {n8n_url}
    """)

    result = create_simple_workflow(n8n_url, n8n_key)

    print(f"\n{'='*60}")
    if result['status'] == 'success':
        print(f"✅ Workflow creado exitosamente")
        print(f"\nDetalles:")
        print(f"  Workflow ID: {result['workflow_id']}")
        print(f"  Nombre: {result['workflow_name']}")
        print(f"  Nodos: {result['nodes_count']}")
        print(f"  Activo: {result['active']}")
        print(f"\nURLs:")
        print(f"  n8n UI: {result['n8n_url']}")
        if result['webhook_url']:
            print(f"  Webhook: {result['webhook_url']}")
        print(f"\n📝 Para probar el workflow:")
        if result['webhook_url']:
            print(f"   curl -X POST {result['webhook_url']} \\")
            print(f"     -H 'Content-Type: application/json' \\")
            print(f"     -d '{{\"prompt\": \"cita mañana 10am\", \"user_id\": \"test\"}}'")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")
        sys.exit(1)
