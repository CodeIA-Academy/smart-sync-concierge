# Multi-stage build for Smart-Sync Concierge
# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 django

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/django/.local

# Copy application code
COPY --chown=django:django . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/staticfiles && \
    chown -R django:django /app/logs /app/data /app/staticfiles

# Set environment variables
ENV PATH=/home/django/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:$PYTHONPATH \
    PORT=9000

# Switch to non-root user
USER django

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9000/api/v1/health/ || exit 1

# Run entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "config.wsgi:application"]
