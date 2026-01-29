# Checklist de Verificación - Despliegue en EasyPanel

## Pre-Despliegue ✓

- [ ] Clonar repositorio en servidor
- [ ] Crear variables de entorno en EasyPanel
- [ ] Generar SECRET_KEY segura
- [ ] Configurar DATABASE_URL de PostgreSQL
- [ ] Configurar ALLOWED_HOSTS correctamente

## Configuración de EasyPanel ✓

### Dominio
- [ ] Host: `smartsync.codeia.dev`
- [ ] Puerto: `9000`
- [ ] Protocolo: **HTTPS** (no HTTP)
- [ ] Ruta: `/`

### SSL
- [ ] SSL habilitado
- [ ] Certificado válido (Let's Encrypt de EasyPanel)

### Variables de Entorno
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY=<clave-generada>`
- [ ] `ALLOWED_HOSTS=smartsync.codeia.dev`
- [ ] `CORS_ALLOWED_ORIGINS=https://smartsync.codeia.dev`
- [ ] `DATABASE_URL=<url-postgresql>`
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `CREATE_SUPERUSER=true`
- [ ] `DJANGO_SUPERUSER_USERNAME=admin`
- [ ] `DJANGO_SUPERUSER_EMAIL=admin@smartsync.dev`
- [ ] `DJANGO_SUPERUSER_PASSWORD=<contraseña-fuerte>`

## Post-Despliegue ✓

### Health Checks Básicos

```bash
# 1. Verificar health endpoint
curl -v https://smartsync.codeia.dev:9000/health/

# Respuesta esperada (200 OK):
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "timestamp": "2026-01-29T..."
# }
```

- [ ] Health check responde 200
- [ ] Status es "healthy"
- [ ] Timestamp es actual

### API Endpoints

```bash
# 2. Verificar API principal
curl https://smartsync.codeia.dev:9000/api/v1/appointments/

# Debería responder con JSON (lista vacía o con datos)
```

- [ ] Appointments endpoint responde 200
- [ ] Respuesta es JSON válido

### Admin Panel

```bash
# 3. Acceder a admin
# Abre en navegador: https://smartsync.codeia.dev:9000/admin/
# Inicia sesión con:
# - Usuario: admin
# - Contraseña: <tu-contraseña-configurada>
```

- [ ] Admin carga correctamente
- [ ] Puedo iniciar sesión
- [ ] Veo el panel administrativo

### Logs

En EasyPanel:
- [ ] Revisa los logs del servicio
- [ ] No hay errores críticos (ERROR, CRITICAL)
- [ ] Ves mensajes de startup exitosos

## Troubleshooting

Si algo falla:

1. **Error de conexión (timeout)**
   - Verifica que HTTPS esté habilitado en EasyPanel
   - Confirma que el servicio está "Running"
   - Revisa logs por errores de startup

2. **Error 500 en health check**
   - Revisa logs por errores de Django
   - Verifica que DATABASE_URL sea válido
   - Confirma que SECRET_KEY esté configurada

3. **Error 403 en admin**
   - Verifica ALLOWED_HOSTS
   - Comprueba que CORS esté configurado correctamente
   - Reinicia el servicio después de cambios

4. **Error de base de datos**
   - Verifica que PostgreSQL esté accessible
   - Comprueba DATABASE_URL y credenciales
   - Asegúrate que la base de datos existe

## Funcionalidad Completa

Una vez pasados todos los checks:

- [ ] Puedo crear citas via API
- [ ] Puedo listar citas
- [ ] Puedo actualizar citas
- [ ] Puedo eliminar citas
- [ ] El admin muestra los datos correctamente

## Performance & Seguridad

- [ ] HTTPS funciona sin errores SSL
- [ ] Certificado SSL es válido
- [ ] No hay warnings en navegador
- [ ] Response time es razonable (<500ms)

---

**Estado**: Listo para verificación
**Fecha**: 2026-01-29
