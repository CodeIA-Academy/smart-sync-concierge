# Checklist MVP v0.1.0 - Smart-Sync Concierge

## Información

- **Versión**: 0.1.0
- **Objetivo**: Lanzamiento MVP de API de citas agentica
- **Fecha objetivo**: [Por definir]
- **Estado**: ⏳ En Planeación

---

## 📋 Checklist Completo

### ✅ Fase 1: Fundamentos del Proyecto

#### Configuración Django
- [ ] Crear proyecto Django 6.0.1
- [ ] Configurar estructura de settings fragmentados
  - [ ] `config/settings/base.py`
  - [ ] `config/settings/ai.py`
  - [ ] `config/settings/observability.py`
  - [ ] `config/settings/storage.py`
- [ ] Configurar URLs (`config/urls.py`)
- [ ] Crear estructura de carpetas (apps, core, docs)

#### Dependencias
- [ ] Crear `requirements.txt`
  - [ ] Django==6.0.1
  - [ ] djangorestframework==3.15.2
  - [ ] django-cors-headers==4.6.0
  - [ ] qwen==2.5.0
  - [ ] python-dateutil==2.9.0
  - [ ] pytz==2024.2
  - [ ] pydantic==2.10.4
- [ ] Crear `.env.example`
- [ ] Documentar instalación en `README.md`

#### Constantes Globales
- [ ] Crear `core/constants.py`
  - [ ] TIMEZONES
  - [ ] DEFAULT_DURATIONS
  - [ ] APPOINTMENT_STATUS
  - [ ] CONTENT_WIDTH (para consistencia UI)
- [ ] Crear `core/exceptions.py`
- [ ] Crear `core/utils.py`

---

### ✅ Fase 2: Framework de Agentes

#### Base Agent
- [ ] Crear `core/agents/base_agent.py`
  - [ ] Clase `BaseAgent` abstracta
  - [ ] Propiedades: `name`, `version`, `recoverable`
  - [ ] Método `process(context: SharedContext)`
  - [ ] Método `safe_process()` con recovery

#### SharedContext
- [ ] Crear `core/agents/context.py`
  - [ ] Clase `SharedContext`
  - [ ] Métodos: `get()`, `update()`
  - [ ] Versionado de cambios
  - [ ] Thread-safe

#### DecisionTrace
- [ ] Crear `core/agents/decision_trace.py`
  - [ ] Clase `Decision`
  - [ ] Clase `DecisionTrace`
  - [ ] Método `record_decision()`
  - [ ] Método `explain()`
  - [ ] Export a JSON

#### CoordinatorAgent
- [ ] Crear `core/agents/coordinator_agent.py`
  - [ ] Seleccionar secuencia de agentes
  - [ ] Orquestar ejecución
  - [ ] Manejar errores de agentes
  - [ ] Compilar resultado final

---

### ✅ Fase 3: Abstracción de IA

#### Interfaz BaseLLM
- [ ] Crear `core/ai/base_llm.py`
  - [ ] Clase `LLMRequest`
  - [ ] Clase `LLMResponse`
  - [ ] Clase abstracta `BaseLLM`
  - [ ] Métodos: `complete()`, `stream_complete()`

#### Proveedores
- [ ] Crear `core/ai/providers/qwen_provider.py`
  - [ ] Clase `QwenLLM`
  - [ ] Implementar `complete()`
  - [ ] Implementar `estimate_cost()`
- [ ] (Opcional) `core/ai/providers/claude_provider.py`
- [ ] (Opcional) `core/ai/providers/openai_provider.py`

#### Factory
- [ ] Crear `core/ai/llm_factory.py`
  - [ ] Clase `LLMFactory`
  - [ ] Método `create(provider, **kwargs)`
  - [ ] Registro dinámico de proveedores

#### Prompts
- [ ] Crear `core/ai/prompts/template_engine.py`
  - [ ] Clase `PromptTemplate`
  - [ ] Método `render(**kwargs)`
  - [ ] Carga desde archivo
- [ ] Crear directorio `core/ai/prompts/templates/`
  - [ ] `extraction.txt`
  - [ ] `validation.txt`
  - [ ] `conflict.txt`

---

### ✅ Fase 4: Agentes de Dominio

#### ParsingAgent
- [ ] Crear `apps/appointments/agents/parsing_agent.py`
  - [ ] Hereda de `BaseAgent`
  - [ ] Extraer entidades del prompt
  - [ ] Detectar intenciones
  - [ ] Detectar ambigüedades
  - [ ] Calcular confianza
- [ ] Escribir tests unitarios
- [ ] Escribir contrato en `docs/contracts/agents/parsing-agent.md`

#### TemporalAgent
- [ ] Crear `core/geo_temporal/temporal_agent.py`
  - [ ] Hereda de `BaseAgent`
  - [ ] Resolver expresiones relativas ("mañana")
  - [ ] Normalizar zonas horarias
  - [ ] Validar restricciones temporales
  - [ ] Generar explicación
- [ ] Escribir tests unitarios
- [ ] Escribir contrato en `docs/contracts/agents/temporal-agent.md`

#### GeoAgent
- [ ] Crear `core/geo_temporal/geo_agent.py`
  - [ ] Hereda de `BaseAgent`
  - [ ] Detectar ubicación usuario
  - [ ] Mapear contacto a ubicación
  - [ ] Validar coherencia geográfica
- [ ] Escribir tests unitarios
- [ ] Escribir contrato

#### ValidationAgent
- [ ] Crear `apps/appointments/agents/validation_agent.py`
  - [ ] Validar contacto existe
  - [ ] Validar servicio disponible
  - [ ] Validar reglas de negocio
- [ ] Escribir tests unitarios

#### AvailabilityAgent
- [ ] Crear `apps/appointments/agents/availability_agent.py`
  - [ ] Buscar citas existentes
  - [ ] Detectar conflictos
  - [ ] Validar disponibilidad
- [ ] Escribir tests unitarios

#### NegotiationAgent
- [ ] Crear `apps/appointments/agents/negotiation_agent.py`
  - [ ] Generar alternativas
  - [ ] Priorizar por cercanía
  - [ ] Justificar cada sugerencia
- [ ] Escribir tests unitarios

---

### ✅ Fase 5: Storage JSON

#### Repositorio Base
- [ ] Crear `core/storage/json_repository.py`
  - [ ] Clase `JSONRepository`
  - [ ] Métodos: `save()`, `get()`, `list()`, `update()`, `delete()`
  - [ ] Atomic writes (temp + rename)
  - [ ] File locking

#### Stores Específicos
- [ ] Crear `apps/appointments/storage/appointment_store.py`
  - [ ] Hereda de `JSONRepository`
  - [ ] Métodos específicos de citas
- [ ] Crear `apps/contacts/storage/contact_store.py`
- [ ] Crear `apps/services/storage/service_store.py`

#### Esquemas JSON
- [ ] Crear `data/appointments.json`
- [ ] Crear `data/contacts.json`
- [ ] Crear `data/services.json`
- [ ] Crear `data/config.json`
- [ ] Crear `data/decisions/decision_log.json`
- [ ] Documentar esquemas en `docs/contracts/schemas/`

---

### ✅ Fase 6: API REST

#### Endpoints de Citas
- [ ] `POST /api/v1/appointments/` - Crear desde prompt
  - [ ] Integrar con CoordinatorAgent
  - [ ] Retornar respuesta con trace_id
- [ ] `GET /api/v1/appointments/` - Listar
  - [ ] Filtros: fecha, contacto, estado
  - [ ] Paginación
- [ ] `GET /api/v1/appointments/{id}/` - Detalle
- [ ] `PUT /api/v1/appointments/{id}/` - Actualizar
- [ ] `DELETE /api/v1/appointments/{id}/` - Cancelar
- [ ] `POST /api/v1/appointments/{id}/reschedule/` - Reprogramar

#### Endpoints de Disponibilidad
- [ ] `GET /api/v1/availability/`
- [ ] `GET /api/v1/availability/slots/`

#### Endpoints de Contactos
- [ ] `GET /api/v1/contacts/`
- [ ] `POST /api/v1/contacts/`
- [ ] `GET /api/v1/contacts/{id}/`

#### Endpoints de Servicios
- [ ] `GET /api/v1/services/`
- [ ] `POST /api/v1/services/`

#### OpenAPI Spec
- [ ] Crear `contracts/api/appointments.yaml`
- [ ] Crear `contracts/api/contacts.yaml`
- [ ] Crear `contracts/api/services.yaml`
- [ ] Integrar con DRF Spectacular

---

### ✅ Fase 7: Observabilidad

#### OpenTelemetry Setup
- [ ] Instalar `opentelemetry-api`, `opentelemetry-sdk`
- [ ] Configurar tracer en `config/settings/observability.py`
- [ ] Crear `core/observability/tracer.py`
  - [ ] Decorador `@traced_agent`

#### Metrics
- [ ] Crear `core/observability/metrics.py`
  - [ ] `appointment_requests_total`
  - [ ] `agent_execution_duration_seconds`
  - [ ] `agent_errors_total`
  - [ ] `llm_tokens_used_total`

#### Logging
- [ ] Configurar logging estructurado
- [ ] Logs a stdout (Docker ready)
- [ ] Niveles: DEBUG (dev), INFO (prod)

#### DecisionTrace
- [ ] Guardar traces en `data/decisions/decision_log.json`
- [ ] Endpoint `GET /api/v1/traces/{id}`

---

### ✅ Fase 8: Admin de Django

#### Configuración
- [ ] Registrar modelos en admin
- [ ] Configurar URLs amigables
  - [ ] `/admin/citas/`
  - [ ] `/admin/citas/agregar/`
  - [ ] `/admin/citas/{id}/`
- [ ] Listas con filtros

#### Vistas Custom
- [ ] Vista de calendario
- [ ] Vista de conflictos
- [ ] Dashboard con métricas

---

### ✅ Fase 9: Testing

#### Unit Tests
- [ ] Tests de ParsingAgent
- [ ] Tests de TemporalAgent
- [ ] Tests de GeoAgent
- [ ] Tests de ValidationAgent
- [ ] Tests de AvailabilityAgent
- [ ] Tests de NegotiationAgent
- [ ] Tests de stores

#### Integration Tests
- [ ] Tests de pipeline completo
- [ ] Tests de endpoints API
- [ ] Tests de coordinación de agentes

#### Coverage
- [ ] >80% cobertura de código
- [ ] Reportes de coverage en HTML

---

### ✅ Fase 10: Documentación

#### ADRs
- [x] ADR-001: Arquitectura Multi-Agente
- [x] ADR-002: Qwen como LLM
- [x] ADR-003: JSON Local Storage
- [x] ADR-004: OpenTelemetry
- [x] ADR-005: Prompt-First

#### Contratos
- [x] ParsingAgent contract
- [x] TemporalAgent contract
- [ ] GeoAgent contract
- [ ] ValidationAgent contract
- [ ] AvailabilityAgent contract
- [ ] NegotiationAgent contract

#### API Docs
- [ ] OpenAPI specs en `contracts/api/`
- [ ] `docs/api_reference.md` actualizado

#### Guías
- [ ] `docs/guides/getting-started.md`
- [ ] `docs/guides/agent-development.md`
- [ ] `docs/guides/prompt-engineering.md`

#### Referencia
- [ ] `docs/reference/api-reference.md`
- [ ] `docs/reference/agent-reference.md`
- [ ] `docs/reference/glossary.md`

---

### ✅ Fase 11: Despliegue

#### Pre-Producción
- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY seguro generado
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] CORS configurado

#### Docker
- [ ] Crear `Dockerfile`
- [ ] Crear `docker-compose.yml`
- [ ] Tests de build y run

#### CI/CD
- [ ] Configurar GitHub Actions
  - [ ] Tests en cada PR
  - [ ] Linting (black, ruff)
  - [ ] Type checking (mypy)

#### Monitoring
- [ ] Jaeger configurado (o compatible)
- [ ] Prometheus configurado
- [ ] Dashboards básicos en Grafana

---

## 📊 Métricas de Éxito

### Funcionales
- [ ] **Precisión de extracción**: >85%
- [ ] **Tasa de ambigüedad**: <20%
- [ ] **Conflictos detectados**: 100%
- [ ] **Sugerencias útiles**: >80%

### Técnicos
- [ ] **Latencia p95**: <3s
- [ ] **Error rate**: <5%
- [ ] **Coverage**: >80%
- [ ] **Uptime**: >95%

### Presupuesto
- [ ] **Coste IA mensual**: <$50
- [ ] **Coste infraestructura**: <$20

---

## 🎯 Definición de "Done"

El MVP está completo cuando:

1. ✅ Usuario puede crear cita con lenguaje natural
2. ✅ Sistema detecta conflictos y sugiere alternativas
3. ✅ Decisiones son trazables (trace_id)
4. ✅ Admin funciona para gestionar citas
5. ✅ Tests pasan con >80% coverage
6. ✅ Documentación está completa
7. ✅ Despliegue en staging funciona

---

## 📝 Notas

- **En orden de prioridad**: Fase 1 → Fase 11
- **Dependencias críticas**: Fase 2 y 3 antes que Fase 4
- **Paralelizable**: Fases 5, 6, 7 pueden ser en paralelo
- **Documentación**: Docs-first, documentar antes de implementar

---

**Propietario**: Tech Lead
**Última actualización**: Enero 22, 2026
