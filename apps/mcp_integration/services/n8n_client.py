"""
Cliente para interactuar con n8n API.
Proporciona métodos para crear, actualizar, activar y eliminar workflows.
"""
import requests
from typing import Dict, Any, List, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class N8NClient:
    """
    Cliente para n8n API v1.

    Métodos disponibles:
    - create_workflow(): Crear nuevo workflow
    - activate_workflow(): Activar workflow
    - deactivate_workflow(): Desactivar workflow
    - get_workflow(): Obtener detalles de workflow
    - list_workflows(): Listar todos los workflows
    - delete_workflow(): Eliminar workflow
    - get_executions(): Ver historial de ejecuciones
    - test_connection(): Verificar conectividad
    """

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 30
    ):
        """
        Inicializar cliente n8n.

        Args:
            base_url: URL base de n8n (ej: https://n8n.codeia.dev)
            api_key: API key JWT de n8n
            timeout: Timeout para requests (segundos)
        """
        self.base_url = (base_url or settings.N8N_API_URL).rstrip('/')
        self.api_key = api_key or settings.N8N_API_KEY
        self.timeout = timeout
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    def test_connection(self) -> bool:
        """
        Verifica que se puede conectar a n8n.

        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            response = requests.get(
                f"{self.base_url}/healthz",
                timeout=self.timeout
            )
            is_healthy = response.status_code == 200
            if is_healthy:
                logger.info(f"✓ Conectado a n8n en {self.base_url}")
            else:
                logger.warning(f"⚠ n8n respondió con código {response.status_code}")
            return is_healthy
        except Exception as e:
            logger.error(f"✗ Error conectando a n8n: {str(e)}")
            return False

    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo workflow en n8n.

        Args:
            workflow_data: JSON con definición del workflow

        Returns:
            Respuesta de n8n con detalles del workflow creado

        Raises:
            requests.exceptions.RequestException: Si hay error HTTP
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                json=workflow_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✓ Workflow creado con ID: {result.get('id')}")
            return result
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ Error HTTP creando workflow: {e.response.text}")
            raise

    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Activa un workflow.

        Args:
            workflow_id: ID del workflow a activar

        Returns:
            Respuesta de n8n con estado actualizado

        Raises:
            requests.exceptions.RequestException: Si hay error HTTP
        """
        try:
            response = requests.patch(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json={"active": True},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"✓ Workflow {workflow_id} activado")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ Error activando workflow: {e.response.text}")
            raise

    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Desactiva un workflow.

        Args:
            workflow_id: ID del workflow a desactivar

        Returns:
            Respuesta de n8n con estado actualizado

        Raises:
            requests.exceptions.RequestException: Si hay error HTTP
        """
        try:
            response = requests.patch(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json={"active": False},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"✓ Workflow {workflow_id} desactivado")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ Error desactivando workflow: {e.response.text}")
            raise

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Obtiene detalles de un workflow específico.

        Args:
            workflow_id: ID del workflow

        Returns:
            Objeto workflow con todos sus detalles

        Raises:
            requests.exceptions.RequestException: Si hay error HTTP
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ Error obteniendo workflow: {e.response.text}")
            raise

    def list_workflows(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Lista todos los workflows.

        Args:
            limit: Máximo número de workflows a retornar
            skip: Número de workflows a saltar (para paginación)

        Returns:
            Lista de workflows

        Raises:
            requests.exceptions.RequestException: Si hay error HTTP
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                params={"limit": limit, "skip": skip},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            # La respuesta puede ser una lista directa o un objeto con "data"
            workflows = data if isinstance(data, list) else data.get("data", [])
            logger.info(f"✓ Encontrados {len(workflows)} workflows")
            return workflows
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ Error listando workflows: {e.response.text}")
            raise

    def delete_workflow(self, workflow_id: str) -> None:
        """
        Elimina un workflow.

        Args:
            workflow_id: ID del workflow a eliminar

        Raises:
            requests.exceptions.RequestException: Si hay error HTTP
        """
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"✓ Workflow {workflow_id} eliminado")
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ Error eliminando workflow: {e.response.text}")
            raise

    def get_executions(
        self,
        workflow_id: str,
        limit: int = 10,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Obtiene historial de ejecuciones de un workflow.

        Args:
            workflow_id: ID del workflow
            limit: Máximo número de ejecuciones a retornar
            skip: Número de ejecuciones a saltar

        Returns:
            Lista de ejecuciones

        Raises:
            requests.exceptions.RequestException: Si hay error HTTP
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/executions",
                headers=self.headers,
                params={
                    "workflowId": workflow_id,
                    "limit": limit,
                    "skip": skip
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            executions = data if isinstance(data, list) else data.get("data", [])
            logger.info(f"✓ Encontradas {len(executions)} ejecuciones")
            return executions
        except requests.exceptions.HTTPError as e:
            logger.error(f"✗ Error obteniendo ejecuciones: {e.response.text}")
            raise

    def find_workflow_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Busca un workflow por nombre.

        Args:
            name: Nombre del workflow

        Returns:
            El workflow si se encuentra, None en caso contrario
        """
        try:
            workflows = self.list_workflows()
            for workflow in workflows:
                if workflow.get("name") == name:
                    logger.info(f"✓ Workflow '{name}' encontrado: {workflow.get('id')}")
                    return workflow
            logger.warning(f"⚠ Workflow '{name}' no encontrado")
            return None
        except Exception as e:
            logger.error(f"✗ Error buscando workflow por nombre: {str(e)}")
            return None
