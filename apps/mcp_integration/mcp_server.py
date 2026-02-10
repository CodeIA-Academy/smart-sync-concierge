"""
MCP Server para integración con n8n.
Proporciona herramientas para crear y gestionar workflows de n8n.
"""
import json
import logging
from typing import Any, Dict, List
import requests

logger = logging.getLogger(__name__)


class N8NMCP:
    """MCP Server para n8n Integration"""

    def __init__(self, api_url: str, api_key: str):
        """Inicializar MCP de n8n"""
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-N8N-API-KEY": api_key,
            "Content-Type": "application/json"
        }

    def create_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo workflow en n8n"""
        resp = requests.post(
            f"{self.api_url}/api/v1/workflows",
            json=workflow_json,
            headers=self.headers,
            timeout=30
        )
        if resp.status_code not in [200, 201]:
            raise Exception(f"Error crear workflow: {resp.status_code} - {resp.text}")
        return resp.json()

    def update_workflow(self, workflow_id: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar workflow existente"""
        # GET para obtener IDs de nodos
        resp = requests.get(
            f"{self.api_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers,
            timeout=30
        )
        if resp.status_code != 200:
            raise Exception(f"Error obtener workflow: {resp.status_code}")

        current = resp.json()

        # Mapear IDs de nodos
        node_id_map = {}
        if len(current['nodes']) >= len(workflow_json['nodes']):
            for i, new_node in enumerate(workflow_json['nodes']):
                old_id = current['nodes'][i]['id']
                node_id_map[new_node['name']] = old_id
                new_node['id'] = old_id

        # Actualizar conexiones con IDs correctos
        new_connections = {}
        for source_name, conn_data in workflow_json['connections'].items():
            if source_name in node_id_map:
                source_id = node_id_map[source_name]
                new_connections[source_id] = conn_data

                if 'main' in conn_data:
                    for connection_list in conn_data['main']:
                        for connection in connection_list:
                            target_name = connection['node']
                            if target_name in node_id_map:
                                connection['node'] = node_id_map[target_name]

        workflow_json['connections'] = new_connections

        # PUT para actualizar
        update_payload = {
            "nodes": workflow_json['nodes'],
            "connections": workflow_json['connections'],
            "settings": workflow_json.get('settings', {}),
            "name": workflow_json['name']
        }

        resp = requests.put(
            f"{self.api_url}/api/v1/workflows/{workflow_id}",
            json=update_payload,
            headers=self.headers,
            timeout=30
        )
        if resp.status_code != 200:
            raise Exception(f"Error actualizar workflow: {resp.status_code} - {resp.text}")
        return resp.json()

    def activate_workflow(self, workflow_id: str) -> bool:
        """Activar workflow"""
        resp = requests.patch(
            f"{self.api_url}/api/v1/workflows/{workflow_id}/activate",
            headers=self.headers,
            timeout=30
        )
        return resp.status_code in [200, 400]

    def deactivate_workflow(self, workflow_id: str) -> bool:
        """Desactivar workflow"""
        resp = requests.patch(
            f"{self.api_url}/api/v1/workflows/{workflow_id}/deactivate",
            headers=self.headers,
            timeout=30
        )
        return resp.status_code in [200, 400]

    def delete_workflow(self, workflow_id: str) -> bool:
        """Eliminar workflow"""
        resp = requests.delete(
            f"{self.api_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers,
            timeout=30
        )
        return resp.status_code == 204

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Obtener detalles del workflow"""
        resp = requests.get(
            f"{self.api_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers,
            timeout=30
        )
        if resp.status_code != 200:
            raise Exception(f"Error obtener workflow: {resp.status_code}")
        return resp.json()

    def list_workflows(self) -> List[Dict[str, Any]]:
        """Listar todos los workflows"""
        resp = requests.get(
            f"{self.api_url}/api/v1/workflows?limit=100",
            headers=self.headers,
            timeout=30
        )
        if resp.status_code != 200:
            raise Exception(f"Error listar workflows: {resp.status_code}")
        return resp.json()

    def get_executions(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener últimas ejecuciones del workflow"""
        resp = requests.get(
            f"{self.api_url}/api/v1/workflows/{workflow_id}/executions?limit={limit}",
            headers=self.headers,
            timeout=30
        )
        if resp.status_code != 200:
            raise Exception(f"Error obtener executions: {resp.status_code}")
        return resp.json()

    def test_connection(self) -> bool:
        """Probar conexión con n8n"""
        try:
            resp = requests.get(
                f"{self.api_url}/api/v1/workflows?limit=1",
                headers=self.headers,
                timeout=5
            )
            return resp.status_code == 200
        except:
            return False


# Funciones públicas para MCP
def create_and_deploy_workflow(
    n8n_api_url: str,
    n8n_api_key: str,
    django_api_url: str,
    django_api_token: str,
    workflow_name: str = "Smart-Sync Concierge - Appointments"
) -> Dict[str, Any]:
    """Crear e implementar workflow completo en n8n"""
    from apps.mcp_integration.services.workflow_builder import SmartSyncWorkflowBuilder

    # Construir workflow
    builder = SmartSyncWorkflowBuilder(django_api_url, django_api_token)
    workflow = builder.build()

    # Conectar con n8n
    mcp = N8NMCP(n8n_api_url, n8n_api_key)

    # Crear o actualizar workflow
    try:
        # Intentar actualizar si existe
        result = mcp.update_workflow("bLmWJ1oeHFjyt1t7", workflow)
        status = "actualizado"
    except:
        # Si no existe, crear nuevo
        result = mcp.create_workflow(workflow)
        status = "creado"

    # Activar
    workflow_id = result['id']
    mcp.activate_workflow(workflow_id)

    return {
        "status": "success",
        "workflow_id": workflow_id,
        "action": status,
        "webhook_url": f"{n8n_api_url}/webhook/default/{workflow_id}/appointments/process",
        "n8n_url": f"{n8n_api_url}/workflow/{workflow_id}",
        "nodes": len(result['nodes']),
        "active": result.get('active', False)
    }
