# Contrato: ValidationAgent

## Versión
1.0.0

## Responsabilidad

Validar que una cita candidata cumpla con todas las reglas de negocio del sistema.

## Interfaz

### Entrada

```python
@dataclass
class ValidationInput:
    """Input del ValidationAgent."""
    appointment_candidate: AppointmentCandidate
    business_rules: BusinessRules
    user_context: Dict

@dataclass
class AppointmentCandidate:
    """Cita candidata a validar."""
    prompt_original: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    duracion_minutos: int
    contacto_id: Optional[str]
    tipo_cita_id: Optional[str]
    ubicacion: Optional[Ubicacion]

@dataclass
class BusinessRules:
    """Reglas de negocio configurables."""
    # Contactos
    contactos_activos: List[str]     # IDs de contactos activos
    contactos_servicios: Dict[str, List[str]]  # contacto_id -> servicios

    # Servicios
    servicios_activos: List[str]

    # Temporales
    anticipacion_minima_minutos: int = 60
    anticipacion_maxima_dias: int = 90
    dias_laborales: List[int] = field(default_factory=lambda: [1,2,3,4,5])  # Lun-Vie

    # Horarios
    horario_laboral: dict = field(default_factory=lambda: {
        "inicio": "09:00",
        "fin": "18:00",
        "pausa_inicio": "12:00",
        "pausa_fin": "14:00"
    })

    # Festivos
    festivos: List[date] = field(default_factory=list)

    # Restricciones
    tiempo_entre_citas: int = 15
    max_citas_por_dia: int = 12
```

### Salida

```python
@dataclass
class ValidationOutput:
    """Output del ValidationAgent."""
    # Resultado general
    is_valid: bool
    validation_errors: List[ValidationError]

    # Validaciones individuales
    checks: ValidationChecks

    # Metadatos
    confidence: float

@dataclass
class ValidationChecks:
    """Resultado de validaciones individuales."""
    contacto_valid: bool
    servicio_valid: bool
    anticipacion_valid: bool
    dia_laboral_valid: bool
    horario_valid: bool
    no_es_festivo: bool
    within_horario_laboral: bool

@dataclass
class ValidationError:
    """Error de validación."""
    code: str
    field: str
    message: str
    severity: str  # "error", "warning"
    suggestion: Optional[str]
```

## Comportamiento

### Pipeline de Validación

```
1. Validar Contacto
   ↓ ¿Existe y está activo?
2. Validar Servicio
   ↓ ¿Existe y está activo?
3. Validar Anticipación
   ↓ ¿Dentro de rango [60min, 90días]?
4. Validar Día Laboral
   ↓ ¿Es Lun-Vie?
5. Validar Horario
   ↓ ¿Dentro de [9:00-18:00]?
6. Validar Pausa
   ↓ ¿No es 12:00-14:00?
7. Validar Festivo
   ↓ ¿No es festivo?
8. TODAS PASARON → isValid = true
```

### Reglas de Validación

#### 1. Contacto

```python
def validate_contact(contacto_id: str, rules: BusinessRules) -> Optional[ValidationError]:
    if not contacto_id:
        return ValidationError(
            code="contact_missing",
            field="contacto",
            message="No especificaste con quién",
            severity="error",
            suggestion="Selecciona un contacto de la lista"
        )

    if contacto_id not in rules.contactos_activos:
        return ValidationError(
            code="contact_inactive",
            field="contacto",
            message=f"El contacto {contacto_id} no está activo",
            severity="error",
            suggestion="Selecciona otro contacto"
        )

    return None
```

#### 2. Servicio

```python
def validate_service(
    tipo_cita_id: str,
    contacto_id: str,
    rules: BusinessRules
) -> Optional[ValidationError]:
    if tipo_cita_id not in rules.servicios_activos:
        return ValidationError(
            code="service_inactive",
            field="tipo_cita",
            message=f"El servicio {tipo_cita_id} no está disponible",
            severity="error"
        )

    # ¿El contacto ofrece este servicio?
    if contacto_id in rules.contactos_servicios:
        if tipo_cita_id not in rules.contactos_servicios[contacto_id]:
            return ValidationError(
                code="service_not_offered",
                field="tipo_cita",
                message=f"{contacto_id} no ofrece {tipo_cita_id}",
                severity="error",
                suggestion=f"Servicios disponibles: {rules.contactos_servicios[contacto_id]}"
            )

    return None
```

#### 3. Anticipación

```python
def validate_anticipation(
    cita_datetime: datetime,
    rules: BusinessRules
) -> Optional[ValidationError]:
    now = datetime.now()
    delta = cita_datetime - now

    # Mínimo
    if delta < timedelta(minutes=rules.anticipacion_minima_minutos):
        return ValidationError(
            code="too_soon",
            field="fecha",
            message=f"Mínimo {rules.anticipacion_minima_minutos} minutos de anticipación",
            severity="error",
            suggestion=f"La cita más cercana es en {rules.anticipacion_minima_minutos} minutos"
        )

    # Máximo
    if delta > timedelta(days=rules.anticipacion_maxima_dias):
        return ValidationError(
            code="too_late",
            field="fecha",
            message=f"Máximo {rules.anticipacion_maxima_dias} días de anticipación",
            severity="error"
        )

    return None
```

#### 4. Día Laboral

```python
def validate_business_day(
    cita_fecha: date,
    rules: BusinessRules
) -> Optional[ValidationError]:
    if cita_fecha.weekday() not in rules.dias_laborales:
        return ValidationError(
            code="non_business_day",
            field="fecha",
            message="Solo se atiende de lunes a viernes",
            severity="error",
            suggestion=f"El {cita_fecha.strftime('%A')} no se atiende. Selecciona un día laboral."
        )

    return None
```

#### 5. Horario Laboral

```python
def validate_business_hours(
    cita_hora: time,
    rules: BusinessRules
) -> Optional[ValidationError]:
    inicio = time.fromisoformat(rules.horario_laboral["inicio"])
    fin = time.fromisoformat(rules.horario_laboral["fin"])

    if cita_hora < inicio or cita_hora > fin:
        return ValidationError(
            code="outside_hours",
            field="hora",
            message=f"Horario de atención: {inicio} a {fin}",
            severity="error",
            suggestion=f"Selecciona una hora entre {inicio} y {fin}"
        )

    return None
```

#### 6. Pausa (Almuerzo)

```python
def validate_break(
    cita_hora: time,
    duracion: int,
    rules: BusinessRules
) -> Optional[ValidationError]:
    if rules.horario_laboral.get("pausa_inicio") and rules.horario_laboral.get("pausa_fin"):
        pausa_inicio = time.fromisoformat(rules.horario_laboral["pausa_inicio"])
        pausa_fin = time.fromisoformat(rules.horario_laboral["pausa_fin"])

        cita_fin = (datetime.combine(date.today(), cita_hora) + timedelta(minutes=duracion)).time()

        if cita_hora < pausa_fin and cita_fin > pausa_inicio:
            return ValidationError(
                code="during_break",
                field="hora",
                message=f"Hora de pausa: {pausa_inicio} a {pausa_fin}",
                severity="error",
                suggestion=f"Evita el horario de {pausa_inicio} a {pausa_fin}"
            )

    return None
```

#### 7. Festivo

```python
def validate_holiday(
    cita_fecha: date,
    rules: BusinessRules
) -> Optional[ValidationError]:
    if cita_fecha in rules.festivos:
        return ValidationError(
            code="holiday",
            field="fecha",
            message=f"Día festivo: {cita_fecha.strftime('%d de %B')}",
            severity="error",
            suggestion="Selecciona otro día"
        )

    return None
```

## Casos de Uso

| Input | Output |
|-------|--------|
| Cita válida | `is_valid=true`, `validation_errors=[]` |
| Sin contacto | `is_valid=false`, `errors=[contact_missing]` |
| Domingo | `is_valid=false`, `errors=[non_business_day]` |
| 3am | `is_valid=false`, `errors=[outside_hours]` |
| 13:00 (con pausa) | `is_valid=false`, `errors=[during_break]` |
| Festivo | `is_valid=false`, `errors=[holiday]` |
| <60 minutos | `is_valid=false`, `errors=[too_soon]` |

## Mensajes de Error Explicativos

```json
{
  "is_valid": false,
  "validation_errors": [
    {
      "code": "outside_hours",
      "field": "hora",
      "message": "La hora 3am está fuera del horario de atención",
      "severity": "error",
      "suggestion": "El horario de atención es de 9:00 a 18:00. ¿Te sirve a las 9am o a las 10am?"
    }
  ],
  "checks": {
    "contacto_valid": true,
    "servicio_valid": true,
    "anticipacion_valid": true,
    "dia_laboral_valid": true,
    "horario_valid": false,
    "no_es_festivo": true,
    "within_horario_laboral": false
  },
  "confidence": 1.0
}
```

## Métricas

| Métrica | Objetivo |
|---------|----------|
| **Tasa de validaciones exitosas** | N/A (depende de calidad de input) |
| **Precisión de validación** | >99% (falsos positivos <1%) |
| **Claridad de mensajes de error** | >90% usuarios entienden |
| **Sugerencias acertadas** | >80% |

## Dependencias

- **SharedContext**: Para acceder a contactos y servicios
- **TemporalAgent**: Para obtener fecha/hora validadas
- **Configuration**: Para reglas de negocio configurables

## Testing

```python
async def test_validacion_exitosa():
    input = ValidationInput(
        appointment_candidate=AppointmentCandidate(
            fecha=date(2026, 1, 23),  # Jueves
            hora_inicio=time(10, 0),
            contacto_id="contact_dr_perez",
            tipo_cita_id="consulta_general"
        ),
        business_rules=BusinessRules()
    )

    output = await agent.process(input)

    assert output.is_valid
    assert len(output.validation_errors) == 0
    assert output.checks.horario_valid == True

async def test_domingo():
    input = ValidationInput(
        appointment_candidate=AppointmentCandidate(
            fecha=date(2026, 1, 25),  # Sábado
            hora_inicio=time(10, 0),
        ),
        business_rules=BusinessRules()
    )

    output = await agent.process(input)

    assert not output.is_valid
    assert not output.checks.dia_laboral_valid
    assert any(e.code == "non_business_day" for e in output.validation_errors)
```

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: AI Team
