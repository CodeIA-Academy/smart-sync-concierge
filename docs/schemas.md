# Esquemas de Datos - Smart-Sync Concierge

Este documento describe los esquemas JSON utilizados para el almacenamiento de datos en Smart-Sync Concierge.

## Índice

1. [Esquema de Citas](#esquema-de-citas-appointmentsjson)
2. [Esquema de Contactos](#esquema-de-contactos-contactsjson)
3. [Esquema de Servicios](#esquema-de-servicios-servicesjson)
4. [Esquema de Disponibilidad](#esquema-de-disponibilidad-availabilityjson)
5. [Esquema de Configuración](#esquema-de-configuración-configjson)

---

## Esquema de Citas (`appointments.json`)

### Estructura Completa

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2026-01-22T10:00:00Z",
    "total_appointments": 0
  },
  "appointments": [
    {
      "id": "apt_20260123_abc123",
      "status": "confirmed",
      "created_at": "2026-01-22T15:30:00Z",
      "updated_at": "2026-01-22T15:30:00Z",

      "prompt_original": "cita mañana 10am con Dr. Pérez",

      "fecha": "2026-01-23",
      "hora_inicio": "10:00",
      "hora_fin": "11:00",
      "duracion_minutos": 60,
      "zona_horaria": "America/Mexico_City",

      "tipo": {
        "id": "consulta_general",
        "nombre": "Consulta General",
        "categoria": "medica"
      },

      "participantes": [
        {
          "id": "contact_dr_perez",
          "nombre": "Dr. Juan Pérez",
          "rol": "prestador",
          "contacto": {
            "email": "drperez@example.com",
            "telefono": "+525512345678"
          }
        }
      ],

      "ubicacion": {
        "tipo": "presencial",
        "direccion": "Consultorio 301",
        "coordenadas": null
      },

      "notas": {
        "cliente": "Primera consulta",
        "interna": "Referencia: website",
        "ia_confidence": 0.95
      },

      "recordatorios": [
        {
          "tipo": "email",
          "enviado": false,
          "programado_para": "2026-01-23T08:00:00Z"
        },
        {
          "tipo": "sms",
          "enviado": false,
          "programado_para": "2026-01-23T09:00:00Z"
        }
      ],

      "metadata_validacion": {
        "contacto_validado": true,
        "servicio_validado": true,
        "horario_validado": true,
        "conflictos_verificados": true,
        "conflictos_encontrados": 0
      }
    }
  ]
}
```

### Campos Descripción

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | string | ✓ | ID único de la cita (formato: `apt_YYYYMMDD_XXXX`) |
| `status` | string | ✓ | Estado: `pending`, `confirmed`, `cancelled`, `completed` |
| `created_at` | datetime | ✓ | Fecha de creación (ISO 8601) |
| `updated_at` | datetime | ✓ | Fecha de última actualización (ISO 8601) |
| `prompt_original` | string | ✓ | Prompt original del usuario |
| `fecha` | date | ✓ | Fecha de la cita (YYYY-MM-DD) |
| `hora_inicio` | time | ✓ | Hora de inicio (HH:MM) |
| `hora_fin` | time | ✓ | Hora de fin (HH:MM) |
| `duracion_minutos` | integer | ✓ | Duración en minutos |
| `zona_horaria` | string | ✓ | Zona horaria (IANA format) |
| `tipo` | object | ✓ | Objeto con id, nombre, categoria |
| `participantes` | array | ✓ | Lista de participantes |
| `ubicacion` | object | ✓ | Objeto con tipo, direccion, coordenadas |
| `notas` | object | ✗ | Objeto con notas cliente, interna, ia_confidence |
| `recordatorios` | array | ✗ | Lista de recordatorios programados |
| `metadata_validacion` | object | ✓ | Metadata del proceso de validación |

---

## Esquema de Contactos (`contacts.json`)

### Estructura Completa

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2026-01-22T10:00:00Z",
    "total_contacts": 0
  },
  "contacts": [
    {
      "id": "contact_dr_perez",
      "tipo": "prestador",
      "activo": true,
      "created_at": "2026-01-22T10:00:00Z",

      "datos_personales": {
        "nombre": "Dr. Juan Pérez",
        "titulo": "Médico General",
        "email": "drperez@example.com",
        "telefono": "+525512345678",
        "idioma": "es"
      },

      "disponibilidad": {
        "horario_laboral": {
          "lunes": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
          "martes": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
          "miercoles": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
          "jueves": { "inicio": "09:00", "fin": "18:00", "pausa": "12:00-14:00" },
          "viernes": { "inicio": "09:00", "fin": "15:00", "pausa": null },
          "sabado": { "inicio": null, "fin": null, "pausa": null },
          "domingo": { "inicio": null, "fin": null, "pausa": null }
        },
        "excepciones": [
          {
            "fecha": "2026-01-25",
            "motivo": "Capacitación",
            "disponible": false
          }
        ],
        "zona_horaria": "America/Mexico_City"
      },

      "especialidades": ["consulta_general", "pediatria"],

      "duraciones_predeterminadas": {
        "consulta_general": 60,
        "pediatria": 45
      },

      "preferencias": {
        "tiempo_entre_citas": 15,
        "anticipacion_reserva": 24,
        "max_citas_dia": 12
      }
    }
  ]
}
```

### Campos Descripción

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | string | ✓ | ID único del contacto |
| `tipo` | string | ✓ | Tipo: `prestador`, `cliente` |
| `activo` | boolean | ✓ | Estado activo/inactivo |
| `created_at` | datetime | ✓ | Fecha de creación |
| `datos_personales` | object | ✓ | Objeto con nombre, titulo, email, telefono, idioma |
| `disponibilidad` | object | ✓ | Objeto con horario_laboral, excepciones, zona_horaria |
| `especialidades` | array | ✗ | Lista de especialidades |
| `duraciones_predeterminadas` | object | ✗ | Objeto servicio -> duración |
| `preferencias` | object | ✗ | Objeto con tiempo_entre_citas, anticipacion_reserva, max_citas_dia |

---

## Esquema de Servicios (`services.json`)

### Estructura Completa

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2026-01-22T10:00:00Z"
  },
  "services": [
    {
      "id": "consulta_general",
      "nombre": "Consulta General",
      "categoria": "medica",
      "descripcion": "Consulta médica de rutina",
      "duracion_default": 60,
      "precio": null,
      "activo": true,
      "requiere_contacto": true,
      "sinonimos_ia": [
        "cita",
        "consulta",
        "revision",
        "chequeo",
        "consulta general"
      ]
    },
    {
      "id": "consulta_seguimiento",
      "nombre": "Consulta de Seguimiento",
      "categoria": "medica",
      "descripcion": "Seguimiento de tratamiento",
      "duracion_default": 30,
      "precio": null,
      "activo": true,
      "requiere_contacto": true,
      "sinonimos_ia": [
        "seguimiento",
        "control",
        "revision tratamiento",
        "consulta control"
      ]
    }
  ]
}
```

### Campos Descripción

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | string | ✓ | ID único del servicio |
| `nombre` | string | ✓ | Nombre del servicio |
| `categoria` | string | ✓ | Categoría: `medica`, `odontologia`, etc. |
| `descripcion` | string | ✓ | Descripción del servicio |
| `duracion_default` | integer | ✓ | Duración predeterminada en minutos |
| `precio` | decimal | ✗ | Precio del servicio (null si gratuito) |
| `activo` | boolean | ✓ | Estado activo/inactivo |
| `requiere_contacto` | boolean | ✓ | Si requiere contacto asignado |
| `sinonimos_ia` | array | ✓ | Sinónimos para reconocimiento IA |

---

## Esquema de Disponibilidad (`availability.json`)

### Estructura Completa

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "2026-01-22T10:00:00Z"
  },
  "availability": {
    "global": {
      "habilitado": true,
      "anticipacion_minima_minutos": 60,
      "anticipacion_maxima_dias": 90,
      "intervalo_minutos": 15
    },
    "horario_operacion": {
      "inicio": "09:00",
      "fin": "18:00",
      "dias_laborales": ["lunes", "martes", "miercoles", "jueves", "viernes"],
      "pausa_inicio": "12:00",
      "pausa_fin": "14:00",
      "festivos": ["2026-01-01", "2026-12-25"]
    },
    "por_contacto": {
      "contact_dr_perez": {
        "overrides": {
          "martes": { "inicio": "10:00", "fin": "17:00" }
        },
        "excepciones": [
          {
            "fecha": "2026-01-25",
            "motivo": "Capacitación",
            "disponible": false
          }
        ]
      }
    }
  }
}
```

### Campos Descripción

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `global.habilitado` | boolean | ✓ | Si el sistema de disponibilidad está habilitado |
| `global.anticipacion_minima_minutos` | integer | ✓ | Anticipación mínima para reserva |
| `global.anticipacion_maxima_dias` | integer | ✓ | Anticipación máxima para reserva |
| `global.intervalo_minutos` | integer | ✓ | Intervalo entre slots |
| `horario_operacion.inicio` | time | ✓ | Hora inicio operación |
| `horario_operacion.fin` | time | ✓ | Hora fin operación |
| `horario_operacion.dias_laborales` | array | ✓ | Días laborales |
| `horario_operacion.pausa_inicio` | time | ✗ | Inicio pausa |
| `horario_operacion.pausa_fin` | time | ✗ | Fin pausa |
| `horario_operacion.festivos` | array | ✓ | Lista de festivos |
| `por_contacto` | object | ✗ | Overrides por contacto |

---

## Esquema de Configuración (`config.json`)

### Estructura Completa

```json
{
  "version": "1.0.0",
  "negocio": {
    "nombre": "Smart-Sync Concierge",
    "zona_horaria_default": "America/Mexico_City",
    "idioma_default": "es",
    "horario_operacion": {
      "inicio": "09:00",
      "fin": "18:00",
      "dias_laborales": ["lunes", "martes", "miercoles", "jueves", "viernes"]
    },
    "anticipacion_minima_reserva": 60,
    "anticipacion_maxima_reserva": 43200,
    "festivos": ["2026-01-01", "2026-12-25"]
  },
  "ia": {
    "modelo": "qwen-2.5",
    "temperatura": 0.3,
    "max_tokens": 500,
    "idioma_soportado": ["es", "en"]
  },
  "validaciones": {
    "permitir_solapamiento": false,
    "tiempo_entre_citas": 15,
    "verificar_festivos": true
  }
}
```

### Campos Descripción

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `negocio.nombre` | string | Nombre del negocio |
| `negocio.zona_horaria_default` | string | Zona horaria por defecto |
| `negocio.idioma_default` | string | Idioma por defecto |
| `negocio.horario_operacion` | object | Horario de operación global |
| `negocio.anticipacion_minima_reserva` | integer | Minutos de anticipación mínima |
| `negocio.anticipacion_maxima_reserva` | integer | Minutos de anticipación máxima |
| `negocio.festivos` | array | Lista de festivos |
| `ia.modelo` | string | Modelo de IA a usar |
| `ia.temperatura` | float | Temperatura para respuestas IA |
| `ia.max_tokens` | integer | Máximo de tokens para IA |
| `ia.idioma_soportado` | array | Idiomas soportados |
| `validaciones.permitir_solapamiento` | boolean | Si permite citas solapadas |
| `validaciones.tiempo_entre_citas` | integer | Tiempo mínimo entre citas |
| `validaciones.verificar_festivos` | boolean | Si verifica festivos |

---

## Convenciones

### IDs

Los IDs siguen el formato `{tipo}_{fecha}_{uuid}`:

- Citas: `apt_20260123_abc123`
- Contactos: `contact_dr_perez`
- Servicios: `consulta_general`

### Fechas y Horas

- **Fechas**: Formato ISO 8601 (`YYYY-MM-DD`)
- **Horas**: Formato 24h (`HH:MM`)
- **Datetime**: ISO 8601 con zona horaria (`YYYY-MM-DDTHH:MM:SSZ`)

### Zonas Horarias

Formato IANA (ejemplos):

- `America/Mexico_City`
- `America/Bogota`
- `Europe/Madrid`
- `America/New_York`

### Estados

**Estados de Cita**:
- `pending`: Pendiente de confirmación
- `confirmed`: Confirmada
- `cancelled`: Cancelada
- `completed`: Completada

**Tipos de Contacto**:
- `prestador`: Prestador de servicio
- `cliente`: Cliente/usuario

---

**Última actualización**: Enero 22, 2026
**Versión**: 0.1.0
