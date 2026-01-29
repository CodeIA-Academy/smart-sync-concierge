# Configuración Correcta de Smart-Sync Concierge en EasyPanel

## Problema Actual

La aplicación está configurada en EasyPanel pero no responde. Las causas son:

1. **HTTP sin HTTPS**: Django está intentando hacer redirect a HTTPS pero EasyPanel está configurado solo con HTTP
2. **SECRET_KEY no configurado**: Necesita ser generada correctamente

## Solución

### Paso 1: Habilitar HTTPS en EasyPanel

En el panel de EasyPanel, en **Actualizar dominio**:

1. Ve a la sección **SSL**
2. Selecciona un certificado SSL (EasyPanel debería tener Let's Encrypt disponible)
3. Cambia el protocolo de **HTTP** a **HTTPS**
4. Guarda los cambios

**Nota**: EasyPanel maneja automáticamente el certificado SSL, no necesitas hacer nada más.

### Paso 2: Variables de Entorno Correctas

En el `.env` de EasyPanel, asegúrate que esté configurado así:

```bash
# Core
SECRET_KEY=<tu-clave-segura-generada>
DEBUG=False

# Domain & CORS
ALLOWED_HOSTS=smartsync.codeia.dev
CORS_ALLOWED_ORIGINS=https://smartsync.codeia.dev

# Database (ya configurada)
DATABASE_URL=postgresql://neondb_owner:npg_pNMxGiXL0CZ5@ep-nameless-recipe-aga8q8eu-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Qwen (opcional, sin esto la app sigue funcionando)
QWEN_API_KEY=<tu-api-key-cuando-la-tengas>

# Security
SECURE_SSL_REDIRECT=True

# Admin
CREATE_SUPERUSER=true
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@smartsync.dev
DJANGO_SUPERUSER_PASSWORD=<tu-contraseña-fuerte>
```

### Paso 3: Generar SECRET_KEY

Si aún no tienes una SECRET_KEY, ejecútala localmente:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y pégalo en la variable `SECRET_KEY` en EasyPanel.

### Paso 4: Reiniciar el Servicio

En EasyPanel:
1. Ve al servicio "Smart-Sync Concierge"
2. Haz clic en **Reiniciar**
3. Espera a que muestre "Running"
4. Revisa los logs para asegurar que no haya errores

### Paso 5: Verificar que Funciona

```bash
# Health check
curl https://smartsync.codeia.dev:9000/health/

# Debería responder algo como:
# {"status": "healthy", "version": "0.1.0", "timestamp": "2026-01-29T..."}

# API
curl https://smartsync.codeia.dev:9000/api/v1/appointments/

# Admin
# Abre en navegador: https://smartsync.codeia.dev:9000/admin/
```

## Cambios en el Código

Se han realizado estos cambios para soportar mejor EasyPanel:

1. **production.py**:
   - `SECRET_KEY` se genera automáticamente si no está configurada (para desarrollo)
   - `SECURE_SSL_REDIRECT` ahora es configurable via `SECURE_SSL_REDIRECT=True`
   - Se agregó soporte para proxy headers: `SECURE_PROXY_SSL_HEADER`

Esto permite que Django funcione correctamente detrás del proxy de EasyPanel.

## Si Aún No Funciona

1. **Revisa los logs** en EasyPanel - busca errores específicos
2. **Verifica DATABASE_URL** - comprueba que la conexión a PostgreSQL sea válida
3. **Reinicia nuevamente** - a veces es necesario esperar a que el contenedor se reinicie completamente
4. **Revisa ALLOWED_HOSTS** - asegúrate que incluya `smartsync.codeia.dev`

## Próximos Pasos

Una vez que todo esté funcionando:

1. Obtén tu API key de Qwen y configúrala
2. Accede al admin en `https://smartsync.codeia.dev:9000/admin/`
3. Comienza a usar la API

---
**Última actualización**: 2026-01-29
