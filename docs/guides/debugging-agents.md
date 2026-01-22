# Debugging de Sistemas Agenticos - Smart-Sync Concierge

Guía completa para diagnosticar y resolver problemas en sistemas multi-agente.

## Fundamentos

### ¿Por qué es Diferente Debuggear Agentes?

Los sistemas agenticos son más difíciles de debuggear que código tradicional porque:

1. **No linealidad**: El output de un agente afecta al siguiente
2. **IA opaca**: El modelo de lenguaje es una caja negra
3. **Estado compartido**: Múltiples agentes modifican el mismo contexto
4. **Async**: La ejecución es asíncrona y distribuida

### Principios de Debugging Agentic

```
1. Observabilidad primero: Ver antes de preguntar
2. Aislar el problema: Identificar el agente específico
3. Reproducir localmente: Simular el escenario
4. Logging estratégico: Logs en puntos clave
5. Tracing completo: Seguir el flujo de principio a fin
```

## Herramientas de Debugging

### 1. OpenTelemetry Jaeger

**Ver traces en tiempo real**:

```bash
# En una terminal, iniciar Jaeger
docker run -d -p 16686:16686 -p 6831:6831 jaegertracing/all-in-one

# Abrir UI
open http://localhost:16686
```

**Buscar traces**:

1. Filtrar por `service.name: "smart-sync"`
2. Buscar por `trace_id` específico
3. Expandir spans para ver input/output de cada agente

### 2. Logging Estructurado

**Configurar logging**:

```python
# core/observability/logger.py
import logging
import json

logger = logging.getLogger(__name__)

class StructuredLogger:
    @staticmethod
    def log_agent_execution(agent_name: str, input_data: dict, output_data: dict):
        logger.info(
            f"Agent={agent_name} | Input={json.dumps(input_data)[:200]} | " +
            f"Output={json.dumps(output_data)[:200]} | " +
            f"Status=success"
        )

    @staticmethod
    def log_agent_error(agent_name: str, error: Exception):
        logger.error(
            f"Agent={agent_name} | Error={type(error).__name__} | " +
            f"Message={str(error)}"
        )
```

### 3. DecisionTrace

**Inspeccionar trace completo**:

```python
# Obtener trace por ID
trace = DecisionTraceStore.get(trace_id="trc_abc123")

# Explicación legible
print(trace.explain())

# Salida:
"""
Trace ID: trc_abc123

1. parsing_agent: entity_extraction
   Razonamiento: Detectada intención de cita médica con fecha relativa

2. temporal_agent: temporal_resolution
   Razonamiento: Usuario en CDMX, 'mañana' resuelto a 2026-01-23

3. availability_agent: conflict_detection
   Razonamiento: Dr. Pérez tiene cita existente en mismo slot
"""
```

### 4. Modo Debug

**Activar logging verbose**:

```python
# config/settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [module:{funcName}:{lineno:d}] {message}',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## Debugging Paso a Paso

### Paso 1: Verificar Request Original

```bash
# Ver request completo
curl -v -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "cita mañana 10am con Dr. Pérez"}'
```

**Qué buscar**:
- ¿El request llegó correctamente? (200, 400, 500)
- ¿El prompt se envió completo?

### Paso 2: Verificar CoordinatorAgent

```python
# En el código, agregar log temporal
class CoordinatorAgent(BaseAgent):
    async def process(self, context: SharedContext):
        print(f"[COORDINATOR] Contexto de entrada: {context._data}")

        results = []
        for agent_class in self.agent_sequence:
            print(f"[COORDINATOR] Ejecutando: {agent_class.name}")
            result = await agent_class().process(context)
            print(f"[COORDINATOR] Resultado: {result}")
            results.append(result)

        return results
```

**Qué buscar**:
- ¿Se ejecutaron todos los agentes?
- ¿Algun agente lanzó excepción?
- ¿El contexto se actualizó entre agentes?

### Paso 3: Verificar ParsingAgent

```python
# Logging en ParsingAgent
class ParsingAgent(BaseAgent):
    async def process(self, context: SharedContext):
        prompt = context.get("prompt")

        # Log antes de llamar a LLM
        logger.info(f"[PARSING] Procesando prompt: {prompt[:100]}")

        llm = LLMFactory.create()
        response = await llm.complete(...)

        # Log respuesta cruda
        logger.debug(f"[PARSING] LLM Response: {response.content[:500]}")

        # Validar JSON
        try:
            result = json.loads(response.content)
            logger.info(f"[PARSING] Parseo exitoso")
        except json.JSONDecodeError as e:
            logger.error(f"[PARSING] JSON inválido: {e}")
            raise

        return result
```

**Qué buscar**:
- ¿El prompt se envía completo al LLM?
- ¿La respuesta del LLM es JSON válido?
- ¿Qué tokens se consumieron?

### Paso 4: Verificar TemporalAgent

```python
# Debugging de resolución temporal
class TemporalAgent(BaseAgent):
    async def process(self, context: SharedContext):
        entities = context.get("parsing_agent")["entities"]

        fecha_raw = entities["fecha"]
        print(f"[TEMPORAL] Fecha cruda: {fecha_raw}")

        # Simular resolución
        if fecha_raw == "mañana":
            resolved = date.today() + timedelta(days=1)
        else:
            resolved = parse_date(fecha_raw)

        print(f"[TEMPORAL] Fecha resuelta: {resolved}")

        # Validar
        is_valid = self._validate_business_hours(resolved)
        print(f"[TEMPORAL] Válido: {is_valid}")

        return TemporalOutput(...)
```

**Qué buscar**:
- ¿La referencia temporal es correcta?
- ¿La zona horaria se considera?
- ¿Las validaciones se aplican correctamente?

### Paso 5: Verificar AvailabilityAgent

```python
# Logging de conflictos
class AvailabilityAgent(BaseAgent):
    async def process(self, context: SharedContext):
        candidate = context.get("candidate_appointment")

        logger.info(f"[AVAILABILITY] Verificando: {candidate.fecha} {candidate.hora_inicio}")

        # Buscar conflictos
        conflicts = self._find_conflicts(candidate)

        if conflicts:
            logger.warning(f"[AVAILABILITY] {len(conflicts)} conflictos encontrados")
            for conflict in conflicts:
                logger.warning(f"[AVAILABILITY] - {conflict.conflicting_appointment_id}")
        else:
            logger.info("[AVAILABILITY] Sin conflictos")

        return AvailabilityOutput(...)
```

## Problemas Comunes y Soluciones

### Problema 1: Baja Precisión de Extracción

**Síntoma**: El ParsingAgent extrae mal las entidades.

**Diagnóstico**:

```python
# Comparar output vs expected
prompt = "cita mañana 10am con Dr. Pérez"
expected = {"fecha": "2026-01-23", "hora": "10:00", "contacto": "Dr. Pérez"}

result = await parsing_agent.process(context)
actual = result.entities

print(f"Expected: {expected}")
print(f"Actual: {actual}")
```

**Solución**: Mejorar el prompt de extracción:

```python
# Añadir más contexto
EXTRACTION_PROMPT = """
Eres un extractor de citas experto.

CONTEXO:
- El negocio es una clínica médica en CDMX
- Los doctores son: Dr. Pérez, Dra. García, Dr. López
- Los servicios son: consulta_general, pediatria, cardiología

{resto_del_prompt}
"""
```

### Problema 2: Falsos Positivos

**Síntoma**: El sistema dice que hay conflicto pero en realidad no lo hay.

**Diagnóstico**:

```python
# Verificar detección de conflictos
conflicts = availability_agent.process(context)

# Buscar manualmente
from apps.appointments.storage import appointment_store
existing = await appointment_store.list_all()

# Buscar overlap manual
for apt in existing:
    if apt.fecha == candidate.fecha:
        if (apt.hora_inicio <= candidate.hora_fin and
            apt.hora_fin >= candidate.hora_inicio):
            print(f"Conflicto real: {apt.id}")
```

**Solución**: Ajustar lógica de detección de overlap.

### Problema 3: Latencia Excesiva

**Síntoma**: El request toma >5 segundos.

**Diagnóstico**:

```python
# Medir tiempo por agente
import time

async def debug_pipeline():
    times = {}

    for agent_class in agent_sequence:
        start = time.time()
        await agent_class().process(context)
        times[agent_class.name] = time.time() - start

    print(f"Tiempos: {times}")
    # Salida: {'ParsingAgent': 1.2, 'TemporalAgent': 0.5, ...}
```

**Solución**:
1. Paralelizar agentes independientes
2. Cachear respuestas de LLM
3. Optimizar prompts (más cortos)

### Problema 4: Contexto No Compartido

**Síntoma**: Un agente no ve los datos del agente anterior.

**Diagnóstico**:

```python
# Verificar SharedContext
print(f"Contexto antes: {context._data}")

await agent1.process(context)

print(f"Contexto después: {context._data}")  # ¿Se actualizó?
```

**Solución**: Asegurar que los agentes actualizan el contexto:

```python
class MiAgente(BaseAgent):
    async def process(self, context: SharedContext):
        # Procesar
        result = await self._logic(context)

        # ACTUALIZAR contexto
        context.update(self.name, result)

        return result
```

## Debugging con Herramientas

### Python Debugger (pdb)

```python
# Insertar breakpoint
async def process(self, context: SharedContext):
    breakpoint()  # Pausa ejecución aquí

    # Inspeccionar variables
    import pdb; pdb.set_trace()

    result = self._logic(context)
    return result
```

### Remote Debugging

```python
# Usando rpdb para debugging remoto
import rpdb

async def process(self, context: SharedContext):
    # Iniciar servidor de debugging
    rpdb.set_trace('localhost', 4444, signal='TERM')

    result = self._logic(context)
    return result
```

## Debugging de LLM

### Ver Request al LLM

```python
# Logging del request
class QwenLLM(BaseLLM):
    async def complete(self, request: LLMRequest) -> LLMResponse:
        logger.info(f"[LLM] Request: {request.prompt[:200]}")
        logger.info(f"[LLM] Temperature: {request.temperature}")
        logger.info(f"[LLM] Max tokens: {request.max_tokens}")

        response = await self.client.chat.completions.create(...)

        logger.info(f"[LLM] Response: {response.choices[0].message.content[:500]}")
        logger.info(f"[LLM] Tokens usados: {response.usage.total_tokens}")

        return response
```

### Ver Calidad de Respuesta

```python
# Validar estructura de respuesta
def validate_llm_response(response: str) -> bool:
    try:
        data = json.loads(response)
        required_fields = ["entities", "confidence"]
        return all(field in data for field in required_fields)
    except:
        return False

# Usar en pruebas
assert validate_llm_response(llm_response.content)
```

## Debugging Async

### Asyncio Debugging

```bash
# Habilitar modo debug de asyncio
PYTHONASYNCIODEBUG=1 python manage.py runserver
```

### Traceback Async

```python
import traceback

async def process(self, context: SharedContext):
    try:
        result = await self._logic(context)
        return result
    except Exception as e:
        # Full traceback async
        traceback.print_exc()
        raise
```

## Casos de Estudio

### Caso 1: Parser no Detecta Contacto

**Problema**: "cita mañana con Dr. Pérez" → contacto = None

**Debugging**:

1. Verificar que el contacto existe en `contacts.json`
2. Verificar que el ParsingAgent recibe los contactos disponibles
3. Verificar el prompt de extracción incluye contactos

**Solución**:

```python
# Asegurar que el prompt incluya contactos
prompt = f"""
{prompt}

CONTACTOS DISPONIBLES:
{contacts_list}
"""
```

### Caso 2: Validación Pasa Pero Hay Conflicto

**Problema**: `validation_agent.is_valid=true` pero `availability_agent` detecta conflicto.

**Debugging**:

1. Verificar orden de agentes
2. ¿ValidationAgent valida disponibilidad o solo reglas?
3. ¿AvailabilityAgent se ejecuta después?

**Solución**:

```python
# ValidationAgent solo valida reglas de negocio
# AvailabilityAgent valida disponibilidad

# Orden correcto:
1. ParsingAgent
2. TemporalAgent
3. ValidationAgent  # Reglas de negocio
4. AvailabilityAgent  # Disponibilidad
5. NegotiationAgent (si aplica)
```

### Caso 3: DecisionTrace Vacío

**Problema**: `trace.decisions` está vacío.

**Debugging**:

1. Verificar que los agentes llamen `context.trace.record_decision()`
2. Verificar que `context.trace` se guarda al final

**Solución**:

```python
# En CoordinatorAgent
async def process(self, context: SharedContext):
    # ...pipeline...

    # Guardar trace al final
    await DecisionTraceStore.save(context.trace)

    return results
```

## Prevención de Problemas

### Testing de Carga

```bash
# Simular 100 requests concurrentes
ab -n 100 -c 10 -p applications.json http://localhost:8000/api/v1/appointments/
```

### Testing de Edge Cases

```python
# Tests de casos extremos
test_cases = [
    "cita en el año 3000",  # Fecha muy futura
    "cita hace 1 segundo",  # Anticipación insuficiente
    "cita con el doctor que no existe",  # Contacto inexistente
    "cita el 32 de febrero",  # Fecha inválida
]

for test_case in test_cases:
    response = await client.post("/api/v1/appointments/", json={
        "prompt": test_case
    })
    print(f"{test_case}: {response.status_code}")
```

## Herramientas de Debugging

### watchmed

```bash
# Monitorear archivos de logs
watchmed "tail -f logs/debug.log"
```

### jq para JSON

```bash
# Formatear respuestas JSON
curl http://localhost:8000/api/v1/appointments/ | jq '.'
```

### grep en traces

```bash
# Buscar traces específicos
grep "cita mañana" data/decisions/decision_log.json
```

---

**Última actualización**: Enero 22, 2026
**Versión**: 0.1.0
**Mantenedor**: Engineering Team
