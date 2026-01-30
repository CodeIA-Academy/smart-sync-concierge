# Migración a PostgreSQL (Neon)

## Resumen

Smart-Sync Concierge ha sido migrado de JSON-based stores a PostgreSQL (Neon) como base de datos principal. Esto proporciona escalabilidad, persistencia confiable y soporte para operaciones complejas.

## Cambios Implementados

### 1. **Modelos Django ORM**

Se crearon tres modelos Django principales:

#### Contact (apps/contacts/models.py)
```python
- id: CharField (primary key)
- nombre: CharField
- titulo: CharField (opcional)
- email: EmailField (opcional)
- telefono: CharField (opcional)
- tipo: CharField (choices: prestador, staff, resource)
- especialidades: JSONField (lista de especialidades)
- activo: BooleanField
- created_at, updated_at: DateTimeField
```

#### Service (apps/services/models.py)
```python
- id: CharField (primary key)
- nombre: CharField
- categoria: CharField (choices: medica, administrativa, etc.)
- descripcion: TextField (opcional)
- duracion_minutos: IntegerField
- activo: BooleanField
- created_at, updated_at: DateTimeField
```

#### Appointment (apps/appointments/models.py)
```python
- id: CharField (primary key)
- fecha: DateField
- hora_inicio, hora_fin: TimeField
- duracion_minutos: IntegerField
- status: CharField (choices: pending, confirmed, cancelled, completed, no_show)
- tipo: JSONField (información del servicio)
- participantes: JSONField (lista de participantes)
- usuario_id: CharField (opcional)
- prompt_original: TextField (opcional)
- notas: JSONField
- metadata: JSONField
- created_at, updated_at: DateTimeField
```

### 2. **Interfaz Admin Django**

Se crearon interfaces admin personalizadas para cada modelo:
- [apps/contacts/admin.py](../../apps/contacts/admin.py)
- [apps/services/admin.py](../../apps/services/admin.py)
- [apps/appointments/admin.py](../../apps/appointments/admin.py)

Accede a http://localhost:9001/admin/ con credenciales de superuser.

### 3. **Migraciones**

Se generaron migraciones iniciales:
- `apps/appointments/migrations/0001_initial.py`
- `apps/contacts/migrations/0001_initial.py`
- `apps/services/migrations/0001_initial.py`

Aplicadas con: `python3 manage.py migrate`

### 4. **Comando de Población de Datos**

Nuevo comando de gestión que crea datos demo:

```bash
python3 manage.py populate_demo_data
```

Crea automáticamente:
- 3 contactos (Dr. Juan Pérez, Dra. María García, Dr. Carlos López)
- 4 servicios (Consulta General, Cardiología, Dermatología, Pediatría)
- 3 citas de demostración

### 5. **Vistas Actualizadas**

Migraron de JSON stores a QuerySets de Django:

#### ContactViewSet (apps/contacts/views.py)
- `list()`: Ahora usa `Contact.objects.all()` con filtros
- Filtra por tipo, activo, búsqueda en nombre/titulo
- Paginación automática

#### ServiceViewSet (apps/services/views.py)
- `list()`: Usa `Service.objects.all()`
- Filtra por categoría, activo, búsqueda
- Paginación automática

#### AppointmentViewSet (apps/appointments/views.py)
- `list()`: Usa `Appointment.objects.all()`
- Filtra por status, fecha_inicio, fecha_fin
- Paginación automática

### 6. **Serializers Actualizados**

Se simplificaron serializers para que funcionen con modelos Django:
- `ContactListSerializer`: Maneja campos del modelo Contact
- `ServiceListSerializer`: Maneja campos del modelo Service
- `AppointmentListSerializer`: Maneja campos del modelo Appointment

## Configuración de Base de Datos

### Neon PostgreSQL

El archivo `.env` contiene la conexión a Neon:

```env
DATABASE_URL=postgresql://[usuario]:[contraseña]@[host]/[base_datos]?sslmode=require&channel_binding=require
```

### Entornos

**Local** (`config/settings/local.py`):
- Usa PostgreSQL (Neon) vía DATABASE_URL
- DEBUG = True
- ALLOWED_HOSTS = localhost, 127.0.0.1

**Producción** (`config/settings/production.py`):
- Usa PostgreSQL (Neon) vía DATABASE_URL
- Validación de ALLOWED_HOSTS en producción
- SECURE_SSL_REDIRECT = True
- SECURE_PROXY_SSL_HEADER para reverse proxy HTTPS

## Datos de Demostración

### Contactos

| ID | Nombre | Especialidad | Tipo |
|----|--------|-------------|------|
| dr_juan_perez | Dr. Juan Pérez | Consulta General, Pediatría | prestador |
| dra_maria_garcia | Dra. María García | Cardiología | prestador |
| dr_carlos_lopez | Dr. Carlos López | Dermatología | prestador |

### Servicios

| ID | Nombre | Categoría | Duración |
|----|--------|-----------|----------|
| consulta_general | Consulta General | medica | 30 min |
| consulta_cardiologia | Consulta Cardiología | medica | 45 min |
| consulta_dermatologia | Consulta Dermatología | medica | 40 min |
| consulta_pediatria | Consulta Pediatría | medica | 25 min |

### Citas

Se crean 3 citas confirmadas para los próximos días.

## Testing de la API

### Obtener Token

```bash
curl -X POST http://localhost:9001/api/v1/token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Listar Contactos

```bash
TOKEN="[tu_token]"
curl -s http://localhost:9001/api/v1/contacts/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### Listar Servicios

```bash
curl -s http://localhost:9001/api/v1/services/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### Listar Citas

```bash
curl -s http://localhost:9001/api/v1/appointments/ \
  -H "Authorization: Token $TOKEN" | jq .
```

## Próximos Pasos

1. **Actualizar vistas pendientes**:
   - GET/POST para create, retrieve, update, delete en cada endpoint
   - Endpoint de availability para contacts
   - Endpoint de rescheduling para appointments

2. **Agregar más validaciones**:
   - Conflictos de citas
   - Disponibilidad de contactos
   - Reglas de negocio por servicio

3. **Mejorar serializers**:
   - Usar ModelSerializer para reducir código
   - Agregar validación anidada
   - Soporte para relaciones

4. **Tests**:
   - Tests unitarios para modelos
   - Tests de integración para endpoints
   - Tests de validación de negocio

## Arquivos Relacionados

- [populate_demo_data.py](../../apps/appointments/management/commands/populate_demo_data.py)
- [models.py - Contacts](../../apps/contacts/models.py)
- [models.py - Services](../../apps/services/models.py)
- [models.py - Appointments](../../apps/appointments/models.py)
- [admin.py - Contacts](../../apps/contacts/admin.py)
- [admin.py - Services](../../apps/services/admin.py)
- [admin.py - Appointments](../../apps/appointments/admin.py)
