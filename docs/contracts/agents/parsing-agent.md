# Contrato: ParsingAgent

## Versión
1.0.0

## Responsabilidad

Extraer entidades y detectar intenciones desde prompts en lenguaje natural.

## Interfaz

### Entrada

```python
@dataclass
class ParsingInput:
    """Input del ParsingAgent."""
    prompt: str                    # Prompt del usuario (ej: "cita mañana 10am con Dr. Pérez")
    language: str = "es"           # Idioma del prompt
    context: Optional[Dict] = None # Contexto adicional (usuario, historial)
    reference_date: datetime = field(default_factory=datetime.now)
```

### Salida

```python
@dataclass
class ParsingOutput:
    """Output del ParsingAgent."""
    # Entidades extraídas
    entities: EntityExtraction

    # Intención detectada
    intent: IntentType  # "create_appointment", "reschedule", "cancel", "query"

    # Confianza de extracción
    confidence: float  # 0.0 - 1.0

    # Ambigüedades detectadas
    ambiguities: List[Ambiguity]

    # Metadatos
    processing_time_ms: int
    llm_tokens_used: int

@dataclass
class EntityExtraction:
    """Entidades extraídas del prompt."""
    fecha: Optional[DateExpression]      # "mañana", "2026-01-23"
    hora: Optional[TimeExpression]       # "10am", "10:00"
    duracion: Optional[int]               # Duración en minutos (default: 60)
    contacto: Optional[str]               # "Dr. Pérez"
    tipo_cita: Optional[str]             # "consulta_general"
    ubicacion: Optional[str]             # "consultorio", "domicilio"
    notas: Optional[str]                 # Notas adicionales

@dataclass
class DateExpression:
    """Expresión de fecha extraída."""
    original: str        # "mañana", "el próximo martes"
    type: str           # "relative", "absolute", "implicit"
    value: Optional[datetime] = None  # Resuelto si es absoluta

@dataclass
class Ambiguity:
    """Ambigüedad detectada."""
    field: str           # "fecha", "contacto"
    issue: str           # "multiple_matches", "missing", "unclear"
    message: str         # Explicación para usuario
    suggestions: List[str] = field(default_factory=list)
```

## Comportamiento

### Casos de Uso

| Input | Output |
|-------|--------|
| "cita mañana 10am con Dr. Pérez" | entities completas, confidence 0.95 |
| "cita con el doctor" | contacto ambiguo, pedir aclaración |
| "cita a las 3am" | entities OK, validation_agent detectará horario inválido |
| "reprogramar mi cita" | intent = "reschedule" |

### Reglas de Extracción

1. **Fecha优先**: Si no se especifica fecha, marcar como ambigüedad
2. **Hora opcional**: Si no se especifica hora, default = horario siguiente disponible
3. **Contacto requerido**: Si no se menciona contacto, pedir aclaración
4. **Tipo default**: Si no se especifica, default = "consulta_general"
5. **Duración default**: 60 minutos, o según tipo de servicio

### Manejo de Ambigüedades

```python
# Ambigüedad leve (confidence >70%)
entities = EntityExtraction(
    fecha="mañana",  # Relative pero claro
    contacto="Dr. Pérez",
    confidence=0.85
)
# → Continuar pipeline, pedir confirmación al final

# Ambigüedad severa (confidence <70%)
entities = EntityExtraction(
    fecha=None,  # No se pudo extraer
    contacto="el doctor",  # Demasiado genérico
    confidence=0.45
)
# → Detener pipeline, pedir aclaración inmediatamente
```

## Prompts

### Prompt de Extracción

```python
EXTRACTION_PROMPT = """
Eres un extractor de información de citas especializado.

PROMPT DEL USUARIO:
{prompt}

CONTEXO:
- Fecha actual: {current_date}
- Idioma: {language}
- Contactos disponibles: {contacts}
- Servicios disponibles: {services}

INSTRUCCIONES:
1. Extrae: fecha, hora, contacto, tipo de cita
2. Si falta información requerida, usa null
3. Detecta ambigüedades (contacto genérico, fecha clara)
4. Devuelve SOLO JSON válido

RESPUESTA (formato JSON):
```json
{{
  "entities": {{
    "fecha": "{original}|{type}|{value}",
    "hora": "{original}",
    "contacto": "{nombre}",
    "tipo": "{tipo}",
    "duración": {minutos}
  }},
  "intent": "{intent}",
  "confidence": 0.0-1.0,
  "ambiguities": [
    {{"field": "contacto", "issue": "generic", "message": "¿Cuál doctor?"}}
  ]
}}
```
```

## Métricas

| Métrica | Objetivo |
|---------|----------|
| **Precisión de extracción** | >90% |
| **Confianza promedio** | >0.80 |
| **Ambigüedades detectadas** | <15% |
| **Latencia p95** | <2s |
| **Tokens por request** | <500 |

## Error Handling

| Error | Acción |
|-------|--------|
| **Prompt muy largo** | Rechazar con error 400 |
| **Idioma no soportado** | Rechazar con error 400 |
| **LLM timeout** | Reintentar 1x, luego fallback a regex |
| **JSON inválido** | Reintentar con prompt más estricto |
| **Confianza muy baja** | Retornar con ambiguities, pedir aclaración |

## Dependencias

- **LLM**: Qwen 2.5 (o configurado)
- **SharedContext**: Para acceder a contactos y servicios
- **DecisionTrace**: Para registrar decisiones

## Testing

### Unit Tests

```python
async def test_extraccion_completa():
    input = ParsingInput(
        prompt="cita mañana 10am con Dr. Pérez",
        reference_date=datetime(2026, 1, 22)
    )

    output = await agent.process(input)

    assert output.entities.fecha.original == "mañana"
    assert output.entities.hora == "10am"
    assert output.entities.contacto == "Dr. Pérez"
    assert output.confidence > 0.9
    assert len(output.ambiguities) == 0
```

### Integration Tests

```python
async def test_prompt_ambiguo():
    input = ParsingInput(
        prompt="cita con el doctor",
    )

    output = await agent.process(input)

    assert len(output.ambiguities) > 0
    assert any(a.field == "contacto" for a in output.ambiguities)
    assert output.confidence < 0.7
```

## Ejemplos de Response

### Éxito

```json
{
  "status": "parsed",
  "entities": {
    "fecha": {
      "original": "mañana",
      "type": "relative",
      "value": null
    },
    "hora": "10am",
    "contacto": "Dr. Pérez",
    "tipo": null,
    "duración": 60
  },
  "intent": "create_appointment",
  "confidence": 0.92,
  "ambiguities": [],
  "processing_time_ms": 1250,
  "llm_tokens_used": 423
}
```

### Con Ambigüedades

```json
{
  "status": "ambiguous",
  "entities": {
    "fecha": null,
    "hora": null,
    "contacto": "el doctor",
    "tipo": null,
    "duración": 60
  },
  "intent": "create_appointment",
  "confidence": 0.45,
  "ambiguities": [
    {
      "field": "fecha",
      "issue": "missing",
      "message": "No especificaste fecha. ¿Para cuándo?",
      "suggestions": ["mañana", "esta semana", "el próximo lunes"]
    },
    {
      "field": "contacto",
      "issue": "generic",
      "message": "¿Con qué doctor?",
      "suggestions": ["Dr. Pérez", "Dra. García", "Dr. López"]
    }
  ],
  "processing_time_ms": 890,
  "llm_tokens_used": 312
}
```

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: AI Team
