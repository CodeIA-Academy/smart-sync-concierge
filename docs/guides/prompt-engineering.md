# Ingeniería de Prompts - Smart-Sync Concierge

Guía completa para diseñar, implementar y optimizar prompts para el sistema de IA.

## Fundamentos

### ¿Qué es un Prompt?

Un **prompt** es la entrada de texto que se envía a un modelo de lenguaje para generar una respuesta.

### Principios de Prompt Engineering

1. **Claridad**: Ser específico y explícito
2. **Contexto**: Proporcionar información relevante
3. **Formato**: Especificar el formato de salida esperado
4. **Ejemplos**: Incluir ejemplos cuando sea posible
5. **Iteración**: Mejorar basado en feedback

## Estructura de un Prompt

### Plantilla Base

```
# Rol
Eres un [rol] especializado en [dominio].

# Tarea
[Descripción clara de la tarea]

# Contexto
- Fecha actual: {current_date}
- Zona horaria: {timezone}
- [Otro contexto relevante]

# Instrucciones
1. Paso 1
2. Paso 2
3. ...

# Formato de Salida
[Sespecificar formato JSON, texto, etc.]

# Ejemplo
Input: [ejemplo de input]
Output: [ejemplo de output esperado]
```

### Prompt de Extracción

**Archivo**: `core/ai/prompts/templates/extraction.txt`

```
# Extracción de Información de Citas

Eres un extractor de información especializado en procesar lenguaje natural para citas médicas.

## Tarea
Analiza el prompt del usuario y extrae las siguientes entidades:
- Fecha (o referencia temporal)
- Hora (o referencia horaria)
- Participantes (nombres de contactos)
- Tipo de cita
- Duración (en minutos, default: 60)
- Ubicación (opcional)

## Contexto
- Fecha actual: {current_date}
- Zona horaria: {timezone}
- Idioma: {language}
- Servicios disponibles: {services}
- Contactos disponibles: {contacts}

## Instrucciones
1. Lee el prompt del usuario atentamente
2. Extrae las entidades solicitadas
3. Si una entidad no está presente, usa null
4. Si hay ambigüedad, anótala en "ambiguedades"
5. Devuelve SOLO JSON válido, sin texto adicional

## Formato de Salida
```json
{{
  "entities": {{
    "fecha": "{original}|{type}|{value_resuelto}",
    "hora": "{hora formato HH:MM}",
    "participantes": ["{nombre}"],
    "tipo": "{tipo_cita}",
    "duración": {duración_en_minutos},
    "ubicacion": "{ubicación}",
    "notas": "{notas_adicionales}"
  }},
  "intención": "{create_appointment|reschedule|cancel|query}",
  "confianza": 0.0-1.0,
  "ambiguedades": [
    {{
      "campo": "{campo}",
      "tipo": "{missing|unclear|multiple}",
      "mensaje": "{descripción}"
    }}
  ]
}}
```

## Prompt del Usuario
{user_prompt}
```

### Prompt de Validación

**Archivo**: `core/ai/prompts/templates/validation.txt`

```
# Validación de Citas

Eres un validador experto en citas médicas que detecta ambigüedades e información faltante.

## Tarea
Revisa los datos extraídos de una cita y valida si es completa y correcta.

## Contexto
- Datos de la cita: {appointment_data}
- Reglas de negocio: {business_rules}
- Fecha y hora actual: {now}

## Reglas de Validación

1. **Contacto**: Debe existir en contactos disponibles
2. **Fecha**: No puede estar en el pasado
3. **Hora**: Debe estar dentro de horario laboral ({horario_laboral})
4. **Anticipación**: Mínimo {anticipacion_minima} minutos
5. **Servicio**: Debe ser un servicio activo

## Validación
Para cada regla, indica:
- ¿Se cumple? (true/false)
- ¿Hay errores? (lista de errores)
- ¿Hay advertencias? (lista de warnings)

## Formato de Salida
```json
{{
  "válido": true/false,
  "errores": [
    {{
      "código": "{contact_missing|invalid_date|outside_hours...}",
      "campo": "{campo}",
      "mensaje": "{descripción}",
      "sugerencia": "{corrección sugerida}"
    }}
  ],
  "advertencias": [],
  "confianza": 0.0-1.0,
  "acción_requerida": "{si es válida, qué acción tomar}"
}}
```

## Datos de la Cita
{appointment_data}
```

### Prompt de Resolución de Conflictos

**Archivo**: `core/ai/prompts/templates/conflict.txt`

```
# Generación de Alternativas para Conflictos

Eres un asistente experto que sugiere alternativas cuando hay conflictos de agendamiento.

## Tarea
Genera 3-5 alternativas inteligentes cuando una cita no puede ser agendada debido a conflictos.

## Contexto
- Cita solicitada: {requested_appointment}
- Conflictos detectados: {conflicts}
- Disponibilidad del contacto: {availability}
- Restricciones: {constraints}

## Estrategia de Sugerencias

Prioriza alternativas en este orden:
1. **Mismo día, hora más cercana**: Slots adyacentes en el mismo día
2. **Siguiente día, misma hora**: Día siguiente con misma hora solicitada
3. **Primera disponibilidad**: Primer slot disponible sin importar cercanía

## Formato de Salida
```json
{{
  "sugerencias": [
    {{
      "rank": 1,
      "fecha": "YYYY-MM-DD",
      "hora_inicio": "HH:MM",
      "hora_fin": "HH:MM",
      "motivo": "{explicación de por qué esta sugerencia}",
      "prioridad": 0.0-1.0
    }}
  ],
  "mejor_sugerencia": 1,
  "razonamiento": "{explicación del proceso de selección}"
}}
```

## Cita Solicitada
{requested_appointment}

## Conflictos
{conflicts}
```

## Mejores Prácticas

### 1. Ser Específico

```
❌ Mal: "Extrae información"

✅ Bien: "Extrae fecha, hora y participantes del prompt. Formato JSON obligatorio."
```

### 2. Proporcionar Contexto

```
❌ Mal: "¿Qué día es mañana?"

✅ Bien: "¿Qué día es mañana? Referencia: hoy es {current_date}"
```

### 3. Usar Ejemplos Few-Shot

```
## Ejemplos

Input: "cita mañana 10am con Dr. Pérez"
Output: {{"fecha": "2026-01-23", "hora": "10:00", ...}}

Input: "cita el próximo martes a las 3pm"
Output: {{"fecha": "2026-01-27", "hora": "15:00", ...}}
```

### 4. Manejar Edge Cases

```
## Casos Especiales

Si el usuario no especifica hora:
- Busca el primer slot disponible del día
- Prioriza: mañana (9am), mediodía (12pm), tarde (3pm)

Si el contacto es ambiguo ("el doctor"):
- Sugiere los contactos disponibles
- Pide aclaración

Si la fecha es festivo:
- Informa que es festivo
- Sugiere día siguiente hábil
```

### 5. Validación en Prompt

```
## Validación
Antes de devolver resultado, verifica:
- La fecha no esté en el pasado
- La hora esté en formato válido (00-23)
- La duración sea razonable (15-480 minutos)
- Los participantes estén en lista (no string)
```

## Optimización de Prompts

### A/B Testing

```python
# Versión A
prompt_v1 = "Extrae información de: {prompt}"

# Versión B (mejor contexto)
prompt_v2 = """
Extrae información de: {prompt}

CONTEXTO:
- Fecha actual: {current_date}
- Zona horaria: {timezone}
- Servicios: {services}

Instrucciones: [detalladas...]
"""

# Testear cuál funciona mejor
results = await ab_test_prompts(prompt_v1, prompt_v2)
```

### Métricas de Calidad

| Métrica | Objetivo | Cómo Medir |
|---------|----------|-------------|
| **Precisión** | >90% | Comparar extracción con ground truth |
| **Confianza promedio** | >0.80 | Promedio de `confidence` |
| **Tasa de ambigüedades** | <15% | Prompt con ambigüedades / total |
| **Tokens usados** | <500 | Promedio de tokens por request |

### Iteración Basada en Feedback

```python
# Recolectar prompts fallidos
failed_prompts = get_failed_prompts()

# Analizar patrones de fallo
for prompt, error in failed_prompts:
    if error == "contacto_no_encontrado":
        # Añadir contactos a ejemplo
        add_contact_to_examples(prompt.contacto)

# Actualizar prompt
update_prompt_with_new_examples()
```

## Prompts para Diferentes Modelos

### Qwen (Principal)

Qwen 2.5 funciona bien con JSON mode nativo:

```python
QwenLLM(
    response_format={"type": "json_object"}  # Soporta nativo
)
```

### Claude (Fallback)

Claude no tiene JSON mode nativo, usar prompting:

```
## Formato de Salida CRÍTICO
Importante: Devuelve SOLO el JSON, sin texto adicional antes o después.

Tu respuesta DEBE comenzar con ```json y terminar con ``` y nada más.
```

### GPT-4o (Avanzado)

GPT-4o tiene excelente razonamiento, usar para casos complejos:

```python
prompt = f"""
Analiza este prompt complejo:

{prompt}

Considera:
- Contexto temporal
- Relaciones implícitas
- Intenciones del usuario

Responde con razonamiento detallado.
"""
```

## Testing de Prompts

### Framework de Testing

```python
import pytest

@pytest.mark.asyncio
async def test_prompt_extraccion():
    prompt = build_prompt("extraction", {
        "user_prompt": "cita mañana 10am con Dr. Pérez",
        "current_date": "2026-01-22",
        "timezone": "America/Mexico_City"
    })

    response = await llm.complete(LLMRequest(prompt=prompt))
    result = json.loads(response.content)

    assert result["entities"]["hora"] == "10:00"
    assert result["confidence"] > 0.8
```

### Evaluación

```python
def evaluate_prompt_precision(test_set: List[dict]) -> float:
    """
    Evalúa precisión de prompt vs ground truth.

    test_set = [
        {"prompt": "cita mañana 10am", "expected": {"fecha": "...", "hora": "10:00"}},
        ...
    ]
    """
    correctas = 0

    for test in test_set:
        result = llm.complete(test["prompt"])
        extracted = extract_entities(result)

        if extracted == test["expected"]:
            correctas += 1

    return correctas / len(test_set)
```

## Troubleshooting

### Problema: JSON Inválido

**Síntoma**: El LLM devuelve JSON mal formado.

**Soluciones**:

1. **Aumentar temperatura** (más creatividad = peor JSON):
```python
LLMRequest(
    prompt=prompt,
    temperature=0.1  # Más bajo = más estructurado
)
```

2. **Prompt más estricto**:
```
CRÍTICO: Devuelve SOLO JSON válido.
No incluyas texto adicional.
```

3. **Usar function calling** (si el modelo lo soporta):
```python
LLMRequest(
    tools=[extract_entities_tool],
    tool_choice="auto"
)
```

### Problema: Baja Confianza

**Síntoma**: `confidence` < 0.7 consistentemente.

**Soluciones**:

1. **Mejorar contexto**: Añadir más información relevante
2. **Simplificar prompt**: Reducir número de entidades
3. **Añadir ejemplos**: Few-shot learning
4. **Cambiar modelo**: Usar modelo más capaz

### Problema: Tokens Excesivos

**Síntoma**: >1000 tokens por request.

**Soluciones**:

1. **Acortar prompt**: Eliminar texto redundante
2. **Reducir contexto**: Solo información esencial
3. **Comprimir contexto**: Usar referencias en lugar de datos completos

```python
# Antes (verbose)
"""
Contactos disponibles:
1. Dr. Juan Pérez - Medicina General - Disponible Lun-Vie
2. Dra. María García - Pediatría - Disponible Lun-Sáb
...
"""

# Después (conciso)
"""
Contactos: Dr. Pérez (MG), Dra. García (Pedia)
"""
```

## Monitoreo de Prompts

### Métricas a Registrar

```python
# En cada request
log_prompt_metrics(
    prompt_template="extraction",
    prompt_length=len(prompt),
    tokens_used=response.usage.total_tokens,
    confidence=result["confidence"],
    processing_time_ms=elapsed_time,
    success=result["entities"] is not None
)
```

### Alertas

Configurar alertas cuando:

- **Precisión < 80%**: Revisar prompt
- **Latencia > 3s**: Optimizar prompt o cambiar modelo
- **Costo > presupuesto**: Considerar modelo más barato
- **Tasa de fallos > 10%**: Actualizar prompt

---

**Última actualización**: Enero 22, 2026
**Versión**: 0.1.0
**Mantenedor**: AI Team
