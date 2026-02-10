"""
Comando Django para crear y activar workflow Smart-Sync en n8n.

Uso:
    python manage.py setup_n8n_workflow --django-url https://abc123.ngrok.io --activate
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.mcp_integration.services.n8n_client import N8NClient
from apps.mcp_integration.services.workflow_builder import SmartSyncWorkflowBuilder
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Crea y activa workflow Smart-Sync en n8n automáticamente'

    def add_arguments(self, parser):
        """Argumentos del comando."""
        parser.add_argument(
            '--django-url',
            type=str,
            help='URL pública de Django API (ej: https://abc123.ngrok.io)',
            required=True
        )
        parser.add_argument(
            '--activate',
            action='store_true',
            help='Activar workflow después de crear',
            default=False
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Reemplazar workflow existente si encuentra uno con el mismo nombre',
            default=False
        )

    def handle(self, *args, **options):
        """Ejecutar comando."""
        self.stdout.write(self.style.SUCCESS("\n" + "="*70))
        self.stdout.write(self.style.SUCCESS("🚀  SETUP DE WORKFLOW SMART-SYNC EN N8N"))
        self.stdout.write(self.style.SUCCESS("="*70 + "\n"))

        # Obtener parametros
        django_url = options.get('django_url', '').rstrip('/')
        activate = options.get('activate', False)
        replace = options.get('replace', False)

        if not django_url:
            raise CommandError("--django-url es requerido")

        self.stdout.write(f"🔧 Configuración:")
        self.stdout.write(f"   N8N API: {settings.N8N_API_URL}")
        self.stdout.write(f"   Django API: {django_url}")
        self.stdout.write(f"   Activar: {'Sí' if activate else 'No'}")
        self.stdout.write(f"   Reemplazar: {'Sí' if replace else 'No'}\n")

        # Paso 1: Conectar a n8n
        self.stdout.write("📡 [1/5] Conectando a n8n...")
        try:
            client = N8NClient()
            if not client.test_connection():
                raise CommandError(
                    f"No se puede conectar a n8n en {settings.N8N_API_URL}\n"
                    "Verifica:\n"
                    "  1. N8N_API_URL está correcto\n"
                    "  2. N8N_API_KEY está configurada\n"
                    "  3. n8n está disponible en línea"
                )
            self.stdout.write(self.style.SUCCESS("✓ Conectado a n8n\n"))
        except Exception as e:
            raise CommandError(f"Error conectando a n8n: {str(e)}")

        # Paso 2: Verificar/eliminar workflow existente
        self.stdout.write("🔍 [2/5] Buscando workflow existente...")
        try:
            existing = client.find_workflow_by_name(settings.N8N_WORKFLOW_NAME)
            if existing:
                if replace:
                    self.stdout.write(f"   Encontrado: {existing.get('id')}")
                    self.stdout.write("   Eliminando...")
                    client.delete_workflow(existing.get('id'))
                    self.stdout.write(self.style.SUCCESS("✓ Workflow anterior eliminado\n"))
                else:
                    raise CommandError(
                        f"Workflow '{settings.N8N_WORKFLOW_NAME}' ya existe (ID: {existing.get('id')})\n"
                        "Usa --replace para reemplazarlo"
                    )
            else:
                self.stdout.write(self.style.SUCCESS("✓ No existe workflow previo\n"))
        except Exception as e:
            if "already exists" not in str(e):
                raise CommandError(f"Error buscando workflow: {str(e)}")

        # Paso 3: Construir workflow
        self.stdout.write("🔨 [3/5] Construyendo workflow...")
        try:
            if not settings.DJANGO_API_TOKEN:
                raise CommandError(
                    "DJANGO_API_TOKEN no está configurado en .env\n"
                    "Genera un token con:\n"
                    "  python manage.py drf_create_token admin"
                )

            builder = SmartSyncWorkflowBuilder(
                django_api_url=django_url,
                django_api_token=settings.DJANGO_API_TOKEN
            )
            workflow_data = builder.build()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Workflow construido ({len(workflow_data['nodes'])} nodos)\n")
            )
        except Exception as e:
            raise CommandError(f"Error construyendo workflow: {str(e)}")

        # Paso 4: Crear workflow en n8n
        self.stdout.write("📤 [4/5] Creando workflow en n8n...")
        try:
            result = client.create_workflow(workflow_data)
            workflow_id = result.get('id')
            if not workflow_id:
                raise CommandError("n8n no retornó ID del workflow")
            self.stdout.write(self.style.SUCCESS(f"✓ Workflow creado: {workflow_id}\n"))
        except Exception as e:
            raise CommandError(f"Error creando workflow: {str(e)}")

        # Paso 5: Activar workflow (opcional)
        if activate:
            self.stdout.write("⚡ [5/5] Activando workflow...")
            try:
                client.activate_workflow(workflow_id)
                self.stdout.write(self.style.SUCCESS("✓ Workflow activado\n"))
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠  Error al activar: {str(e)}\n")
                )
                self.stdout.write("   Puedes activarlo manualmente en n8n UI")
        else:
            self.stdout.write("⏸  [5/5] Workflow NO activado (usa --activate)\n")

        # Resumen final
        webhook_url = f"{settings.N8N_API_URL}/webhook/appointments/process"

        self.stdout.write(self.style.SUCCESS("="*70))
        self.stdout.write(self.style.SUCCESS("✅ SETUP COMPLETADO EXITOSAMENTE"))
        self.stdout.write(self.style.SUCCESS("="*70 + "\n"))

        self.stdout.write(self.style.HTTP_INFO("📋 INFORMACIÓN DEL WORKFLOW:"))
        self.stdout.write(f"   ID: {workflow_id}")
        self.stdout.write(f"   Nombre: {settings.N8N_WORKFLOW_NAME}")
        self.stdout.write(f"   URL Webhook: {webhook_url}")
        self.stdout.write(f"   Estado: {'ACTIVO ✓' if activate else 'INACTIVO (usa --activate)'}")

        self.stdout.write("\n" + self.style.HTTP_INFO("🧪 TESTING DEL WORKFLOW:"))
        self.stdout.write("""
Prueba con curl:

curl -X POST %s \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
        """ % webhook_url)

        self.stdout.write(self.style.HTTP_INFO("\n📊 MONITOREO:"))
        self.stdout.write(f"   Ver workflow en n8n: {settings.N8N_API_URL}/workflow/{workflow_id}")
        self.stdout.write(f"   Ver traces Django: {django_url}/api/v1/traces/")
        self.stdout.write(f"   Ver ejecuciones: {settings.N8N_API_URL}/workflow/{workflow_id}/executions\n")

        self.stdout.write(self.style.SUCCESS("="*70 + "\n"))
