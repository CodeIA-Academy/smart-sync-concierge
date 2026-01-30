# Configuración Local - Smart-Sync Concierge

## Requisitos Previos

- Python 3.9+
- PostgreSQL (Neon account para desarrollo)
- git
- curl (para probar la API)

## Paso 1: Clonar el Repositorio

```bash
cd /ruta/del/proyecto
git clone <url-del-repositorio>
cd Smart-Sync-Concierge
```

## Paso 2: Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# o venv\Scripts\activate  # Windows
```

## Paso 3: Instalar Dependencias

```bash
pip3 install -r requirements.txt
```

## Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DEBUG=True
SECRET_KEY=your-secret-key-for-development
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://usuario:contraseña@host/basedatos?sslmode=require&channel_binding=require
DJANGO_SETTINGS_MODULE=config.settings.local
```

**Obtener DATABASE_URL de Neon**:
1. Ir a https://console.neon.tech
2. Seleccionar tu proyecto
3. Copiar la connection string PostgreSQL
4. Usarla en DATABASE_URL

## Paso 5: Ejecutar Migraciones

```bash
python3 manage.py migrate
```

Esto crea las tablas en PostgreSQL.

## Paso 6: Crear Superuser (Admin)

```bash
python3 manage.py createsuperuser
```

O resetea el admin existente:

```bash
python3 manage.py shell
```

En el shell de Django:

```python
from django.contrib.auth.models import User
admin = User.objects.get(username='admin')
admin.set_password('tu_nueva_contraseña')
admin.save()
exit()
```

## Paso 7: Poblar Datos de Demostración (Opcional)

```bash
python3 manage.py populate_demo_data
```

Esto crea automáticamente:
- 3 contactos (doctores)
- 4 servicios (tipos de consulta)
- 3 citas de ejemplo

## Paso 8: Iniciar Servidor de Desarrollo

```bash
python3 manage.py runserver 9001
```

El servidor estará disponible en `http://localhost:9001`

## Verificar que Todo Funciona

### 1. Health Check

```bash
curl http://localhost:9001/api/v1/health/ | jq .
```

**Respuesta esperada**:

```json
{
  "status": "healthy",
  "message": "Smart-Sync Concierge API is running",
  "version": "0.1.0",
  "timestamp": null
}
```

### 2. Obtener Token de Autenticación

```bash
curl -X POST http://localhost:9001/api/v1/token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tu_contraseña"}'
```

**Respuesta esperada**:

```json
{
  "status": "success",
  "token": "tu_token_aqui",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@smartsync.dev"
  }
}
```

Guarda el `token` para los siguientes requests.

### 3. Listar Contactos

```bash
TOKEN="tu_token_aqui"
curl -s http://localhost:9001/api/v1/contacts/ \
  -H "Authorization: Token $TOKEN" | jq .
```

**Respuesta esperada**:

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "dr_juan_perez",
      "nombre": "Dr. Juan Pérez",
      "tipo": "prestador",
      "titulo": "Médico General",
      "email": "juan.perez@hospital.com",
      "telefono": "+34912345678",
      "especialidades": ["consulta_general", "pediatria"],
      "activo": true
    }
    // ... más contactos
  ]
}
```

### 4. Listar Servicios

```bash
curl -s http://localhost:9001/api/v1/services/ \
  -H "Authorization: Token $TOKEN" | jq .
```

### 5. Listar Citas

```bash
curl -s http://localhost:9001/api/v1/appointments/ \
  -H "Authorization: Token $TOKEN" | jq .
```

## Acceder al Admin Django

1. Abre http://localhost:9001/admin/
2. Inicia sesión con username `admin` y tu contraseña
3. Aquí puedes:
   - Ver/editar Contactos
   - Ver/editar Servicios
   - Ver/editar Citas

## Solución de Problemas

### Error: "No such table"

```
Solución: Ejecutar migraciones
python3 manage.py migrate
```

### Error: "Credenciales inválidas" en token

```
Solución: Resetear contraseña del admin
python3 manage.py shell
```

```python
from django.contrib.auth.models import User
admin = User.objects.get(username='admin')
admin.set_password('nueva_contraseña')
admin.save()
```

### Error: "Could not connect to database"

```
Verificar:
1. DATABASE_URL en .env es correcto
2. La base de datos Neon existe
3. Las credenciales de Neon son correctas
4. La conexión SSL está habilitada
```

### El servidor no inicia

```
Verificar:
1. El puerto 9001 no está en uso
   lsof -i :9001  # macOS/Linux
   netstat -ano | findstr :9001  # Windows

2. Matar el proceso si está en uso
   kill -9 <PID>  # macOS/Linux

3. Usar otro puerto
   python3 manage.py runserver 8080
```

## Base de Datos - Neon

### Conectarse directamente (opcional)

```bash
psql postgresql://usuario:contraseña@host/basedatos
```

### Ver esquema

```sql
\dt  -- Ver todas las tablas
SELECT * FROM contacts_contact;  -- Ver contactos
SELECT * FROM services_service;  -- Ver servicios
SELECT * FROM appointments_appointment;  -- Ver citas
```

## Documentación Adicional

- [Database Migration](./DATABASE_MIGRATION.md) - Detalles de la migración a PostgreSQL
- [API Endpoints](./ENDPOINTS_SUMMARY.md) - Resumen de endpoints
- README principal en la raíz del proyecto

## Próximos Pasos

1. Explorar la API usando Postman o curl
2. Crear nuevos contactos/servicios/citas
3. Revisar el código en `apps/`
4. Contribuir al desarrollo
