from django.apps import AppConfig


class McpIntegrationConfig(AppConfig):
    """App de integración con n8n.

    Proporciona:
    - Cliente para n8n API
    - Constructor automático de workflows
    - Comando Django para setup
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mcp_integration'
    verbose_name = 'MCP Integration (n8n)'
