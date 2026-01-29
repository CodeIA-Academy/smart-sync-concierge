.PHONY: help build up down logs migrate shell test clean healthcheck collectstatic migrate-data

help:
	@echo "Smart-Sync Concierge v0.2.0 - Comandos disponibles:"
	@echo ""
	@echo "Gestión de contenedores:"
	@echo "  make build              Construir imagen Docker"
	@echo "  make up                 Iniciar servicios (PostgreSQL + Django)"
	@echo "  make down               Detener servicios"
	@echo "  make logs               Ver logs en tiempo real"
	@echo "  make clean              Eliminar contenedores y volúmenes"
	@echo ""
	@echo "Base de datos:"
	@echo "  make migrate            Ejecutar migraciones Django"
	@echo "  make migrate-data       Migrar datos de JSON a PostgreSQL"
	@echo "  make shell              Abrir shell de Django"
	@echo ""
	@echo "Testing:"
	@echo "  make test               Ejecutar tests con pytest"
	@echo "  make healthcheck        Verificar salud de la aplicación"
	@echo "  make collectstatic      Recolectar archivos estáticos"
	@echo ""

build:
	@echo "🔨 Construyendo imagen Docker..."
	docker-compose build

up:
	@echo "🚀 Iniciando servicios..."
	docker-compose up -d
	@echo ""
	@echo "✅ Servicios iniciados:"
	@echo "   - API: http://localhost:9000"
	@echo "   - PostgreSQL: localhost:5432"
	@echo ""
	@echo "Esperando que la aplicación esté lista..."
	@sleep 5
	@echo "✅ Aplicación lista. Intenta: curl http://localhost:9000/api/v1/health/"

down:
	@echo "⏹️  Deteniendo servicios..."
	docker-compose down

logs:
	@echo "📋 Mostrando logs en tiempo real (Ctrl+C para salir)..."
	docker-compose logs -f web

migrate:
	@echo "🔄 Ejecutando migraciones..."
	docker-compose exec web python manage.py migrate

shell:
	@echo "🐍 Abriendo shell de Django..."
	docker-compose exec web python manage.py shell

test:
	@echo "🧪 Ejecutando tests..."
	docker-compose exec web pytest -v

clean:
	@echo "🗑️  Limpiando contenedores y volúmenes..."
	docker-compose down -v
	@echo "✅ Limpieza completada"

healthcheck:
	@echo "❤️  Verificando salud de la aplicación..."
	@docker-compose exec web curl -s http://localhost:9000/api/v1/health/ || echo "❌ API no responde"

collectstatic:
	@echo "📦 Recolectando archivos estáticos..."
	docker-compose exec web python manage.py collectstatic --noinput --clear

migrate-data:
	@echo "📥 Migrando datos de JSON a PostgreSQL..."
	docker-compose exec web python data/migrate_to_db.py --dry-run
	@echo ""
	@read -p "¿Deseas ejecutar la migración? (s/n): " confirm && \
	if [ "$$confirm" = "s" ]; then \
		docker-compose exec web python data/migrate_to_db.py; \
	else \
		echo "Migración cancelada"; \
	fi

createsuperuser:
	@echo "👤 Creando superuser..."
	docker-compose exec web python manage.py createsuperuser

backup-db:
	@echo "💾 Haciendo backup de la base de datos..."
	docker-compose exec postgres pg_dump -U postgres smartsync > backup-$(shell date +%Y%m%d-%H%M%S).sql
	@echo "✅ Backup completado"

psql:
	@echo "🐘 Accediendo a PostgreSQL..."
	docker-compose exec postgres psql -U postgres -d smartsync

info:
	@echo "📊 Información de la aplicación:"
	@echo ""
	@docker ps -a --filter "name=smartsync" --format "table {{.Names}}\t{{.Status}}"
	@echo ""
	@echo "URLs importantes:"
	@echo "  - API Root: http://localhost:9000/api/v1/"
	@echo "  - Health: http://localhost:9000/api/v1/health/"
	@echo "  - Admin: http://localhost:9000/admin/"
	@echo ""
