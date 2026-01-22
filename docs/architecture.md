# Arquitectura Agentica - Smart-Sync Concierge

## Visión General

Smart-Sync Concierge es una **API de citas agentica** donde un sistema de agentes de IA colabora para transformar lenguaje natural en acciones estructuradas, gestionando el ciclo de vida completo de citas mediante:

- **Arquitectura Multi-Agente**: Especialización de agentes por dominio
- **Pipeline Prompt-First**: Lenguaje natural como interfaz primaria
- **Validación Geo-Temporal**: Contexto de ubicación y tiempo en tiempo real
- **Abstracción de IA**: Desacoplamiento del modelo subyacente
- **Observabilidad Nativa**: Trazabilidad completa de decisiones

## Filosofía Agentica

### Paradigma: De "Extraer" a "Razonar"

```
┌─────────────────────────────────────────────────────────────┐
│                    ENFOQUE TRADICIONAL                       │
│  Usuario → Parser → Extractor de Entidades → Validación     │
│  "Extraer datos y validar"                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ENFOQUE AGENTICO                          │
│  Usuario → Agente Coordinador → Especialistas → Acción      │
│  "Razonar sobre intenciones y ejecutar"                      │
└─────────────────────────────────────────────────────────────┘
```

### Principios Agenticos

| Principio | Descripción | Implementación |
|-----------|-------------|----------------|
| **Especialización** | Cada agente domina un dominio | ParserAgent, TemporalAgent, NegotiatorAgent |
| **Colaboración** | Agentes comparten contexto | SharedContext con memoria |
| **Autonomía** | Agentes toman decisiones independientes | Validación local antes de compartir |
| **Transparencia** | Cada decisión es trazable | DecisionTrace en cada paso |
| **Recuperabilidad** | Fallos de un agente no colapsan el sistema | CircuitBreaker por agente |

---

## Stack Tecnológico

| Componente | Tecnología | Versión | Justificación |
|------------|------------|---------|---------------|
| Framework | Django | 6.0.1 | Ecosistema maduro, ORM flexible |
| API REST | Django REST Framework | 3.15.2 | Serialización, permisos, throttling |
| Motor IA | **Pluggable** | - | Abstracción permite swap |
| ├── Default | Qwen | 2.5 | Código abierto, coste competitivo |
| ├── Alternative | Claude | 3.5 | Razonamiento superior |
| └── Alternative | GPT-4 | o1 | Planificación compleja |
| Orquestación | LangGraph | 0.2+ | Stateful multi-agent workflows |
| Storage | JSON Local | - | Prototipado rápido |
| Observabilidad | OpenTelemetry | 1.20+ | Tracing, metrics, logs |
| Validación Temporal | dateutil + zoneinfo | - | Manejo robusto zonas horarias |
| Arquitectura | Single-tenant → Multi-tenant | - | Camino de migración claro |

---

## Estructura del Proyecto Agentico

```
smart_sync_concierge/
├── config/
│   ├── settings/
│   │   ├── base.py                # Configuración base
│   │   ├── ai.py                  # Configuración IA (pluggable)
│   │   ├── observability.py       # OpenTelemetry config
│   │   └── agents.py              # Configuración agentes
│   └── urls.py
│
├── core/
│   ├── agents/                    # 🆕 Framework de agentes
│   │   ├── base_agent.py          # Agente base abstracto
│   │   ├── coordinator_agent.py   # Orquestador principal
│   │   ├── context.py             # SharedContext entre agentes
│   │   ├── memory.py              # Memoria de conversación
│   │   └── decision_trace.py      # Registro de decisiones
│   │
│   ├── ai/                        # 🆕 Abstracción IA
│   │   ├── base_llm.py            # Interfaz LLM abstracta
│   │   ├── providers/
│   │   │   ├── qwen_provider.py   # Implementación Qwen
│   │   │   ├── claude_provider.py # Implementación Claude
│   │   │   └── openai_provider.py # Implementación GPT
│   │   ├── prompts/
│   │   │   ├── template_engine.py # Motor de templates
│   │   │   └── prompt_registry.py # Registro de prompts
│   │   └── tools/
│   │       ├── function_calling.py # Function calling
│   │       └── response_parser.py  # Parseo estructurado
│   │
│   ├── geo_temporal/              # 🆕 Validación geo-temporal
│   │   ├── temporal_agent.py      # Agente especializado tiempo
│   │   ├── geo_agent.py           # Agente especializado ubicación
│   │   ├── timezone_resolver.py   # Resolución zonas horarias
│   │   ├── business_hours.py      # Cálculo horarios negocio
│   │   ├── holiday_calendar.py    # Calendario festivos
│   │   └── conflict_detector.py   # Detección conflictos temp
│   │
│   ├── observability/             # 🆕 Observabilidad
│   │   ├── tracer.py              # OpenTelemetry wrapper
│   │   ├── metrics.py             # Métricas personalizadas
│   │   ├── logger.py              # Logging estructurado
│   │   └── event_bus.py           # Bus de eventos
│   │
│   ├── constants.py               # Constantes globales
│   ├── exceptions.py              # Excepciones personalizadas
│   └── utils.py                   # Utilidades
│
├── apps/
│   ├── appointments/
│   │   ├── agents/                # 🆕 Agentes de dominio
│   │   │   ├── parsing_agent.py   # Agente parser
│   │   │   ├── validation_agent.py # Agente validación
│   │   │   ├── scheduling_agent.py # Agente planificación
│   │   │   └── negotiation_agent.py # Agente negociación
│   │   │
│   │   ├── services/              # Servicios tradicionales
│   │   │   ├── parser_service.py
│   │   │   ├── validator_service.py
│   │   │   └── scheduler_service.py
│   │   │
│   │   ├── storage/
│   │   │   └── appointment_store.py
│   │   │
│   │   └── schemas/
│   │       └── appointment_schema.py
│   │
│   ├── contacts/                  # Gestión contactos
│   ├── services/                  # Catálogo servicios
│   └── availability/              # Gestión disponibilidad
│
├── data/                          # JSON local (fase inicial)
│   ├── appointments.json
│   ├── contacts.json
│   ├── services.json
│   └── decisions/                 # 🆕 Log de decisiones agentas
│       └── decision_log.json
│
├── docs/
│   ├── architecture.md            # Este archivo
│   ├── agents.md                  # 🆕 Documentación agentes
│   ├── observability.md           # 🆕 Guía observabilidad
│   └── api_reference.md
│
└── tests/
    ├── unit/
    │   ├── agents/                # Tests agentes
    │   └── geo_temporal/          # Tests geo-temporal
    └── integration/
        └── agent_workflows/       # Tests workflows
```

---

## Pipeline Prompt-First Agentico

### Arquitectura de Flujo Multi-Agente

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. INTENCIÓN DE USUARIO                       │
│                  POST /api/v1/appointments/                      │
│           { "prompt": "cita mañana 10am con Dr. Pérez" }        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              2. COORDINADOR DE AGENTES (Entry Point)            │
│  • Recibe prompt del usuario                                     │
│  • Inicializa SharedContext vacío                                │
│  • Crea DecisionTrace para trazabilidad                          │
│  • Selecciona secuencia de agentes apropiada                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              3. AGENTE DE PARSEO (ParsingAgent)                  │
│  • Extrae entidades: fecha, hora, participantes                 │
│  • Detecta ambigüedades ("mañana" sin referencia)              │
│  • Anota intenciones secundarias (urgencia, preferencias)       │
│  • Registra decisión: "Detectado cita médica"                  │
│  Output: StructuredIntent {                                     │
│    type: "appointment_request",                                 │
│    entities: {...},                                             │
│    confidence: 0.85,                                            │
│    ambiguities: ["mañana requiere fecha base"]                  │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            4. AGENTE TEMPORAL (TemporalAgent) 🆕                 │
│  • Resuelve "mañana" → "2026-01-23"                             │
│  • Normaliza "10am" → "10:00" en zona horaria usuario           │
│  • Calcula hora fin: 10:00 + 60min = 11:00                      │
│  • Valida: 23/01/2026 es jueves, día laboral                   │
│  • Valida: 10:00 está dentro de horario (9:00-18:00)           │
│  Registra decision: {                                           │
│    "resolved_date": "2026-01-23",                               │
│    "timezone": "America/Mexico_City",                           │
│    "reasoning": "Usuario en CDMX, 'mañana' = siguiente día hábil"│
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              5. AGENTE GEO (GeoAgent) 🆕                         │
│  • Detecta ubicación implícita: "CDMX" del contexto             │
│  • Mapea "Dr. Pérez" → contacto existente                       │
│  • Verifica disponibilidad geográfica: consultorio en CDMX      │
│  • Valida: usuario y prestador en misma zona                   │
│  Registra decision: {                                           │
│    "location_match": true,                                      │
│    "contact_found": "contact_dr_perez",                         │
│    "timezone_validation": "consistent"                          │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            6. AGENTE DE VALIDACIÓN (ValidationAgent)            │
│  • Contacto: ✓ "Dr. Pérez" encontrado                            │
│  • Servicio: ✓ "consulta_general" mapeado                       │
│  • Horario: ✓ 10:00-11:00 válido                                │
│  • Festivo: ✗ 23/01 no es festivo                               │
│  Registra decision: {                                           │
│    "validation_status": "passed",                               │
│    "checks": ["contact", "service", "hours", "holiday"],        │
│    "failed_checks": []                                          │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          7. AGENTE DE DISPONIBILIDAD (AvailabilityAgent)         │
│  • Busca citas existentes: 1 cita encontrada                    │
│  • Cita existente: 10:00-11:00 con Dr. Pérez                   │
│  • CONFLICTO DETECTADO                                           │
│  Registra decision: {                                           │
│    "conflict_detected": true,                                   │
│    "conflicting_appointment": "apt_20260123_xyz789",            │
│    "reason": "Dr. Pérez ya tiene cita a esa hora"               │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            8. AGENTE NEGOCIADOR (NegotiationAgent) 🆕            │
│  • Analiza conflicto con razonamiento                           │
│  • Genera 3 alternativas estratégicas:                          │
│    1. Mismo día, siguiente slot (11:00-12:00)                  │
│    2. Día siguiente, misma hora (24/01 10:00-11:00)            │
│    3. Mismo día, primera hora libre (09:00-10:00)              │
│  • Prioriza por: cercanía + preferencias usuario                │
│  Registra decision: {                                           │
│    "negotiation_strategy": "closest_alternatives",              │
│    "suggestions_count": 3,                                      │
│    "best_alternative": "11:00-12:00 mismo día"                 │
│  }                                                              │
│  Output: NegotiationResult con alternativas justificadas        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                9. COORDINADOR → RESPUESTA                        │
│  • Compila resultados de todos los agentes                      │
│  • Genera respuesta enriquecida:                                │
│    - Estado: "conflict"                                         │
│    - Razón: Justificación del agente de disponibilidad          │
│    - Alternativas: Con razonamiento de cada una                │
│    - Links: Para acción rápida ("reservar sugerencia 1")        │
│  • Publica evento: "appointment_negotiation_completed"          │
│  • Guarda DecisionTrace completo en decision_log.json           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    10. RESPUESTA AL USUARIO                      │
│  Status: 409 Conflict                                           │
│  {                                                              │
│    "status": "conflict",                                        │
│    "reasoning": {                                               │
│      "agent": "AvailabilityAgent",                              │
│      "finding": "Dr. Pérez tiene cita existente",              │
│      "conflict_id": "apt_20260123_xyz789"                       │
│    },                                                           │
│    "suggestions": [                                             │
│      {                                                           │
│        "when": "2026-01-23 11:00-12:00",                        │
│        "why": "Slot inmediato posterior, mismo día",           │
│        "agent": "NegotiationAgent",                             │
│        "confidence": 0.95                                       │
│      },                                                          │
│      {...}                                                      │
│    ],                                                           │
│    "actions": [                                                 │
│      {                                                           │
│        "type": "accept_suggestion",                             │
│        "href": "/api/v1/appointments/?suggest=0",              │
│        "method": "POST"                                         │
│      }                                                          │
│    ],                                                           │
│    "trace_id": "trc_abc123",                                    │
│    "_links": {                                                   │
│      "self": "/api/v1/decisions/trc_abc123/"                    │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Comparativa: Pipeline Tradicional vs Agentico

| Aspecto | Tradicional | Agentico |
|---------|-------------|----------|
| **Extracción** | Entidades estáticas | Entidades + contexto + intenciones |
| **Validación temporal** | Simple timezone | Multi-timezone con negociación |
| **Conflictos** | Boolean + lista | Análisis + estrategia + priorización |
| **Razonamiento** | Oculto | Expuesto en respuesta |
| **Trazabilidad** | Logs básicos | DecisionTrace completo |
| **Recuperación** | Reinicia pipeline | Agente aislado, otros continúan |
| **Explicabilidad** | Mensaje simple | Cadena de decisiones de agentes |

---

## Validación Geo-Temporal

### Arquitectura de Capas Temporales

```
┌─────────────────────────────────────────────────────────────┐
│          CAPA 1: NORMALIZACIÓN TEMPORAL                     │
│  • "mañana" → 2026-01-23 (relative anchor)                 │
│  • "10am" → 10:00 (time parsing)                           │
│  • "en 2 semanas" → 2026-02-05 (duration calc)             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          CAPA 2: RESOLUCIÓN DE ZONA HORARIA                 │
│  • Detectar TZ implícita del contexto usuario               │
│  • Mapear "mañana" a TZ del usuario                         │
│  • Convertir todas las horas a UTC para storage            │
│  • Preservar TZ original para display                       │
│                                                              │
│  Ejemplo:                                                    │
│  Usuario en CDMX (UTC-6): "mañana 10am"                     │
│  → 2026-01-23 10:00 America/Mexico_City                     │
│  → 2026-01-23 16:00 UTC (storage)                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          CAPA 3: VALIDACIÓN DE REGLAS TEMPORALES            │
│  • ¿Está dentro de horario laboral?                        │
│  • ¿Es día laboral (lun-vie)?                               │
│  • ¿Es festivo en esa ubicación?                           │
│  • ¿Cumple anticipación mínima (60min)?                     │
│  • ¿No excede anticipación máxima (90 días)?               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          CAPA 4: DETECCIÓN DE CONFLICTOS GEO-TEMPORALES     │
│  • Superposición de rangos en misma TZ                     │
│  • Considerar tiempo de desplazamiento (si aplicable)      │
│  • Validar disponibilidad del prestador en su TZ           │
│  • Detectar conflictos跨-zona horaria                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│          CAPA 5: NEGOCIACIÓN TEMPORAL INTELIGENTE           │
│  • Proponer slots cercanos temporalmente                   │
│  • Considerar TZ de ambas partes                            │
│  • Optimizar para minimizar reprogramaciones                │
│  • Sugerir alternativas跨-días si necesario                │
└─────────────────────────────────────────────────────────────┘
```

### Agente Temporal Especializado

**Ubicación**: `core/geo_temporal/temporal_agent.py`

```python
class TemporalAgent(BaseAgent):
    """
    Agente especializado en razonamiento temporal.

    Responsabilidades:
    - Resolver referencias temporales relativas ("mañana", "la próxima semana")
    - Normalizar zonas horarias multi-contexto
    - Validar restricciones temporales de negocio
    - Detectar anomalías temporales ("domingo a las 3am")
    """

    name = "temporal_agent"
    version = "1.0.0"

    async def process(self, context: SharedContext) -> TemporalResult:
        """
        Pipeline de procesamiento temporal:
        1. Extraer expresiones temporales del prompt
        2. Resolver referencias relativas usando fecha base
        3. Detectar zona horaria del contexto
        4. Normalizar a UTC
        5. Validar contra reglas de negocio
        6. Anotar DecisionTrace
        """
        # Step 1: Extracción
        temporal_expressions = await self._extract_temporal_entities(
            context.user_prompt,
            context.language
        )

        # Step 2: Resolución
        resolved_datetime = await self._resolve_relative_expressions(
            temporal_expressions,
            context.reference_date  # "ahora" del usuario
        )

        # Step 3: Zona horaria
        detected_tz = await self._detect_timezone(context)
        localized_datetime = self._localize_datetime(
            resolved_datetime,
            detected_tz
        )

        # Step 4: Normalización UTC
        utc_datetime = self._convert_to_utc(localized_datetime)

        # Step 5: Validación
        validation_result = await self._validate_temporal_constraints(
            utc_datetime,
            context.business_rules
        )

        # Step 6: Trazabilidad
        context.trace.record_decision(
            agent=self.name,
            decision="temporal_resolution",
            input=temporal_expressions,
            output={
                "resolved": utc_datetime.isoformat(),
                "original_tz": str(detected_tz),
                "validation": validation_result
            },
            reasoning=self._explain_resolution()
        )

        return TemporalResult(
            datetime=utc_datetime,
            original_timezone=detected_tz,
            validation=validation_result,
            confidence=self._calculate_confidence()
        )
```

### Agente Geo Espacializado

**Ubicación**: `core/geo_temporal/geo_agent.py`

```python
class GeoAgent(BaseAgent):
    """
    Agente especializado en razonamiento geográfico.

    Responsabilidades:
    - Detectar ubicación implícita del contexto
    - Validar coherencia geográfica (usuario-prestador)
    - Considerar factores geográficos en disponibilidad
    - Manejar multi-zona horaria
    """

    async def process(self, context: SharedContext) -> GeoResult:
        """
        Pipeline geográfico:
        1. Detectar ubicación usuario (IP, contexto, explícito)
        2. Mapear contacto a ubicación física
        3. Validar coherencia geográfica
        4. Determinar TZ base para cálculos
        """
        user_location = await self._detect_user_location(context)
        contact_location = await self._resolve_contact_location(
            context.contact_id
        )

        geo_coherence = self._validate_geo_coherence(
            user_location,
            contact_location
        )

        return GeoResult(
            user_location=user_location,
            contact_location=contact_location,
            is_coherent=geo_coherence,
            recommended_timezone=self._determine_common_tz(
                user_location,
                contact_location
            )
        )
```

---

## Abstracción de Inteligencia Artificial

### Problema: Vendor Lock-in

```
┌─────────────────────────────────────────────────────────────┐
│                    ACOPLOPLADO (Anti-pattern)               │
│                                                              │
│  from qwen import QwenClient                                │
│  client = QwenClient(api_key)                              │
│  response = client.generate(prompt)  # ❌ Vendor específico│
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    DESACOPLADO (Pattern)                    │
│                                                              │
│  from core.ai import LLMFactory                             │
│  llm = LLMFactory.create(provider="qwen")  # ✅ Interfaz    │
│  response = await llm.complete(prompt)                     │
│                                                              │
│  # Swap fácil:                                               │
│  llm = LLMFactory.create(provider="claude")                 │
└─────────────────────────────────────────────────────────────┘
```

### Interfaz LLM Unificada

**Ubicación**: `core/ai/base_llm.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class LLMRequest:
    """Request estándar para cualquier proveedor."""
    prompt: str
    max_tokens: int = 500
    temperature: float = 0.3
    tools: Optional[List[Dict]] = None  # Function calling
    response_format: Optional[str] = None  # "json", "text"

@dataclass
class LLMResponse:
    """Response estándar de cualquier proveedor."""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    raw_response: Dict[str, Any]

class BaseLLM(ABC):
    """
    Interfaz abstracta para proveedores de LLM.

    Permite swap entre Qwen, Claude, GPT-4 sin cambios en código.
    """

    provider_name: str
    default_model: str

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Genera respuesta desde prompt."""
        pass

    @abstractmethod
    async def stream_complete(self, request: LLMRequest):
        """Genera respuesta streaming."""
        pass

    @abstractmethod
    def supports_function_calling(self) -> bool:
        """Si el modelo soporta function calling."""
        pass

    @abstractmethod
    def supports_json_mode(self) -> bool:
        """Si el modelo soporta JSON mode nativo."""
        pass

    @abstractmethod
    def estimate_cost(self, tokens: int) -> float:
        """Estima coste en USD por token."""
        pass
```

### Implementaciones de Proveedores

#### Qwen Provider

**Ubicación**: `core/ai/providers/qwen_provider.py`

```python
class QwenLLM(BaseLLM):
    provider_name = "qwen"
    default_model = "qwen-2.5"

    def __init__(self, api_key: str):
        self.client = QwenClient(api_key=api_key)

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Implementación específica Qwen."""
        response = await self.client.chat.completions.create(
            model=self.default_model,
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            response_format={"type": "json_object"} if request.response_format == "json" else None
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump()
        )

    def supports_function_calling(self) -> bool:
        return True  # Qwen 2.5+ soporta

    def supports_json_mode(self) -> bool:
        return True

    def estimate_cost(self, tokens: int) -> float:
        # Qwen: ~$0.0001 por 1K tokens (input)
        return (tokens / 1000) * 0.0001
```

#### Claude Provider

**Ubicación**: `core/ai/providers/claude_provider.py`

```python
class ClaudeLLM(BaseLLM):
    provider_name = "anthropic"
    default_model = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Implementación específica Claude."""
        response = await self.client.messages.create(
            model=self.default_model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            messages=[{"role": "user", "content": request.prompt}],
            tools=request.tools if request.tools else None
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            raw_response=response.model_dump()
        )

    def supports_function_calling(self) -> bool:
        return True

    def supports_json_mode(self) -> bool:
        return False  # Claude no tiene JSON mode nativo, usar prompts

    def estimate_cost(self, tokens: int) -> float:
        # Claude Sonnet: ~$0.003 por 1K tokens (input)
        return (tokens / 1000) * 0.003
```

### Factory Pattern para Selección Dinámica

**Ubicación**: `core/ai/llm_factory.py`

```python
class LLMFactory:
    """
    Factory para crear instancias LLM basado en configuración.

    Permite cambiar de proveedor sin modificar código de negocio.
    """

    _providers = {
        "qwen": QwenLLM,
        "claude": ClaudeLLM,
        "openai": OpenAILLM,
    }

    @classmethod
    def create(cls, provider: str = None, **kwargs) -> BaseLLM:
        """
        Crea instancia LLM.

        Args:
            provider: Nombre del proveedor (usa config si es None)
            **kwargs: Argumentos específicos del proveedor (api_key, etc.)
        """
        provider = provider or settings.AI_DEFAULT_PROVIDER

        if provider not in cls._providers:
            raise ValueError(f"Proveedor no soportado: {provider}")

        provider_class = cls._providers[provider]
        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Registra nuevo proveedor en runtime."""
        cls._providers[name] = provider_class
```

### Uso en Código de Negocio

```python
# ❌ ACOPLODADO
from qwen import QwenClient
client = QwenClient(api_key)
response = client.generate(prompt)

# ✅ DESACOPLADO
from core.ai import LLMFactory

llm = LLMFactory.create(
    provider=settings.AI_DEFAULT_PROVIDER,  # "qwen", "claude", etc.
    api_key=settings.AI_API_KEY
)

response = await llm.complete(LLMRequest(
    prompt=prompt,
    response_format="json"
))

# Cambio de proveedor: solo actualizar settings.AI_DEFAULT_PROVIDER
```

### Prompt Template Engine

**Ubicación**: `core/ai/prompts/template_engine.py`

```python
class PromptTemplate:
    """
    Motor de templates para prompts consistentes.

    Permite:
    - Variables con tipo safe
    - Versionado de prompts
    - A/B testing de prompts
    """

    def __init__(self, template: str, version: str = "1.0"):
        self.template = template
        self.version = version
        self.variables = self._extract_variables(template)

    def render(self, **kwargs) -> str:
        """Renderiza template con variables."""
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Faltan variables: {missing}")

        return self.template.format(**kwargs)

    @classmethod
    def from_file(cls, path: str) -> "PromptTemplate":
        """Carga template desde archivo."""
        with open(path) as f:
            content = f.read()
            # Extract version from header if exists
            version = cls._extract_version(content) or "1.0"
            return cls(content, version)
```

**Ejemplo de Template**: `core/ai/prompts/templates/extraction.txt`

```
# Version: 2.0
# Last updated: 2026-01-22

Eres un extractor de información de citas especializado.

INSTRUCCIONES:
1. Analiza el prompt del usuario
2. Extrae las entidades solicitadas
3. Devuelve SOLO JSON válido

PROMPT DEL USUARIO:
{user_prompt}

CONTEXO:
- Fecha actual: {current_date}
- Zona horaria: {timezone}
- Servicios disponibles: {services}

RESPUESTA (formato JSON):
```json
{{
  "fecha": "YYYY-MM-DD",
  "hora": "HH:MM",
  "participantes": ["..."],
  "tipo": "...",
  "confianza": 0.0-1.0
}}
```

**Uso**:

```python
from core.ai.prompts import PromptTemplate

template = PromptTemplate.from_file("extraction.txt")

prompt = template.render(
    user_prompt="cita mañana 10am",
    current_date="2026-01-22",
    timezone="America/Mexico_City",
    services=["consulta_general", "pediatria"]
)

response = await llm.complete(LLMRequest(prompt=prompt))
```

---

## Observabilidad Nativa

### Principios de Observabilidad Agentica

```
┌─────────────────────────────────────────────────────────────┐
│              LAS 3 COLUMNAS DE OBSERVABILIDAD               │
│                                                              │
│  1. TRAZAS (Traces):  Flujo de ejecución completa           │
│     ├── Request → Agentes → Decisions → Response           │
│     └── Padre/hijo entre spans                              │
│                                                              │
│  2. MÉTRICAS (Metrics):  Agregaciones numéricas             │
│     ├── Latencia por agente                                 │
│     ├── Tasa de errores                                     │
│     ├── Coste IA por request                                │
│     └── Satisfacción usuario                                │
│                                                              │
│  3. LOGS (Logs):  Eventos discretos                         │
│     ├── Decisiones de agentes                               │
│     ├── Errores con contexto                                │
│     └── Eventos de negocio                                  │
└─────────────────────────────────────────────────────────────┘
```

### OpenTelemetry Integration

**Configuración**: `config/settings/observability.py`

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configurar tracer
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()

# Exportar a Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name=settings.JAEGER_HOST,
    agent_port=settings.JAEGER_PORT,
)
tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Tracer global
tracer = trace.get_tracer(__name__)
```

### Decorador de Trazado de Agentes

**Ubicación**: `core/observability/tracer.py`

```python
from functools import wraps
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def traced_agent(agent_name: str):
    """
    Decorador para tracing automático de agentes.

    Crea span para cada ejecución de agente con:
    - Inputs del agente
    - Outputs del agente
    - Decisiones tomadas
    - Duración de ejecución
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, context: SharedContext, *args, **kwargs):
            with tracer.start_as_current_span(agent_name) as span:
                # Atributos del span
                span.set_attribute("agent.version", self.version)
                span.set_attribute("agent.input", str(context)[:1000])
                span.set_attribute("user_id", context.user_id)

                # Ejecutar agente
                try:
                    result = await func(self, context, *args, **kwargs)

                    # Exitoso
                    span.set_attribute("agent.status", "success")
                    span.set_attribute("agent.output", str(result)[:1000])
                    span.set_status(Status(HttpStatusCode(200)))

                    return result

                except Exception as e:
                    # Error
                    span.set_attribute("agent.status", "error")
                    span.set_attribute("agent.error", str(e))
                    span.record_exception(e)
                    span.set_status(Status(HttpStatusCode(500), str(e)))
                    raise

        return wrapper
    return decorator
```

**Uso**:

```python
from core.observability import traced_agent

class ParsingAgent(BaseAgent):
    @traced_agent("parsing_agent")
    async def process(self, context: SharedContext):
        # Span automático con métricas
        result = await self._parse(context)
        return result
```

### Decision Trace

**Ubicación**: `core/agents/decision_trace.py`

```python
@dataclass
class Decision:
    """
    Registro de decisión individual de un agente.

    Permite reconstrucción post-hoc del razonamiento.
    """
    timestamp: datetime
    agent: str
    agent_version: str
    decision_type: str  # "temporal_resolution", "conflict_detection", etc.
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning: str  # Explicación en lenguaje natural
    confidence: float  # 0.0 - 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionTrace:
    """
    Trace completo de decisiones en un request.

    Permite:
    - Debugging de decisiones
    - Análisis de comportamiento de agentes
    - Mejora continua de prompts
    - Explicación al usuario final
    """
    trace_id: str  # UUID
    user_id: Optional[str]
    session_id: Optional[str]
    request_prompt: str
    decisions: List[Decision]
    final_result: Dict[str, Any]
    started_at: datetime
    completed_at: datetime

    def to_dict(self) -> Dict:
        """Exporta a JSON para storage/análisis."""
        return {
            "trace_id": self.trace_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request": self.request_prompt,
            "decisions": [asdict(d) for d in self.decisions],
            "result": self.final_result,
            "duration_ms": (
                self.completed_at - self.started_at
            ).total_seconds() * 1000
        }

    def explain(self) -> str:
        """Genera explicación legible del trace."""
        explanation = [f"Trace ID: {self.trace_id}\n"]

        for i, decision in enumerate(self.decisions, 1):
            explanation.append(
                f"{i}. {decision.agent}: {decision.decision_type}\n"
                f"   Razonamiento: {decision.reasoning}\n"
            )

        return "\n".join(explanation)
```

### Storage de Traces

**Ubicación**: `data/decisions/decision_log.json`

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2026-01-22T10:00:00Z",
    "total_traces": 150
  },
  "traces": [
    {
      "trace_id": "trc_abc123",
      "user_id": "user_456",
      "session_id": "sess_789",
      "request_prompt": "cita mañana 10am con Dr. Pérez",
      "decisions": [
        {
          "timestamp": "2026-01-22T15:30:00Z",
          "agent": "parsing_agent",
          "decision_type": "entity_extraction",
          "reasoning": "Detectada intención de cita médica con fecha relativa",
          "confidence": 0.95,
          "output": {
            "entities": {
              "fecha": "mañana",
              "hora": "10am",
              "contacto": "Dr. Pérez"
            }
          }
        },
        {
          "timestamp": "2026-01-22T15:30:01Z",
          "agent": "temporal_agent",
          "decision_type": "temporal_resolution",
          "reasoning": "Usuario en CDMX, 'mañana' resuelto a 2026-01-23",
          "confidence": 1.0,
          "output": {
            "resolved_date": "2026-01-23",
            "timezone": "America/Mexico_City"
          }
        },
        {
          "timestamp": "2026-01-22T15:30:02Z",
          "agent": "availability_agent",
          "decision_type": "conflict_detection",
          "reasoning": "Dr. Pérez tiene cita existente en mismo slot",
          "confidence": 1.0,
          "output": {
            "conflict": true,
            "conflicting_appointment": "apt_20260123_xyz789"
          }
        }
      ],
      "result": {
        "status": "conflict",
        "suggestions": [...]
      },
      "duration_ms": 2500
    }
  ]
}
```

### Métricas Personalizadas

**Ubicación**: `core/observability/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge

# Contadores
appointment_requests = Counter(
    "appointment_requests_total",
    "Total de requests de citas",
    ["status"]  # confirmed, conflict, error
)

agent_executions = Counter(
    "agent_executions_total",
    "Total de ejecuciones de agentes",
    ["agent_name", "status"]  # success, error
)

# Histogramas (latencia)
agent_latency = Histogram(
    "agent_latency_seconds",
    "Latencia de ejecución de agentes",
    ["agent_name"]
)

request_latency = Histogram(
    "request_latency_seconds",
    "Latencia total de request"
)

# Gauges (valores actuales)
llm_cost_tracker = Gauge(
    "llm_cost_usd_total",
    "Coste total de IA en USD",
    ["provider"]
)

active_sessions = Gauge(
    "active_sessions",
    "Sesiones activas actualmente"
)

# Uso en código
@appointment_requests.labels(status="confirmed").inc()
agent_latency.labels(agent_name="temporal_agent").observe(0.5)
```

### Endpoint de Diagnóstico

**Ubicación**: `apps/monitoring/views.py`

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def trace_detail(request, trace_id: str):
    """
    Retorna detalle completo de un trace.

    GET /api/v1/traces/trc_abc123
    """
    trace = DecisionTraceStore.get(trace_id)

    if not trace:
        return Response({"error": "Trace not found"}, status=404)

    return Response({
        "trace_id": trace.trace_id,
        "request": trace.request_prompt,
        "duration_ms": trace.duration_ms,
        "decisions": [
            {
                "agent": d.agent,
                "decision": d.decision_type,
                "reasoning": d.reasoning,
                "confidence": d.confidence,
                "timestamp": d.timestamp.isoformat()
            }
            for d in trace.decisions
        ],
        "explanation": trace.explain(),
        "_links": {
            "session": f"/api/v1/sessions/{trace.session_id}/" if trace.session_id else None,
            "user": f"/api/v1/users/{trace.user_id}/" if trace.user_id else None
        }
    })

@api_view(["GET"])
def agent_performance(request):
    """
    Métricas de rendimiento de agentes.

    GET /api/v1/observability/agents/performance
    """
    return Response({
        "agents": [
            {
                "name": "parsing_agent",
                "total_executions": agent_executions.labels(
                    agent_name="parsing_agent",
                    status="success"
                )._value.get(),
                "avg_latency_s": agent_latency.labels(
                    agent_name="parsing_agent"
                ).observe.__self__._sum.get() / agent_executions.labels(
                    agent_name="parsing_agent",
                    status="success"
                )._value.get() if agent_executions.labels(
                    agent_name="parsing_agent",
                    status="success"
                )._value.get() > 0 else 0,
                "error_rate": agent_executions.labels(
                    agent_name="parsing_agent",
                    status="error"
                )._value.get() / max(agent_executions.labels(
                    agent_name="parsing_agent",
                    status="success"
                )._value.get(), 1)
            }
        ]
    })
```

---

## Decisiones de Alcance (Scope Decisions)

### MVP vs. Futuro

| Componente | MVP (v0.1.0) | v0.3.0+ | v1.0.0+ |
|------------|--------------|---------|---------|
| **Motor IA** | Qwen 2.5 | Swap a Claude/GPT | Multi-modelo |
| **Agentes** | 3 básicos | 5-7 especializados | Agentes auto-optimizantes |
| **Geo-Temporal** | 1 TZ | Multi-TZ | Geo-aware con desplazamiento |
| **Observabilidad** | Logs + traces básicos | Métricas + dashboard | Alertas + auto-remediación |
| **Storage** | JSON local | PostgreSQL | Distribuido |
| **Validaciones** | Reglas estáticas | Aprendizaje | Predictivo |
| **Negociación** | Alternativas simples | Estrategias | Multi-objeto optimización |

### Decisiones de Arquitectura

#### ✅ INCLUIDO EN MVP

1. **Pipeline Agentico Básico**
   - 3 agentes: Parser, Validator, Scheduler
   - SharedContext simple
   - DecisionTrace básico

2. **Validación Geo-Temporal**
   - Resolución de zonas horarias
   - Validación de horarios laborales
   - Detección básica de conflictos

3. **Abstracción IA**
   - Interfaz BaseLLM
   - Implementación Qwen
   - Factory para swap

4. **Observabilidad**
   - Traces con OpenTelemetry
   - DecisionTrace en JSON
   - Endpoint de diagnóstico

#### ❌ EXCLUIDO DEL MVP (Futuro)

1. **Aprendizaje Automático**
   - Entrenamiento de modelos personalizados
   - Optimización de prompts con feedback
   - Detección de patrones de usuario

2. **Negociación Compleja**
   - Multi-objetivo (usuario + negocio + prestador)
   - Restricciones blandas (preferences vs. requirements)
   - Algoritmo de asignación óptima

3. **Integraciones Externas**
   - Calendarios (Google, Outlook)
   - Video conferencias (Zoom, Meet)
   - Notificaciones (Email, SMS, Push)

4. **Multi-Tenant**
   - Aislamiento de datos por negocio
   - Configuración por tenant
   - Rate limiting per-tenant

### Justificaciones de Alcance

#### ¿Por qué JSON local en MVP?

```
Ventajas:
✓ Zero-config (no setup DB)
✓ Portabilidad (copia de archivo = backup)
✓ Debugging (abrir archivo = ver datos)
✓ Prototipado rápido (no migrations)

Costes:
✗ Escalabilidad limitada (~10K citas)
✗ Concurrency (race conditions)
✗ Query complejos

Decisión: MVP usa JSON, migración a DB en v0.3.0
```

#### ¿Por qué Qwen en MVP?

```
Ventajas:
✓ Código abierto (no vendor lock-in)
✓ Coste competitivo (~$0.0001/1K tokens)
✓ Rendimiento suficiente para extracción
✓ Soporta function calling + JSON mode

Costes:
✗ Razonamiento inferior a GPT-4/Claude
✗ Ecosistema más pequeño

Decisión: MVP usa Qwen, interfaz permite swap
```

#### ¿Por qué 3 agentes básicos?

```
Agentes MVP:
1. ParsingAgent: Entidades + intenciones
2. ValidationAgent: Reglas de negocio
3. SchedulerAgent: Disponibilidad

Agentes Futuro:
4. NegotiationAgent: Alternativas inteligentes
5. LearningAgent: Optimización con feedback
6. SentimentAgent: Detección de urgencia/frustración

Decisión: MVP con 3 agentes, añadir según necesidad
```

#### ¿Por qué OpenTelemetry?

```
Ventajas:
✓ Standard de facto (no vendor lock-in)
✓ Compatible con Jaeger, Zipkin, etc.
✓ Soporte nativo en cloud providers
✓ Metrics + traces + logs unificados

Costes:
✓ Overhead (~5-10% latencia)
✓ Complejidad de setup

Decisión: Incluir desde inicio para no añadir deuda técnica
```

---

## Patrones de Diseño Agenticos

### 1. Coordinator Pattern

El CoordinatorAgent orquesta el flujo entre agentes especializados.

```python
class CoordinatorAgent(BaseAgent):
    """
    Orquestador principal de agentes.

    Responsabilidades:
    - Seleccionar secuencia de agentes apropiada
    - Manejar SharedContext entre agentes
    - Recuperar errores de agentes individuales
    - Compilar resultado final
    """

    async def process(self, context: SharedContext) -> CoordinationResult:
        # Determinar flujo de agentes
        agent_sequence = self._determine_agent_sequence(context)

        results = []
        for agent_class in agent_sequence:
            agent = agent_class()

            try:
                result = await agent.process(context)
                results.append(result)
                context.update(agent.name, result)

            except AgentError as e:
                # Recuperación: continuar con siguiente agente
                context.trace.record_error(agent.name, e)
                if not agent.recoverable:
                    raise

        return self._compile_results(results)
```

### 2. SharedContext Pattern

Memoria compartida entre agentes con versionado.

```python
class SharedContext:
    """
    Contexto compartido entre agentes.

    Características:
    - Inmutable por agente (solo lectura)
    - Update por coordinator
    - Versionado para trazabilidad
    """

    def __init__(self):
        self._data = {}
        self._version = 0
        self.trace = DecisionTrace()

    def get(self, key: str, agent_name: str) -> Any:
        """Obtiene valor (lectura)."""
        return self._data.get(key)

    def update(self, agent_name: str, updates: Dict[str, Any]):
        """Actualiza contexto (solo coordinator)."""
        self._data.update(updates)
        self._version += 1

        # Registrar en trace
        self.trace.record_update(agent_name, updates, self._version)
```

### 3. Agent Recovery Pattern

Recuperación granular de fallos de agentes.

```python
class BaseAgent(ABC):
    """
    Base para todos los agentes.

    Propiedades:
    - recoverable: Si el fallo permite continuar
    - fallback: Alternativa si el agente falla
    """

    recoverable: bool = True
    fallback: Optional["BaseAgent"] = None

    async def safe_process(self, context: SharedContext):
        """Ejecución con recovery."""
        try:
            return await self.process(context)

        except Exception as e:
            if self.recoverable and self.fallback:
                return await self.fallback.process(context)
            raise
```

### 4. Decision Trace Pattern

Registro completo de decisiones para explicabilidad.

```python
@dataclass
class DecisionTrace:
    """
    Trace de decisiones de agentes.

    Permite:
    - Explicación al usuario
    - Debugging
    - Análisis offline
    - Mejora continua
    """
    trace_id: str
    decisions: List[Decision]

    def explain_to_user(self) -> str:
        """Genera explicación amigable."""
        pass

    def analyze_for_improvement(self) -> Insights:
        """Analiza para optimización."""
        pass
```

---

## Seguridad en Arquitectura Agentica

### Consideraciones Específicas

| Amenaza | Mitigación Agentica |
|---------|---------------------|
| **Prompt Injection** | Sanitización + validación de output |
| **Data Exfiltration** | SharedContext sandbox por agente |
| **Model Poisoning** | Versionado de prompts + A/B testing |
| **Cost Attack** | Rate limiting + cost tracking por agente |
| **Info Leak** | Redacción de datos sensibles en prompts |

### Ejemplo: Sanitización de Prompts

```python
class PromptSanitizer:
    """
    Sanitiza prompts para prevenir inyección.

    Estrategias:
    - Eliminar instrucciones de sistema
    - Limitar longitud
    - Redactar datos sensibles
    """

    MAX_LENGTH = 1000

    def sanitize(self, prompt: str, user_id: str) -> str:
        # 1. Validar longitud
        if len(prompt) > self.MAX_LENGTH:
            raise PromptTooLongError(len(prompt), self.MAX_LENGTH)

        # 2. Detectar instrucciones de sistema
        if self._detect_system_instructions(prompt):
            logger.warning(f"Prompt injection detectado: user={user_id}")
            return self._strip_system_instructions(prompt)

        # 3. Redactar PII (opcional)
        if settings.REDACT_PII:
            prompt = self._redact_pii(prompt)

        return prompt
```

---

## Evolución y Migración

### Roadmap de Arquitectura

```
v0.1.0 (Actual)
├── 3 agentes básicos
├── Qwen como único LLM
├── JSON local
└── Observabilidad básica

v0.3.0
├── 5 agentes (+ Negotiation, Learning)
├── Multi-LLM (Qwen + Claude)
├── PostgreSQL
└── Métricas + Dashboard

v0.5.0
├── Agentes auto-optimizantes
├── Integraciones (Calendarios)
└── Multi-tenant básico

v1.0.0
├── Agentes con RLHF
├── Predicción de demanda
├── Optimización multi-objetivo
└── Arquitectura distribuida
```

### Estrategia de Migración

#### JSON → PostgreSQL

```python
# Abstracción para migración transparente
class AppointmentRepository(ABC):
    @abstractmethod
    async def save(self, appointment: Appointment) -> str:
        pass

class JSONAppointmentRepository(AppointmentRepository):
    """Implementación JSON (MVP)."""
    async def save(self, appointment: Appointment) -> str:
        # Guardar en appointments.json
        pass

class PostgresAppointmentRepository(AppointmentRepository):
    """Implementación PostgreSQL (v0.3.0+)."""
    async def save(self, appointment: Appointment) -> str:
        # INSERT INTO appointments ...
        pass

# Uso con inyección de dependencias
repository = AppointmentRepository(
    json_repo if settings.USE_JSON_STORAGE else postgres_repo
)
```

#### Single LLM → Multi LLM

```python
# Estrategia de routing de LLMs
class LLMRouter:
    """
    Router inteligente de LLMs.

    Selecciona modelo según:
    - Complejidad del request
    - Coste disponible
    - Latencia requerida
    """

    async def route(self, request: LLMRequest) -> BaseLLM:
        complexity = await self._estimate_complexity(request)

        if complexity == "simple":
            return QwenLLM()  # Rápido, barato

        elif complexity == "medium":
            return ClaudeLLM()  # Balance

        else:  # complex
            return GPT4LLM()  # Mejor razonamiento
```

---

## Glosario Agentico

| Término | Definición |
|---------|------------|
| **Agente** | Entidad que percibe, razona y actúa sobre un dominio específico |
| **Coordinator** | Agente orquestador que coordina otros agentes |
| **SharedContext** | Memoria compartida entre agentes durante un request |
| **DecisionTrace** | Registro completo de decisiones tomadas por agentes |
| **Prompt-First** | Paradigma donde lenguaje natural es interfaz primaria |
| **Geo-Temporal** | Combinación de ubicación geográfica y tiempo |
| **Observability** | Capacidad de inferir estado interno desde outputs externos |
| **Recoverable** | Propiedad de un agente de permitir continuidad tras fallo |
| **Multi-LLM** | Uso de múltiples modelos de lenguaje según contexto |
| **Vendor Lock-in** | Dependencia excesiva de un proveedor específico |

---

**Última actualización**: Enero 22, 2026
**Versión**: 0.1.0 (Arquitectura Agentica)
**Autor**: Smart-Sync Concierge Architecture Team
