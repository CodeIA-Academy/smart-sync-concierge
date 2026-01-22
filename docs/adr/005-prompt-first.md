# ADR 005 - Paradigma Prompt-First

## Estado
✅ Aceptado

## Contexto

Smart-Sync Concierge es un sistema de agendamiento que necesita ser accesible para:

- Usuarios finales no técnicos (pacientes, clientes)
- Staff administrativo (recepcionistas, asistentes)
- Integraciones con otros sistemas (chatbots, voz)

### Problema

Las APIs tradicionales requieren conocimiento de estructuras de datos:

```json
// ❌ API tradicional - difícil para usuarios
POST /api/v1/appointments/
{
  "contact_id": "contact_dr_perez",
  "start_time": "2026-01-23T10:00:00-06:00",
  "duration_minutes": 60,
  "service_type": "consulta_general"
}
```

### Objetivo

Hacer el sistema accesible mediante lenguaje natural:

```text
// ✅ Prompt-first - intuitivo
"cita mañana 10am con Dr. Pérez"
```

## Decisión

**Adoptar paradigma prompt-first como interfaz primaria.**

### Definición

**Prompt-First**: El lenguaje natural es la interfaz principal y preferida para interactuar con el sistema. Los endpoints estructurados existen pero son secundarios.

### Principios

1. **NLP como UI**: El prompt es la UI principal
2. **Progresivo**: Comenzar simple, añadir complejidad según necesidad
3. **Explicativo**: El sistema explica qué entiende y por qué
4. **Recuperable**: Ambigüedades se resuelven con preguntas
5. **Estructurado por detrás**: Prompt → Datos estructurados → Acción

## Consecuencias

### Positivas

- ✅ **Accesibilidad**:任何人 puede usar, sin conocimientos técnicos
- ✅ **UX natural**: Como hablar con un asistente humano
- ✅ **Flexibilidad**: Un mismo prompt puede expresar cosas de múltiples formas
- ✅ **Adaptable**: Fácil añadir nuevas capacidades (modificando prompts)
- ✅ **Voz-friendly**: Prompt-first facilita integración con voz
- ✅ **Reducido entrenamiento**: Usuarios aprenden rápido

### Negativas

- ❌ **Ambigüedad**: Lenguaje natural es inherentemente ambiguo
- ❌ **Complejidad de parsing**: Requiere IA para interpretar
- ❌ **Coste de IA**: Cada prompt consume tokens
- ❌ **Latencia**: IA añade ~1s vs API directa
- ❌ **Falsos positivos**: IA puede malinterpretar
- ❌ **Difícil testing**: Más variabilidad que inputs estructurados

### Riesgos

- **Expectativas no realistas**: Usuarios pueden pensar que el sistema "entiende" como un humano
- **Coste de escala**: Cada cuesta tokens, puede ser costoso
- **Frustración**: Si IA malinterpreta frecuentemente
- **Dependencia de IA**: Si servicio IA cae, sistema inutilizable

### Mitigaciones

- **Fallback a estructurado**: API estructurada disponible para integraciones
- **Confirmación activa**: "¿Confirmas cita para el 23 de enero a las 10am con Dr. Pérez?"
- **Confidence scoring**: Si confianza <80%, pedir confirmación
- **Aprendizaje**: Mejorar prompts con feedback de usuarios
- **Caché**: Prompts comunes cachean respuestas

## Alternativas Consideradas

### 1. UI Tradicional con Formularios

**Descripción**: Formulario web con campos estructurados.

**Por qué NO**:
- ❌ Requiere entrenamiento de usuario
- ❌ Menos natural que lenguaje
- ✅ Más preciso (no ambigüedad)
- ✅ No depende de IA

**Decisión**: Formulario disponible como alternativa, no primario

### 2. Command-Based

**Descripción**: Comandos estructurados pero en texto: `/cita Dr. Pérez mañana 10am`

**Por qué NO**:
- ❌ Requiere aprender sintaxis de comandos
- ❌ Less flexible
- ✅ Más simple de parsear
- ✅ No requiere IA

**Decisión**: Commands disponibles para power users, no primario

### 3. Hybrid (Prompt + Structured)

**Descripción**: Prompt principal, pero UI muestra campos estructurados para editar.

**Por qué SÍ como complemento**:
- ✅ Mejor de ambos mundos
- ✅ Usuario puede ver qué entendió el sistema
- ✅ Puede corregir antes de confirmar

**Decisión**: Implementar en v0.2.0+

## Diseño de Interacción Prompt-First

### Niveles de Sofisticación

```
Nivel 1: Básico (MVP)
Usuario: "cita mañana 10am con Dr. Pérez"
Sistema: "Entendido: cita mañana (23/01) a las 10am con Dr. Pérez. ¿Confirmas?"

Nivel 2: Con Corrección
Usuario: "cita mañana 10am con Dr. Pérez"
Sistema: {
  "fecha": "2026-01-23",
  "hora": "10:00",
  "contacto": "Dr. Pérez",
  "tipo": "consulta_general"
}
Usuario: [Edita "consulta_general" a "pediatria"]
Sistema: "Cita confirmada: pediatria con Dr. Pérez, mañana a las 10am"

Nivel 3: Conversacional
Usuario: "quiero una cita"
Sistema: "¿Con quién y para cuándo?"
Usuario: "con el Dr. Pérez, mañana"
Sistema: "¿A qué hora?"
Usuario: "a las 10am"
Sistema: "Cita confirmada: Dr. Pérez, mañana a las 10am"
```

### Manejo de Ambigüedades

```
Usuario: "cita con el doctor"
→ Ambigüedad detectada (confidence <80%)
→ Preguntar: "¿Qué doctor? [Dr. Pérez, Dra. García, Dr. López]"

Usuario: "cita el martes por la tarde"
→ Ambigüedad detectada
→ Preguntar: "¿El martes 27 o el martes 3?"

Usuario: "cita a las 10am"
→ Ambigüedad detectada (¿qué día?)
→ Preguntar: "¿Para qué día?"
```

### Explicación de Razonamiento

```
Usuario: "cita mañana con Dr. Pérez a las 3am"

Sistema:
{
  "status": "invalid",
  "reasoning": {
    "agent": "validation_agent",
    "issues": [
      {
        "field": "hora",
        "problem": "Fuera de horario laboral",
        "detected": "03:00",
        "valid_range": "09:00-18:00"
      }
    ],
    "suggestion": "Dr. Pérez atiende de 9am a 6pm. ¿Te sirve a las 9am o a las 10am?"
  }
}
```

## API Endpoints

### Primario: Prompt-First

```http
POST /api/v1/appointments/
Content-Type: application/json

{
  "prompt": "cita mañana 10am con Dr. Pérez",
  "opciones": {
    "idioma": "es",
    "zona_horaria": "America/Mexico_City"
  }
}
```

### Secundario: Estructurado (para integraciones)

```http
POST /api/v1/appointments/structured
Content-Type: application/json

{
  "contact_id": "contact_dr_perez",
  "start_time": "2026-01-23T10:00:00-06:00",
  "duration_minutes": 60,
  "service_type": "consulta_general"
}
```

### Conversacional (v0.3.0+)

```http
POST /api/v1/appointments/conversation
Content-Type: application/json

{
  "session_id": "sess_abc123",
  "message": "quiero una cita"
}
```

## Métricas de Éxito

| Métrica | Objetivo MVP | Objetivo v0.5.0 |
|---------|-------------|----------------|
| **Precisión de extracción** | >85% | >95% |
| **Tasa de ambigüedad** | <20% | <10% |
| **Confirmaciones requeridas** | <15% | <5% |
| **Satisfacción usuario** | >4/5 | >4.5/5 |
| **Coste por request** | <$0.01 | <$0.005 |

## Aprendizaje y Mejora

### Feedback Loop

```python
# Usuario confirma cita
await confirm_appointment(appointment)

# Prompt original vs. entidades extraídas
log_prompt_feedback(
    prompt="cita mañana 10am con Dr. Pérez",
    extracted_entities={
        "fecha": "2026-01-23",
        "hora": "10:00",
        "contacto": "Dr. Pérez"
    },
    user_confirmed=True,  # Usuario confirmó correcto
    user_corrections=None  # Usuario no corrigió
)

# Analizar feedback para mejorar prompts
if user_corrections:
    await optimize_prompt_for_corrections(corrections)
```

### A/B Testing de Prompts

```python
# Dos versiones de prompt
prompt_v1 = "Extrae fecha, hora, contacto de: {prompt}"
prompt_v2 = """
Eres un asistente experto en agendamiento.
Analiza: {prompt}
Extrae entidades en formato JSON.
"""

# Testear cuál funciona mejor
results = await ab_test_prompts(
    prompt_a=prompt_v1,
    prompt_b=prompt_v2,
    metric="accuracy"
)
```

## Plan de Implementación

### MVP (v0.1.0)

- [ ] Endpoint `POST /api/v1/appointments/` con prompt
- [ ] ParsingAgent básico
- [ ] Manejo de ambigüedades simples
- [ ] Confirmación de cita

### v0.2.0

- [ ] Explicación de razonamiento en respuesta
- [ ] Corrección de entidades mal interpretadas
- [ ] Feedback loop para mejora

### v0.3.0+

- [ ] Interacción conversacional multi-turno
- [ ] Aprendizaje con feedback de usuario
- [ ] A/B testing de prompts
- [ ] Personalización por usuario

## Implementación

### Estado
- ✅ Propuesto: 2026-01-22
- ✅ Aceptado: 2026-01-22
- ⏳ En Progreso: Diseño

### Componentes

| Componente | Estado |
|------------|--------|
| Prompt endpoint | ⏸ Pendiente |
| ParsingAgent (prompt→entidades) | ⏸ Pendiente |
| Confirmation flow | ⏸ Pendiente |
| Ambiguity detection | ⏸ Pendiente |
| Feedback collection | ⏸ Pendiente |

### Referencias

- [Prompt Engineering Guide](../guides/prompt-engineering.md)
- [Contrato ParsingAgent](../contracts/agents/parsing-agent.md)
- [API Reference](../reference/api-reference.md)

## Supersedes

Supersede: Ninguno

## Superseded By

Ninguno (activo)

---

**Autor**: Architecture Team
**Fecha**: Enero 22, 2026
**Revisado por**: Tech Lead, Product Owner, UX Designer
