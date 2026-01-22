# Contrato: NegotiationAgent

## Versión
1.0.0

## Responsabilidad

Generar alternativas inteligentes cuando una cita no puede ser agendada debido a conflictos o restricciones.

## Interfaz

### Entrada

```python
@dataclass
class NegotiationInput:
    """Input del NegotiationAgent."""
    original_request: AppointmentRequest
    conflict: Conflict
    conflicts: List[Conflict]
    user_constraints: Optional[UserConstraints]
    availability: AvailabilityOutput

@dataclass
class AppointmentRequest:
    """Request original de cita."""
    prompt: str
    preferred_date: Optional[date]
    preferred_time: Optional[time]
    contact_id: str
    tipo_cita: Optional[str]

@dataclass
class UserConstraints:
    """Restricciones del usuario."""
    date_range: Optional[DateRange]  # "próxima semana"
    time_range: Optional[TimeRange]  # "mañana", "tarde"
    flexibility: str  # "low", "medium", "high"
```

### Salida

```python
@dataclass
class NegotiationOutput:
    """Output del NegotiationAgent."""
    # Alternativas generadas
    suggestions: List[Suggestion]

    # Metadatos
    negotiation_strategy: str
    total_suggestions: int
    best_suggestion_rank: Optional[int]  # 1-3
    reasoning: str

@dataclass
class Suggestion:
    """Sugerencia alternativa."""
    rank: int                    # 1 = mejor
    fecha: date
    hora_inicio: time
    hora_fin: time
    contacto_id: str
    motivo: str                 # Por qué se sugiere
    prioridad: float            # 0.0 - 1.0
    distance_from_original: Optional[str]  # "same_day", "next_day", etc.

    # Métricas
    is_available: bool
    confidence: float
```

## Comportamiento

### Estrategias de Negociación

```python
NEGOTIATION_STRATEGIES = {
    "closest_alternatives": "Slots más cercanos temporalmente",
    "same_day_priority": "Priorizar mismo día",
    "next_day_availability": "Siguiente día con disponibilidad",
    "user_preference": "Basado en preferencias de usuario",
    "business_optimization": "Optimizar para fill de agenda"
}
```

### Algoritmo de Generación de Alternativas

#### Paso 1: Analizar Conflicto

```python
def analyze_conflict(conflict: Conflict) -> ConflictAnalysis:
    """
    Analiza el conflicto para entender restricciones.

    Returns:
        ConflictAnalysis con:
        - tipo_conflicto: full, partial, back_to_back
        - cita_conflictiva: appointment que causa conflicto
        - duracion_conflicto: minutos de overlap
        - posibilidad_mover: si la cita conflictiva puede moverse
    """
    return ConflictAnalysis(
        tipo_conflicto=conflict.type,
        cita_conflictiva=conflict.conflicting_appointment_id,
        duracion_minutos=conflict.overlap_duration_minutes,
        posibilidad_mover=assess_if_movable(conflict)
    )
```

#### Paso 2: Buscar Slots Disponibles

```python
def find_alternative_slots(
    original_date: date,
    original_time: time,
    contacto_id: str,
    days_to_search: int = 3,
    slots_per_day: int = 3
) -> List[TimeSlot]:
    """
    Busca slots disponibles alternativos.

    Estrategia:
    1. Mismo día, horas cercanas
    2. Días siguientes, misma hora
    3. Días siguientes, horas disponibles
    """
    slots = []

    for day_offset in range(days_to_search + 1):
        fecha = original_date + timedelta(days=day_offset)

        # Generar slots del día
        daily_slots = generate_time_slots(
            fecha=fecha,
            contacto_id=contacto_id,
            duration=60
        )

        # Filtrar y ordenar por cercanía al original
        if day_offset == 0:
            # Mismo día: slots más cercanos
            slot_scores = [
                (slot, abs(time_diff(slot.hora, original_time)))
                for slot in daily_slots
                if slot.is_available
            ]
            slot_scores.sort(key=lambda x: x[1])
            slots.extend([s[0] for s in slot_scores[:slots_per_day]])

        else:
            # Días siguientes: primeras horas disponibles
            available = [s for s in daily_slots if s.is_available]
            slots.extend(available[:slots_per_day])

    return slots
```

#### Paso 3: Priorizar Alternativas

```python
def prioritize_suggestions(
    slots: List[TimeSlot],
    original: AppointmentRequest,
    analysis: ConflictAnalysis
) -> List[Suggestion]:
    """
    Prioriza alternativas según múltiples factores.

    Factores de prioridad:
    1. Cercanía temporal (misma hora, mismo día)
    2. Disponibilidad confirmada
    3. Preferencias de usuario (si especificadas)
    """
    suggestions = []

    for rank, slot in enumerate(slots, 1):
        # Calcular prioridad
        priority_score = calculate_priority(
            slot=slot,
            original=original,
            analysis=analysis
        )

        # Determinar motivo
        motivo = generate_reason(slot, original, analysis)

        suggestions.append(Suggestion(
            rank=rank,
            fecha=slot.fecha,
            hora_inicio=slot.hora_inicio,
            hora_fin=slot.hora_fin,
            contacto_id=original.contact_id,
            motivo=motivo,
            prioridad=priority_score,
            distance_from_original=calculate_distance(slot, original),
            is_available=True,
            confidence=0.9
        ))

    # Ordenar por prioridad
    suggestions.sort(key=lambda s: s.prioridad, reverse=True)

    # Re-rank después de ordenar
    for i, s in enumerate(suggestions, 1):
        s.rank = i

    return suggestions
```

### Generación de Motivos

```python
def generate_reason(
    slot: TimeSlot,
    original: AppointmentRequest,
    analysis: ConflictAnalysis
) -> str:
    """Genera explicación de por qué se sugiere este slot."""

    # Mismo día, hora cercana
    if slot.fecha == original.preferred_date:
        delta = time_diff(slot.hora_inicio, original.preferred_time)
        return f"Mismo día, {delta} minutos después de tu hora preferida"

    # Siguiente día, misma hora
    if slot.fecha == original.preferred_date + timedelta(days=1):
        return "Siguiente día, misma hora que solicitaste"

    # Primera disponibilidad después
    days_diff = (slot.fecha - original.preferred_date).days
    return f"Primera disponibilidad en {days_diff} días"

    # Específico para back-to-back
    if analysis.tipo_conflicto == "back_to_back":
        return "Después de la cita existente (con tiempo de buffer)"

    # Default
    return "Horario disponible"
```

## Casos de Uso

| Input | Output |
|-------|--------|
| Conflicto completo (10:00-11:00 ocupado) | Alternativas: 11:00-12:00, 09:00-10:00, siguiente día |
| Múltiples conflictos | Alternativas evitando todos los conflictos |
| Usuario flexible | Más alternativas (hasta 5) |
| Usuario rígido | Solo alternativas muy cercanas |

## Ejemplos de Response

### Conflicto Simple

```json
{
  "suggestions": [
    {
      "rank": 1,
      "fecha": "2026-01-23",
      "hora_inicio": "11:00",
      "hora_fin": "12:00",
      "contacto_id": "contact_dr_perez",
      "motivo": "Inmediatamente después de la cita existente (10:00-11:00)",
      "prioridad": 0.95,
      "distance_from_original": "same_day",
      "is_available": true,
      "confidence": 0.95
    },
    {
      "rank": 2,
      "fecha": "2026-01-23",
      "hora_inicio": "09:00",
      "hora_fin": "10:00",
      "contacto_id": "contact_dr_perez",
      "motivo": "Antes de la cita existente (10:00-11:00)",
      "prioridad": 0.90,
      "distance_from_original": "same_day",
      "is_available": true,
      "confidence": 0.90
    },
    {
      "rank": 3,
      "fecha": "2026-01-24",
      "hora_inicio": "10:00",
      "hora_fin": "11:00",
      "contacto_id": "contact_dr_perez",
      "motivo": "Siguiente día, misma hora solicitada",
      "prioridad": 0.85,
      "distance_from_original": "next_day",
      "is_available": true,
      "confidence": 0.90
    }
  ],
  "negotiation_strategy": "closest_alternatives",
  "total_suggestions": 3,
  "best_suggestion_rank": 1,
  "reasoning": "El Dr. Pérez tiene cita existente de 10:00-11:00. Sugiero slots cercanos en mismo día y siguiente día mismo horario."
}
```

### Con Preferencias de Usuario

```json
{
  "suggestions": [
    {
      "rank": 1,
      "fecha": "2026-01-23",
      "hora_inicio": "14:00",
      "hora_fin": "15:00",
      "motivo": "Disponible en tarde (preferencia: tarde)",
      "prioridad": 0.92
    },
    {
      "rank": 2,
      "fecha": "2026-01-23",
      "hora_inicio": "16:00",
      "hora_fin": "17:00",
      "motivo": "Otra opción en tarde",
      "prioridad": 0.88
    }
  ],
  "negotiation_strategy": "user_preference",
  "reasoning": "Usuario prefiere tarde. Sugiero slots disponibles en tarde del mismo día."
}
```

## Estrategias Avanzadas

### Optimización de Agenda

```python
def optimize_schedule(
    contact_id: str,
    week_start: date
) -> List[Suggestion]:
    """
    Optimiza agenda del contacto para minimizar huecos.

    Objetivo: Maximizar utilización del contacto.
    """
    # Obtener todos los slots de la semana
    week_slots = get_week_slots(contact_id, week_start)

    # Identificar huecos (gaps largos)
    gaps = identify_gaps(week_slots)

    # Si hay hueco de 2 horas, sugerir dividir
    for gap in gaps:
        if gap.duration >= 120:
            return suggest_split_gap(gap)

    return []
```

### Negociación Multi-Objetivo

```python
def negotiate_multi_objective(
    user_preferences: UserConstraints,
    business_optimization: bool,
    contact_fatigue: bool
) -> List[Suggestion]:
    """
    Negocia considerando múltiples objetivos.

    Objetivos:
    - Satisfacción de usuario (horario cercano)
    - Optimización de negocio (llenar agenda)
    - Fatiga del contacto (evitar carga alta)
    """
    suggestions = []

    # Equilibrar preferencias usuario con optimización negocio
    if business_optimization:
        suggestions.extend(find_fill_gaps())
    else:
        suggestions.extend(find_closest_to_user())

    return suggestions[:5]  # Máximo 5 alternativas
```

## Métricas

| Métrica | Objetivo |
|---------|----------|
| **Tasa de aceptación de sugerencias** | >70% |
| **Sugerencias útiles** | >85% |
| **Sugerencias confirmables** | >95% |
| **Latencia p95** | <500ms |

## Dependencias

- **AvailabilityAgent**: Para obtener disponibilidad
- **ValidationAgent**: Para verificar reglas
- **SharedContext**: Para acceder a citas y preferencias

## Testing

```python
async def test_sugerencias_conflicto_simple():
    conflict = Conflict(
        conflicting_appointment_id="apt_123",
        type="full_overlap",
        overlap_duration_minutes=60
    )

    input = NegotiationInput(
        original_request=AppointmentRequest(
            preferred_date=date(2026, 1, 23),
            preferred_time=time(10, 0),
            contact_id="contact_dr_perez"
        ),
        conflict=conflict,
        conflicts=[conflict]
    )

    output = await agent.process(input)

    assert len(output.suggestions) >= 2
    assert output.suggestions[0].rank == 1
    assert output.suggestions[0].is_available

async def test_con_preferencias_usuario():
    input = NegotiationInput(
        user_constraints=UserConstraints(
            time_range=TimeRange(
                inicio=time(14, 0),
                fin=time(19, 0)
            ),
            flexibility="medium"
        ),
        ...
    )

    output = await agent.process(input)

    # Todas las sugerencias deben ser en tarde
    for s in output.suggestions:
        assert s.hora_inicio >= time(14, 0)
```

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: AI Team
