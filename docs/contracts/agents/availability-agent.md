# Contrato: AvailabilityAgent

## Versión
1.0.0

## Responsabilidad

Detectar conflictos de disponibilidad para una cita candidata y retornar citas que se superponen.

## Interfaz

### Entrada

```python
@dataclass
class AvailabilityInput:
    """Input del AvailabilityAgent."""
    candidate_appointment: AppointmentCandidate
    existing_appointments: List[Appointment]
    contact_id: str
    consider_travel_time: bool = True
    buffer_between_appointments: int = 15  # minutos

@dataclass
class Appointment:
    """Cita existente en el sistema."""
    id: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    contacto_id: str
    estado: str

@dataclass
class AppointmentCandidate:
    """Cita candidata a verificar."""
    fecha: date
    hora_inicio: time
    hora_fin: time
    contacto_id: str
```

### Salida

```python
@dataclass
class AvailabilityOutput:
    """Output del AvailabilityAgent."""
    # Disponibilidad
    is_available: bool

    # Conflictos detectados
    conflicts: List[Conflict]
    conflicting_appointments: List[Appointment]

    # Métricas
    total_appointments_in_day: int
    available_slots_before: int
    available_slots_after: int

    # Metadatos
    reasoning: str

@dataclass
class Conflict:
    """Conflicto detectado."""
    conflict_id: str
    conflicting_appointment_id: str
    type: str  # "full_overlap", "partial_overlap", "back_to_back"
    severity: str  # "error", "warning"
    overlap_duration_minutes: int
    description: str
```

## Comportamiento

### Detección de Conflictos

```python
def detect_conflicts(
    candidate: AppointmentCandidate,
    existing: List[Appointment],
    buffer_minutos: int = 15
) -> List[Conflict]:
    """
    Detecta conflictos entre cita candidata y existentes.

    Tipos de conflicto:
    1. Full overlap: Cita se superpone completamente
    2. Partial overlap: Superposición parcial
    3. Back-to-back: Sin tiempo de buffer entre citas
    """
    conflicts = []

    candidate_start = datetime.combine(candidate.fecha, candidate.hora_inicio)
    candidate_end = datetime.combine(candidate.fecha, candidate.hora_fin)

    for apt in existing:
        if apt.fecha != candidate.fecha:
            continue

        apt_start = datetime.combine(apt.fecha, apt.hora_inicio)
        apt_end = datetime.combine(apt.fecha, apt.hora_fin)

        # Mismo contacto
        if apt.contacto_id != candidate.contacto_id:
            continue

        # Detectar overlap
        overlap_type = detect_overlap_type(
            candidate_start, candidate_end,
            apt_start, apt_end
        )

        if overlap_type is not None:
            # Calcular duración de overlap
            overlap_start = max(candidate_start, apt_start)
            overlap_end = min(candidate_end, apt_end)
            overlap_duration = (overlap_end - overlap_start).seconds / 60

            conflicts.append(Conflict(
                conflict_id=f"conflict_{candidate.fecha}_{apt.id}",
                conflicting_appointment_id=apt.id,
                type=overlap_type,
                severity="error" if overlap_type != "back_to_back" else "warning",
                overlap_duration_minutes=int(overlap_duration),
                description=describe_conflict(apt, overlap_type, overlap_duration)
            ))

    return conflicts
```

### Tipos de Overlap

```
Full Overlap:
Candidato:    10:00 --------- 11:00
Existente:       10:00 --------- 11:00

Partial Overlap:
Candidato:    10:00 --------- 11:00
Existente:        10:30 --------- 11:30

Back-to-Back (sin buffer):
Candidato:    10:00 ---- 10:30
Existente:                    10:30 ---- 11:00
                      ↑
                 Sin 15min de buffer
```

### Lógica de Detección

```python
def detect_overlap_type(
    cand_start: datetime,
    cand_end: datetime,
    exist_start: datetime,
    exist_end: datetime
) -> Optional[str]:
    """
    Detecta tipo de overlap entre dos rangos de tiempo.

    Returns:
        "full_overlap", "partial_overlap", "back_to_back", or None
    """
    BUFFER = timedelta(minutes=15)

    # No overlap
    if cand_end <= exist_start + BUFFER or cand_start >= exist_end + BUFFER:
        return None

    # Full overlap
    if cand_start >= exist_start and cand_end <= exist_end:
        return "full_overlap"

    # Partial overlap
    if (cand_start < exist_end and cand_end > exist_start or
        exist_start < cand_end and exist_end > cand_start):
        return "partial_overlap"

    # Back-to-back
    if (abs((cand_end - exist_start).total_seconds()) < BUFFER.total_seconds() or
        abs((exist_end - cand_start).total_seconds()) < BUFFER.total_seconds()):
        return "back_to_back"

    return None
```

### Conteo de Citas por Día

```python
def count_appointments_in_day(
    contacto_id: str,
    fecha: date,
    existing: List[Appointment]
) -> int:
    """Cuenta citas de un contacto en una fecha."""
    return sum(
        1 for apt in existing
        if apt.fecha == fecha and apt.contacto_id == contacto_id
    )
```

### Cálculo de Slots Disponibles

```python
def count_available_slots(
    contacto_id: str,
    fecha: date,
    existing: List[Appointment],
    business_hours: dict
) -> Tuple[int, int]:
    """
    Cuenta slots disponibles antes y después de la hora deseada.

    Returns:
        (slots_before, slots_after)
    """
    hora_deseada = time(10, 0)  # Del candidato

    # Generar todos los slots del día
    slots = generate_time_slots(
        fecha=fecha,
        inicio=business_hours["inicio"],
        fin=business_hours["fin"],
        duration=60,
        buffer=15
    )

    # Filtrar slots ocupados
    occupied_slots = set()
    for apt in existing:
        if apt.contacto_id == contacto_id and apt.fecha == fecha:
            occupied_slots.add(apt.hora_inicio)

    # Contar disponibles antes y después
    slots_before = 0
    slots_after = 0

    for slot in slots:
        if slot in occupied_slots:
            continue
        if slot < hora_deseada:
            slots_before += 1
        elif slot > hora_deseada:
            slots_after += 1

    return slots_before, slots_after
```

## Casos de Uso

| Input | Output |
|-------|--------|
| Sin conflictos | `is_available=true`, `conflicts=[]` |
| Conflicto completo | `is_available=false`, `conflicts=[...]` |
| Back-to-back (sin buffer) | `is_available=false`, `conflicts=[warning]` |
| 5 citas ese día | `total=5`, `slots_before=2`, `slots_after=3` |

## Ejemplos de Response

### Sin Conflictos

```json
{
  "is_available": true,
  "conflicts": [],
  "conflicting_appointments": [],
  "total_appointments_in_day": 3,
  "available_slots_before": 2,
  "available_slots_after": 5,
  "reasoning": "No se detectaron conflictos para el Dr. Pérez el 23/01/2026 a las 10:00.",
  "confidence": 1.0
}
```

### Con Conflicto

```json
{
  "is_available": false,
  "conflicts": [
    {
      "conflict_id": "conflict_20260123_apt_abc",
      "conflicting_appointment_id": "apt_20260123_xyz789",
      "type": "full_overlap",
      "severity": "error",
      "overlap_duration_minutes": 60,
      "description": "El Dr. Pérez ya tiene cita de 10:00 a 11:00"
    }
  ],
  "conflicting_appointments": [
    {
      "id": "apt_20260123_xyz789",
      "fecha": "2026-01-23",
      "hora_inicio": "10:00",
      "hora_fin": "11:00",
      "contacto_id": "contact_dr_perez",
      "estado": "confirmed"
    }
  ],
  "total_appointments_in_day": 4,
  "available_slots_before": 2,
  "available_slots_after": 3,
  "reasoning": "Conflicto detectado: apt_20260123_xyz789 se superpone completamente.",
  "confidence": 1.0
}
```

### Back-to-Back (Advertencia)

```json
{
  "is_available": false,
  "conflicts": [
    {
      "conflict_id": "conflict_back_to_back",
      "conflicting_appointment_id": "apt_20260123_abc123",
      "type": "back_to_back",
      "severity": "warning",
      "overlap_duration_minutes": 0,
      "description": "Cita anterior termina a las 10:00, necesitas 15min de buffer"
    }
  ],
  "total_appointments_in_day": 5,
  "available_slots_before": 0,
  "available_slots_after": 4,
  "reasoning": "Sin tiempo suficiente entre citas (se requieren 15min de buffer).",
  "confidence": 1.0
}
```

## Reglas de Negocio

### Buffer Entre Citas

```
Tiempo mínimo entre citas: 15 minutos

Ejemplo:
Cita 1: 10:00 - 10:30
Cita 2 no puede ser antes de 10:45 (10:30 + 15min buffer)
```

### Máximo de Citas por Día

```python
MAX_APPOINTMENTS_PER_DAY = 12

if count_appointments_in_day(contacto_id, fecha, existing) >= MAX_APPOINTMENTS_PER_DAY:
    raise ValidationError("El contacto ha alcanzado el máximo de citas del día")
```

### Prioridad de Conflictos

1. **Full overlap**: Error crítico - cita ya ocupada
2. **Partial overlap**: Error - superposición parcial
3. **Back-to-back**: Warning - posible pero no recomendado

## Métricas

| Métrica | Objetivo |
|---------|----------|
| **Tasa de falsos positivos** | <1% |
| **Tasa de falsos negativos** | <0.5% |
| **Precisión de detección de overlap** | >99% |
| **Latencia p95** | <200ms |

## Optimización

### Indexamiento Temporal

Para bases de datos grandes, usar índices temporales:

```python
# PostgreSQL example
CREATE INDEX idx_appointments_contacto_fecha
ON appointments(contacto_id, fecha, hora_inicio);
```

### Caching de Disponibilidad

```python
@cache(ttl=300)  # 5 minutos
def get_availability(contacto_id: str, fecha: date) -> AvailabilityOutput:
    return calculate_availability(contacto_id, fecha)
```

## Dependencias

- **TemporalAgent**: Para fecha/hora validadas
- **SharedContext**: Para acceder a citas existentes
- **Configuration**: Para reglas de buffer y máximos

## Testing

```python
async def test_sin_conflictos():
    input = AvailabilityInput(
        candidate_appointment=AppointmentCandidate(
            fecha=date(2026, 1, 23),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            contacto_id="contact_dr_perez"
        ),
        existing_appointments=[],
        contact_id="contact_dr_perez"
    )

    output = await agent.process(input)

    assert output.is_available
    assert len(output.conflicts) == 0

async def test_conflicto_completo():
    existing = [
        Appointment(
            id="apt_123",
            fecha=date(2026, 1, 23),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            contacto_id="contact_dr_perez",
            estado="confirmed"
        )
    ]

    input = AvailabilityInput(
        candidate_appointment=AppointmentCandidate(
            fecha=date(2026, 1, 23),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            contacto_id="contact_dr_perez"
        ),
        existing_appointments=existing,
        contact_id="contact_dr_perez"
    )

    output = await agent.process(input)

    assert not output.is_available
    assert len(output.conflicts) == 1
    assert output.conflicts[0].type == "full_overlap"
```

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: AI Team
