# Contrato: Eventos de Citas

## Versión
1.0.0

## Propósito

Definir el contrato de eventos del dominio de citas para integración con sistemas externos y auditoría.

---

## Arquitectura de Eventos

```
┌─────────────────────────────────────────────────────────┐
│                    Smart-Sync Concierge                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    ┌─────────┐
                    │  Event  │
                    │  Bus    │
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Webhook │    │  Queue  │    │  Audit  │
    │Consumers│    │Consumers│    │   Log   │
    └─────────┘    └─────────┘    └─────────┘
```

---

## Tipos de Eventos

### 1. AppointmentCreated

**Descripción**: Se crea una nueva cita

```python
@dataclass
class AppointmentCreatedEvent:
    """Evento de creación de cita"""

    # Metadatos del evento
    event_id: str                      # "evt_20260123_abc123"
    event_type: str = "appointment.created"
    event_version: str = "1.0.0"
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Datos de la cita
    appointment_id: str                # "apt_20260123_a1b2c3d4"
    fecha: date
    hora_inicio: time
    hora_fin: time

    # Participantes
    contacto:
        id: str                        # "contact_dr_perez"
        nombre: str                    # "Dr. Pérez"
        tipo: str                      # "doctor"

    tipo_cita:
        id: str                        # "service_consulta_general"
        nombre: str                    # "Consulta General"
        duracion_minutos: int          # 60

    # Contexto
    ubicacion:
        tipo: str                      # "consultorio"
        nombre: str                    # "Consultorio Principal"
        direccion: str                 # "Av. Reforma 123"

    usuario:
        id: Optional[str]              # "user_12345"
        timezone: str                  # "America/Mexico_City"

    # Metadatos de creación
    created_via: str                   # "api", "admin", "webhook"
    prompt_original: Optional[str]     # "cita mañana 10am con Dr. Pérez"
    trace_id: str                      # "trc_abc123"
    confidence: float                  # 0.95

    # Validaciones
    validation_passed: bool = True
    validation_warnings: List[str] = field(default_factory=list)
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_20260123_a1b2c3d4",
  "event_type": "appointment.created",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T15:30:00Z",
  "appointment_id": "apt_20260123_x9y8z7",
  "fecha": "2026-01-24",
  "hora_inicio": "10:00",
  "hora_fin": "11:00",
  "contacto": {
    "id": "contact_dr_perez",
    "nombre": "Dr. Pérez",
    "tipo": "doctor"
  },
  "tipo_cita": {
    "id": "service_consulta_general",
    "nombre": "Consulta General",
    "duracion_minutos": 60
  },
  "ubicacion": {
    "tipo": "consultorio",
    "nombre": "Consultorio Principal",
    "direccion": "Av. Reforma 123, CDMX"
  },
  "usuario": {
    "id": "user_12345",
    "timezone": "America/Mexico_City"
  },
  "created_via": "api",
  "prompt_original": "cita mañana 10am con Dr. Pérez",
  "trace_id": "trc_abc123",
  "confidence": 0.95,
  "validation_passed": true,
  "validation_warnings": []
}
```

### 2. AppointmentCancelled

**Descripción**: Se cancela una cita existente

```python
@dataclass
class AppointmentCancelledEvent:
    """Evento de cancelación de cita"""

    event_id: str
    event_type: str = "appointment.cancelled"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Datos de la cita
    appointment_id: str
    fecha: date
    hora_inicio: time
    contacto_id: str
    contacto_nombre: str

    # Contexto de cancelación
    cancelled_by: str                  # "user", "admin", "system"
    cancelled_at: datetime
    motivo: Optional[str]              # "Paciente solicitó cambio"
    reason_code: str                   # "user_request", "no_show", "emergency"

    # Repercusiones
    notificacion_enviada: bool
    notificacion_canal: Optional[str]  # "email", "sms", "whatsapp"
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_20260123_def456",
  "event_type": "appointment.cancelled",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T16:00:00Z",
  "appointment_id": "apt_20260123_x9y8z7",
  "fecha": "2026-01-24",
  "hora_inicio": "10:00",
  "contacto_id": "contact_dr_perez",
  "contacto_nombre": "Dr. Pérez",
  "cancelled_by": "user",
  "cancelled_at": "2026-01-23T16:00:00Z",
  "motivo": "El paciente solicitó cambio por conflicto personal",
  "reason_code": "user_request",
  "notificacion_enviada": true,
  "notificacion_canal": "email"
}
```

### 3. AppointmentRescheduled

**Descripción**: Se reprograma una cita a nueva fecha/hora

```python
@dataclass
class AppointmentRescheduledEvent:
    """Evento de reprogramación de cita"""

    event_id: str
    event_type: str = "appointment.rescheduled"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Datos de la cita
    appointment_id: str

    # Horario original
    original_fecha: date
    original_hora_inicio: time
    original_hora_fin: time

    # Horario nuevo
    new_fecha: date
    new_hora_inicio: time
    new_hora_fin: time

    # Contexto
    rescheduled_by: str
    rescheduled_at: datetime
    motivo: Optional[str]

    # Diferencia
    dias_cambiados: int                # Diferencia en días
    horas_cambiadas: int               # Diferencia en horas
    timezone: str
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_20260123_ghi789",
  "event_type": "appointment.rescheduled",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T16:30:00Z",
  "appointment_id": "apt_20260123_x9y8z7",
  "original_fecha": "2026-01-24",
  "original_hora_inicio": "10:00",
  "original_hora_fin": "11:00",
  "new_fecha": "2026-01-25",
  "new_hora_inicio": "14:00",
  "new_hora_fin": "15:00",
  "rescheduled_by": "user",
  "rescheduled_at": "2026-01-23T16:30:00Z",
  "motivo": "Conflicto laboral del paciente",
  "dias_cambiados": 1,
  "horas_cambiadas": 4,
  "timezone": "America/Mexico_City"
}
```

### 4. AppointmentConflictDetected

**Descripción**: Se detectó un conflicto de disponibilidad

```python
@dataclass
class AppointmentConflictDetectedEvent:
    """Evento de detección de conflicto"""

    event_id: str
    event_type: str = "appointment.conflict_detected"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Cita conflictiva
    candidate_appointment:
        fecha: date
        hora_inicio: time
        hora_fin: time
        contacto_id: str

    # Conflicto detectado
    conflict_type: str                 # "full_overlap", "partial_overlap", "back_to_back"
    conflicting_appointment_id: str
    overlap_duration_minutes: int

    # Respuesta del sistema
    suggestions_generated: int
    suggestions:
        - rank: int
          fecha: date
          hora_inicio: time
          motivo: str

    # Outcome
    user_action: Optional[str]         # "accepted_suggestion", "rescheduled", "cancelled"
    action_taken_at: Optional[datetime]
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_20260123_jkl012",
  "event_type": "appointment.conflict_detected",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T17:00:00Z",
  "candidate_appointment": {
    "fecha": "2026-01-24",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "contacto_id": "contact_dr_perez"
  },
  "conflict_type": "full_overlap",
  "conflicting_appointment_id": "apt_20260124_existing",
  "overlap_duration_minutes": 60,
  "suggestions_generated": 3,
  "suggestions": [
    {
      "rank": 1,
      "fecha": "2026-01-24",
      "hora_inicio": "11:00",
      "motivo": "Inmediatamente después de la cita existente"
    },
    {
      "rank": 2,
      "fecha": "2026-01-24",
      "hora_inicio": "09:00",
      "motivo": "Antes de la cita existente"
    },
    {
      "rank": 3,
      "fecha": "2026-01-25",
      "hora_inicio": "10:00",
      "motivo": "Siguiente día, misma hora"
    }
  ],
  "user_action": "accepted_suggestion",
  "action_taken_at": "2026-01-23T17:05:00Z"
}
```

### 5.AppointmentReminder

**Descripción**: Recordatorio de cita próximo

```python
@dataclass
class AppointmentReminderEvent:
    """Evento de recordatorio"""

    event_id: str
    event_type: str = "appointment.reminder"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Datos de la cita
    appointment_id: str
    fecha: date
    hora_inicio: time
    contacto_nombre: str
    ubicacion:
        tipo: str
        nombre: str
        direccion: Optional[str]

    # Recordatorio
    reminder_type: str                 # "email", "sms", "whatsapp"
    minutos_antes: int                 # 60, 1440 (1 día), etc.
    mensaje: str

    # Estado
    enviado: bool
    enviado_at: Optional[datetime]
    error: Optional[str]
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_20260123_mno345",
  "event_type": "appointment.reminder",
  "event_version": "1.0.0",
  "timestamp": "2026-01-23T09:00:00Z",
  "appointment_id": "apt_20260124_x9y8z7",
  "fecha": "2026-01-24",
  "hora_inicio": "10:00",
  "contacto_nombre": "Dr. Pérez",
  "ubicacion": {
    "tipo": "consultorio",
    "nombre": "Consultorio Principal",
    "direccion": "Av. Reforma 123, CDMX"
  },
  "reminder_type": "whatsapp",
  "minutos_antes": 60,
  "mensaje": "Recordatorio: Cita mañana a las 10:00am con Dr. Pérez en Consultorio Principal",
  "enviado": true,
  "enviado_at": "2026-01-23T09:00:05Z",
  "error": null
}
```

### 6. AppointmentCompleted

**Descripción**: Se completó una cita

```python
@dataclass
class AppointmentCompletedEvent:
    """Evento de cita completada"""

    event_id: str
    event_type: str = "appointment.completed"
    event_version: str = "1.0.0"
    timestamp: datetime

    # Datos de la cita
    appointment_id: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    contacto_id: str
    tipo_cita_id: str

    # Contexto de completado
    completed_at: datetime
    completed_by: str                  # "contacto", "admin", "system"

    # Outcome
    no_show: bool = False
    notas: Optional[str] = None
    proxima_cita_sugerida: Optional[dict] = None
```

**Ejemplo JSON**:
```json
{
  "event_id": "evt_20260124_pqr678",
  "event_type": "appointment.completed",
  "event_version": "1.0.0",
  "timestamp": "2026-01-24T11:00:00Z",
  "appointment_id": "apt_20260124_x9y8z7",
  "fecha": "2026-01-24",
  "hora_inicio": "10:00",
  "hora_fin": "11:00",
  "contacto_id": "contact_dr_perez",
  "tipo_cita_id": "service_consulta_general",
  "completed_at": "2026-01-24T11:00:00Z",
  "completed_by": "contacto",
  "no_show": false,
  "notas": "Consulta exitosa, paciente debe regresar en 2 semanas",
  "proxima_cita_sugerida": {
    "fecha": "2026-02-07",
    "motivo": "Seguimiento"
  }
}
```

---

## Integración con Event Bus

### Publicación de Eventos

```python
# core/events/publisher.py
class EventPublisher:
    """Publica eventos al message bus"""

    def __init__(self, bus_type: str = "redis"):
        self.bus_type = bus_type
        self.client = self._connect()

    def _connect(self):
        if self.bus_type == "redis":
            import redis
            return redis.Redis(host='localhost', port=6379)
        elif self.bus_type == "rabbitmq":
            import pika
            connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
            return connection.channel()
        elif self.bus_type == "kafka":
            from kafka import KafkaProducer
            return KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )

    async def publish(self, event: dict):
        """Publica evento al bus"""
        topic = f"appointments.{event['event_type'].split('.')[-1]}"

        if self.bus_type == "redis":
            self.client.publish(topic, json.dumps(event))

        elif self.bus_type == "rabbitmq":
            self.client.basic_publish(
                exchange='appointments',
                routing_key=topic,
                body=json.dumps(event)
            )

        elif self.bus_type == "kafka":
            self.client.send(topic, event)

        # Log para auditoría
        logger.info(f"Event published: {event['event_id']} -> {topic}")
```

### Consumo de Eventos

```python
# core/events/consumer.py
class EventConsumer:
    """Consume eventos del message bus"""

    def __init__(self, bus_type: str = "redis"):
        self.bus_type = bus_type
        self.client = self._connect()
        self.handlers = {}

    def subscribe(self, event_type: str, handler: Callable):
        """Registra handler para tipo de evento"""
        self.handlers[event_type] = handler

    async def start(self):
        """Inicia consumo de eventos"""
        if self.bus_type == "redis":
            pubsub = self.client.pubsub()
            pubsub.subscribe('appointments.*')

            for message in pubsub.listen():
                if message['type'] == 'message':
                    event = json.loads(message['data'])
                    await self._handle(event)

        elif self.bus_type == "rabbitmq":
            self.client.basic_consume(
                queue='appointments',
                on_message_callback=self._handle_rabbitmq
            )
            self.client.start_consuming()

    async def _handle(self, event: dict):
        """Rutea evento al handler correspondiente"""
        event_type = event['event_type']

        if event_type in self.handlers:
            try:
                await self.handlers[event_type](event)
            except Exception as e:
                logger.error(f"Error handling {event_type}: {e}")
```

---

## Webhooks

### Registro de Webhooks

```python
# apps/webhooks/models.py
@dataclass
class Webhook:
    """Configuración de webhook"""

    id: str                            # "whk_abc123"
    url: str                           # "https://example.com/webhook"
    events: List[str]                  # ["appointment.created", "appointment.cancelled"]
    secret: str                        # Para firmar payloads
    active: bool = True
    created_at: datetime

    # Headers opcionales
    headers: Dict[str, str] = field(default_factory=dict)

    # Retry config
    max_retries: int = 3
    retry_delay_seconds: int = 60
```

### Envío de Webhooks

```python
# apps/webhooks/sender.py
class WebhookSender:
    """Envía eventos a webhooks registrados"""

    async def send(self, event: dict):
        """Envía evento a webhooks suscritos"""
        event_type = event['event_type']

        # Buscar webhooks suscritos a este evento
        webhooks = webhook_store.get_by_event(event_type)

        for webhook in webhooks:
            if not webhook.active:
                continue

            try:
                await self._send_webhook(webhook, event)
            except Exception as e:
                logger.error(f"Webhook failed: {webhook.id} - {e}")

                # Reintentar si config lo permite
                if webhook.max_retries > 0:
                    await self._retry_webhook(webhook, event)

    async def _send_webhook(self, webhook: Webhook, event: dict):
        """Envía a URL específica"""
        # Firmar payload
        signature = self._sign_payload(event, webhook.secret)

        # Enviar request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook.url,
                json=event,
                headers={
                    **webhook.headers,
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": event['event_type'],
                    "X-Webhook-ID": event['event_id']
                },
                timeout=10
            )

            response.raise_for_status()

    def _sign_payload(self, payload: dict, secret: str) -> str:
        """Firma payload con HMAC"""
        import hmac
        import hashlib

        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
```

---

## Auditoría

### Log de Eventos

```python
# core/audit/event_log.py
class EventLog:
    """Log persistente de todos los eventos"""

    async def append(self, event: dict):
        """Agrega evento al log"""
        log_entry = {
            "event": event,
            "received_at": datetime.utcnow().isoformat(),
            "processed": False
        }

        # Guardar en archivo JSON
        with open("data/audit/events.logl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # O en DB (cuando migremos)
        # await EventLogDB.insert(event)

    async def get_by_date(self, date: date) -> List[dict]:
        """Obtiene eventos de una fecha específica"""
        events = []

        with open("data/audit/events.logl", "r") as f:
            for line in f:
                entry = json.loads(line)
                event_date = datetime.fromisoformat(
                    entry['received_at']
                ).date()

                if event_date == date:
                    events.append(entry['event'])

        return events
```

---

## Testing

### Test de Publicación

```python
# tests/events/test_publisher.py
async def test_event_published():
    """Verifica que evento se publica correctamente"""
    publisher = EventPublisher(bus_type="redis")

    event = {
        "event_id": "evt_test",
        "event_type": "appointment.created",
        "appointment_id": "apt_test"
    }

    await publisher.publish(event)

    # Verificar que llegó al bus
    # (depende de implementación del bus)
```

### Test de Webhook

```python
# tests/webhooks/test_sender.py
async def test_webhook_delivery():
    """Verifica entrega de webhook"""
    # Mock servidor webhook
    webhook_url = "https://httpbin.org/post"

    webhook = Webhook(
        id="whk_test",
        url=webhook_url,
        events=["appointment.created"],
        secret="test_secret"
    )

    sender = WebhookSender()
    event = {
        "event_id": "evt_test",
        "event_type": "appointment.created",
        "appointment_id": "apt_test"
    }

    await sender.send(event)

    # Verificar que httpbin recibió el request
```

---

## Métricas

| Métrica | Descripción | Objetivo |
|---------|-------------|----------|
| **event_publish_rate** | Eventos publicados por segundo | >100/s |
| **event_delivery_rate** | Eventos entregados exitosamente | >99% |
| **webhook_success_rate** | Webhooks entregados exitosamente | >95% |
| **event_latency_p95** | Tiempo de publicación a entrega | <500ms |
| **dead_letter_queue_size** | Eventos fallidos | <0.1% |

---

## Versión de Contrato

| Versión | Cambios | Fecha |
|---------|---------|-------|
| 1.0.0 | Versión inicial | 2026-01-22 |

---

**Versión**: 1.0.0
**Última actualización**: Enero 22, 2026
**Mantenedor**: Integration Team
