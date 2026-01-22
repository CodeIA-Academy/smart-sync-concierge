# Runbook: Fallo de Agente

## Versión
1.0.0

## Propósito

Guía paso a paso para diagnosticar y resolver fallos en agentes del sistema Smart-Sync Concierge.

---

## 🚨 Síntomas de Fallo

### Indicadores de Alerta

```
- Agent returns 500 error
- Timeout en ejecución (>30s)
- Output con confidence < 0.5
- DecisionTrace con decisiones vacías
- LLM rate limiting
```

### Métricas de Monitoreo

```yaml
critical_alerts:
  - agent_errors_total > 10 en 5min
  - agent_execution_duration_seconds p95 > 10s
  - llm_tokens_used_total > límite de cuota

warning_indicators:
  - confidence_avg < 0.7
  - retry_rate > 20%
  - parsing_ambiguity_rate > 30%
```

---

## 🔍 Diagnóstico Paso a Paso

### Paso 1: Identificar el Agente Fallido

```bash
# Ver logs recientes
tail -f logs/smart-sync.log | grep ERROR

# Buscar por agente específico
grep "parsing_agent" logs/smart-sync.log | tail -20

# Ver métricas en Jaeger
# http://localhost:16686
# Buscar: service.name="smart-sync", operation.name="parsing_agent.process"
```

**Qué buscar**:
- ¿Cuál agente falló? (parsing, temporal, geo, validation, availability, negotiation)
- ¿Error es transitorio o persistente?
- ¿Afecta a todos los requests o solo casos específicos?

### Paso 2: Obtener el Trace Completo

```bash
# Del response, obtener trace_id
# Ejemplo: "trace_id": "trc_abc123"

# Consultar trace
curl http://localhost:8000/api/v1/traces/trc_abc123/

# O vía admin
# http://localhost:8000/admin/traces/trc_abc123/
```

**Output esperado**:
```json
{
  "id": "trc_abc123",
  "decisions": [
    {
      "agent": "parsing_agent",
      "decision": "entity_extraction",
      "reasoning": "...",
      "error": "LLM timeout after 30s"
    }
  ]
}
```

### Paso 3: Reproducir el Error Localmente

```python
# En Python shell
import asyncio
from apps.appointments.agents.parsing_agent import ParsingAgent
from core.agents.context import SharedContext

async def test():
    context = SharedContext()
    context.update("user_prompt", {
        "prompt": "cita mañana 10am con Dr. Pérez",
        "timezone": "America/Mexico_City"
    })

    agent = ParsingAgent()
    try:
        result = await agent.process(context)
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        # Ver traceback completo
        import traceback
        traceback.print_exc()

asyncio.run(test())
```

### Paso 4: Verificar el Input del Agente

```python
# Ver qué recibió el agente
print("Input:", context.get("parsing_agent"))

# Verificar que el SharedContext tenga lo necesario
print("Contexto completo:", context._data)
```

**Problemas comunes de input**:
- Contexto vacío o mal formado
- Datos del agente anterior faltantes
- Timezone inválido
- Prompt muy largo (>500 chars)

---

## 🛠️ Soluciones por Agente

### ParsingAgent

#### Problema: Baja Precisión

**Síntoma**: `confidence < 0.7` en entities extraídas

**Diagnóstico**:
```python
# Ver output del LLM
response = await llm.complete(request)
print("LLM Response:", response.content)
print("Tokens:", response.usage.total_tokens)
```

**Solución 1**: Mejorar prompt
```python
# core/ai/prompts/templates/extraction.txt
# Añadir ejemplos específicos del negocio

EJEMPLOS:
Input: "cita con el doctor"
Output: {"contacto": null, "ambigüedad": "¿Cuál doctor?"}

Input: "cita mañana 10am con Dr. Pérez"
Output: {"contacto": "Dr. Pérez", "fecha": "mañana", "hora": "10am"}
```

**Solución 2**: Ajustar temperatura
```python
# core/ai/providers/qwen_provider.py
# Reducir temperatura para respuestas más deterministas
temperature = 0.1  # bajar de 0.5
```

#### Problema: LLM Timeout

**Síntoma**: `TimeoutError after 30s`

**Diagnóstico**:
```bash
# Ver si es problema de red o del proveedor
curl -X POST https://api.qwen.example.com/v1/chat/completions \
  -H "Authorization: Bearer $QWEN_API_KEY" \
  -d '{"model": "qwen-2.5", "messages": [{"role": "user", "content": "test"}]}'
```

**Solución**: Aumentar timeout
```python
# core/ai/providers/qwen_provider.py
timeout = 60  # aumentar de 30 a 60 segundos
```

#### Problema: JSON Inválido

**Síntoma**: `JSONDecodeError: Expecting value`

**Diagnóstico**:
```python
# Ver respuesta cruda
print("Raw response:", response.content)

# Validar antes de parsear
import json
try:
    data = json.loads(response.content)
except json.JSONDecodeError:
    # Reintentar con prompt más estricto
    retry_response = await llm.complete(retry_request)
```

**Solución**: Prompt más estricto
```python
EXTRACTION_PROMPT_STRICT = """
Debes responder ÚNICAMENTE con JSON válido.
Sin texto antes o después.
Sin markdown (```json ... ```).

Solo el JSON puro.
"""
```

### TemporalAgent

#### Problema: Resolución Incorrecta

**Síntoma**: "mañana" resuelto a fecha equivocada

**Diagnóstico**:
```python
# Ver referencia temporal
reference = context.get("reference_date")
print("Reference date:", reference)  # ¿Es la fecha correcta?

# Ver timezone
user_tz = context.get("user_timezone")
print("User timezone:", user_tz)  # ¿Es "America/Mexico_City"?
```

**Solución**: Corregir referencia
```python
# Asegurar que reference_date esté en TZ del usuario
from datetime import datetime
import pytz

now = datetime.now(pytz.timezone(user_tz))
context.update("reference_date", now)
```

#### Problema: Validación Rechaza Todo

**Síntoma**: Todas las citas marcan `outside_hours`

**Diagnóstico**:
```python
# Ver reglas de negocio
rules = context.get("business_rules")
print("Business hours:", rules.horario_laboral)
# ¿Son correctos? {"inicio": "09:00", "fin": "18:00"}
```

**Solución**: Ajustar reglas
```python
# data/config.json
{
  "business_rules": {
    "horario_laboral": {
      "inicio": "09:00",
      "fin": "19:00"  # Extender hora fin
    }
  }
}
```

### GeoAgent

#### Problema: Ubicación No Detectada

**Síntoma**: `user_location: None`

**Diagnóstico**:
```python
# Ver si user_id existe
user_id = context.get("user_id")
print("User ID:", user_id)

# Ver si hay ubicación en DB
from apps.users.storage import user_store
user = user_store.get(user_id)
print("User location:", user.location)
```

**Solución**: Usar IP geolocation fallback
```python
# core/geo_temporal/geo_agent.py
import requests

def detect_location_from_ip(ip_address):
    response = requests.get(f"http://ip-api.com/json/{ip_address}")
    data = response.json()
    return {
        "country": data["countryCode"],
        "city": data["city"],
        "timezone": data["timezone"]
    }
```

### ValidationAgent

#### Problema: Falso Positivo

**Síntoma**: Dice que hay error pero en realidad no

**Diagnóstico**:
```python
# Ver cuál validación falló
errors = validation_output.validation_errors
for error in errors:
    print(f"Check: {error.code}, Message: {error.message}")

# Verificar manualmente
from apps.contacts.storage import contact_store
contact = contact_store.get(contact_id)
print("Contacto existe:", contact is not None)  # ¿True?
```

**Solución**: Ajustar lógica de validación
```python
# apps/appointments/agents/validation_agent.py
def validate_contact(contact_id: str) -> bool:
    # No fallar si contacto existe y está activo
    contact = contact_store.get(contact_id)
    if contact and contact.activo:
        return True
    return False
```

### AvailabilityAgent

#### Problema: Conflicto No Detectado

**Síntoma**: Cita se superpone pero no marca conflicto

**Diagnóstico**:
```python
# Ver citas existentes
from apps.appointments.storage import appointment_store
existing = appointment_store.list_all()

# Buscar overlap manual
from datetime import datetime, timedelta
candidate_start = datetime(2026, 1, 23, 10, 0)
candidate_end = datetime(2026, 1, 23, 11, 0)

for apt in existing:
    if apt.fecha == candidate_start.date():
        apt_start = datetime.combine(apt.fecha, apt.hora_inicio)
        apt_end = datetime.combine(apt.fecha, apt.hora_fin)
        # Verificar overlap
        if (apt_start < candidate_end and apt_end > candidate_start):
            print(f"Conflicto real con {apt.id}")
```

**Solución**: Corregir lógica de overlap
```python
def has_overlap(candidate, existing):
    # Overlap existe si:
    # (candidate_start < existing_end) AND (candidate_end > existing_start)
    return (
        candidate.start < existing.end and
        candidate.end > existing.start
    )
```

### NegotiationAgent

#### Problema: Sugerencias Útiles

**Síntoma**: Sugiere horarios no disponibles

**Diagnóstico**:
```python
# Verificar disponibilidad real de sugerencias
for suggestion in output.suggestions:
    # Ver si realmente está disponible
    is_available = availability_agent.check_slot(
        fecha=suggestion.fecha,
        hora=suggestion.hora_inicio
    )
    print(f"Suggestion {suggestion.rank}: available={is_available}")
```

**Solución**: Validar antes de sugerir
```python
def generate_suggestions(conflict):
    slots = find_alternative_slots(...)
    valid_suggestions = []

    for slot in slots:
        # Verificar disponibilidad REAL
        if check_availability(slot):
            valid_suggestions.append(slot)

    return valid_suggestions
```

---

## 🔄 Recuperación Automática

### Mecanismo de Retry

```python
# core/agents/base_agent.py
class BaseAgent:
    async def safe_process(self, context: SharedContext):
        max_retries = 3
        retry_delay = 1  # segundo

        for attempt in range(max_retries):
            try:
                return await self.process(context)
            except TemporaryError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{max_retries}: {e}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # exponential backoff
                else:
                    raise
            except PermanentError:
                # No reintentar errores permanentes
                raise
```

### Fallback Agent

```python
# Si ParsingAgent falla, usar regex fallback
class ParsingAgent(BaseAgent):
    fallback = RegexParsingAgent()

    async def safe_process(self, context):
        try:
            return await self.process(context)
        except LLMError:
            logger.warning("LLM failed, using regex fallback")
            return await self.fallback.process(context)
```

---

## 📊 Post-Incidente

### Root Cause Analysis (RCA)

```markdown
## Incidente: ParsingAgent Timeout - 2026-01-22

### Impacto
- Duración: 15 minutos
- Requests afectados: 127
- Error rate: 100% (todos fallaron)

### Causa Raíz
- Proveedor Qwen tenía latencia alta (>30s)
- Nuestro timeout era 30s, muy justo

### Acción Inmediata
- Aumentar timeout a 60s
- Cambiar proveedor a fallback (Claude)

### Acción Correctiva
- Implementar circuit breaker
- Monitorear latencia de Qwen continuamente
- Preparar multi-LLM strategy

### Prevención
- Tests de carga con latencia alta
- Alertas tempranas de latencia >10s
```

### Mejora de Monitoreo

```python
# core/observability/metrics.py
from prometheus_client import Counter, Histogram

agent_errors = Counter(
    'agent_errors_total',
    'Total de errores de agentes',
    ['agent_name', 'error_type']
)

agent_duration = Histogram(
    'agent_execution_duration_seconds',
    'Duración de ejecución de agentes',
    ['agent_name'],
    buckets=[0.5, 1, 2, 5, 10, 30, 60]  # buckets hasta 60s
)
```

---

## 🧪 Testing Post-Reparación

### Test Unitario del Agente

```python
# tests/appointments/agents/test_parsing_agent.py
async def test_parsing_agent_timeout_recovery():
    """Test que ParsingAgent se recupera de timeout"""
    # Mock LLM que timeoutea
    with patch('core.ai.providers.qwen_provider.QwenLLM.complete') as mock_llm:
        mock_llm.side_effect = [
            TimeoutError(),  # Primer intento falla
            mock_response(json_data={"entities": {...}})  # Segundo éxito
        ]

        agent = ParsingAgent()
        context = SharedContext()
        context.update("user_prompt", {"prompt": "cita mañana"})

        result = await agent.safe_process(context)

        assert result.confidence > 0.8
        assert mock_llm.call_count == 2  # Reintentó una vez
```

### Test de Integración

```python
# tests/integration/test_agent_pipeline.py
async def test_pipeline_with_parsing_failure():
    """Test que pipeline se recupera de fallo de parsing"""
    response = await client.post("/api/v1/appointments/", json={
        "prompt": "texto ambiguo que causa parsing error"
    })

    # Debe retornar error controlado, no 500
    assert response.status_code in [400, 422]

    data = response.json()
    assert "error" in data
    assert "trace_id" in data  # Trace debe existir aún con error
```

---

## 📞 Escalation

### Cuándo Escalar

| Situación | Acción | Tiempo |
|-----------|--------|--------|
| Agente down >5min | Revisar logs, intentar restart | Inmediato |
| Error rate >50% | Escalar a Tech Lead | 5min |
| Datos corruptos | Escalar a Engineering + Data | 10min |
| Security issue | Escalar a CTO | Inmediato |

### Contactos

```
On-Call: +52 55 1234 5678
Tech Lead: tech-lead@smartsync.example.com
CTO: cto@smartsync.example.com
```

---

## ✅ Checklist de Resolución

- [ ] Identificar agente fallido
- [ ] Obtener trace completo
- [ ] Reproducir error localmente
- [ ] Verificar input del agente
- [ ] Aplicar solución específica
- [ ] Verificar que tests pasan
- [ ] Hacer deploy a staging
- [ ] Verificar métricas en staging
- [ ] Deploy a producción
- [ ] Monitorear por 1 hora
- [ ] Documentar RCA
- [ ] Cerrar incidente

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: DevOps Team
