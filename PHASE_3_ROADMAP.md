# Phase 3: AI Agent Integration Roadmap - v0.2.0

**Estado:** 📋 Planificación
**Versión Objetivo:** 0.2.0
**Fecha Inicio Planificada:** 2026-01-27
**Duración Estimada:** -

---

## Visión General

En Phase 3 implementaremos la **integración de agentes IA** que transforman prompts en lenguaje natural a citas estructuradas. El sistema utilizará una arquitectura de agentes especializados que trabajan en pipeline para:

1. **Parsear** prompts en lenguaje natural
2. **Razonar temporalmente** con fechas relativas
3. **Razonar geográficamente** con ubicaciones
4. **Validar** datos extraídos
5. **Verificar disponibilidad** en tiempo real
6. **Negociar** conflictos con sugerencias

---

## Arquitectura de Agentes (6 agentes especializados)

### 1. Parsing Agent
**Responsabilidad:** Extraer entidades de lenguaje natural

**Entrada:**
```python
{
    "prompt": "cita mañana 10am con Dr. Pérez en la clínica norte",
    "user_timezone": "America/Mexico_City",
    "user_context": {...}
}
```

**Salida:**
```python
{
    "fecha": "2026-01-24",  # YYYY-MM-DD
    "hora_inicio": "10:00",  # HH:MM
    "contacto_nombre": "Dr. Pérez",
    "ubicacion": "clínica norte",
    "ambiguities": []
}
```

**Métodos:**
- Extrae: fechas, horas, nombres de contactos, ubicaciones, servicios
- Identifica: entidades ambiguas o faltantes
- Normaliza: formato de datos

**Tecnología:** Qwen 2.5 / LLM genérico

---

### 2. Temporal Reasoning Agent
**Responsabilidad:** Resolver fechas y horas relativas

**Entrada:**
```python
{
    "raw_date": "mañana",
    "raw_time": "10am",
    "user_timezone": "America/Mexico_City",
    "current_datetime": "2026-01-23T15:30:00-06:00"
}
```

**Salida:**
```python
{
    "fecha": "2026-01-24",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "timezone": "America/Mexico_City",
    "confidence": 0.95
}
```

**Métodos:**
- Resuelve: "mañana", "próxima semana", "en 3 días", etc.
- Maneja: rangos de tiempo ("10am a 11am")
- Convierte: entre zonas horarias
- Valida: horas en horario comercial

**Tecnología:** LLM + librería dateutil/arrow

---

### 3. Geographical Reasoning Agent
**Responsabilidad:** Resolver referencias geográficas

**Entrada:**
```python
{
    "location_reference": "clínica norte",
    "contact_id": "contact_dr_perez_123",
    "available_locations": [
        {"id": "loc_1", "nombre": "Clínica Centro", ...},
        {"id": "loc_2", "nombre": "Clínica Norte", ...}
    ]
}
```

**Salida:**
```python
{
    "location_id": "loc_2",
    "location_name": "Clínica Norte",
    "matched_by": "fuzzy_match",
    "confidence": 0.92
}
```

**Métodos:**
- Resuelve: referencias vaguasticamente ("la clínica" → "Clínica Centro")
- Matching: fuzzy string matching (difflib)
- Validación: verifica ubicación existe para contacto
- Fallback: sugiere opciones si hay ambigüedad

**Tecnología:** LLM + difflib / fuzzy matching

---

### 4. Validation Agent
**Responsabilidad:** Validar integridad de datos

**Entrada:**
```python
{
    "contacto_id": "contact_dr_perez_123",
    "fecha": "2026-01-24",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "ubicacion_id": "loc_2",
    "servicio_id": "service_consulta"
}
```

**Salida:**
```python
{
    "valid": true,
    "errors": [],
    "warnings": [],
    "validated_data": {...}
}
```

**Métodos:**
- Valida: formatos (YYYY-MM-DD, HH:MM, IDs)
- Verifica: entidades existen (contacto, ubicación, servicio)
- Comprueba: duraciones válidas
- Detecta: cambios de atributos no permitidos

**Tecnología:** Validadores DRF + lógica personalizada

---

### 5. Availability Agent
**Responsabilidad:** Verificar disponibilidad en tiempo real

**Entrada:**
```python
{
    "contacto_id": "contact_dr_perez_123",
    "fecha": "2026-01-24",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "ubicacion_id": "loc_2",
    "servicio_id": "service_consulta"
}
```

**Salida:**
```python
{
    "available": true,
    "reason": null,
    "conflicts": [],
    "slots_disponibles": [...]
}
```

**Métodos:**
- Consulta: horarios de contacto
- Detecta: solapamientos de citas
- Valida: duración de servicio
- Retorna: slots alternativos si hay conflicto

**Tecnología:** AppointmentStore + ContactStore

---

### 6. Negotiation Agent
**Responsabilidad:** Manejar conflictos y proponer alternativas

**Entrada:**
```python
{
    "appointment_data": {...},
    "conflicts": [
        {
            "type": "full_overlap",
            "existing_apt_id": "apt_20260124_xyz",
            "message": "..."
        }
    ],
    "user_preferences": {
        "flexible_date": true,
        "flexible_time": true
    }
}
```

**Salida:**
```python
{
    "negotiation_needed": true,
    "status": "conflict",
    "suggestions": [
        {
            "fecha": "2026-01-24",
            "hora_inicio": "11:00",
            "confidence": 0.95,
            "reason": "Siguiente slot disponible"
        },
        {
            "fecha": "2026-01-25",
            "hora_inicio": "10:00",
            "confidence": 0.85,
            "reason": "Próximo día, misma hora"
        }
    ]
}
```

**Métodos:**
- Analiza: razón del conflicto
- Genera: alternativas (10 slots próximos)
- Ordena: por confianza/proximidad
- Retorna: top 5 sugerencias

**Tecnología:** Algoritmo de sugerencias + scoring

---

## Pipeline de Procesamiento

```
┌─────────────────┐
│   Raw Prompt    │
│  "cita mañana   │
│   10am con      │
│  Dr. Pérez"     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  1. PARSING AGENT           │
│  Extrae entidades           │
│  Output: contacto_nombre,   │
│  fecha_raw, hora_raw, etc.  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  2. TEMPORAL REASONING      │
│  Resuelve "mañana" → fecha  │
│  Resuelve "10am" → hora     │
│  Output: fecha, hora_inicio │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  3. GEO REASONING           │
│  Resuelve "clínica norte"   │
│  Output: location_id        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  4. VALIDATION AGENT        │
│  Valida: formatos, IDs      │
│  Output: validated_data     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  5. AVAILABILITY AGENT      │
│  Verifica disponibilidad    │
│  Output: available?         │
└────────┬──────┬─────────────┘
         │      │
      YES│      │NO
         │      ▼
         │  ┌──────────────────┐
         │  │ 6. NEGOTIATION   │
         │  │ Genera sugerencias
         │  │ Output: alternatives
         │  └──────────────────┘
         │
         ▼
    ┌─────────────┐
    │ Create Apt  │
    │ Response    │
    └─────────────┘
```

---

## Flujo de Decision Trace

Cada agente registra su decisión en un **DecisionTrace** que permite observabilidad completa:

```python
{
    "trace_id": "trace_20260123_abc123",
    "timestamp": "2026-01-23T15:30:00-06:00",
    "input_prompt": "cita mañana 10am con Dr. Pérez",
    "agents": [
        {
            "agent": "parsing",
            "status": "success",
            "input": {...},
            "output": {...},
            "duration_ms": 250,
            "confidence": 0.98
        },
        {
            "agent": "temporal_reasoning",
            "status": "success",
            "input": {...},
            "output": {...},
            "duration_ms": 150,
            "confidence": 0.95
        },
        # ... más agentes
    ],
    "final_status": "success",
    "final_output": {"appointment_id": "apt_..."},
    "total_duration_ms": 850
}
```

---

## Tareas de Implementación

### Tarea 1: Implementar Parsing Agent
**Estimación:** -
**Prioridad:** ⭐⭐⭐ CRÍTICA

1. Crear `apps/agents/parsing_agent.py`
2. Implementar clase `ParsingAgent`
3. Métodos:
   - `extract_date()` - Extrae referencias a fechas
   - `extract_time()` - Extrae referencias a horas
   - `extract_contact()` - Extrae nombre de contacto
   - `extract_location()` - Extrae ubicación
   - `extract_service()` - Extrae tipo de servicio
   - `detect_ambiguities()` - Identifica datos faltantes
   - `run()` - Orquesta extracción

4. Tests unitarios para cada método

---

### Tarea 2: Implementar Temporal Reasoning Agent
**Estimación:** -
**Prioridad:** ⭐⭐⭐ CRÍTICA

1. Crear `apps/agents/temporal_agent.py`
2. Implementar clase `TemporalReasoningAgent`
3. Métodos:
   - `resolve_date()` - Convierte "mañana" → "2026-01-24"
   - `resolve_time()` - Convierte "10am" → "10:00"
   - `resolve_range()` - Maneja "10am a 11am"
   - `convert_timezone()` - Convierte entre zonas horarias
   - `validate_business_hours()` - Verifica horario comercial

4. Tests para casos especiales (madrugada, fines de semana, etc.)

---

### Tarea 3: Implementar Geographical Reasoning Agent
**Estimación:** -
**Prioridad:** ⭐⭐ ALTA

1. Crear `apps/agents/geo_agent.py`
2. Implementar clase `GeoReasoningAgent`
3. Métodos:
   - `match_location()` - Fuzzy match de ubicaciones
   - `validate_location_for_contact()` - Verifica ubicación del contacto
   - `resolve_location()` - Resuelve referencia completa

4. Tests para fuzzy matching

---

### Tarea 4: Implementar Validation Agent
**Estimación:** -
**Prioridad:** ⭐⭐⭐ CRÍTICA

1. Crear `apps/agents/validation_agent.py`
2. Implementar clase `ValidationAgent`
3. Métodos:
   - `validate_all()` - Valida todo el appointment_data
   - `validate_format()` - Valida formatos
   - `validate_entities()` - Verifica existencia de entidades
   - `validate_duration()` - Valida duración del servicio

---

### Tarea 5: Implementar Availability Agent
**Estimación:** -
**Prioridad:** ⭐⭐⭐ CRÍTICA

1. Crear `apps/agents/availability_agent.py`
2. Usar: AppointmentStore + ContactStore
3. Métodos:
   - `check_availability()` - Verifica disponibilidad
   - `detect_conflicts()` - Identifica solapamientos
   - `get_available_slots()` - Retorna slots libres

---

### Tarea 6: Implementar Negotiation Agent
**Estimación:** -
**Prioridad:** ⭐⭐ ALTA

1. Crear `apps/agents/negotiation_agent.py`
2. Implementar clase `NegotiationAgent`
3. Métodos:
   - `generate_suggestions()` - Crea alternativas
   - `score_suggestion()` - Calcula confianza
   - `rank_suggestions()` - Ordena por relevancia

---

### Tarea 7: Crear Orchestrator Agent
**Estimación:** -
**Prioridad:** ⭐⭐⭐ CRÍTICA

1. Crear `apps/agents/orchestrator.py`
2. Implementar clase `AgentOrchestrator`
3. Responsabilidades:
   - Orquestar pipeline de 6 agentes
   - Manejar errores y fallbacks
   - Registrar DecisionTrace
   - Retornar respuesta final

**Método principal:**
```python
def process_appointment_prompt(self, prompt, user_timezone, user_id):
    """
    Procesa prompt en lenguaje natural.

    Flujo:
    1. Parsing Agent → extrae entidades
    2. Temporal Agent → resuelve fechas/horas
    3. Geo Agent → resuelve ubicaciones
    4. Validation Agent → valida datos
    5. Availability Agent → verifica disponibilidad
    6. Si hay conflicto → Negotiation Agent
    7. Registra DecisionTrace
    8. Retorna resultado
    """
```

---

### Tarea 8: Integrar Agentes en ViewSet
**Estimación:** -
**Prioridad:** ⭐⭐⭐ CRÍTICA

1. Actualizar `apps/appointments/views.py`
2. Reemplazar `_parse_appointment_prompt()` placeholder
3. Usar `AgentOrchestrator` en:
   - `AppointmentViewSet.create()` - Procesar prompts
   - `AppointmentViewSet.reschedule()` - Nuevas fechas

---

### Tarea 9: Crear Traces Endpoint
**Estimación:** -
**Prioridad:** ⭐ MEDIA

1. Crear `apps/traces/views.py`
2. Implementar `TracesViewSet`
3. Endpoints:
   - `GET /api/v1/traces/` - Listar traces
   - `GET /api/v1/traces/{id}/` - Detalle de trace
   - `GET /api/v1/appointments/{id}/trace/` - Trace de cita

---

### Tarea 10: Tests y Validación
**Estimación:** -
**Prioridad:** ⭐⭐⭐ CRÍTICA

1. Escribir tests unitarios para cada agente
2. Escribir tests de integración para orchestrator
3. Validar DecisionTrace output
4. Tester casos de error (ambigüedad, no encontrado, conflicto)

---

## Dependencias y Librerías

### Nuevas Librerías a Instalar

```bash
# Ya disponibles (instaladas en requirements.txt)
- djangorestframework==3.15.2
- python-dateutil  # Para parsing de fechas relativas
- arrow  # Para manejo de timezones
- difflib  # Fuzzy string matching (stdlib)

# Posibles futuras (v0.3.0+)
- ollama  # Para LLM local (alternativa a Qwen)
- langchain  # Para orquestación de agentes
- pydantic  # Para validación de esquemas
```

### Tecnología de LLM

**MVP (v0.2.0):** Usar Qwen 2.5 via API o local
**Futuro:** Permitir pluggable LLM providers

---

## Esquema de Base de Datos (JSON inicialmente)

Se agregará nueva estructura a `data/traces.json`:

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2026-01-23T15:30:00Z",
    "total_traces": 250,
    "description": "Agent decision traces for observability"
  },
  "traces": [
    {
      "trace_id": "trace_20260123_abc123",
      "timestamp": "2026-01-23T15:30:00-06:00",
      "appointment_id": "apt_20260124_xyz789",
      "input_prompt": "cita mañana 10am con Dr. Pérez",
      "user_timezone": "America/Mexico_City",
      "user_id": "user_123",
      "agents": [...],
      "final_status": "success",
      "total_duration_ms": 850
    }
  ]
}
```

---

## Ejemplos de Casos de Uso

### Caso 1: Prompt Simple, Resultado Exitoso

**Entrada:**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Token abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

**Procesamiento:**
1. Parsing → {contacto: "Dr. Pérez", fecha_raw: "mañana", hora_raw: "10am"}
2. Temporal → {fecha: "2026-01-24", hora_inicio: "10:00"}
3. Geo → {location_id: "loc_2"}
4. Validation → ✅ Válido
5. Availability → ✅ Disponible
6. Create Appointment

**Salida:**
```json
{
  "status": "success",
  "data": {
    "id": "apt_20260124_xyz789",
    "contacto_id": "contact_dr_perez_123",
    "fecha": "2026-01-24",
    "hora_inicio": "10:00",
    "status": "confirmed"
  },
  "trace_id": "trace_20260123_abc123",
  "_links": {
    "self": "/api/v1/appointments/apt_20260124_xyz789/",
    "trace": "/api/v1/traces/trace_20260123_abc123/"
  }
}
```

### Caso 2: Conflicto de Disponibilidad

**Entrada:**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Token abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita hoy 3pm con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

**Procesamiento:**
1. Parsing → {contacto: "Dr. Pérez", fecha_raw: "hoy", hora_raw: "3pm"}
2. Temporal → {fecha: "2026-01-23", hora_inicio: "15:00"}
3. Geo → {location_id: "loc_2"}
4. Validation → ✅ Válido
5. Availability → ❌ Conflicto (ya hay cita 15:00-16:00)
6. Negotiation → Genera 5 sugerencias

**Salida:**
```json
{
  "status": "error",
  "code": "CONFLICT",
  "message": "La hora solicitada no está disponible",
  "details": {
    "requested": {
      "fecha": "2026-01-23",
      "hora_inicio": "15:00"
    },
    "conflict": {
      "type": "full_overlap",
      "existing_appointment_id": "apt_20260123_xyz"
    }
  },
  "suggestions": [
    {
      "fecha": "2026-01-23",
      "hora_inicio": "16:00",
      "confidence": 0.95,
      "reason": "Siguiente slot disponible hoy"
    },
    {
      "fecha": "2026-01-24",
      "hora_inicio": "15:00",
      "confidence": 0.85,
      "reason": "Mañana a la misma hora"
    }
  ],
  "trace_id": "trace_20260123_abc123"
}
```

### Caso 3: Prompt Ambiguo

**Entrada:**
```bash
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Authorization: Token abc123" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita con el doctor",
    "user_timezone": "America/Mexico_City"
  }'
```

**Procesamiento:**
1. Parsing → Detecta ambigüedades: contacto ambiguo, fecha faltante
2. Retorna error 400 con detalles

**Salida:**
```json
{
  "status": "error",
  "code": "INSUFFICIENT_INFO",
  "message": "El prompt es ambiguo y requiere más información",
  "ambiguities": [
    {
      "field": "contacto",
      "message": "No especificó qué doctor",
      "suggestions": ["Dr. Pérez Cardiology", "Dr. García Pediatrics"]
    },
    {
      "field": "fecha",
      "message": "No especificó cuándo"
    }
  ]
}
```

---

## Criterios de Éxito (Fase 3)

- ✅ 6 agentes implementados y testeados
- ✅ Orchestrator funcionando correctamente
- ✅ Prompts simples procesados exitosamente
- ✅ Conflictos detectados y sugerencias generadas
- ✅ DecisionTrace registrado para observabilidad
- ✅ Tests unitarios + integración (>80% coverage)
- ✅ Documentación completa
- ✅ Ejemplo funcional en README

---

## Timeline Aproximado

| Tarea | Estimación |
|-------|------------|
| Tareas 1-3 (Agents básicos) | - |
| Tareas 4-6 (Agents verificación) | - |
| Tarea 7 (Orchestrator) | - |
| Tarea 8 (Integración ViewSet) | - |
| Tarea 9 (Traces Endpoint) | - |
| Tarea 10 (Tests) | - |
| **Total Phase 3** | **-** |

---

## Notas Importantes

1. **Fallback Graceful**: Si LLM falla, usar parsing basado en reglas
2. **Logging Completo**: Registrar cada decisión de agente para debugging
3. **Rate Limiting**: Aplicar límites a API de LLM para control de costos
4. **Versioning**: DecisionTrace incluye versión de cada agente
5. **Extensibilidad**: Arquitectura permite agregar nuevos agentes fácilmente

---

## Siguiente Fase (Phase 4 - v0.3.0)

- Migración de JSON a PostgreSQL
- Indexación de búsqueda
- Caché distribuido (Redis)
- Webhooks y eventos
- API webhooks para integraciones externas

---

**Estado:** 📋 Planificación completa
**Revisado:** 2026-01-27
**Siguiente Revisión:** Después de confirmar inicio de Phase 3
