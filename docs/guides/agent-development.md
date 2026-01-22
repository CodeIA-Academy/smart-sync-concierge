# Desarrollo de Agentes - Smart-Sync Concierge

Guía completa para crear, implementar y probar agentes en el sistema multi-agente de Smart-Sync Concierge.

## Fundamentos

### ¿Qué es un Agente?

Un **agente** es una entidad especializada que:

1. **Percibe**: Recibe input (SharedContext)
2. **Razona**: Procesa información usando su conocimiento especializado
3. **Actúa**: Produce output para el siguiente agente o el usuario

### Características de un Agente

```python
class MiAgente(BaseAgent):
    # Identidad
    name = "mi_agente"
    version = "1.0.0"

    # Configuración
    recoverable = True  # Si falla, ¿puede continuar?
    fallback = None  # Agente alternativo si falla

    # Procesamiento
    async def process(self, context: SharedContext) -> MiOutput:
        """
        1. Extraer input del contexto
        2. Realizar lógica especializada
        3. Validar resultado
        4. Registrar decisión en trace
        5. Retornar output
        """
        pass
```

## Estructura de un Agente

### Plantilla Base

```python
from core.agents.base_agent import BaseAgent
from core.agents.context import SharedContext
from core.agents.decision_trace import Decision
from core.observability.tracer import traced_agent

@traced_agent("mi_agente")
class MiAgente(BaseAgent):
    """Descripción breve del agente."""

    name = "mi_agente"
    version = "1.0.0"
    recoverable = True
    fallback = None

    async def process(self, context: SharedContext) -> MiOutput:
        """
        Pipeline de procesamiento del agente.

        Args:
            context: SharedContext con datos de agentes previos

        Returns:
            MiOutput con resultado del agente
        """
        # 1. Extraer input del contexto
        input_data = self._extract_input(context)

        # 2. Validar input
        self._validate_input(input_data)

        # 3. Realizar lógica principal
        result = await self._process_logic(input_data)

        # 4. Registrar decisión
        context.trace.record_decision(
            agent=self.name,
            decision="descripcion_decision",
            input=input_data,
            output=result,
            reasoning="Por qué se tomó esta decisión",
            confidence=0.9
        )

        # 5. Retornar output estructurado
        return MiOutput(
            result=result,
            confidence=0.9
        )

    def _extract_input(self, context: SharedContext) -> Dict:
        """Extrae input específico para este agente."""
        return context.get("mi_agente_input", {})

    def _validate_input(self, input_data: Dict):
        """Valida que el input sea correcto."""
        if not input_data:
            raise ValueError("Input requerido para MiAgente")

    async def _process_logic(self, input_data: Dict) -> Any:
        """
        Lógica principal del agente.

        Este es el método principal a implementar.
        """
        # Tu lógica aquí
        pass
```

## Crear un Nuevo Agente

### Paso 1: Definir Responsabilidad

¿Qué problema resuelve tu agente?

```
Ejemplo: "Validar que una cita cumpla con reglas de negocio"

Responsabilidades:
- Contacto existe y está activo
- Servicio está disponible
- Horario es válido
- No es festivo
```

### Paso 2: Definir Interfaz

#### Input

```python
@dataclass
class ValidationInput:
    """Input del ValidationAgent."""
    candidate_appointment: AppointmentCandidate
    business_rules: BusinessRules
    user_context: Dict
```

#### Output

```python
@dataclass
class ValidationOutput:
    """Output del ValidationAgent."""
    is_valid: bool
    validation_errors: List[ValidationError]
    checks: ValidationChecks
    confidence: float
```

### Paso 3: Implementar Lógica

```python
async def _process_logic(self, input: ValidationInput) -> dict:
    """Valida cita contra reglas de negocio."""

    # Validar contacto
    contacto_valido = self._validate_contact(
        input.candidate_appointment.contacto_id,
        input.business_rules
    )

    # Validar servicio
    servicio_valido = self._validate_service(
        input.candidate_appointment.tipo_cita_id,
        input.business_rules
    )

    # Validar horario
    horario_valido = self._validate_business_hours(
        input.candidate_appointment.hora_inicio,
        input.business_rules
    )

    # Compilar resultado
    is_valid = all([contacto_valido, servicio_valido, horario_valido])

    return {
        "is_valid": is_valid,
        "checks": {
            "contacto_valid": contacto_valido,
            "servicio_valid": servicio_valido,
            "horario_valid": horario_valido
        }
    }
```

### Paso 4: Registrar Decisiones

```python
context.trace.record_decision(
    agent=self.name,
    decision="validation_check",
    input={
        "candidate": input.candidate_appointment.__dict__,
        "rules": input.business_rules.__dict__
    },
    output={
        "is_valid": is_valid,
        "checks": checks
    },
    reasoning="Validación completa exitosa" if is_valid else "Fallo en validación",
    confidence=1.0
)
```

## Patrones Comunes

### Agente con LLM

```python
from core.ai import LLMFactory

class LLMasedAgent(BaseAgent):
    """Agente que usa LLM para procesar."""

    async def _process_logic(self, input: Dict) -> Dict:
        # Crear prompt
        template = PromptTemplate.from_file("mi_agente/prompt.txt")
        prompt = template.render(
            user_input=input["user_prompt"],
            contexto=input.get("contexto", "")
        )

        # Llamar a LLM
        llm = LLMFactory.create()
        response = await llm.complete(LLMRequest(
            prompt=prompt,
            response_format="json"
        ))

        # Parsear respuesta
        result = json.loads(response.content)
        return result
```

### Agente con Validación

```python
class ValidatingAgent(BaseAgent):
    """Agente con validación de input."""

    def _validate_input(self, input_data: Dict):
        super()._validate_input(input_data)

        # Validaciones específicas
        if "fecha" not in input_data:
            raise ValueError("fecha es requerido")

        if input_data["fecha"] < date.today():
            raise ValueError("fecha no puede estar en el pasado")

        if "hora" not in input_data:
            # Valor default
            input_data["hora"] = "10:00"
```

### Agente con Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryAgent(BaseAgent):
    """Agente con reintentos automáticos."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def _call_external_service(self, data: Dict):
        """Llama a servicio externo con reintentos."""
        # Tu lógica aquí
        pass
```

## Testing de Agentes

### Unit Tests

```python
import pytest
from core.agents.validation_agent import ValidationAgent
from apps.appointments.schemas import AppointmentCandidate

@pytest.mark.asyncio
async def test_validation_exitosa():
    agent = ValidationAgent()

    input = ValidationInput(
        candidate_appointment=AppointmentCandidate(
            fecha=date(2026, 1, 23),
            hora_inicio=time(10, 0),
            contacto_id="contact_dr_perez",
            tipo_cita_id="consulta_general"
        ),
        business_rules=BusinessRules()
    )

    output = await agent.process(SharedContext(input=input))

    assert output.is_valid
    assert output.checks.contacto_valid

@pytest.mark.asyncio
asyncio
async def test_validation_fallo_contacto_inactivo():
    agent = ValidationAgent()

    input = ValidationInput(
        candidate_appointment=AppointmentCandidate(
            contacto_id="contact_inactivo"  # No está en activos
        ),
        business_rules=BusinessRules()
    )

    output = await agent.process(SharedContext(input=input))

    assert not output.is_valid
    assert not output.checks.contacto_valid
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_pipeline_completo():
    """Test agente en contexto de pipeline."""

    # Preparar contexto
    context = SharedContext()
    context.update("parser_agent", {
        "entities": {
            "fecha": "2026-01-23",
            "hora": "10am",
            "contacto": "Dr. Pérez"
        }
    })

    # Ejecutar agente
    agent = ValidationAgent()
    output = await agent.process(context)

    # Verificar
    assert output.is_valid
```

## Debugging de Agentes

### Logging

```python
import logging

logger = logging.getLogger(__name__)

class DebugAgent(BaseAgent):
    async def process(self, context: SharedContext):
        logger.info(f"Procesando con {self.name}")
        logger.debug(f"Contexto: {context._data}")

        try:
            result = await self._process_logic(...)
            logger.info(f"Resultado exitoso: {result}")
            return result
        except Exception as e:
            logger.error(f"Error en {self.name}: {e}")
            raise
```

### Tracing

Los agentes están automáticamente decorados con `@traced_agent` que:

1. Crea un span de OpenTelemetry
2. Registra input y output
3. Mide latencia
4. Captura errores

Ver traces en: `http://localhost:16686/search` (Jaeger UI)

## Ejemplos de Agentes

### 1. Agente Simple (sin LLM)

```python
class TimeFormatAgent(BaseAgent):
    """Normaliza formatos de hora."""

    name = "time_format_agent"
    version = "1.0.0"

    async def process(self, context: SharedContext) -> TimeFormatOutput:
        hora_raw = context.get("hora")

        # Normalizar: "10am" -> "10:00"
        hora_normalizada = self._normalize_hora(hora_raw)

        return TimeFormatOutput(
            hora_normalizada=hora_normalizada,
            formato_detectado=self._detect_format(hora_raw),
            confidence=1.0
        )
```

### 2. Agente con LLM

```python
class EntityExtractorAgent(BaseAgent):
    """Extrae entidades usando LLM."""

    name = "entity_extractor_agent"
    version = "1.0.0"

    async def process(self, context: SharedContext) -> ExtractionOutput:
        prompt = context.get("prompt")

        # Llamar a LLM
        llm = LLMFactory.create()
        response = await llm.complete(LLMRequest(
            prompt=self._build_extraction_prompt(prompt),
            response_format="json"
        ))

        # Parsear
        entities = json.loads(response.content)

        return ExtractionOutput(
            entities=entities,
            confidence=entities.get("confidence", 0.0)
        )
```

### 3. Agente con Dependencies

```python
class ComplexAgent(BaseAgent):
    """Agente que depende de otros agentes."""

    async def process(self, context: SharedContext) -> ComplexOutput:
        # Esperar que ParsingAgent haya terminado
        parsing_result = context.get("parsing_agent")
        if not parsing_result:
            raise ValueError("ParsingAgent no ha ejecutado aún")

        # Usar resultado del agente previo
        entities = parsing_result["entities"]

        # Lógica adicional
        enriched = await self._enrich_entities(entities)

        return ComplexOutput(enriched=enriched)
```

## Mejores Prácticas

### 1. Mantener Agentes Simples

```python
# ❌ Mal: Agente que hace demasiado
class SuperAgent(BaseAgent):
    async def process(self, context):
        # Valida
        # Extrae entidades
        # Verifica disponibilidad
        # Genera alternativas
        # Envía email
        # ... 200 líneas de código
```

```python
# ✅ Bien: Agentes especializados
class ValidationAgent(BaseAgent):
    async def process(self, context):
        # Solo valida, nada más
        pass

class AvailabilityAgent(BaseAgent):
    async def process(self, context):
        # Solo verifica disponibilidad
        pass
```

### 2. Recuperabilidad de Errores

```python
class RobustAgent(BaseAgent):
    recoverable = True
    fallback = SimpleAgent()  # Fallback a versión simple

    async def safe_process(self, context: SharedContext):
        try:
            return await self.process(context)
        except Exception as e:
            logger.warning(f"Error en RobustAgent: {e}")
            return await self.fallback.process(context)
```

### 3. Testing Exhaustivo

```python
# Tests unitarios para cada método
async def test_extract_input():
    agent = MiAgente()
    context = SharedContext({...})
    # Test
    pass

async def test_validate_input():
    agent = MiAgente()
    with pytest.raises(ValueError):
        agent._validate_input({})
    # Test
    pass

# Tests de integración
async def test_full_pipeline():
    # Test agente en contexto real
    pass
```

## Referencias

- [Contratos de Agentes](../contracts/agents/)
- [BaseAgent en código](../../core/agents/base_agent.py)
- [DecisionTrace](../architecture.md#decision-trace)
- [Observabilidad](../architecture.md#observabilidad-nativa)

---

**Última actualización**: Enero 22, 2026
**Versión**: 0.1.0
**Mantenedor**: AI Team
