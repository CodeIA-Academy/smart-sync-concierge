# Contrato: Eventos de Agentes

## Versión
1.0.0

## Propósito

Definir el contrato de eventos internos de agentes para debugging, observabilidad y análisis.

---

## Arquitectura de Eventos de Agentes

```
┌─────────────────────────────────────────────────────┐
│              Pipeline de Agentes                     │
│                                                      │
│  User → Coordinator → Parsing → Temporal → ...      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
                  ┌──────────┐
                  │   Event  │
                  │  Emitter │
                  └────┬─────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Jaeger  │  │ Metrics │  │  Logs   │
    │  Traces │  │ Prometheus│  │  File  │
    └─────────┘  └─────────┘  └─────────┘
```

---

## Tipos de Eventos

### 1. AgentExecutionStarted

**Descripción**: Se inicia ejecución de un agente

```python
@dataclass
class AgentExecutionStartedEvent:
    """Evento de inicio de ejecución"""

    # Metadatos del evento
    event_id: str
    event_type: str = "agent.execution.started"
    event_version: str = "1.0.0"
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Identificación del agente
    agent_name: str                     # "parsing_agent"
    agent_version: str                  # "1.0.0"

    # Contexto de ejecución
    trace_id: str                       # "trc_abc123"
    request_id: str                     # "req_xyz789"
    parent_trace_id: Optional[str]      # Si es sub-agente

    # Input del agente
    input_type: str                     # "ParsingInput"
    input_summary: str                  # Resumen del input (max 200 chars)
    input_size_bytes: int

    # Configuración
    llm_provider: str                   # "qwen"
    llm_model: str                      # "qwen-2.5"
    temperature: float
    max_tokens: int
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_agent_start_abc123",
  "event_type": "agent.execution.started",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:00:00Z",
  "agent_name": "parsing_agent",
  "agent_version": "1.0.0",
  "trace_id": "trc_main_abc123",
  "request_id": "req_xyz789",
  "parent_trace_id": null,
  "input_type": "ParsingInput",
  "input_summary": "prompt: 'cita mañana 10am con Dr. Pérez'",
  "input_size_bytes": 256,
  "llm_provider": "qwen",
  "llm_model": "qwen-2.5",
  "temperature": 0.3,
  "max_tokens": 500
}
```

### 2. AgentExecutionCompleted

**Descripción**: Agente completó ejecución exitosamente

```python
@dataclass
class AgentExecutionCompletedEvent:
    """Evento de completado exitoso"""

    event_id: str
    event_type: str = "agent.execution.completed"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Identificación
    agent_name: str
    agent_version: str
    trace_id: str
    request_id: str

    # Métricas de ejecución
    execution_time_ms: int
    execution_time_seconds: float

    # Output del agente
    output_type: str                    # "ParsingOutput"
    output_summary: str
    output_size_bytes: int

    # Calidad del resultado
    confidence: float                   # 0.0 - 1.0
    decision_type: str                  # "entity_extraction"
    reasoning: str                      # Explicación de la decisión

    # LLM metrics (si aplicable)
    llm_tokens_used: Optional[int] = None
    llm_prompt_tokens: Optional[int] = None
    llm_completion_tokens: Optional[int] = None
    llm_cost_usd: Optional[float] = None

    # Recoverability
    was_retried: bool = False
    retry_count: int = 0
    fallback_used: bool = False
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_agent_complete_def456",
  "event_type": "agent.execution.completed",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:00:02Z",
  "agent_name": "parsing_agent",
  "agent_version": "1.0.0",
  "trace_id": "trc_main_abc123",
  "request_id": "req_xyz789",
  "execution_time_ms": 1850,
  "execution_time_seconds": 1.85,
  "output_type": "ParsingOutput",
  "output_summary": "entities: {contacto: 'Dr. Pérez', fecha: 'mañana', hora: '10am'}",
  "output_size_bytes": 512,
  "confidence": 0.92,
  "decision_type": "entity_extraction",
  "reasoning": "Detectada intención de cita médica con fecha relativa clara",
  "llm_tokens_used": 423,
  "llm_prompt_tokens": 287,
  "llm_completion_tokens": 136,
  "llm_cost_usd": 0.00042,
  "was_retried": false,
  "retry_count": 0,
  "fallback_used": false
}
```

### 3. AgentExecutionFailed

**Descripción**: Agente falló en ejecución

```python
@dataclass
class AgentExecutionFailedEvent:
    """Evento de fallo"""

    event_id: str
    event_type: str = "agent.execution.failed"
    event_version": str = "1.0.0"
    timestamp: datetime

    # Identificación
    agent_name: str
    trace_id: str
    request_id: str

    # Error
    error_type: str                    # "LLMTimeoutError", "JSONDecodeError"
    error_message: str
    error_code: str                    # "LLM_TIMEOUT", "JSON_INVALID"
    error_category: str                # "transient", "permanent", "validation"

    # Contexto del error
    stage: str                         # "llm_call", "json_parse", "validation"
    input_at_error: Optional[dict] = None
    partial_output: Optional[dict] = None

    # Stack trace (para debugging)
    stack_trace: Optional[str] = None

    # Intentos de recuperación
    was_retried: bool
    retry_count: int
    max_retries_reached: bool
    fallback_attempted: bool
    fallback_successful: Optional[bool] = None

    # Métricas
    execution_time_before_failure_ms: int
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_agent_failed_ghi789",
  "event_type": "agent.execution.failed",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:05:30Z",
  "agent_name": "parsing_agent",
  "trace_id": "trc_main_ghi789",
  "request_id": "req_jkl012",
  "error_type": "LLMTimeoutError",
  "error_message": "LLM request timeout after 30s",
  "error_code": "LLM_TIMEOUT",
  "error_category": "transient",
  "stage": "llm_call",
  "input_at_error": {
    "prompt": "cita mañana 10am con Dr. Pérez"
  },
  "partial_output": null,
  "stack_trace": "Traceback (most recent call last):\n  File \"...\"",
  "was_retried": true,
  "retry_count": 3,
  "max_retries_reached": true,
  "fallback_attempted": true,
  "fallback_successful": true,
  "execution_time_before_failure_ms": 30000
}
```

### 4. AgentDecisionRecorded

**Descripción**: Agente registró una decisión en el trace

```python
@dataclass
class AgentDecisionRecordedEvent:
    """Evento de registro de decisión"""

    event_id: str
    event_type: str = "agent.decision.recorded"
    event_version": str = "1.0.0"
    timestamp: datetime

    # Identificación
    agent_name: str
    trace_id: str
    decision_id: str                   # "dec_abc123"

    # La decisión
    decision_type: str                 # "entity_extraction", "temporal_resolution"
    decision_category: str             # "extraction", "validation", "resolution"

    # Razonamiento
    reasoning: str
    confidence: float

    # Input y Output
    input_data: dict
    output_data: dict

    # Metadatos
    decision_duration_ms: int
    was_cached: bool = False
    cache_hit_key: Optional[str] = None
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_decision_mno345",
  "event_type": "agent.decision.recorded",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:00:01Z",
  "agent_name": "temporal_agent",
  "trace_id": "trc_main_abc123",
  "decision_id": "dec_temporal_001",
  "decision_type": "temporal_resolution",
  "decision_category": "resolution",
  "reasoning": "'mañana' resuelto a 2026-01-23 considerando fecha de referencia 2026-01-22 y zona horaria America/Mexico_City",
  "confidence": 1.0,
  "input_data": {
    "fecha_original": "mañana",
    "reference_date": "2026-01-22",
    "timezone": "America/Mexico_City"
  },
  "output_data": {
    "fecha_resuelta": "2026-01-23",
    "hora_resuelta": "10:00",
    "timezone_utc": "-06:00"
  },
  "decision_duration_ms": 150,
  "was_cached": false,
  "cache_hit_key": null
}
```

### 5. AgentRetryAttempted

**Descripción**: Se intentó retry de agente

```python
@dataclass
class AgentRetryAttemptedEvent:
    """Evento de retry"""

    event_id: str
    event_type: str = "agent.retry.attempted"
    event_version": str = "1.0.0"
    timestamp: datetime

    # Identificación
    agent_name: str
    trace_id: str
    retry_attempt: int                  # 1, 2, 3...

    # Contexto del retry
    original_error: str
    retry_reason: str                   # "timeout", "error", "low_confidence"
    retry_strategy: str                 # "exponential_backoff", "fixed_delay"

    # Timing
    delay_seconds: float
    next_retry_at: datetime

    # Resultado del retry
    retry_successful: Optional[bool] = None  # Null si está en progreso
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_retry_pqr678",
  "event_type": "agent.retry.attempted",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:00:35Z",
  "agent_name": "parsing_agent",
  "trace_id": "trc_main_abc123",
  "retry_attempt": 2,
  "original_error": "LLMTimeoutError: timeout after 30s",
  "retry_reason": "timeout",
  "retry_strategy": "exponential_backoff",
  "delay_seconds": 4.0,
  "next_retry_at": "2026-01-23T10:00:39Z",
  "retry_successful": null
}
```

### 6. AgentFallbackTriggered

**Descripción**: Se activó fallback a backup

```python
@dataclass
class AgentFallbackTriggeredEvent:
    """Evento de activación de fallback"""

    event_id: str
    event_type: str = "agent.fallback.triggered"
    "event_version": str = "1.0.0"
    timestamp: datetime

    # Identificación
    primary_agent: str
    fallback_agent: str
    trace_id: str

    # Contexto
    trigger_reason: str                 # "max_retries_exceeded", "llm_unavailable"
    primary_error: str

    # Resultado
    fallback_successful: bool
    fallback_output_summary: Optional[str] = None
    fallback_confidence: Optional[float] = None

    # Degradación
    quality_delta: Optional[float] = None  # Diferencia en calidad
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_fallback_stu901",
  "event_type": "agent.fallback.triggered",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:01:00Z",
  "primary_agent": "parsing_agent",
  "fallback_agent": "regex_parsing_agent",
  "trace_id": "trc_main_abc123",
  "trigger_reason": "max_retries_exceeded",
  "primary_error": "LLM service unavailable after 3 retries",
  "fallback_successful": true,
  "fallback_output_summary": "Parsed with regex: contacto='Dr. Pérez', fecha='mañana'",
  "fallback_confidence": 0.65,
  "quality_delta": -0.27
}
```

### 7. AgentPipelineStarted

**Descripción**: Se inició pipeline completo de agentes

```python
@dataclass
class AgentPipelineStartedEvent:
    """Evento de inicio de pipeline"""

    event_id: str
    event_type": str = "agent.pipeline.started"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Contexto del pipeline
    trace_id: str
    request_id: str
    pipeline_type: str                 # "appointment_creation", "rescheduling"

    # Secuencia de agentes
    agent_sequence: List[str]           # ["parsing", "temporal", "geo", ...]
    sequence_length: int

    # Input original
    user_prompt: str
    user_timezone: str
    user_id: Optional[str] = None
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_pipeline_start_vwx234",
  "event_type": "agent.pipeline.started",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:00:00Z",
  "trace_id": "trc_main_abc123",
  "request_id": "req_xyz789",
  "pipeline_type": "appointment_creation",
  "agent_sequence": [
    "parsing_agent",
    "temporal_agent",
    "geo_agent",
    "validation_agent",
    "availability_agent"
  ],
  "sequence_length": 5,
  "user_prompt": "cita mañana 10am con Dr. Pérez",
  "user_timezone": "America/Mexico_City",
  "user_id": "user_12345"
}
```

### 8. AgentPipelineCompleted

**Descripción**: Pipeline completó ejecución

```python
@dataclass
class AgentPipelineCompletedEvent:
    """Evento de completado de pipeline"""

    event_id: str
    event_type: str = "agent.pipeline.completed"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Contexto
    trace_id: str
    request_id: str
    pipeline_type: str

    # Resultado
    status: str                         # "success", "partial_success", "failed"
    final_outcome: str                  # "appointment_created", "conflict_detected"

    # Métricas
    total_execution_time_ms: int
    agents_executed: int
    agents_succeeded: int
    agents_failed: int
    agents_retried: int

    # Output final
    output_summary: str
    final_confidence: float
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_pipeline_complete_yz345",
  "event_type": "agent.pipeline.completed",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T10:00:05Z",
  "trace_id": "trc_main_abc123",
  "request_id": "req_xyz789",
  "pipeline_type": "appointment_creation",
  "status": "success",
  "final_outcome": "appointment_created",
  "total_execution_time_ms": 4850,
  "agents_executed": 5,
  "agents_succeeded": 5,
  "agents_failed": 0,
  "agents_retried": 0,
  "output_summary": "Appointment apt_20260123_a1b2c3d4 created for Dr. Pérez at 2026-01-24 10:00",
  "final_confidence": 0.89
}
```

---

## Integración con OpenTelemetry

### Spans y Attributes

```python
# core/observability/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

tracer = trace.get_tracer(__name__)

@traced_agent("parsing_agent")
async def process_with_tracing(self, context: SharedContext):
    """Procesa con tracing automático"""

    with tracer.start_as_current_span("parsing_agent.process") as span:
        # Attributes del span
        span.set_attribute("agent.name", "parsing_agent")
        span.set_attribute("agent.version", "1.0.0")
        span.set_attribute("trace_id", context.trace_id)

        # Sub-span para LLM call
        with tracer.start_as_current_span("parsing_agent.llm_call") as llm_span:
            llm_span.set_attribute("llm.provider", "qwen")
            llm_span.set_attribute("llm.model", "qwen-2.5")
            llm_span.set_attribute("llm.temperature", 0.3)

            response = await self.llm.complete(request)

            llm_span.set_attribute("llm.tokens_used", response.usage.total_tokens)

        # Sub-span para validación
        with tracer.start_as_current_span("parsing_agent.validation") as val_span:
            val_span.set_attribute("validation.confidence", output.confidence)

        return output
```

### Events en Spans

```python
# Agregar events al span
span.add_event(
    "retry_attempted",
    attributes={
        "attempt": 2,
        "error": "timeout",
        "delay_seconds": 4.0
    }
)

span.add_event(
    "decision_recorded",
    attributes={
        "decision_type": "entity_extraction",
        "confidence": 0.92
    }
)
```

---

## Métricas Prometheus

### Definiciones

```python
# core/observability/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Contadores
agent_executions_total = Counter(
    'agent_executions_total',
    'Total de ejecuciones de agentes',
    ['agent_name', 'status']
)

agent_errors_total = Counter(
    'agent_errors_total',
    'Total de errores de agentes',
    ['agent_name', 'error_type', 'error_category']
)

agent_retries_total = Counter(
    'agent_retries_total',
    'Total de retries de agentes',
    ['agent_name', 'retry_reason']
)

agent_fallbacks_total = Counter(
    'agent_fallbacks_total',
    'Total de activaciones de fallback',
    ['primary_agent', 'fallback_agent']
)

# Histogramas
agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Duración de ejecución de agentes',
    ['agent_name'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)

llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'Duración de requests al LLM',
    ['llm_provider'],
    buckets=[0.5, 1, 2, 5, 10, 20, 30]
)

# Gauges
agent_confidence = Gauge(
    'agent_confidence',
    'Confianza de agentes',
    ['agent_name']
)

llm_tokens_remaining = Gauge(
    'llm_tokens_remaining',
    'Tokens restantes en quota',
    ['llm_provider']
)
```

### Export

```python
# Exponer endpoint para Prometheus
from prometheus_client import start_http_server

start_http_server(9090)  # http://localhost:9090/metrics
```

---

## Logging Estructurado

### Formato de Log

```python
# core/observability/logging.py
import structlog

logger = structlog.get_logger()

# Uso en agente
logger.info(
    "agent_execution_started",
    agent_name="parsing_agent",
    trace_id="trc_abc123",
    input_summary="prompt: 'cita mañana...'"
)

logger.info(
    "agent_execution_completed",
    agent_name="parsing_agent",
    trace_id="trc_abc123",
    execution_time_ms=1850,
    confidence=0.92
)

logger.error(
    "agent_execution_failed",
    agent_name="parsing_agent",
    trace_id="trc_abc123",
    error_type="LLMTimeoutError",
    was_retried=True,
    retry_count=3
)
```

### Output

```json
{
  "event": "agent_execution_completed",
  "agent_name": "parsing_agent",
  "trace_id": "trc_abc123",
  "execution_time_ms": 1850,
  "confidence": 0.92,
  "timestamp": "2026-01-23T10:00:02Z",
  "level": "info",
  "logger": "apps.appointments.agents.parsing_agent"
}
```

---

## Debugging con Eventos

### Replay de Ejecución

```python
# core/debugging/replay.py
class AgentExecutionReplay:
    """Replay de ejecución de agente para debugging"""

    async def replay(self, trace_id: str) -> dict:
        """Replay ejecución completa"""
        # Obtener eventos del trace
        events = await self.get_events_by_trace(trace_id)

        # Ordenar cronológicamente
        events.sort(key=lambda e: e['timestamp'])

        # Reconstruir timeline
        timeline = []
        for event in events:
            timeline.append({
                "time": event['timestamp'],
                "event": event['event_type'],
                "details": event
            })

        return {
            "trace_id": trace_id,
            "timeline": timeline,
            "summary": self._generate_summary(events)
        }

    def _generate_summary(self, events: List[dict]) -> dict:
        """Genera summary de ejecución"""
        return {
            "total_events": len(events),
            "agents_executed": len(set(e['agent_name'] for e in events)),
            "total_time_ms": self._calculate_total_time(events),
            "errors": len([e for e in events if 'failed' in e['event_type']]),
            "retries": len([e for e in events if 'retry' in e['event_type']])
        }
```

---

## Testing

### Test de Eventos

```python
# tests/events/test_agent_events.py
async def test_agent_events_emitted():
    """Verifica que todos los eventos se emiten"""

    # Mock event collector
    collector = MockEventCollector()

    # Ejecutar agente
    agent = ParsingAgent(event_collector=collector)
    context = SharedContext()

    await agent.process(context)

    # Verificar eventos
    events = collector.get_events()

    assert any(e['event_type'] == 'agent.execution.started' for e in events)
    assert any(e['event_type'] == 'agent.execution.completed' for e in events)
    assert any(e['event_type'] == 'agent.decision.recorded' for e in events)
```

---

## Métricas de Eventos

| Métrica | Descripción | Objetivo |
|---------|-------------|----------|
| **event_emit_rate** | Eventos emitidos por segundo | >1000/s |
| **event_loss_rate** | Eventos perdidos | <0.01% |
| **trace_completion_rate** | Traces completados exitosamente | >95% |
| **event_latency_p95** | Tiempo de emisión de evento | <100ms |

---

## Versión de Contrato

| Versión | Cambios | Fecha |
|---------|---------|-------|
| 1.0.0 | Versión inicial | 2026-01-22 |

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: Observability Team
