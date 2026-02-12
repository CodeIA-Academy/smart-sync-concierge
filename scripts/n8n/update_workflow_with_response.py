#!/usr/bin/env python3
"""
Script para actualizar workflow existente en n8n.
Agrega el nodo Webhook Response y conecta Gmail → Webhook Response.
"""
import os
import sys
import requests
import json
from typing import Dict, Any

# Añadir el proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

def update_workflow_add_response(
    n8n_api_url: str,
    n8n_api_key: str,
    workflow_id: str
) -> Dict[str, Any]:
    """
    Actualiza un workflow existente para agregar el nodo Webhook Response.

    Args:
        n8n_api_url: URL de n8n (ej: https://n8n.codeia.dev)
        n8n_api_key: API key de n8n
        workflow_id: ID del workflow a actualizar

    Returns:
        Resultado de la actualización
    """
    headers = {
        "X-N8N-API-KEY": n8n_api_key,
        "Content-Type": "application/json"
    }

    print(f"\n📋 Obteniendo workflow actual ({workflow_id})...")

    # Obtener workflow actual
    resp = requests.get(
        f"{n8n_api_url}/api/v1/workflows/{workflow_id}",
        headers=headers,
        timeout=30
    )

    if resp.status_code != 200:
        print(f"❌ Error obteniendo workflow: {resp.status_code}")
        print(resp.text)
        return {"status": "error", "message": f"HTTP {resp.status_code}"}

    workflow = resp.json()
    print(f"✓ Workflow obtenido. Nodos actuales: {len(workflow['nodes'])}")

    # Mostrar nodos actuales
    print("\nNodos actuales:")
    for i, node in enumerate(workflow['nodes'], 1):
        print(f"  {i}. {node['name']} (type: {node['type']})")

    # Crear el nodo Webhook Response
    webhook_response_node = {
        "id": "webhook_response_node",  # n8n lo reemplazará con un UUID
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

    # Agregar el nodo
    workflow['nodes'].append(webhook_response_node)
    print(f"\n✓ Nodo Webhook Response agregado")

    # Actualizar conexiones: Gmail → Webhook Response
    # Primero, encontrar el nodo Gmail
    gmail_node_name = None
    for node in workflow['nodes']:
        if "gmail" in node['type'].lower() or "Enviar" in node['name']:
            gmail_node_name = node['name']
            break

    if gmail_node_name:
        print(f"✓ Encontrado nodo Gmail: {gmail_node_name}")

        # Actualizar conexión del nodo Gmail para apuntar a Webhook Response
        if gmail_node_name in workflow['connections']:
            workflow['connections'][gmail_node_name]['main'][0] = [
                {"node": "Webhook Response", "type": "main", "index": 0}
            ]
        else:
            workflow['connections'][gmail_node_name] = {
                "main": [[{"node": "Webhook Response", "type": "main", "index": 0}]]
            }

        print(f"✓ Conexión actualizada: {gmail_node_name} → Webhook Response")
    else:
        print("⚠ No se encontró nodo Gmail, saltando actualización de conexiones")

    # Agregar conexión para Webhook Response (vacía, es el final)
    workflow['connections']['Webhook Response'] = {"main": [[]]}

    print("\n📤 Enviando actualización a n8n...")

    # Actualizar el workflow
    update_payload = {
        "name": workflow.get('name', 'Smart-Sync Test - Email Response'),
        "nodes": workflow['nodes'],
        "connections": workflow['connections'],
        "settings": workflow.get('settings', {})
    }

    resp = requests.put(
        f"{n8n_api_url}/api/v1/workflows/{workflow_id}",
        json=update_payload,
        headers=headers,
        timeout=30
    )

    if resp.status_code != 200:
        print(f"❌ Error actualizando workflow: {resp.status_code}")
        print(resp.text)
        return {"status": "error", "message": f"HTTP {resp.status_code}"}

    result = resp.json()
    print(f"✓ Workflow actualizado correctamente")
    print(f"✓ Nuevos nodos: {len(result['nodes'])}")

    # Mostrar nodos finales
    print("\nNodos finales:")
    for i, node in enumerate(result['nodes'], 1):
        print(f"  {i}. {node['name']} (type: {node['type']})")

    return {
        "status": "success",
        "workflow_id": workflow_id,
        "nodes_count": len(result['nodes']),
        "active": result.get('active', False),
        "n8n_url": f"{n8n_api_url}/workflow/{workflow_id}"
    }


if __name__ == "__main__":
    # Obtener variables de entorno
    n8n_url = os.environ.get("N8N_API_URL", "https://n8n.codeia.dev")
    n8n_key = os.environ.get("N8N_API_KEY", "")
    workflow_id = os.environ.get("N8N_WORKFLOW_ID", "BkmU9DTalYI0OVml")

    if not n8n_key:
        print("❌ Error: N8N_API_KEY no configurada")
        sys.exit(1)

    print(f"""
╔════════════════════════════════════════╗
║  Actualizar Workflow n8n con Response  ║
╚════════════════════════════════════════╝

n8n URL: {n8n_url}
Workflow ID: {workflow_id}
    """)

    result = update_workflow_add_response(n8n_url, n8n_key, workflow_id)

    print(f"\n{'='*50}")
    if result['status'] == 'success':
        print(f"✅ Workflow actualizado exitosamente")
        print(f"   URL: {result['n8n_url']}")
        print(f"   Nodos: {result['nodes_count']}")
        print(f"   Activo: {result['active']}")
        print(f"\n📝 Para probar el workflow:")
        print(f"   curl -X POST {n8n_url}/webhook/smartsync-test/response \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"prompt\": \"cita mañana 10am\", \"user_id\": \"test\"}}'")
    else:
        print(f"❌ Error: {result.get('message', 'Unknown error')}")
        sys.exit(1)
