# Guía de Despliegue - Smart-Sync Concierge

## Requisitos del Sistema

### Mínimos
- Python 3.11+
- 500MB de almacenamiento
- 1GB RAM
- 1 vCPU

### Recomendados
- Python 3.12+
- 2GB de almacenamiento (para crecimiento)
- 2GB RAM
- 2 vCPU

## Instalación Local

### 1. Clonar el Repositorio

```bash
git clone https://github.com/your-org/smart-sync-concierge.git
cd smart-sync-concierge
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

Variables requeridas:

```bash
SECRET_KEY=genera-una-clave-secreta-segura
DEBUG=True
QWEN_API_KEY=tu-api-key-de-qwen
TIMEZONE=America/Mexico_City
```

### 5. Inicializar Datos

```bash
# Crear archivos JSON iniciales
python manage.py init_data
```

### 6. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

La API estará disponible en `http://localhost:8000`

El panel de admin en `http://localhost:8000/admin`

## Configuración de Producción

### 1. Variables de Entorno

```bash
SECRET_KEY=clave-secreta-muy-larga-y-segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,api.tu-dominio.com

# IA
QWEN_API_KEY=tu-api-key-produccion
QWEN_MODEL=qwen-2.5
QWEN_TEMPERATURA=0.3

# Base de datos/Storage
DATA_DIR=/var/www/smart-sync/data
JSON_BACKUP_ENABLED=True

# Seguridad
CORS_ALLOWED_ORIGINS=https://tu-dominio.com
RATE_LIMIT_PER_MINUTE=60

# Logs
LOG_LEVEL=INFO
LOG_FILE=/var/log/smart-sync/app.log
```

### 2. Configuración de Servidor Web

#### Usando Gunicorn + Nginx

**Instalar Gunicorn:**

```bash
pip install gunicorn
```

**Crear archivo de servicio systemd:**

`/etc/systemd/system/smart-sync.service`:

```ini
[Unit]
Description=Smart-Sync Concierge Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/smart-sync
Environment="PATH=/var/www/smart-sync/venv/bin"
ExecStart=/var/www/smart-sync/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/smart-sync/smart-sync.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Iniciar servicio:**

```bash
sudo systemctl start smart-sync
sudo systemctl enable smart-sync
```

**Configuración Nginx:**

`/etc/nginx/sites-available/smart-sync`:

```nginx
upstream smart-sync {
    server unix:/var/www/smart-sync/smart-sync.sock;
}

server {
    listen 80;
    server_name api.tu-dominio.com;

    location / {
        proxy_pass http://smart-sync;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/smart-sync/static/;
    }

    location /media/ {
        alias /var/www/smart-sync/media/;
    }
}
```

**Activar sitio:**

```bash
sudo ln -s /etc/nginx/sites-available/smart-sync /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Configuración HTTPS con Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.tu-dominio.com
```

### 4. Configuración de Backup

**Script de backup (`backup.sh`):**

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/smart-sync"
DATA_DIR="/var/www/smart-sync/data"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Comprimir datos JSON
tar -czf $BACKUP_DIR/data_$DATE.tar.gz -C $DATA_DIR .

# Eliminar backups antiguos (mantener últimos 30)
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +30 -delete

echo "Backup completado: data_$DATE.tar.gz"
```

**Añadir a crontab:**

```bash
# Ejecutar backup diario a las 2 AM
0 2 * * * /path/to/backup.sh
```

### 5. Monitoreo

#### Usando systemd monitoring

```bash
# Verificar estado
sudo systemctl status smart-sync

# Ver logs
sudo journalctl -u smart-sync -f
```

#### Configurar Uptime Monitor

Servicios recomendados:
- UptimeRobot
- Pingdom
- StatusCake

## Despliegue en Docker

### Dockerfile

```dockerfile
FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . /app/

# Crear directorio de datos
RUN mkdir -p /app/data

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - QWEN_API_KEY=${QWEN_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/static
      - ./media:/media
    depends_on:
      - app
    restart: unless-stopped
```

### Ejecutar con Docker

```bash
# Construir imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## Configuración de CI/CD

### GitHub Actions

`.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/smart-sync
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            sudo systemctl reload smart-sync
```

## Verificación del Despliegue

### 1. Verificar API

```bash
curl https://api.tu-dominio.com/api/v1/appointments/
```

### 2. Verificar Health Check

```bash
curl https://api.tu-dominio.com/health/
```

Respuesta esperada:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-01-22T10:00:00Z"
}
```

### 3. Verificar Admin

Acceder a `https://api.tu-dominio.com/admin/`

## Solución de Problemas

### Error: Permiso denegado en archivos JSON

```bash
sudo chown -R www-data:www-data /var/www/smart-sync/data
sudo chmod -R 755 /var/www/smart-sync/data
```

### Error: Conexión con Qwen falla

Verificar API key y conexión:

```bash
curl -H "Authorization: Bearer $QWEN_API_KEY" https://api.qwen.example.com/v1/models
```

### Error: Rate limiting excedido

Aumentar límite o implementar cache:

```python
# settings/base.py
RATE_LIMIT_PER_MINUTE = 120
```

### Error: Archivo JSON corrupto

Recuperar desde backup:

```bash
tar -xzf /var/backups/smart-sync/data_latest.tar.gz -C /var/www/smart-sync/
```

## Seguridad

### 1. Actualizaciones de Seguridad

```bash
# Actualizar dependencias regularmente
pip install --upgrade -r requirements.txt

# Verificar vulnerabilidades
pip-audit
```

### 2. Firewall

```bash
# UFW configuración
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. Monitoreo de Logs

```bash
# Ver logs en tiempo real
tail -f /var/log/smart-sync/app.log

# Buscar errores
grep ERROR /var/log/smart-sync/app.log
```

## Escalabilidad

### Migración a Base de Datos

Cuando JSON local no sea suficiente:

1. Instalar PostgreSQL
2. Modificar `settings/base.py` para usar DB
3. Crear migraciones
4. Migrar datos JSON a DB

### Migración a Redis

Para cache y colas:

```bash
pip install redis
```

Configurar en `settings/base.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

*Última actualización: 2026-01-22*
*Versión: 0.1.0*
