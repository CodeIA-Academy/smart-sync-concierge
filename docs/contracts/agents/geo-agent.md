# Contrato: GeoAgent

## Versión
1.0.0

## Responsabilidad

Validar coherencia geográfica y detectar/zona horaria del usuario para procesamiento geo-temporal correcto.

## Interfaz

### Entrada

```python
@dataclass
class GeoInput:
    """Input del GeoAgent."""
    entities: EntityExtraction  # Del ParsingAgent
    user_id: Optional[str]       # ID del usuario si está autenticado
    user_context: Dict          # Contexto adicional (IP, user agent, etc.)
    contacts: List[Contact]      # Contactos disponibles

@dataclass
class Contact:
    """Contacto del sistema."""
    id: str
    nombre: str
    ubicacion: Optional[GeoLocation]
    timezone: Optional[str]
```

### Salida

```python
@dataclass
class GeoOutput:
    """Output del GeoAgent."""
    # Ubicación detectada
    user_location: GeoLocation
    user_timezone: str           # IANA timezone (ej: "America/Mexico_City")

    # Contacto mapeado
    contact_matched: Optional[ContactMatch]
    contact_multiple_matches: Optional[List[ContactMatch]]

    # Validación
    is_geo_coherent: bool       # Usuario y prestador en misma zona
    distance_km: Optional[float] # Distancia si aplica

    # Metadatos
    reasoning: str               # Explicación de detección
    confidence: float

@dataclass
class GeoLocation:
    """Ubicación geográfica."""
    type: str                   # "ip", "explicit", "inferred"
    country: str
    city: Optional[str]
    timezone: str              # IANA timezone
    coordinates: Optional[Coordinates]

@dataclass
class ContactMatch:
    """Contacto mapeado desde el prompt."""
    contact: Contact
    match_score: float         # 0.0 - 1.0
    match_reason: str          # "exact_name", "partial_name", "inferred"
```

## Comportamiento

### Detección de Ubicación

#### Prioridad de Fuentes

1. **Explícita**: Usuario especifica ubicación ("en CDMX", "en Madrid")
2. **IP Geolocation**: Detectar desde IP del request
3. **Contexto**: Ubicación de contactos mencionados
4. **Default**: Zona horaria del negocio

### Reglas de Detección

```python
def detect_location(user_context: Dict) -> GeoLocation:
    # 1. ¿Ubicación explícita en prompt?
    if "en" in prompt and city_name in prompt:
        return parse_explicit_location(prompt)

    # 2. ¿Geolocation desde IP?
    ip = user_context.get("ip_address")
    if ip:
        location = geolocate_from_ip(ip)
        if location:
            return location

    # 3. ¿Ubicación del contacto mencionado?
    contact = find_contact_in_prompt(prompt)
    if contact and contact.ubicacion:
        return contact.ubicacion

    # 4. Default
    return business_default_location
```

### Mapeo de Contactos

```python
def map_contact(entity_contact: str, contacts: List[Contact]) -> ContactMatch:
    """
    Mapea string de contacto a Contact object.

    Estrategias:
    1. Coincidencia exacta de nombre
    2. Coincidencia parcial (apellidos)
    3. Búsqueda fonética (similares)
    4. Sugerencias si múltiples
    """
    matches = []

    # Exact match
    for contact in contacts:
        if contact.nombre.lower() == entity_contact.lower():
            return ContactMatch(
                contact=contact,
                match_score=1.0,
                match_reason="exact_name"
            )

    # Partial match
    for contact in contacts:
        if entity_contact.lower() in contact.nombre.lower():
            matches.append((contact, 0.8))

    # Fonética (simplificada)
    for contact in contacts:
        if phonetic_similarity(entity_contact, contact.nombre) > 0.8:
            matches.append((contact, 0.7))

    # Retornar mejor match o sugerir
    if matches:
        best = sorted(matches, key=lambda x: x[1], reverse=True)[0]
        return ContactMatch(contact=best[0], match_score=best[1], match_reason="partial_name")

    return None
```

### Validación de Coherencia Geo-Temporal

```python
def validate_geo_coherence(
    user_location: GeoLocation,
    contact: Contact
) -> Tuple[bool, Optional[str]]:
    """
    Valida si usuario y contacto están en zona geográfica coherente.

    Returns:
        (is_coherent, warning_message)
    """
    # Diferencia de zona horaria
    user_tz = pytz.timezone(user_location.timezone)
    contact_tz = pytz.timezone(contact.timezone)

    offset_diff = abs(
        user_tz.utcoffset(datetime.now()).seconds // 3600 -
        contact_tz.utcoffset(datetime.now()).seconds // 3600
    )

    # Si diferencia > 3 horas, advertir
    if offset_diff > 3:
        return False, f"Diferencia de zona horaria significativa ({offset_diff}h). Confirma que es correcto."

    return True, None
```

## Casos de Uso

| Input | Output |
|-------|--------|
| "cita mañana 10am con Dr. Pérez" (usuario CDMX) | Ubicación: CDMX, TZ: America/Mexico_City |
| "cita con Dr. Pérez" (IP detecta Madrid) | Ubicación: Madrid, TZ: Europe/Madrid |
| "cita en Madrid con Dr. Pérez" (Dr. Pérez en CDMX) | Advertencia: Zonas diferentes |

## Edge Cases

| Caso | Manejo |
|------|--------|
| Sin información de ubicación | Usar default del negocio |
| Ubicación ambigua ("el médico") | Pedir aclaración |
| Multi-zona (usuario y contacto en distintos países) | Advertir, requerir confirmación |
| IP no detectable | Usar default o pedir confirmación |

## Métricas

| Métrica | Objetivo |
|---------|----------|
| **Precisión de detección de ubicación** | >90% |
| **Precisión de mapeo de contactos** | >85% |
| **Tasa de ambigüedades geográficas** | <10% |
| **Latencia p95** | <300ms (geo es rápido) |

## Error Handling

| Error | Acción |
|-------|--------|
| **IP geolocation falla** | Usar default del negocio |
| **Contacto no encontrado** | Sugerir contactos similares |
| **Múltiples contactos encontrados** | Retornar lista para que usuario elija |
| **Geo service timeout** | Fallback a default, log warning |

## Dependencias

- **IP Geolocation**: `geoip2` o API externa
- **Timezone**: `pytz` para zonas horarias
- **Fuzzy matching**: `thefuzz` para similitud de nombres
- **SharedContext**: Para acceder a contactos

## Testing

```python
async def test_deteccion_explicita():
    input = GeoInput(
        entities=EntityExtraction(
            prompt="cita en Madrid con Dr. Pérez"
        ),
        user_context={}
    )

    output = await agent.process(input)

    assert output.user_location.city == "Madrid"
    assert output.user_location.timezone == "Europe/Madrid"
    assert output.confidence > 0.95

async def test_map_contacto_exacto():
    dr_perez = Contact(
        id="contact_dr_perez",
        nombre="Dr. Juan Pérez"
    )

    input = GeoInput(
        entities=EntityExtraction(contacto="Dr. Pérez"),
        contacts=[dr_perez]
    )

    output = await agent.process(input)

    assert output.contact_matched.contact.id == "contact_dr_perez"
    assert output.contact_matched.match_score == 1.0

async def test_multi_match():
    dr_perez = Contact(id="1", nombre="Dr. Juan Pérez")
    dra_garcia = Contact(id="2", nombre="Dra. María García")

    input = GeoInput(
        entities=EntityExtraction(contacto="dr"),
        contacts=[dr_perez, dra_garcia]
    )

    output = await agent.process(input)

    assert output.contact_multiple_matches is not None
    assert len(output.contact_multiple_matches) == 2
```

## Ejemplos de Response

### Éxito con Ubicación Explícita

```json
{
  "user_location": {
    "type": "explicit",
    "country": "México",
    "city": "CDMX",
    "timezone": "America/Mexico_City",
    "coordinates": null
  },
  "user_timezone": "America/Mexico_City",
  "contact_matched": {
    "contact": {
      "id": "contact_dr_perez",
      "nombre": "Dr. Juan Pérez",
      "ubicacion": {
        "type": "presencial",
        "country": "México",
        "city": "CDMX"
      },
      "timezone": "America/Mexico_City"
    },
    "match_score": 1.0,
    "match_reason": "exact_name"
  },
  "contact_multiple_matches": null,
  "is_geo_coherent": true,
  "distance_km": null,
  "reasoning": "Ubicación explícita 'en CDMX' detectada. Contacto 'Dr. Pérez' mapeado exactamente.",
  "confidence": 0.98
}
```

### Con Múltiples Matches

```json
{
  "user_location": {
    "type": "ip",
    "country": "México",
    "city": "CDMX",
    "timezone": "America/Mexico_City"
  },
  "user_timezone": "America/Mexico_City",
  "contact_matched": null,
  "contact_multiple_matches": [
    {
      "contact": {"id": "contact_dr_perez", "nombre": "Dr. Juan Pérez"},
      "match_score": 0.85,
      "match_reason": "partial_name"
    },
    {
      "contact": {"id": "contact_dra_perez", "nombre": "Dra. Ana Pérez"},
      "match_score": 0.80,
      "match_reason": "phonetic_similarity"
    }
  ],
  "is_geo_coherent": false,
  "reasoning": "Múltiples contactos coinciden con 'Pérez'. Usuario debe seleccionar.",
  "confidence": 0.60
}
```

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: AI Team
