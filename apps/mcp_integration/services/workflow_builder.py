"""
Constructor de workflows n8n para Smart-Sync Concierge.
Genera el JSON completo del workflow de forma programática.
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SmartSyncWorkflowBuilder:
    """
    Constructor del workflow Smart-Sync para n8n.

    El workflow tiene 6 nodos profesionales:
    1. Webhook Input: Recibe POST en /webhook/appointments/process
    2. Preparar Datos: Enriquece con metadata (Function node)
    3. HTTP Request a Django: Procesa la cita
    4. AI Agent: Genera respuesta personalizada con IA
    5. OpenRouter LLM: Modelo Haiku 4.5
    6. Webhook Response: Retorna respuesta al cliente

    El flujo es: [1] → [2] → [3] → [4] ← [5] → [6]
    """

    def __init__(self, django_api_url: str, django_api_token: str, openrouter_api_key: str = ""):
        """
        Inicializar builder.

        Args:
            django_api_url: URL pública de Django API
            django_api_token: Token de autenticación Django
            openrouter_api_key: API key de Openrouter
        """
        self.django_api_url = django_api_url.rstrip('/')
        self.django_api_token = django_api_token
        self.openrouter_api_key = openrouter_api_key
        logger.info(f"Builder inicializado para {django_api_url}")

    def build(self) -> Dict[str, Any]:
        """
        Construye el JSON completo del workflow profesional.

        Returns:
            Dict con estructura completa del workflow n8n
        """
        workflow = {
            "name": "Smart-Sync Concierge - Appointments",
            "nodes": [
                self._node_webhook_input(),
                self._node_prepare_data(),
                self._node_http_django(),
                self._node_ai_agent(),
                self._node_openrouter_llm(),
                self._node_webhook_response()
            ],
            "connections": self._connections(),
            "settings": {}
        }
        logger.info(f"Workflow construido con {len(workflow['nodes'])} nodos")
        return workflow

    def _node_webhook_input(self) -> Dict[str, Any]:
        """
        Nodo 1: Webhook que recibe POST desde Postman/cliente.

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
        Nodo 2: Preparar datos para procesar.

        Extrae y enriquece con metadata.
        """
        function_code = '''const input = $input.item.json;
const data = input.body || input;
return {
  prompt: data.prompt || "",
  user_timezone: data.user_timezone || "Europe/Madrid",
  user_id: data.user_id || "anonymous",
  metadata: {
    n8n_execution_id: $execution.id,
    timestamp: new Date().toISOString(),
    source: "n8n_webhook"
  }
};'''

        return {
            "parameters": {
                "functionCode": function_code
            },
            "name": "Preparar Datos",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [450, 300]
        }

    def _node_http_django(self) -> Dict[str, Any]:
        """
        Nodo 3: HTTP Request a Django API.

        Procesa la cita en Django y retorna datos estructurados.
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
                        },
                        {
                            "name": "Content-Type",
                            "value": "application/json"
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

    def _node_ai_agent(self) -> Dict[str, Any]:
        """
        Nodo 4: AI Agent que genera respuesta personalizada.

        Usa el modelo LLM de OpenRouter (Haiku 4.5).
        """
        return {
            "parameters": {
                "agentType": "openAiFunctionsAgent",
                "input": "={{$json.prompt}}",
                "tools": [],
                "model": {
                    "value": {
                        "__rl": True,
                        "value": "OpenRouter Chat Model",
                        "resource": "openRouterModel"
                    }
                },
                "options": {
                    "maxIterations": 10
                }
            },
            "name": "AI Agent (Haiku)",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 3.1,
            "position": [850, 300]
        }

    def _node_openrouter_llm(self) -> Dict[str, Any]:
        """
        Nodo 5: OpenRouter Chat Model con Haiku 4.5.

        Proporciona el LLM al AI Agent.
        """
        return {
            "parameters": {
                "model": "openrouter/anthropic/claude-haiku-4.5:beta",
                "options": {
                    "temperature": 0.7,
                    "maxTokens": 300
                }
            },
            "name": "OpenRouter Chat Model",
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenRouter",
            "typeVersion": 1,
            "position": [850, 450],
            "credentials": {
                "openRouterApi": {
                    "id": "openRouterApi",
                    "name": "OpenRouter API"
                }
            }
        }

    def _node_webhook_response(self) -> Dict[str, Any]:
        """
        Nodo 6: Webhook Response que retorna al cliente.

        Devuelve la respuesta del AI Agent en JSON.
        """
        return {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{$json}}",
                "statusCode": 200,
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

        Flujo principal: [1] → [2] → [3] → [4] → [6]
        El nodo 5 (OpenRouter LLM) está conectado al nodo 4 (AI Agent)
        """
        return {
            "Webhook Input": {
                "main": [[{"node": "Preparar Datos", "type": "main", "index": 0}]]
            },
            "Preparar Datos": {
                "main": [[{"node": "Llamar Django API", "type": "main", "index": 0}]]
            },
            "Llamar Django API": {
                "main": [[{"node": "AI Agent (Haiku)", "type": "main", "index": 0}]]
            },
            "AI Agent (Haiku)": {
                "main": [[{"node": "Webhook Response", "type": "main", "index": 0}]]
            },
            "OpenRouter Chat Model": {}
        }
