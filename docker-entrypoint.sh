#!/bin/bash
set -e

echo "🚀 Iniciando Smart-Sync Concierge v0.2.0..."
echo "⏳ Esperando que PostgreSQL esté listo..."

# Wait for PostgreSQL to be ready
while ! pg_isready -h "$DATABASE_HOST" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-postgres}" 2>/dev/null; do
  echo "   PostgreSQL aún no está disponible, esperando..."
  sleep 2
done

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
