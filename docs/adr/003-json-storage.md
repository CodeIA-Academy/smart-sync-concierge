# ADR 003 - JSON Local para Storage en MVP

## Estado
✅ Aceptado

## Contexto

Smart-Sync Concierge necesita almacenar:

- Citas (appointments)
- Contactos
- Servicios
- Configuración de negocio
- Traces de decisiones de agentes

### Requisitos de Storage MVP

- **Simplicidad**: Configuración mínima, no infraestructura
- **Portabilidad**: Fácil backup y migración
- **Debugging**: Acceso directo a datos para desarrollo
- **Performance**: Suficiente para MVP (~1K-10K citas)

### Restricciones

- Presupuesto limitado (no infraestructura gestionada)
- Equipo pequeño (no DBA)
- MVP rápido (no tiempo para setup DB complejo)

## Decisión

**Usar archivos JSON locales para storage en MVP.**

```python
data/
├── appointments.json
├── contacts.json
├── services.json
├── config.json
└── decisions/
    └── decision_log.json
```

### Justificación

1. **Zero-config**: No requiere setup de base de datos
2. **Portabilidad**: Archivo = backup
3. **Debugging**: Abrir JSON = ver datos
4. **Velocidad**: Prototipado extremadamente rápido
5. **Suficiente**: Para MVP con <10K registros

## Consecuencias

### Positivas

- ✅ **Zero-config**: No setup, no migrations, no DBA
- ✅ **Portabilidad total**: Copia de archivo = backup completo
- ✅ **Debugging trivial**: Abrir JSON en editor = ver datos
- ✅ **Version control**: Schema en Git ( diffs claros)
- ✅ **Rapidez de desarrollo**: No ORM, no migrations, no SQL
- ✅ **Testing fácil**: Mock data = archivos JSON

### Negativas

- ❌ **Escalabilidad limitada**: ~10K registros antes de degradar
- ❌ **Concurrent writes**: Race conditions posibles
- ❌ **Query complejo**: Sin joins, agregaciones costosas
- ❌ **No ACID**: Riesgo de corrupción si crash durante write
- ❌ **Sin índices**: Búsquedas O(n) en lugar de O(log n)

### Riesgos

- **Pérdida de datos**: Crash durante write puede corromper JSON
- **Race conditions**: Dos requests simultáneos pueden sobrescribir
- **Escalabilidad**: Performance degrada con >10K registros
- **Migración dolorosa**: Migrar a DB después requiere ETL

### Mitigaciones

- **File locking**: `fcntl` o `filelock` para evitar race conditions
- **Atomic writes**: Write to temp + rename (operación atómica)
- **Auto-backup**: Backup antes de cada write
- **Monitor de tamaño**: Alerta si JSON >10MB (~10K citas)
- **Preparar migración**: Repositorio pattern ya lista para DB

## Alternativas Consideradas

### 1. PostgreSQL (Desde el inicio)

**Descripción**: Usar PostgreSQL como base de datos desde MVP.

**Por qué NO**:
- ❌ Overhead de setup (instalar, configurar, migraciones)
- ❌ Requiere DBA o conocimientos DB
- ❌ Más lento de prototipar (escribir migrations)
- ✅ Escalabilidad infinita
- ✅ ACID, joins, índices

**Decisión**: Migrar a PostgreSQL cuando se justifique (v0.3.0+)

### 2. SQLite

**Descripción**: Base de datos SQL embebida en archivo.

**Por qué NO**:
- ✅ ACID, SQL, índices
- ✅ Mejor que JSON puro
- ❌ Requiere ORM (Django ORM)
- ❌ Migrations necesarias
- ❌ Menos portable (binario vs texto)

**Decisión**: JSON más simple para MVP, SQLite como alternativa si JSON no funciona

### 3. MongoDB

**Descripción**: Base de datos NoSQL documental.

**Por qué NO**:
- ✅ Esquema flexible
- ✅ Escalable
- ❌ Requiere infraestructura (Docker o managed)
- ❌ Coste (Atlas o self-hosted)
- ❌ Overhead para MVP

### 4 Firebase Firestore

**Descripción**: Base de datos managed NoSQL de Google.

**Por qué NO**:
- ✅ Managed, no infra
- ✅ Real-time
- ❌ Vendor lock-in
- ❌ Coste (aunque tiene tier gratuito)
- ❌ Latencia (depende de ubicación)

## Plan de Migración a Base de Datos

### Cuándo Migrar

Indicadores para migrar de JSON a PostgreSQL:

| Métrica | Umbral | Acción |
|---------|--------|--------|
| Citas almacenadas | >10K | Planificar migración |
| Tamaño appointments.json | >10MB | Migrar inmediatamente |
| Latencia p95 API | >500ms | Optimizar o migrar |
| Race conditions detectadas | >1/semana | Migrar urgentemente |

### Estrategia de Migración

```python
# Abstracción para migración transparente
class AppointmentRepository(ABC):
    @abstractmethod
    async def save(self, appointment: Appointment) -> str:
        pass

    @abstractmethod
    async def get(self, id: str) -> Optional[Appointment]:
        pass

class JSONAppointmentRepository(AppointmentRepository):
    """Implementación JSON (MVP)."""
    async def save(self, appointment: Appointment) -> str:
        # Guardar en appointments.json
        pass

class PostgresAppointmentRepository(AppointmentRepository):
    """Implementación PostgreSQL (v0.3.0+)."""
    async def save(self, appointment: Appointment) -> str:
        # INSERT INTO appointments ...
        pass

# Configuración dinámica
repository = JSONAppointmentRepository() if settings.USE_JSON_STORAGE else PostgresAppointmentRepository()
```

### Timeline Estimado

```
v0.1.0 (MVP)
└── JSON local

v0.2.0
└── JSON local + preparación migración
    ├── Escribir ETL scripts
    ├── Crear schema PostgreSQL
    └── Tests de migración

v0.3.0
├── JSON local (existente)
└── PostgreSQL (nuevo, modo shadow)
        └── Dual-write (JSON + Postgres)

v0.4.0
├── PostgreSQL (principal)
└── JSON (backup, read-only)

v0.5.0
└── PostgreSQL (únicamente)
    └── JSON eliminado
```

### Script de Migración

```python
# scripts/migrate_json_to_postgres.py
async def migrate_json_to_postgres():
    """Migra datos de JSON a PostgreSQL."""
    # 1. Leer JSON
    json_repo = JSONAppointmentRepository()
    appointments = await json_repo.list_all()

    # 2. Escribir a PostgreSQL
    pg_repo = PostgresAppointmentRepository()
    for apt in appointments:
        await pg_repo.save(apt)

    # 3. Verificar
    json_count = len(appointments)
    pg_count = await pg_repo.count()
    assert json_count == pg_count, f"Mismatch: {json_count} != {pg_count}"

    # 4. Backup JSON
    shutil.copy("data/appointments.json", "data/backups/appointments_pre_migration.json")
```

## Implementación

### Estado
- ✅ Propuesto: 2026-01-22
- ✅ Aceptado: 2026-01-22
- ⏳ En Progreso: [PR-51](https://github.com/...)

### Componentes

| Componente | Estado |
|------------|--------|
| JSONRepository base | ✅ Completado |
| AppointmentStore | ✅ Completado |
| ContactStore | ✅ Completado |
| File locking | ⏳ En Progreso |
| Atomic writes | ⏳ En Progreso |
| Auto-backup | ⏸ Pendiente |
| Monitor tamaño | ⏸ Pendiente |

### Configuración

```python
# config/settings/storage.py
STORAGE_TYPE = "json"  # "json" | "postgres"

JSON_STORAGE_DIR = BASE_DIR / "data"
JSON_BACKUP_ENABLED = True
JSON_BACKUP_DIR = BASE_DIR / "data" / "backups"
JSON_AUTO_BACKUP_BEFORE_WRITE = True
JSON_MAX_FILE_SIZE_MB = 10  # Alerta si >10MB

POSTGRES_HOST = env("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = env("POSTGRES_PORT", default=5432)
POSTGRES_DB = env("POSTGRES_DB", default="smart_sync")
```

### Patrones de Uso

```python
# Guardar con atomic write
async def save_appointment(appointment: Appointment):
    # 1. Backup si está habilitado
    if settings.JSON_AUTO_BACKUP_BEFORE_WRITE:
        await backup_json_file("appointments.json")

    # 2. Write to temp
    temp_path = settings.JSON_STORAGE_DIR / "appointments.json.tmp"
    async with aiofiles.open(temp_path, "w") as f:
        await f.write(json.dumps(data))

    # 3. Atomic rename
    final_path = settings.JSON_STORAGE_DIR / "appointments.json"
    temp_path.rename(final_path)  # Atómico en POSIX
```

### Referencias

- [Esquemas JSON](../contracts/schemas/)
- [Repository Pattern](../architecture/patterns.md#repository)
- [Plan de Migración](../operations/migration-plan.md)

## Supersedes

Supersede: Ninguno

## Superseded By

Ninguno (activo en MVP)

---

**Autor**: Architecture Team
**Fecha**: Enero 22, 2026
**Revisado por**: Tech Lead
**Aprobado por**: CTO (con migración planificada a v0.3.0)
