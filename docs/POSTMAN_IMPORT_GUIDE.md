# 📮 Guía de Importación - Postman Collection

**Versión:** 0.2.0
**Fecha:** 28 de Enero, 2026
**Estado:** ✅ Lista para importar

---

## 🚀 IMPORTAR EN 3 PASOS

### Paso 1: Descargar / Ubicar el archivo

El archivo `POSTMAN_COLLECTION.json` está en:
```
docs/POSTMAN_COLLECTION.json
```

**Ubicación completa:**
```
/Volumes/Externo/Proyectos/CodeIA Academy Projects/Sesion 15/Smart-Sync-Concierge/docs/POSTMAN_COLLECTION.json
```

### Paso 2: Abrir Postman e Importar

1. **Abre Postman** (descárgalo desde https://www.postman.com/downloads/ si no lo tienes)

2. **Haz click en "Import"** (esquina superior izquierda)
   ```
   File → Import
   O presiona: Ctrl+K (Windows) / Cmd+K (Mac)
   ```

3. **Selecciona "Upload Files"** en el modal que abre

4. **Busca y selecciona** el archivo:
   ```
   docs/POSTMAN_COLLECTION.json
   ```

5. **Haz click en "Import"**

**Espera:** La colección debería importarse en ~2 segundos.

### Paso 3: Verificar Importación

✅ **Debería ver:**
- Una colección llamada **"Smart-Sync Concierge API v0.2.0"**
- **5 carpetas:**
  - ✓ Quick Start - Run These First
  - ✓ Health & Status
  - ✓ Appointments - AI Pipeline
  - ✓ Traces - Observability
  - ✓ Contacts
  - ✓ Services

- **Variables globales:**
  - `base_url` = `http://localhost:9000`
  - `trace_id` = (vacío, se auto-completa)
  - `appointment_id` = (vacío, se auto-completa)

---

## ✅ VERIFICAR QUE FUNCIONA

### 1. Asegurar que Django está corriendo

En una terminal, ejecuta:
```bash
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge

python3 manage.py runserver 0.0.0.0:9000
```

**Espera:** Debería ver:
```
Starting development server at http://0.0.0.0:9000/
```

### 2. En Postman, ir a la carpeta "Quick Start"

En el panel izquierdo, expande la colección y abre la carpeta **"Quick Start - Run These First"**

### 3. Ejecutar "1. Health Check"

1. Haz click en **"1. Health Check"**
2. Presiona **"Send"** (botón azul a la derecha)

**Esperado:** Debería ver respuesta `200 OK` con:
```json
{
  "status": "healthy",
  "message": "Smart-Sync Concierge API is running",
  "version": "0.2.0"
}
```

✅ **Si ves esto, la colección funciona correctamente.**

---

## 🎯 PRÓXIMOS PASOS

### Quick Start Flow (3 requests)

Ejecuta en orden:

1. **"1. Health Check"** - Verifica servidor
2. **"2. Create Appointment (Simple)"** - Crea cita con IA
   - **Resultado:** trace_id se auto-guarda
3. **"3. View Trace Details"** - Ve todas las decisiones de agentes
   - **Nota:** trace_id se auto-completa del paso anterior

### Otros Tests

En la carpeta **"Appointments - AI Pipeline"**:
- **Create - Success Case** - Cita que debería funcionar
- **Create - Conflict Case** - Cita con conflicto horario
- **Create - Ambiguous Case** - Cita incompleta (genera error)
- **List Appointments** - Ver todas las citas

En la carpeta **"Traces - Observability"**:
- **List All Traces** - Ver todos los traces
- **Get Specific Trace** - Ver detalle de un trace
- **Filter by Status** - Filtrar por success/error/conflict
- **Filter by User** - Filtrar por usuario
- **Get Agent Decisions** - Ver decisiones de cada agente
- **Get Performance Metrics** - Ver cuánto tardó cada agente

---

## 🔧 TROUBLESHOOTING

### ❌ Problema: "Connection refused" o "Server not running"

**Solución:**
```bash
# Verificar que Django está corriendo
ps aux | grep "manage.py runserver"

# Si no aparece, ejecutar:
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge
python3 manage.py runserver 0.0.0.0:9000
```

### ❌ Problema: "Cannot find module django"

**Solución:**
```bash
# Instalar dependencias
pip install -r requirements.txt

# O usar python3
python3 -m pip install -r requirements.txt
```

### ❌ Problema: El JSON se ve "vacío" en Postman

**Solución:**
1. Cierra Postman completamente
2. Borra el archivo importado (en Postman, click derecho → Delete)
3. Vuelve a importar desde `docs/POSTMAN_COLLECTION.json`
4. Si persiste, verifica que el archivo sea válido:
   ```bash
   python3 -m json.tool docs/POSTMAN_COLLECTION.json
   ```
   Debería salir sin errores.

### ❌ Problema: Las variables no se auto-guardan

**Nota:** Las variables se guardan como "Globals" en Postman.

Para verificar:
1. En Postman, haz click en el ícono de ojo (arriba a la derecha)
2. Selecciona "Globals"
3. Deberías ver las variables listadas

Si no aparecen:
1. Haz click en "Create"
2. Crea una variable llamada `base_url` con valor `http://localhost:9000`
3. Crea otra llamada `trace_id` (vacía)
4. Crea otra llamada `appointment_id` (vacía)

---

## 📊 ESTRUCTURA DE LA COLECCIÓN

```
Smart-Sync Concierge API v0.2.0/
├── Variables Globales:
│   ├── base_url = http://localhost:9000
│   ├── trace_id = (auto-se rellena)
│   └── appointment_id = (auto-se rellena)
│
├── Quick Start - Run These First/
│   ├── 1. Health Check
│   ├── 2. Create Appointment (Simple)
│   └── 3. View Trace Details
│
├── Health & Status/
│   ├── Health Check
│   └── API Root
│
├── Appointments - AI Pipeline/
│   ├── Create - Success Case
│   ├── Create - Conflict Case
│   ├── Create - Ambiguous Case
│   └── List Appointments
│
├── Traces - Observability/
│   ├── List All Traces
│   ├── Get Specific Trace
│   ├── Filter by Status (success)
│   ├── Filter by Status (error)
│   ├── Filter by Status (conflict)
│   ├── Filter by User
│   ├── Get Agent Decisions
│   └── Get Performance Metrics
│
├── Contacts/
│   ├── List Contacts
│   └── Create Contact
│
└── Services/
    └── List Services
```

---

## 📝 NOTAS IMPORTANTES

### Variables Auto-populables
Los siguientes requests tienen **test scripts** que guardan automáticamente valores en las variables globales:

- **"2. Create Appointment (Simple)"** → Guarda `trace_id`
- **"Create - Success Case"** → Guarda `trace_id`
- **"Create - Conflict Case"** → Guarda `trace_id`

**Esto significa que después de ejecutar cualquiera de estos, el `trace_id` se auto-completa en los siguientes requests.**

### URLs con Variables
Todos los URLs usan variables, por ejemplo:
```
{{base_url}}/api/v1/health/
{{base_url}}/api/v1/traces/{{trace_id}}/
```

**Si cambias el puerto o servidor, solo necesitas cambiar la variable `base_url` una vez.**

### Respuestas de Ejemplo
Cada request incluye una descripción que explica:
- Qué hace
- Qué respuesta esperar
- Código HTTP esperado

---

## 🎓 EJEMPLOS DE USO

### Ejemplo 1: Crear una cita exitosa

```
1. Click en "Quick Start" → "1. Health Check"
2. Click "Send"
3. Ver respuesta 200 ✓

4. Click en "Quick Start" → "2. Create Appointment (Simple)"
5. Click "Send"
6. Ver respuesta 201 o 409
7. Ver en Postman Console: "✓ Trace ID saved: trace_xxx"

8. Click en "Quick Start" → "3. View Trace Details"
9. Click "Send"
10. Ver todas las decisiones de los 6 agentes
```

### Ejemplo 2: Ver todas las citas creadas

```
1. Ir a "Appointments - AI Pipeline" → "List Appointments"
2. Click "Send"
3. Ver todas las citas como JSON array
```

### Ejemplo 3: Filtrar traces por usuario

```
1. Ir a "Traces - Observability" → "Filter by User"
2. Cambiar user_id en el URL (si necesitas)
3. Click "Send"
4. Ver traces solo de ese usuario
```

---

## 🆘 ¿NECESITAS AYUDA?

1. **Ver documentación completa:** [TESTING_WITH_POSTMAN.md](TESTING_WITH_POSTMAN.md)
2. **Ver quick start:** [QUICK_START_POSTMAN.md](QUICK_START_POSTMAN.md)
3. **Ver índice de documentos:** [INDEX.md](INDEX.md)

---

**Último actualizado:** 28 de Enero, 2026
**Versión:** 0.2.0
**Status:** ✅ Listo para usar
