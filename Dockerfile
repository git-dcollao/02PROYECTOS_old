# Utiliza una imagen base de Python
FROM python:3.11-slim AS base

# Metadatos
LABEL maintainer="Proyectos DCV"
LABEL version="1.0"
LABEL description="Proyecto de control de avances de proyectos"

# Variables de construcción
ARG FLASK_ENV=production
ARG USER_ID=1000
ARG GROUP_ID=1000

# Instalar dependencias del sistema y herramientas MySQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    mariadb-client \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -g ${GROUP_ID} appgroup && \
    useradd -r -u ${USER_ID} -g appgroup appuser

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias Python primero (para cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY --chown=appuser:appgroup . .

# Crear directorios necesarios
RUN mkdir -p logs uploads tmp backups && \
    chown -R appuser:appgroup /app

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV FLASK_APP=init_app.py
ENV FLASK_ENV=${FLASK_ENV}
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5050/health || exit 1

# Exponer puerto
EXPOSE 5050

# Comando de inicio
CMD ["python", "init_app.py"]