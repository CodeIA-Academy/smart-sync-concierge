# 🚀 Quick Start - Postman Testing

**30 segundos para empezar a testear**

---

## 1️⃣ Terminal - Iniciar Server

```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge

python3 manage.py runserver 0.0.0.0:9000
```

**Esperado:**
```
Starting development server at http://0.0.0.0:9000/
Quit the server with CONTROL-C.
```

---

## 2️⃣ Postman - Importar Colección

1. Abre **Postman**
2. Click en **Import** (arriba a la izquierda)
3. Selecciona **Upload Files**
4. Elige: `docs/POSTMAN_COLLECTION.json`
5. Click **Import**

✓ ¡Colección importada!

---

## 3️⃣ Testear - 3 Requests Simples

### Request 1: Health Check
```
GET http://localhost:9000/api/v1/health/
```

Postman: busca "Health Check" en la colección y click Send

✓ Debería ver: `"status": "healthy"`

---

### Request 2: Create Appointment

```
POST http://localhost:9000/api/v1/appointments/
```

Body:
```json
{
  "prompt": "cita mañana 10am con Dr. García",
  "user_timezone": "America/Mexico_City"
}
```

Postman: busca "Create Appointment" y click Send

✓ Respuesta incluye `trace_id`

---

### Request 3: Ver Trace

```
GET http://localhost:9000/api/v1/traces/{trace_id}/
```

Reemplaza `{trace_id}` con el valor de la respuesta anterior

Postman: busca "Get Specific Trace" y reemplaza {{trace_id}}

✓ Ves todas las decisiones de los 6 agentes

---

## 4️⃣ Más Detalles

Para guía completa, ver: **[TESTING_WITH_POSTMAN.md](TESTING_WITH_POSTMAN.md)**

- 10 secciones detalladas
- Todos los endpoints
- Troubleshooting
- Test cases completos

---

## 5️⃣ URLs Rápidas

```
Health:        http://localhost:9000/api/v1/health/
API Root:      http://localhost:9000/api/v1/
Appointments:  http://localhost:9000/api/v1/appointments/
Traces:        http://localhost:9000/api/v1/traces/
Contacts:      http://localhost:9000/api/v1/contacts/
Services:      http://localhost:9000/api/v1/services/
```

---

## 🟢 Listo!

Si todo funciona, puedes:
- Testear todos los endpoints
- Ver las decisiones de los 6 agentes
- Análizar performance metrics
- Filtrar traces por usuario o status

**Ver documentación completa en [TESTING_WITH_POSTMAN.md](TESTING_WITH_POSTMAN.md)**
