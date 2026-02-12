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

    def _node_webhook_input(self, path: str = "appointments/process", webhook_id: str = "default") -> Dict[str, Any]:
        """
        Nodo 1: Webhook que recibe POST desde Postman/cliente.

        Escucha en: /webhook/{path}
        Acepta: POST con JSON { prompt, user_timezone, user_id }
        """
        return {
            "parameters": {
                "httpMethod": "POST",
                "path": path,
                "responseMode": "responseNode",
                "options": {}
            },
            "name": "Webhook Input",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300],
            "webhookId": webhook_id
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

    def build_simple_test_workflow(self, webhook_path: str = "appointments/test-simple", webhook_id: str = "smartsync_webhook") -> Dict[str, Any]:
        """
        Construye un workflow SIMPLE para pruebas sin IA Agent.

        4 nodos:
        1. Webhook Input: Recibe solicitud
        2. Generar Respuesta: Function node que procesa los datos
        3. Gmail: Envía respuesta por email
        4. Webhook Response: Devuelve respuesta al cliente

        Este workflow es para testear el flujo básico sin AI Agent.
        """
        workflow = {
            "name": "Smart-Sync Test - Email Response",
            "nodes": [
                self._node_webhook_input(path=webhook_path, webhook_id=webhook_id),
                self._node_generate_response_simple(),
                self._node_send_email(),
                self._node_webhook_response_only()
            ],
            "connections": self._connections_simple_with_response(),
            "settings": {}
        }
        logger.info(f"Workflow de prueba construido con {len(workflow['nodes'])} nodos")
        return workflow

    def _node_generate_response_simple(self) -> Dict[str, Any]:
        """
        Nodo Function que genera respuesta simple sin IA.

        Toma los datos del webhook y genera una respuesta estructurada.
        """
        function_code = '''const input = $input.item.json;
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

        return {
            "parameters": {
                "functionCode": function_code
            },
            "name": "Generar Respuesta",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [450, 300]
        }

    def _node_send_email(self) -> Dict[str, Any]:
        """
        Nodo Gmail para enviar la respuesta por email.

        Envía a: yosnap@gmail.com
        """
        return {
            "parameters": {
                "toEmail": "yosnap@gmail.com",
                "subject": "Solicitud de Cita Recibida - Smart-Sync",
                "message": "={{$json.message}}",
                "options": {}
            },
            "name": "Enviar por Email",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2,
            "position": [650, 300],
            "credentials": {
                "gmailOAuth2": {
                    "id": "gmailOAuth2",
                    "name": "Gmail OAuth2"
                }
            }
        }

    def _connections_simple(self) -> Dict[str, Any]:
        """
        Conexiones para workflow simple (sin IA Agent, sin respuesta HTTP).

        Flujo: [1] Webhook → [2] Generar Respuesta → [3] Gmail
        """
        return {
            "Webhook Input": {
                "main": [[{"node": "Generar Respuesta", "type": "main", "index": 0}]]
            },
            "Generar Respuesta": {
                "main": [[{"node": "Enviar por Email", "type": "main", "index": 0}]]
            },
            "Enviar por Email": {
                "main": [[]]
            }
        }

    def _connections_simple_with_response(self) -> Dict[str, Any]:
        """
        Conexiones para workflow con Gmail y respuesta HTTP.

        Flujo: [1] Webhook → [2] Generar Respuesta → [3] Gmail → [4] Webhook Response
        """
        return {
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
        }

    def _node_webhook_response_only(self) -> Dict[str, Any]:
        """
        Nodo Webhook Response que devuelve la respuesta generada.

        Solo para testing sin dependencias externas.
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
            "position": [650, 300]
        }

    def _connections_simple_no_deps(self) -> Dict[str, Any]:
        """
        Conexiones sin dependencias externas.

        Flujo: [1] Webhook → [2] Generar Respuesta → [3] Webhook Response
        """
        return {
            "Webhook Input": {
                "main": [[{"node": "Generar Respuesta", "type": "main", "index": 0}]]
            },
            "Generar Respuesta": {
                "main": [[{"node": "Webhook Response", "type": "main", "index": 0}]]
            },
            "Webhook Response": {
                "main": [[]]
            }
        }

    def build_simple_test_workflow_no_deps(self, webhook_path: str = "smartsync-test/response", webhook_id: str = "smartsync_test_webhook") -> Dict[str, Any]:
        """
        Workflow sin dependencias externas (sin Gmail, sin AI Agent).

        Solo devolverá la respuesta al cliente sin enviar email.
        Este es el workflow más simple para testear la funcionalidad básica.
        """
        workflow = {
            "name": "Smart-Sync Test - Simple Response (No Deps)",
            "nodes": [
                self._node_webhook_input(path=webhook_path, webhook_id=webhook_id),
                self._node_generate_response_simple(),
                self._node_webhook_response_only()
            ],
            "connections": self._connections_simple_no_deps(),
            "settings": {}
        }
        logger.info(f"Workflow sin deps construido con {len(workflow['nodes'])} nodos")
        return workflow
