# Deployment a Producción - Integración n8n

Guía para desplegar Smart-Sync Concierge con integración n8n en producción.

**Versión:** 0.1.0
**Fecha:** 2026-02-10
**Enfoque:** Production-first (sin ngrok)

## Arquitectura de Producción

```
┌──────────────────────────────────┐
│    n8n Cloud                     │
│  (n8n.codeia.dev)               │
└────────────────┬─────────────────┘
                 │
                 │ HTTPS
                 ↓
┌──────────────────────────────────┐
│  Smart-Sync API (Producción)     │
│  - Railway / Render / AWS        │
│  - Dominio público               │
│  - PostgreSQL (Neon/AWS RDS)     │
│  - Puerto 8000 (interno)         │
└──────────────────────────────────┘
```

## Opción 1: Railway.app (Recomendado)

Railway es la opción más simple y rápida.

### Paso 1: Preparar Repositorio

```bash
# Asegurar que los cambios están en git
cd /Volumes/Externo/Proyectos/CodeIA\ Academy\ Projects/Sesion\ 15/Smart-Sync-Concierge

git status  # Verificar que todo está limpio

# Si hay cambios sin commit:
git add .
git commit -m "Preparar para deployment a Railway"

# Push a remoto
git push origin main
```

### Paso 2: Crear Proyecto en Railway

1. Ir a https://railway.app
2. Sign up / Login
3. Click "Create new Project"
4. Seleccionar "Deploy from GitHub"
5. Conectar repositorio de Smart-Sync-Concierge
6. Railway detectará automáticamente que es Django

### Paso 3: Configurar Variables de Entorno

En Railway dashboard:
1. Project Settings → Environment
2. Agregar variables:

```bash
DEBUG=False
SECRET_KEY=<generar_uno_nuevo_o_usar_existente>
ALLOWED_HOSTS=api.smartsync.dev,yourdomain.railway.app
DATABASE_URL=postgresql://...  # Railway genera automáticamente

# N8N Integration
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DJANGO_API_URL=https://api.smartsync.dev  # Tu dominio en Railway
DJANGO_API_TOKEN=a75267088f61b319d75ffef873ac095e93558a37
WEBHOOK_SECRET=<generar_secreto_aleatorio>
WEBHOOK_VERIFY_SIGNATURE=True  # En producción
```

### Paso 4: Configurar Dominio Personalizado

1. Railway → Project Settings → Domains
2. Agregar dominio: `api.smartsync.dev`
3. Apuntar DNS de tu dominio a Railway

### Paso 5: Deploy

Railway hace deploy automático cuando haces push a main.

```bash
# En tu máquina local:
git push origin main

# Railway verá el cambio y hará deploy automático
# Puedes ver logs en: railway.app dashboard
```

## Opción 2: Render.com

Alternativa a Railway.

### Paso 1: Conectar Repositorio

1. Ir a https://render.com
2. Sign up / Login
3. Click "New +"  → "Web Service"
4. Conectar repositorio GitHub

### Paso 2: Configuración

1. **Build Command:** `pip install -r requirements.txt && python manage.py migrate`
2. **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
3. **Environment:** Select "Python 3.9"

### Paso 3: Environment Variables

Agregar en Render:

```bash
DEBUG=False
SECRET_KEY=...
DATABASE_URL=postgresql://...  # Usar PostgreSQL en Render
ALLOWED_HOSTS=api.smartsync.dev

# N8N
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=...
DJANGO_API_URL=https://api.smartsync.dev
DJANGO_API_TOKEN=a75267088f61b319d75ffef873ac095e93558a37
WEBHOOK_VERIFY_SIGNATURE=True
```

### Paso 4: Deploy

```bash
git push origin main
# Render hace deploy automático
```

## Opción 3: AWS (EC2 + RDS)

Para máximo control.

### Paso 1: Crear Instancia EC2

```bash
# 1. AWS Console → EC2 → Launch Instance
# 2. Ubuntu 22.04 LTS (t3.small mínimo)
# 3. Configure security group:
#    - Port 80 (HTTP)
#    - Port 443 (HTTPS)
#    - Port 22 (SSH)
# 4. Create and download key pair
```

### Paso 2: Conectar y Preparar

```bash
# Desde tu máquina
ssh -i your-key.pem ubuntu@your-ec2-ip

# En la instancia EC2:
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.9 python3-pip postgresql-client nginx

# Clonar repositorio
git clone https://github.com/youruser/Smart-Sync-Concierge.git
cd Smart-Sync-Concierge

# Instalar dependencias
pip3 install -r requirements.txt
```

### Paso 3: Configurar PostgreSQL (RDS)

```bash
# En AWS Console:
# RDS → Create Database → PostgreSQL
# Configurar security group para que EC2 pueda conectar

# Variable en .env:
DATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/smartsync
```

### Paso 4: Configurar Nginx

```bash
# /etc/nginx/sites-available/smartsync
server {
    listen 80;
    server_name api.smartsync.dev;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Paso 5: Ejecutar Django

```bash
# En instancia EC2:
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4
```

## Paso Final: Configurar n8n para Producción

Una vez que tengas tu dominio público:

### 1. Actualizar Variable en n8n

No necesitas hacer nada si ya configuraste en `.env` correctamente.

### 2. Ejecutar Setup en Producción

```bash
# SSH a tu servidor en producción
ssh user@api.smartsync.dev

# Ejecutar setup
python manage.py setup_n8n_workflow \
  --django-url https://api.smartsync.dev \
  --activate
```

### 3. Verificar Webhook

```bash
# Desde tu máquina local
curl -X POST https://n8n.codeia.dev/webhook/appointments/process \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "cita mañana 10am con Dr. Pérez",
    "user_timezone": "America/Mexico_City"
  }'
```

## Variables de Entorno - Producción

```bash
# Security
DEBUG=False
SECRET_KEY=<generar_nuevo>
ALLOWED_HOSTS=api.smartsync.dev,yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@rds.amazonaws.com:5432/smartsync

# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production

# N8N Integration
N8N_API_URL=https://n8n.codeia.dev
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DJANGO_API_URL=https://api.smartsync.dev
DJANGO_API_TOKEN=a75267088f61b319d75ffef873ac095e93558a37
WEBHOOK_SECRET=<generar_secreto_aleatorio>
WEBHOOK_VERIFY_SIGNATURE=True

# SSL (Railway/Render/AWS)
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Monitoreo en Producción

### Railway

```
https://railway.app → Project → Deployments → Logs
```

### Render

```
https://render.com → Dashboard → Logs
```

### AWS CloudWatch

```
AWS Console → CloudWatch → Logs
```

### Ver Traces

```bash
curl https://api.smartsync.dev/api/v1/traces/ \
  -H "Authorization: Token a75267088f61b319d75ffef873ac095e93558a37" | jq
```

## Checklist de Deployment

- [ ] Variables de entorno configuradas
- [ ] Database (PostgreSQL) configurada
- [ ] SECRET_KEY generado nuevo
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] SSL/HTTPS activo
- [ ] Dominio público funcional
- [ ] Django migrations ejecutadas
- [ ] n8n API key configurada
- [ ] Django token disponible
- [ ] Setup n8n ejecutado
- [ ] Webhook testeado
- [ ] Logs monitoreados

## Troubleshooting

### Error: "Connection refused" en n8n

```bash
# Verificar que Django está respondiendo
curl https://api.smartsync.dev/api/v1/health/

# Ver logs del servidor
ssh user@server
tail -f /var/log/django.log
```

### Error: "Database connection error"

```bash
# Verificar DATABASE_URL
# Asegurar que security group permite conexión
# Testear conexión a RDS:
psql -h your-rds-endpoint -U user -d smartsync
```

### Error: "Invalid token"

```bash
# Verificar DJANGO_API_TOKEN en producción
# Regenerar si es necesario:
python manage.py drf_create_token admin
```

## Próximas Mejoras

- [ ] SSL certificate (Let's Encrypt)
- [ ] Auto-backup de base de datos
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring y alertas
- [ ] Rate limiting por IP
- [ ] Validación HMAC de webhooks

## Referencias

- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Django Deployment Guide](https://docs.djangoproject.com/en/4.2/howto/deployment/)
