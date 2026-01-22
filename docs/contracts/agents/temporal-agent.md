# Contrato: TemporalAgent

## Versión
1.0.0

## Responsabilidad

Resolver referencias temporales relativas ("mañana", "la próxima semana") y validar restricciones temporales de negocio.

## Interfaz

### Entrada

```python
@dataclass
class TemporalInput:
    """Input del TemporalAgent."""
    entities: EntityExtraction  # Del ParsingAgent
    reference_date: datetime     # "Ahora" del usuario
    user_timezone: str           # Zona horaria del usuario
    business_rules: BusinessRules

@dataclass
class BusinessRules:
    """Reglas temporales de negocio."""
    horario_laboral: dict       # {"inicio": "09:00", "fin": "18:00"}
    dias_laborales: list        # [1, 2, 3, 4, 5] (lun-vie)
    anticipacion_minima_minutos: int = 60
    anticipacion_maxima_dias: int = 90
    festivos: list[date]
```

### Salida

```python
@dataclass
class TemporalOutput:
    """Output del TemporalAgent."""
    # Fecha y hora resueltas
    resolved_start: datetime      # En UTC
    resolved_end: datetime        # En UTC
    original_timezone: str        # TZ del usuario

    # Validación
    is_valid: bool
    validation_errors: List[ValidationError]

    # Metadatos
    reasoning: str               # Explicación de resolución
    confidence: float

@dataclass
class ValidationError:
    """Error de validación temporal."""
    code: str                    # "outside_hours", "holiday", "too_soon"
    field: str                   # "fecha", "hora"
    message: str                 # Explicación usuario
    suggestion: Optional[str]    # Sugerencia de corrección
```

## Comportamiento

### Resolución de Expresiones Temporales

| Expresión | Ejemplo | Resolución |
|-----------|---------|------------|
| "mañana" | referencia: 2026-01-22 | 2026-01-23 |
| "la próxima semana" | referencia: 2026-01-22 (jue) | 2026-01-26 (lun siguiente) |
| "el martes que viene" | referencia: 2026-01-22 | 2026-01-27 |
| "en 2 semanas" | referencia: 2026-01-22 | 2026-02-05 |
| "el 15" | referencia: 2026-01-22 | 2026-01-15 (pasado) → 2026-02-15 |
| "10am" | - | 10:00 TZ usuario |

### Validaciones

1. **Anticipación mínima**: No menos de 60 minutos
2. **Anticipación máxima**: No más de 90 días
3. **Días laborales**: Lunes a viernes
4. **Horario laboral**: 9:00 - 18:00
5. **Festivos**: No agendar en festivos configurados

### Manejo de Zonas Horarias

```
Usuario en CDMX (UTC-6): "mañana 10am"
→ 2026-01-23 10:00 America/Mexico_City
→ 2026-01-23 16:00 UTC (storage)

Usuario en Madrid (UTC+1): "mañana 10am"
→ 2026-01-23 10:00 Europe/Madrid
→ 2026-01-23 09:00 UTC (storage)
```

## Lógica de Resolución

### Paso 1: Normalizar Fecha

```python
def resolve_relative_date(expression: str, reference: date) -> date:
    if expression == "mañana":
        return reference + timedelta(days=1)

    elif expression == "la próxima semana":
        # Encontrar próximo lunes
        days_ahead = 7 - reference.weekday()
        return reference + timedelta(days=days_ahead if days_ahead else 7)

    elif "semana" in expression:
        # Extraer número: "en 2 semanas"
        weeks = extract_number(expression)
        return reference + timedelta(weeks=weeks)

    # ... más casos
```

### Paso 2: Normalizar Hora

```python
def resolve_time(expression: str, reference: time) -> time:
    if "am" in expression:
        hour = extract_hour(expression)
        return time(hour=hour, minute=0)

    elif "pm" in expression:
        hour = extract_hour(expression) + 12
        return time(hour=hour, minute=0)

    # Hora explícita: "10:30"
    if ":" in expression:
        return time.fromisoformat(expression)
```

### Paso 3: Validar

```python
def validate_temporal(dt: datetime, rules: BusinessRules) -> List[ValidationError]:
    errors = []

    # 1. Anticipación mínima
    if dt < now() + timedelta(minutes=rules.anticipacion_minima):
        errors.append(ValidationError(
            code="too_soon",
            message=f"Mínimo {rules.anticipacion_minuta} minutos de anticipación"
        ))

    # 2. Anticipación máxima
    if dt > now() + timedelta(days=rules.anticipacion_maxima):
        errors.append(ValidationError(
            code="too_late",
            message=f"Máximo {rules.anticipacion_maxima} días de anticipación"
        ))

    # 3. Día laboral
    if dt.weekday() not in rules.dias_laborales:
        errors.append(ValidationError(
            code="non_business_day",
            message="Solo se atiende de lunes a viernes"
        ))

    # 4. Horario laboral
    hora = dt.time()
    if hora < rules.horario_laboral["inicio"] or hora > rules.horario_laboral["fin"]:
        errors.append(ValidationError(
            code="outside_hours",
            message=f"Horario de {rules.horario_laboral['inicio']} a {rules.horario_laboral['fin']}"
        ))

    # 5. Festivo
    if dt.date() in rules.festivos:
        errors.append(ValidationError(
            code="holiday",
            message="Día festivo, no se atiende"
        ))

    return errors
```

## Ejemplos

### Caso Exitoso

**Input**:
```python
TemporalInput(
    entities=EntityExtraction(
        fecha=DateExpression(original="mañana", type="relative"),
        hora="10am",
        duracion=60
    ),
    reference_date=datetime(2026, 1, 22, 15, 0),  # 22/01 3pm
    user_timezone="America/Mexico_City"
)
```

**Output**:
```json
{
  "resolved_start": "2026-01-23T16:00:00Z",
  "resolved_end": "2026-01-23T17:00:00Z",
  "original_timezone": "America/Mexico_City",
  "is_valid": true,
  "validation_errors": [],
  "reasoning": "'mañana' resuelto a 2026-01-23, 10am en CDMX. Horario válido dentro de laborales (9-18).",
  "confidence": 1.0
}
```

### Con Error de Validación

**Input**:
```python
TemporalInput(
    entities=EntityExtraction(
        hora="3am",
        duracion=60
    ),
    reference_date=datetime(2026, 1, 22),
    user_timezone="America/Mexico_City"
)
```

**Output**:
```json
{
  "resolved_start": "2026-01-23T09:00:00Z",
  "resolved_end": "2026-01-23T10:00:00Z",
  "original_timezone": "America/Mexico_City",
  "is_valid": false,
  "validation_errors": [
    {
      "code": "outside_hours",
      "field": "hora",
      "message": "Horario de atención es 9:00-18:00",
      "suggestion": "¿Te sirve a las 9am o a las 10am?"
    }
  ],
  "reasoning": "3am (9am UTC) está fuera de horario laboral (9-18).",
  "confidence": 1.0
}
```

## Edge Cases

| Caso | Manejo |
|------|--------|
| Fecha en pasado | Sugerir fecha próxima |
| "el 15" y hoy es 20 | Asumir mes siguiente |
| Sin fecha | Retornar error, pedir fecha |
| Sin hora | Usar siguiente slot disponible |
| Zona horaria no especificada | Usar default del negocio |

## Métricas

| Métrica | Objetivo |
|---------|----------|
| **Precisión de resolución** | >98% |
| **Tasa de errores de validación** | <10% |
| **Latencia p95** | <500ms (más rápido que parsing) |
| **Sugerencias acertadas** | >90% |

## Testing

```python
async def test_resolucion_mañana():
    input = TemporalInput(
        entities=EntityExtraction(fecha=DateExpression("mañana", "relative")),
        reference_date=datetime(2026, 1, 22),
        user_timezone="America/Mexico_City"
    )

    output = await agent.process(input)

    assert output.resolved_start.day == 23
    assert output.resolved_start.month == 1
    assert output.resolved_start.year == 2026
    assert output.is_valid

async def test_festivo():
    # Asumir que 2026-01-01 es festivo
    input = TemporalInput(
        entities=EntityExtraction(
            fecha=DateExpression("2026-01-01", "absolute"),
            hora="10am"
        ),
        reference_date=datetime(2025, 12, 31),
        user_timezone="America/Mexico_City"
    )

    output = await agent.process(input)

    assert not output.is_valid
    assert any(e.code == "holiday" for e in output.validation_errors)
```

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: AI Team
