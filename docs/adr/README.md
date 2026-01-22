# Architecture Decision Records (ADRs)

## ¿Qué son los ADRs?

Los **Architecture Decision Records (ADRs)** documentan decisiones arquitectónicas significativas en el proyecto. Cada ADR captura:

1. **Contexto**: El problema o situación que requiere una decisión
2. **Decisión**: La solución elegida
3. **Consecuencias**: Impacto positivo y negativo de la decisión
4. **Alternativas consideradas**: Opciones descartadas y por qué

## Por qué ADRs

- **Trazabilidad**: Entender por qué se tomaron decisiones
- **Onboarding**: Nuevos miembros entienden arquitectura rápidamente
- **Revisión**: Permite cuestionar y revertir decisiones
- **Comunicación**: Compartir decisiones con stakeholders

## Estructura de un ADR

```markdown
# Número - Título de la Decisión

## Estado
[Propuesto | Aceptado | Deprecado | Suplantado]

## Contexto
¿Qué problema estamos resolviendo? ¿Qué restricciones existen?

## Decisión
Descripción clara de la decisión tomada.

## Consecuencias
- **Positivas**: Beneficios de esta decisión
- **Negativas**: Costes y desventajas
- **Riesgos**: Qué podría salir mal

## Alternativas Consideradas
1. **Alternativa 1**: Descripción y por qué no se eligió
2. **Alternativa 2**: Descripción y por qué no se eligió

## Referencias
- Links a documentación relevante
- Discusiones del equipo
- PRs relacionados

## Implementación
- Estado de implementación
- Links a código/PRs
```

## ADRs de Smart-Sync Concierge

| ADR | Título | Estado | Fecha |
|-----|--------|--------|-------|
| [001](001-use-agents.md) | Arquitectura Multi-Agente | ✅ Aceptado | 2026-01-22 |
| [002](002-qwen-mvp.md) | Qwen como LLM por defecto | ✅ Aceptado | 2026-01-22 |
| [003](003-json-storage.md) | JSON Local para MVP | ✅ Aceptado | 2026-01-22 |
| [004](004-opentelemetry.md) | OpenTelemetry para Observabilidad | ✅ Aceptado | 2026-01-22 |
| [005](005-prompt-first.md) | Paradigma Prompt-First | ✅ Aceptado | 2026-01-22 |

## Flujo de Creación de ADR

### 1. Proponer

```bash
# Copiar plantilla
cp adr/template.md adr/006-decision-title.md

# Completar secciones del ADR
# Estado: "Propuesto"
```

### 2. Discutir

- Crear PR con el ADR propuesto
- Solicitar feedback del equipo
- Revisar en arquitectura weekly

### 3. Decidir

- Consenso del equipo: Cambiar estado a "Aceptado"
- Rechazado: Archivar con notas
- Modificar: Iterar hasta consenso

### 4. Implementar

- Referenciar ADR en PRs de código
- Actualizar ADR con enlaces a implementación
- Marcar como completado cuando corresponda

### 5. Revisar

- Periodicamente revisar ADRs
- Actualizar si contexto cambia
- Suplantar si decisión se revierte

## Plantilla de ADR

Ver [template.md](template.md) para la plantilla completa.

## Convenciones

### Nomenclatura

- Formato: `NNN-titulo-corto.md`
- NNN: Número secuencial (001, 002, ...)
- Título: kebab-case, descriptivo
- Ejemplo: `003-json-storage.md`

### Estados

| Estado | Descripción | Cuándo usar |
|--------|-------------|-------------|
| Propuesto | Bajo revisión | Inicialmente |
| Aceptado | Decisión tomada | Después de aprobación |
| Deprecado | Ya no se aplica | Cuando se reemplaza |
| Suplantado | Reemplazado por otro | Referencia al nuevo ADR |

### Contenido Mínimo

Todo ADR debe incluir:

- ✅ Contexto claro
- ✅ Decisión explícita
- ✅ Consecuencias (positivas y negativas)
- ✅ Al menos 2 alternativas consideradas
- ✅ Fecha y autor

## Archivo de ADRs

ADRs no se eliminan, se marcan como **Deprecado** o **Suplantado**.

```
001-use-agents.md          # Aceptado
002-qwen-mvp.md            # Aceptado
003-json-storage.md        # Suplantado por 015-postgres-migration.md
004-opentelemetry.md       # Aceptado
005-prompt-first.md        # Aceptado
...
```

## Herramientas

### Visualización

- [adr-viewer](https://github.com/npryce/adr-tools): Visualizador de ADRs
- VS Code: Extension de Markdown preview

### Integración con Git

```bash
# Listar ADRs
ls -1 adr/*.md | grep -v template

# Buscar ADR por estado
grep -l "Aceptado" adr/*.md

# Encontrar ADRs que referencian "agents"
grep -r "agents" adr/*.md
```

## Lecturas Recomendadas

- [Record Architecture Decisions](https://www.thoughtworks.com/insights/blog/record-architecture-decisions)
- [Markdown Architecture Decision Records](https://adr.github.io/)
- [Documenting Architecture Decisions](https://www.infoq.com/articles/documenting-architecture-decisions/)

---

**Última actualización**: Enero 22, 2026
**Mantenedor**: Architecture Team
