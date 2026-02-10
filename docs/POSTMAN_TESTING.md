# Testing con Postman - Smart-Sync n8n Workflow

## 📋 Resumen

Workflow profesional de 6 nodos en n8n que procesa solicitudes de citas a través de:
1. **Webhook Input**: Recibe POST desde Postman
2. **Preparar Datos**: Enriquece con metadata
3. **Llamar Django API**: Procesa en Django
4. **AI Agent (Haiku)**: Genera respuesta personalizada con IA
5. **OpenRouter Chat Model**: Modelo Haiku 4.5
6. **Webhook Response**: Retorna JSON al cliente

## 🔧 URL del Webhook

```
POST https://n8n.codeia.dev/webhook/appointments/process
```

## 📤 Estructura de Petición (Postman)

### Headers
```
Content-Type: application/json
```

### Body (JSON)
```json
{
  "prompt": "necesito una cita con cardiólogo para la próxima semana",
  "user_timezone": "America/Mexico_City",
  "user_id": "user_12345"
}
```

### Parámetros
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `prompt` | string | Sí | Solicitud de cita del usuario |
| `user_timezone` | string | No | Zona horaria (default: Europe/Madrid) |
| `user_id` | string | No | ID del usuario (default: anonymous) |

## 📥 Estructura de Respuesta

```json
{
  "status": "success",
  "message": "Respuesta personalizada generada por Haiku 4.5",
  "appointment": {
    "id": "apt_abc123",
    "prompt": "necesito una cita...",
    "specialization": "Cardiología",
    "doctor_name": "Dr. García",
    "appointment_datetime": "2026-02-15T10:00:00Z",
    "location": "Hospital Central"
  },
  "confirmation": {
    "message": "Tu cita ha sido confirmada. Por favor llega 10 minutos antes.",
    "timezone": "America/Mexico_City"
  }
}
```

## 🧪 Ejemplos de Prueba

### Ejemplo 1: Cardiología
```bash
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita con cardiólogo urgente",
    "user_timezone": "America/Mexico_City",
    "user_id": "patient_001"
  }'
```

### Ejemplo 2: Medicina General
```bash
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "check-up general para mañana",
    "user_timezone": "Europe/Madrid"
  }'
```

## 🔍 Flujo de Datos

```
Postman Request
    ↓
Webhook Input (recibe JSON)
    ↓
Preparar Datos (extrae + metadata)
    ↓
Llamar Django API (POST /api/v1/appointments/)
    ↓
AI Agent (Haiku) ← OpenRouter Chat Model
    ↓
Webhook Response (retorna al cliente)
    ↓
Postman Response
```

## ✅ Checklist de Configuración en n8n

- [ ] Crear webhook en `/webhook/appointments/process`
- [ ] Conectar 6 nodos en orden correcto
- [ ] Configurar token Django en nodo "Llamar Django API"
- [ ] Verificar credenciales OpenRouter en nodo LLM
- [ ] Activar workflow
- [ ] Probar con curl o Postman

## 🚀 Primeros Pasos

1. Abre n8n en https://n8n.codeia.dev/
2. Crea un nuevo workflow
3. Agrega los 6 nodos según la estructura
4. Conecta nodos en orden
5. Activa el workflow
6. Prueba con curl/Postman

## 📌 Notas Importantes

- El token Django debe ser válido en la base de datos
- OpenRouter API key debe estar configurada en n8n
- La URL de Django debe ser accesible desde n8n
- responseMode debe ser "responseNode" para que responda correctamente

## 🐛 Troubleshooting

**Error: 404 Webhook not registered**
- Verifica que el webhook esté activo en n8n
- Copia la URL exacta: `https://n8n.codeia.dev/webhook/appointments/process`

**Error: 401 Unauthorized**
- Token Django inválido o no existe
- Genera nuevo token: `python manage.py drf_create_token admin`

**Error: Timeout**
- Django API no responde
- Verifica que Django esté corriendo: `http://localhost:8000/api/v1/appointments/`

**Respuesta vacía**
- Webhook Response no configurado correctamente
- Verifica que `responseMode` = "responseNode"
