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

    El workflow tiene 6 nodos:
    1. Webhook Input: Recibe POST en /webhook/appointments/process
    2. Preparar Datos: Enriquece con metadata (Function node)
    3. HTTP Request (Django): POST a Django API /api/v1/appointments/
    4. HTTP Request (Openrouter): Llamar Haiku 4.5 para generar respuesta personalizada
    5. Procesar Respuesta: Estructura la respuesta final (Function node)
    6. Webhook Response: Devuelve respuesta al usuario

    El flujo es: [1] → [2] → [3] → [4] → [5] → [6]
    """

    def __init__(self, django_api_url: str, django_api_token: str, openrouter_api_key: str = ""):
        """
        Inicializar builder.

        Args:
            django_api_url: URL pública de Django API
            django_api_token: Token de autenticación Django
            openrouter_api_key: API key de Openrouter (opcional)
        """
        self.django_api_url = django_api_url.rstrip('/')
        self.django_api_token = django_api_token
        self.openrouter_api_key = openrouter_api_key
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
                self._node_http_django(),
                self._node_http_openrouter(),
                self._node_process_response(),
                self._node_webhook_response()
            ],
            "connections": self._connections(),
            "settings": {}
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

        Extrae el body del webhook y enriquece con metadata.
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

    def _node_http_django(self) -> Dict[str, Any]:
        """
        Nodo 3: HTTP Request a Django API.

        Procesa la cita y obtiene datos estructurados.
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

    def _node_http_openrouter(self) -> Dict[str, Any]:
        """
        Nodo 4: HTTP Request a Openrouter API.

        Llama a Haiku 4.5 para generar respuesta personalizada al usuario.
        """
        function_code_prepare = '''
// Preparar contexto para Haiku
const django_response = $input.item.json;

const prompt = `Eres un asistente de conserje amable.
El usuario solicitó: "${$json.prompt}"

La cita fue ${django_response.status === 'success' ? 'creada exitosamente' : 'no se pudo crear'}.

${django_response.data ? `Detalles: ${JSON.stringify(django_response.data, null, 2)}` : ''}

Responde de forma amable y personalizada. Sé conciso (1-2 párrafos máximo).`;

return {
  model: "openai/gpt-4-turbo-preview",
  messages: [
    {
      role: "user",
      content: prompt
    }
  ],
  temperature: 0.7,
  max_tokens: 300
};
        '''.strip()

        return {
            "parameters": {
                "method": "POST",
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "Authorization",
                            "value": f"Bearer {self.openrouter_api_key}" if self.openrouter_api_key else "Bearer YOUR_OPENROUTER_KEY"
                        },
                        {
                            "name": "HTTP-Referer",
                            "value": "https://smartsync.dev"
                        }
                    ]
                },
                "sendBody": True,
                "bodyParametersJson": "={{$json}}",
                "options": {
                    "timeout": 30000,
                    "ignoreHttpStatusCode": False
                }
            },
            "name": "Llamar Openrouter (Haiku)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [850, 300]
        }

    def _node_process_response(self) -> Dict[str, Any]:
        """
        Nodo 5: Procesa respuesta de Openrouter y Django.

        Combina la respuesta personalizada de Haiku con los datos de la cita.
        """
        function_code = '''
// Respuesta de Django
const django = $input.item.json;

// Respuesta de Haiku/Openrouter
const haiku = $input.item.json.choices?.[0]?.message?.content || "Solicitud procesada";

return {
  status: django.status || "success",
  message: haiku,
  appointment: django.data || null,
  suggestions: django.suggestions || [],
  trace_id: django.trace_id || "",
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
            "position": [1050, 300]
        }

    def _node_webhook_response(self) -> Dict[str, Any]:
        """
        Nodo 6: Respuesta al usuario (Webhook Response).

        Devuelve la respuesta procesada al cliente.
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
            "position": [1250, 300]
        }

    def _connections(self) -> Dict[str, Any]:
        """
        Define las conexiones entre nodos.

        Flujo: [1] → [2] → [3] → [4] → [5] → [6]
        """
        return {
            "Webhook Input": {
                "main": [[{"node": "Preparar Datos", "type": "main", "index": 0}]]
            },
            "Preparar Datos": {
                "main": [[{"node": "Llamar Django API", "type": "main", "index": 0}]]
            },
            "Llamar Django API": {
                "main": [[{"node": "Llamar Openrouter (Haiku)", "type": "main", "index": 0}]]
            },
            "Llamar Openrouter (Haiku)": {
                "main": [[{"node": "Procesar Respuesta", "type": "main", "index": 0}]]
            },
            "Procesar Respuesta": {
                "main": [[{"node": "Webhook Response", "type": "main", "index": 0}]]
            }
        }
