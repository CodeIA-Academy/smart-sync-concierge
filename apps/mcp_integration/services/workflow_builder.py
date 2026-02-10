"""
Constructor de workflows n8n para Smart-Sync Concierge.
Genera el JSON completo del workflow de forma programática.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class SmartSyncWorkflowBuilder:
    """
    Constructor del workflow Smart-Sync para n8n.

    El workflow tiene 5 nodos:
    1. Webhook Input: Recibe POST en /webhook/appointments/process
    2. Preparar Datos: Enriquece con metadata (Function node)
    3. HTTP Request: POST a Django API /api/v1/appointments/
    4. Procesar Respuesta: Extrae campos relevantes (Function node)
    5. Webhook Response: Devuelve respuesta al usuario

    El flujo es: [1] → [2] → [3] → [4] → [5]
    """

    def __init__(self, django_api_url: str, django_api_token: str):
        """
        Inicializar builder.

        Args:
            django_api_url: URL pública de Django API
            django_api_token: Token de autenticación Django
        """
        self.django_api_url = django_api_url.rstrip('/')
        self.django_api_token = django_api_token
        logger.info(f"Builder inicializado para {django_api_url}")

    def build(self) -> Dict[str, Any]:
        """
        Construye el JSON completo del workflow.

        Returns:
            Dict con estructura completa del workflow n8n
        """
        workflow = {
            "name": "Smart-Sync Concierge - Appointments",
            "nodes": [
                self._node_webhook_input(),
                self._node_prepare_data(),
                self._node_http_request(),
                self._node_process_response(),
                self._node_webhook_response()
            ],
            "connections": self._connections(),
            "active": False,
            "settings": {
                "saveExecutionProgress": True,
                "saveManualExecutions": True,
                "executionTimeout": 60,
                "errorHandler": "stop"
            }
        }
        logger.info(f"Workflow construido con {len(workflow['nodes'])} nodos")
        return workflow

    def _node_webhook_input(self) -> Dict[str, Any]:
        """
        Nodo 1: Webhook que recibe la solicitud POST.

        Escucha en: /webhook/appointments/process
        Acepta: POST con JSON { prompt, user_timezone, user_id }
        """
        return {
            "parameters": {
                "httpMethod": "POST",
                "path": "appointments/process",
                "responseMode": "responseNode",
                "options": {}
            },
            "name": "Webhook Input",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300],
            "webhookId": "default"
        }

    def _node_prepare_data(self) -> Dict[str, Any]:
        """
        Nodo 2: Preparar datos antes de enviar a Django.

        Extrae el body del webhook y enriquece con metadata:
        - n8n_execution_id: ID de la ejecución en n8n
        - timestamp: Cuándo se recibió
        - source: Origen de la solicitud
        """
        function_code = '''
// Extraer datos del webhook
const body = $input.item.json.body || {};

// Enriquecer con metadata
return {
  prompt: body.prompt || "",
  user_timezone: body.user_timezone || "America/Mexico_City",
  user_id: body.user_id || "anonymous",
  metadata: {
    n8n_execution_id: $execution.id,
    timestamp: new Date().toISOString(),
    source: "n8n_webhook"
  }
};
        '''.strip()

        return {
            "parameters": {
                "functionCode": function_code
            },
            "name": "Preparar Datos",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [450, 300]
        }

    def _node_http_request(self) -> Dict[str, Any]:
        """
        Nodo 3: HTTP Request a Django API.

        Envía POST a: /api/v1/appointments/
        Headers:
          - Authorization: Token {django_api_token}
          - Content-Type: application/json
        Body:
          - prompt
          - user_timezone
          - user_id
        """
        return {
            "parameters": {
                "method": "POST",
                "url": f"{self.django_api_url}/api/v1/appointments/",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "Authorization",
                            "value": f"Token {self.django_api_token}"
                        }
                    ]
                },
                "sendBody": True,
                "bodyParametersJson": "={{$json}}",
                "options": {
                    "timeout": 30000,
                    "redirects": {
                        "follow": True,
                        "maxRedirects": 21
                    },
                    "ignoreHttpStatusCode": False
                }
            },
            "name": "Llamar Django API",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [650, 300]
        }

    def _node_process_response(self) -> Dict[str, Any]:
        """
        Nodo 4: Procesa respuesta de Django.

        Extrae los campos importantes de la respuesta:
        - status: success/error
        - data: Objeto appointment creado
        - suggestions: Alternativas si hay conflicto
        - trace_id: ID de la traza en Django
        """
        function_code = '''
// Obtener respuesta de Django
const response = $input.item.json;

// Estructura de respuesta estándar
return {
  status: response.status || "error",
  message: response.message || response.detail || "",
  data: response.data || response || null,
  suggestions: response.suggestions || [],
  trace_id: response.trace_id || "",
  timestamp: new Date().toISOString()
};
        '''.strip()

        return {
            "parameters": {
                "functionCode": function_code
            },
            "name": "Procesar Respuesta",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [850, 300]
        }

    def _node_webhook_response(self) -> Dict[str, Any]:
        """
        Nodo 5: Respuesta al usuario (Webhook Response).

        Devuelve la respuesta procesada al cliente que envió la solicitud.
        Status HTTP se toma de la respuesta de Django.
        """
        return {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{$json}}",
                "statusCode": "={{$json.statusCode || 200}}",
                "options": {}
            },
            "name": "Webhook Response",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [1050, 300]
        }

    def _connections(self) -> Dict[str, Any]:
        """
        Define las conexiones entre nodos.

        Flujo: [1] → [2] → [3] → [4] → [5]
        """
        return {
            "Webhook Input": {
                "main": [[{"node": "Preparar Datos", "type": "main", "index": 0}]]
            },
            "Preparar Datos": {
                "main": [[{"node": "Llamar Django API", "type": "main", "index": 0}]]
            },
            "Llamar Django API": {
                "main": [[{"node": "Procesar Respuesta", "type": "main", "index": 0}]]
            },
            "Procesar Respuesta": {
                "main": [[{"node": "Webhook Response", "type": "main", "index": 0}]]
            }
        }
