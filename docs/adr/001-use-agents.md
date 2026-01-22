# ADR 001 - Arquitectura Multi-Agente

## Estado
✅ Aceptado

## Contexto

Smart-Sync Concierge requiere procesar lenguaje natural para crear citas, con múltiples validaciones y consideraciones:

- **Extracción de información**: Fecha, hora, participantes, tipo de cita
- **Validación temporal**: Zonas horarias, horarios laborales, festivos
- **Validación de negocio**: Contactos existentes, servicios disponibles
- **Detección de conflictos**: Superposición de citas
- **Generación de alternativas**: Slots disponibles cuando hay conflicto

### Restricciones

- El sistema debe ser **explicable**: Usuarios deben entender por qué se toma una decisión
- El sistema debe ser **escalable**: Añadir nuevas validaciones sin refactor
- El sistema debe ser **recuperable**: Fallo de una validación no debe colapsar todo
- El sistema debe ser **observable**: Trazabilidad completa de decisiones

## Decisión

**Adoptar arquitectura multi-agente especializada.**

Cada agente es responsable de un dominio específico y colabora mediante un contexto compartido:

```
Usuario → CoordinatorAgent → [Specialized Agents] → Response
```

### Agentes Iniciales

| Agente | Responsabilidad |
|--------|-----------------|
| **ParsingAgent** | Extraer entidades e intenciones del prompt |
| **TemporalAgent** | Resolver referencias temporales y zonas horarias |
| **GeoAgent** | Validar coherencia geográfica y ubicaciones |
| **ValidationAgent** | Validar reglas de negocio |
| **AvailabilityAgent** | Detectar conflictos de disponibilidad |
| **NegotiationAgent** | Generar alternativas cuando hay conflictos |

### Patrón de Comunicación

1. **SharedContext**: Memoria compartida entre agentes
2. **DecisionTrace**: Registro de cada decisión tomada
3. **CoordinatorAgent**: Orquesta el flujo y maneja errores

## Consecuencias

### Positivas

- ✅ **Especialización**: Cada agente domina su dominio
- ✅ **Escalabilidad**: Añadir agentes sin modificar existentes
- ✅ **Recuperabilidad**: Fallo de un agente no colapsa el sistema
- ✅ **Explicabilidad**: DecisionTrace completo de razonamiento
- ✅ **Testabilidad**: Cada agente se testea independientemente
- ✅ **Mantenibilidad**: Cambios locales sin efectos globales

### Negativas

- ❌ **Complejidad inicial**: Más complejo que parser monolítico
- ❌ **Latencia**: Múltiples agentes agregan overhead (~10-20%)
- ❌ **Coordinación**: Requiere SharedContext bien diseñado
- ❌ **Debugging**: Más difícil que flujo lineal

### Riesgos

- **Coordinación de estado**: SharedContext puede volverse complejo
- **Performance**: Orquestación añade latencia
- **Consistencia**: Diferentes agentes pueden tener visiones conflictivas
- **Mantenimiento**: Más componentes que mantener

### Mitigaciones

- **Interfaces claras**: Cada agente tiene input/output bien definido
- **DecisionTrace**: Trazabilidad completa ayuda debugging
- **Circuit breakers**: Fallo de agente no afecta otros
- **Tests integrales**: Validar interacción entre agentes

## Alternativas Consideradas

### 1. Parser Monolítico

**Descripción**: Un solo servicio que procesa el prompt y valida todo.

**Por qué NO**:
- ❌ Difícil de mantener (todo en un lugar)
- ❌ Difícil de testear (acoplamiento alto)
- ❌ Difícil de extender (cambios afectan todo)
- ❌ Poca explicabilidad (caja negra)

### 2. Pipeline Lineal

**Descripción**: Pasos secuenciales donde cada paso recibe output del anterior.

**Por qué NO**:
- ❌ Fallo en paso temprano detiene todo
- ❌ Difícil añadir validaciones en medio
- ❌ No permite paralelización
- ❌ Contexto perdido entre pasos

### 3. Microservicios

**Descripción**: Cada agente como microservicio independiente.

**Por qué NO**:
- ❌ Overhead de comunicación red
- ❌ Complejidad operacional alta
- ❌ Demasiado para MVP
- ❌ Latencia de red significativa

**Nota**: Arquitectura permite migración a microservicios en el futuro si es necesario.

## Implementación

### Estado
- ✅ Propuesto: 2026-01-22
- ✅ Aceptado: 2026-01-22
- ⏳ En Progreso: [PR-123](https://github.com/...) (Implementación base)
- ⏸ Pendiente: Implementación completa de todos los agentes

### Componentes

| Componente | Estado | PR |
|------------|--------|-----|
| BaseAgent | ✅ Completado | [#45](https://github.com/...) |
| CoordinatorAgent | ✅ Completado | [#46](https://github.com/...) |
| SharedContext | ✅ Completado | [#47](https://github.com/...) |
| DecisionTrace | ✅ Completado | [#48](https://github.com/...) |
| ParsingAgent | ⏳ En Progreso | [#49](https://github.com/...) |
| TemporalAgent | ⏸ Pendiente | - |
| GeoAgent | ⏸ Pendiente | - |
| ValidationAgent | ⏸ Pendiente | - |
| AvailabilityAgent | ⏸ Pendiente | - |
| NegotiationAgent | ⏸ Pendiente | - |

### Referencias

- [Contratos de Agentes](../contracts/agents/)
- [Guía de Desarrollo de Agentes](../guides/agent-development.md)
- [System Design Doc](../architecture/agent-system.md)

## Supersedes

Supersede: Ninguno (primer ADR arquitectónico)

## Superseded By

Ninguno (activo)

---

**Autor**: Architecture Team
**Fecha**: Enero 22, 2026
**Revisado por**: Tech Lead, Product Owner
