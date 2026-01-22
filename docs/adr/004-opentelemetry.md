# ADR 004 - OpenTelemetry para Observabilidad

## Estado
✅ Aceptado

## Contexto

Smart-Sync Concierge es un sistema multi-agente donde:

- Múltiples agentes procesan cada request
- Cada agente toma decisiones que necesitan trazabilidad
- Latencia y errores deben ser atribuibles a agentes específicos
- Debugging de sistemas distribuidos es inherentemente difícil

### Requisitos de Observabilidad

- **Tracing**: Seguir flujo completo de request a través de agentes
- **Metrics**: Medir latencia, errores, coste por agente
- **Logging**: Eventos discretos con contexto estructurado
- **Explicabilidad**: Reconstruir razonamiento de decisiones

### Desafíos Específicos

1. **Multi-agente**: ¿Cuál agente causó latencia/error?
2. **IA opaca**: ¿Qué prompt generó qué respuesta?
3. **Decisiones**: ¿Por qué el NegotiationAgent sugirió X y no Y?
4. **Coste**: ¿Cuánto costó cada request en tokens IA?

## Decisión

**Adoptar OpenTelemetry para observabilidad unificada.**

### Componentes

```
OpenTelemetry Stack
├── Tracing (Jaeger/Zipkin)
│   └── Request → Agentes → Decisions → Response
├── Metrics (Prometheus)
│   ├── Latencia por agente
│   ├── Tasa de errores
│   └── Coste IA por request
└── Logging (Structured)
    ├── Decisiones de agentes
    ├── Errores con contexto
    └── Eventos de negocio
```

### Integración con Arquitectura Agentica

```python
# Cada agente es un span
@traced_agent("parsing_agent")
async def process(self, context: SharedContext):
    with tracer.start_as_current_span("parse_entities"):
        # Span hijo: extracción
        entities = await self._extract_entities(prompt)

    with tracer.start_as_current_span("validate_entities"):
        # Span hijo: validación
        self._validate(entities)

    # Decision trace complementa OTEL tracing
    context.trace.record_decision(
        agent=self.name,
        decision="entities_extracted",
        output=entities
    )
```

## Consecuencias

### Positivas

- ✅ **Standard de facto**: OpenTelemetry es estándar, no vendor lock-in
- ✅ **Vendor-agnostic**: Compatible con Jaeger, Zipkin, Honeycomb, etc.
- ✅ **Multi-language**: Si añadimos servicios en otros lenguajes
- ✅ **Completo**: Traces + metrics + logs unificados
- ✅ **Auto-instrumentation**: Django auto-instrumenta endpoints
- ✅ **Ecosistema**: Herramientas maduras (Grafana, Prometheus, etc.)

### Negativas

- ❌ **Overhead**: ~5-10% latencia adicional
- ❌ **Complejidad de setup**: Configurar OTEL + collectors + backends
- ❌ **Coste de infraestructura**: Jaeger/ClickHouse/Prometheus requieren infra
- ❌ **Curva de aprendizaje**: Equipo necesita aprender OTEL

### Riesgos

- **Performance**: Overhead puede afectar UX si no se optimiza
- **Coste de storage**: Traces consumen significativo storage
- **Complejidad operacional**: Mover piezas adicionales
- **Sampling incorrecto**: Perder información importante si sampling muy agresivo

### Mitigaciones

- **Sampling inteligente**: 100% de errores, 10% de éxito
- **Async exporters**: No bloquear request con export
- **Compression**: Comprimir traces antes de enviar
- **TTL**: Retener traces por 7 días, métricas por 30 días
- **Local development**: Deshabilitar OTEL en dev para reducir overhead

## Alternativas Consideradas

### 1. Logging Simple (archivos de texto)

**Descripción**: Solo logs estructurados en archivos.

**Por qué NO**:
- ❌ Difícil correlacionar logs entre agentes
- ❌ Sin visualización de flujo distribuido
- ❌ Sin métricas automáticas
- ✅ Más simple, menos overhead

### 2. Cloud-Specific Solutions (AWS X-Ray, GCP Cloud Trace)

**Descripción**: Usar solución nativa del cloud provider.

**Por qué NO**:
- ❌ Vendor lock-in al cloud provider
- ❌ Difícil cambiar de cloud en el futuro
- ✅ Zero-setup si ya en ese cloud
- ✅ Integración nativa con otros servicios

**Nota**: Considerar si se compromete a cloud específico

### 3. Datadog/New Relic (APM comercial)

**Descripción**: Usar solución APM comercial.

**Por qué NO**:
- ❌ Coste elevado ($50+ por host)
- ❌ Vendor lock-in
- ✅ Excelente UI y dashboards
- ✅ Soporte y features avanzadas

**Nota**: Considerar para v1.0+ si presupuesto lo permite

### 4. OpenTracing (antecesor de OpenTelemetry)

**Descripción**: OpenTracing (ahora merge en OpenTelemetry).

**Por qué NO**:
- ❌ Proyecto deprecated, merge en OpenTelemetry
- ❌ Menor ecosistema

## Arquitectura de Observabilidad

### Stack Propuesto

```
┌─────────────────────────────────────────────────────────┐
│                    Aplicación Django                    │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐│
│  │ Auto-Instrument│  │ Manual Spans │  │ Custom Metrics││
│  │ (Django, DRF) │  │ (@traced_agent)│ │ (Prometheus) ││
│  └───────────────┘  └───────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              OpenTelemetry Python SDK                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐│
│  │   Tracer    │  │   Meter      │  │    Logger     ││
│  └──────────────┘  └──────────────┘  └───────────────┘│
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   OTEL Collector                         │
│  Procesa, batchea, envía a múltiples backends           │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Jaeger     │  │ Prometheus   │  │   Loki       │
│  (Traces)    │  │  (Metrics)   │  │   (Logs)     │
└──────────────┘  └──────────────┘  └──────────────┘
        ↓                 ↓                 ↓
┌─────────────────────────────────────────────────────────┐
│                    Grafana                               │
│            Dashboards y visualización                    │
└─────────────────────────────────────────────────────────┘
```

### Atributos de Span por Agente

Cada span de agente incluye:

```python
span.set_attributes({
    # Identificación
    "agent.name": "parsing_agent",
    "agent.version": "1.0.0",
    "agent.type": "extraction",

    # Input
    "agent.input.prompt": user_prompt[:1000],  # Truncado
    "agent.input.language": "es",

    # Output
    "agent.output.status": "success",
    "agent.output.confidence": 0.95,

    # Decisiones
    "agent.decision": "entities_extracted",
    "agent.decision.reasoning": "Detected appointment intent",

    # LLM específico
    "llm.provider": "qwen",
    "llm.model": "qwen-2.5",
    "llm.tokens_used": 450,
    "llm.estimated_cost_usd": 0.000045,

    # Negocio
    "business.user_id": user_id,
    "business.session_id": session_id,
})
```

### Métricas Clave

| Métrica | Tipo | Labels | Descripción |
|---------|------|--------|-------------|
| `appointment_requests_total` | Counter | status | Total requests de citas |
| `agent_execution_duration_seconds` | Histogram | agent_name | Duración de agente |
| `agent_errors_total` | Counter | agent_name, error_type | Errores de agente |
| `llm_tokens_used_total` | Counter | provider, model | Tokens consumidos |
| `llm_cost_usd_total` | Gauge | provider | Coste acumulado IA |
| `decision_confidence` | Histogram | agent_name, decision_type | Confianza de decisión |

## Plan de Implementación

### Fase 1: MVP (v0.1.0)

- [ ] Configurar OpenTelemetry SDK
- [ ] Auto-instrumentación Django/DRF
- [ ] Decorador `@traced_agent`
- [ ] Exportar traces a consola (dev)
- [ ] Métricas básicas (latencia, errores)

### Fase 2: Producción (v0.2.0)

- [ ] Desplegar Jaeger para traces
- [ ] Desplegar Prometheus para métricas
- [ ] Configurar OTEL Collector
- [ ] Dashboard en Grafana
- [ ] Sampling inteligente

### Fase 3: Avanzado (v0.3.0+)

- [ ] Correlation traces con logs
- [ ] Real-time alerting
- [ ] Anomaly detection
- [ ] Cost optimization por agente

## Implementación

### Estado
- ✅ Propuesto: 2026-01-22
- ✅ Aceptado: 2026-01-22
- ⏸ Pendiente: Implementación

### Componentes

| Componente | Prioridad | Estado |
|------------|-----------|--------|
| OTEL SDK config | Alta | ⏸ Pendiente |
| Decorador @traced_agent | Alta | ⏸ Pendiente |
| Prometheus exporter | Alta | ⏸ Pendiente |
| Jaeger exporter | Media | ⏸ Pendiente |
| Grafana dashboards | Media | ⏸ Pendiente |
| OTEL Collector | Baja | ⏸ Pendiente |

### Configuración

```python
# config/settings/observability.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Solo en producción
if not settings.DEBUG:
    trace.set_tracer_provider(TracerProvider())
    provider = trace.get_tracer_provider()

    # Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.JAEGER_HOST,
        agent_port=settings.JAEGER_PORT,
    )
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
```

### Referencias

- [OpenTelemetry Docs](https://opentelemetry.io/docs/instrumentation/python/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)

## Supersedes

Supersede: Ninguno

## Superseded By

Ninguno (activo)

---

**Autor**: Architecture Team
**Fecha**: Enero 22, 2026
**Revisado por**: Tech Lead, SRE
