# Documentación - Smart-Sync Concierge

Bienvenido al centro de documentación de Smart-Sync Concierge.

## 📚 Estructura de Documentación

```
docs/
├── README.md                    # Este archivo - Guía de navegación
│
├── architecture/                # Documentación arquitectónica
│   ├── overview.md              # Visión general del sistema
│   ├── agent-system.md          # Sistema multi-agente
│   ├── geo-temporal.md          # Validación geo-temporal
│   ├── ai-abstraction.md        # Abstracción de IA
│   └── observability.md         # Observabilidad y tracing
│
├── adr/                         # Architecture Decision Records
│   ├── README.md                # Guía de ADRs
│   ├── 001-use-agents.md        # Por qué arquitectura agentica
│   ├── 002-qwen-mvp.md          # Por qué Qwen en MVP
│   ├── 003-json-storage.md      # Por qué JSON local inicial
│   ├── 004-opentelemetry.md     # Por qué OpenTelemetry
│   ├── 005-prompt-first.md      # Por qué prompt-first paradigm
│   └── template.md              # Plantilla para nuevos ADRs
│
├── contracts/                   # Contratos y especificaciones
│   ├── api/                     # Especificaciones de API
│   │   ├── appointments.yaml    # OpenAPI spec citas
│   │   ├── contacts.yaml        # OpenAPI spec contactos
│   │   └── agents.yaml          # OpenAPI spec agentes
│   │
│   ├── agents/                  # Contratos de agentes
│   │   ├── parsing-agent.md     # ParserAgent contrato
│   │   ├── temporal-agent.md    # TemporalAgent contrato
│   │   ├── geo-agent.md         # GeoAgent contrato
│   │   ├── validation-agent.md  # ValidationAgent contrato
│   │   └── negotiation-agent.md # NegotiationAgent contrato
│   │
│   ├── events/                  # Contratos de eventos
│   │   ├── appointment-events.md # Eventos de citas
│   │   └── agent-events.md       # Eventos de agentes
│   │
│   └── schemas/                 # Esquemas de datos
│       ├── appointment.json     # Schema de cita
│       ├── contact.json         # Schema de contacto
│       ├── decision-trace.json  # Schema de trace
│       └── shared-context.json  # Schema de contexto
│
├── checklists/                  # Checklists de implementación
│   ├── mvp-checklist.md         # Checklist MVP v0.1.0
│   ├── agent-implementation.md  # Implementación de agentes
│   ├── api-endpoint.md          # Implementación de endpoints
│   ├── testing.md               # Checklist de testing
│   └── deployment.md            # Checklist de despliegue
│
├── guides/                      # Guías prácticas
│   ├── getting-started.md       # Primeros pasos
│   ├── agent-development.md     # Desarrollo de agentes
│   ├── prompt-engineering.md    # Ingeniería de prompts
│   └── debugging-agents.md      # Debugging de sistemas agenticos
│
├── operations/                  # Documentación operacional
│   ├── monitoring.md            # Monitoreo y alertas
│   ├── incident-response.md     # Respuesta a incidentes
│   └── runbooks/                # Runbooks operacionales
│       ├── agent-failure.md     # Fallo de agente
│       └── llm-degradation.md   # Degradación LLM
│
└── reference/                   # Referencia técnica
    ├── api-reference.md         # Referencia completa API
    ├── agent-reference.md       # Referencia de agentes
    └── glossary.md              # Glosario de términos
```

## 🚀 Comenzando

### ¿Nuevo en el proyecto?

1. Lee [architecture/overview.md](architecture/overview.md) para entender el sistema
2. Revisa [adr/README.md](adr/README.md) para entender decisiones arquitectónicas
3. Consulta [checklists/mvp-checklist.md](checklists/mvp-checklist.md) para tareas pendientes

### ¿Desarrollando un agente?

1. Lee [guides/agent-development.md](guides/agent-development.md)
2. Revisa [contracts/agents/](contracts/agents/) para contratos
3. Usa [checklists/agent-implementation.md](checklists/agent-implementation.md)

### ¿Implementando un endpoint?

1. Consulta [contracts/api/](contracts/api/) para especificaciones OpenAPI
2. Revisa [checklists/api-endpoint.md](checklists/api-endpoint.md)
3. Lee [guides/getting-started.md](guides/getting-started.md)

## 📋 Documentación por Rol

### Desarrolladores

- [Architecture Overview](architecture/overview.md)
- [Agent System](architecture/agent-system.md)
- [Agent Development Guide](guides/agent-development.md)
- [API Reference](reference/api-reference.md)

### Arquitectos

- [ADRs](adr/README.md) - Decisiones arquitectónicas
- [Architecture Documents](architecture/)
- [System Design](architecture/overview.md#system-design)

### DevOps/SRE

- [Deployment Checklist](checklists/deployment.md)
- [Monitoring](operations/monitoring.md)
- [Incident Response](operations/incident-response.md)
- [Runbooks](operations/runbooks/)

### QA/Testing

- [Testing Checklist](checklists/testing.md)
- [Agent Contracts](contracts/agents/)
- [API Contracts](contracts/api/)

## 🔍 Búsqueda Rápida

### Preguntas Frecuentes

| Pregunta | Documentación |
|----------|---------------|
| ¿Por qué agentes? | [ADR-001](adr/001-use-agents.md) |
| ¿Cómo implemento un agente? | [Agent Development Guide](guides/agent-development.md) |
| ¿Formato de API? | [OpenAPI Specs](contracts/api/) |
| ¿Testing de agentes? | [Testing Checklist](checklists/testing.md) |
| ¿Monitoreo? | [Monitoring Guide](operations/monitoring.md) |
| ¿Trazabilidad? | [Observability](architecture/observability.md) |

## 📝 Convenciones de Documentación

### Formatos

| Tipo | Formato | Ubicación |
|------|---------|-----------|
| Arquitectura | Markdown | `architecture/*.md` |
| ADRs | Markdown | `adr/*.md` |
| API Specs | OpenAPI 3.0 YAML | `contracts/api/*.yaml` |
| Contratos Agentes | Markdown | `contracts/agents/*.md` |
| Schemas | JSON Schema | `contracts/schemas/*.json` |
| Checklists | Markdown | `checklists/*.md` |
| Guías | Markdown | `guides/*.md` |

### Estándares de Escritura

- **Idioma**: Español (documentación), Inglés (código)
- **Títulos**: PascalCase para títulos, kebab-case para archivos
- **Código**: Bloques de código con sintaxis highlighting
- **Diagrams**: Mermaid o ASCII art
- **Versionado**: Incluir versión y fecha en cada documento

### Plantillas

- **ADR**: [adr/template.md](adr/template.md)
- **Agente Contract**: [contracts/agents/.template.md](contracts/agents/.template.md)
- **API Spec**: [contracts/api/.template.yaml](contracts/api/.template.yaml)

## 🔄 Actualización de Documentación

### Cuándo Actualizar

- **Antes de implementar**: ADRs, contratos, arquitectura
- **Durante implementación**: Checklists, guías
- **Después de implementar**: Referencia, runbooks

### Proceso de Actualización

1. **Crear branches**: `docs/feature-name`
2. **Actualizar documentación relevante**
3. **Actualizar índices**: Este archivo, README.md de secciones
4. **Pull request**: Incluir link a issue/code PR

### Review de Documentación

- Requerido para: ADRs, contratos API, arquitectura principal
- Opcional para: Guías, runbooks, checklists
- Reviewers: Architect + Tech Lead

## 📊 Métricas de Documentación

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| ADRs publicados | 5+ | 6 |
| Contratos de agentes | 6 | 6 |
| Contratos de eventos | 2 | 2 |
| Especificaciones API | 3+ | 3 |
| Guías prácticas | 4+ | 4 |
| Runbooks operacionales | 2+ | 2 |
| Esquemas JSON | 5+ | 5 |

## 🚧 Estado de Documentación

| Sección | Completitud | Última Actualización |
|---------|-------------|---------------------|
| Architecture | 100% | 2026-01-22 |
| ADRs | 100% (6/6) | 2026-01-22 |
| Contracts | 100% | 2026-01-22 |
| Checklists | 100% | 2026-01-22 |
| Guides | 100% (4/4) | 2026-01-22 |
| Operations | 100% | 2026-01-22 |
| Reference | 80% | 2026-01-22 |

## 🔗 Recursos Externos

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [OpenTelemetry](https://opentelemetry.io/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Qwen AI](https://qwen.readthedocs.io/)

## 🤝 Contribuir a la Documentación

Ver [CONTRIBUTING.md](../CONTRIBUTING.md) para guías de contribución.

### Líneas Guía

1. **Docs-first**: Documentación antes que código
2. **ADRs para decisiones**: Registrar decisiones arquitectónicas
3. **Contratos para interfaces**: Especificar antes de implementar
4. **Checklists para implementación**: Validar antes de merge
5. **Runbooks para operaciones**: Documentar incidentes

---

**Última actualización**: Enero 22, 2026
**Versión**: 0.1.0
**Mantenedor**: Architecture Team
