#!/bin/bash
set -e

echo "🚀 Iniciando Smart-Sync Concierge v0.2.0..."
echo "⏳ Esperando que PostgreSQL esté listo..."

# Debug: show if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
  echo "   DATABASE_URL está configurada (primeros 50 caracteres: ${DATABASE_URL:0:50}...)"
else
  echo "   ⚠️  DATABASE_URL NO está configurada"
fi

# Parse DATABASE_URL to extract connection details if using DATABASE_URL
if [ -n "$DATABASE_URL" ]; then
  # Extract host, port, user from DATABASE_URL (postgres://user:pass@host:port/db)
  DATABASE_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:\/]*\).*/\1/p')
  DATABASE_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]\+\).*/\1/p')
  DATABASE_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\).*/\1/p')

  if [ -z "$DATABASE_PORT" ]; then
    DATABASE_PORT="5432"
  fi

  echo "   Conectando a PostgreSQL en $DATABASE_HOST:$DATABASE_PORT..."

  # Wait for PostgreSQL to be ready
  while ! pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" 2>/dev/null; do
    echo "   PostgreSQL aún no está disponible, esperando..."
    sleep 2
  done
else
  echo "   Warning: DATABASE_URL no está configurada, saltando check de PostgreSQL"
fi

echo "✅ PostgreSQL está listo!"

# Run migrations
echo "🔄 Ejecutando migraciones Django..."
python manage.py migrate --noinput
echo "✅ Migraciones completadas!"

# Collect static files
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear
echo "✅ Archivos estáticos recolectados!"

# Create superuser if requested
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "👤 Creando superuser..."
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print("✅ Superuser creado exitosamente!")
else:
    print("ℹ️  Superuser ya existe")
END
fi

echo "✅ Inicialización completada!"
echo "🚀 Iniciando aplicación..."

# Execute the main command
exec "$@"
