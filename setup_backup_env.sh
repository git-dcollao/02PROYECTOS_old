#!/bin/bash

# Script para configurar el entorno de backups

echo "🔧 Configurando entorno de backups..."

# Crear directorio de backups si no existe
BACKUP_DIR="/app/backups"
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    echo "✅ Directorio de backups creado: $BACKUP_DIR"
else
    echo "ℹ️  Directorio de backups ya existe: $BACKUP_DIR"
fi

# Verificar si mysqldump está disponible
if command -v mysqldump >/dev/null 2>&1; then
    echo "✅ mysqldump está disponible"
    mysqldump_version=$(mysqldump --version)
    echo "   Versión: $mysqldump_version"
else
    echo "❌ mysqldump no está disponible"
    echo "🔧 Instalando mysql-client..."
    
    # Actualizar repositorios e instalar mysql-client
    apt-get update -q
    apt-get install -y mysql-client
    
    if command -v mysqldump >/dev/null 2>&1; then
        echo "✅ mysql-client instalado correctamente"
    else
        echo "❌ Error instalando mysql-client"
        exit 1
    fi
fi

# Verificar si mysql está disponible para restauraciones
if command -v mysql >/dev/null 2>&1; then
    echo "✅ mysql cliente está disponible"
else
    echo "❌ mysql cliente no está disponible"
    exit 1
fi

# Establecer permisos correctos
chmod 755 "$BACKUP_DIR"
echo "✅ Permisos establecidos para directorio de backups"

# Verificar conexión a la base de datos
echo "🔍 Verificando conexión a la base de datos..."

# Cargar variables específicas del archivo .env
if [ -f "/app/.env" ]; then
    # Extraer solo las variables de MySQL que necesitamos
    MYSQL_PORT=$(grep '^MYSQL_PORT=' /app/.env | cut -d'=' -f2 | tr -d '\r')
    MYSQL_USER=$(grep '^MYSQL_USER=' /app/.env | cut -d'=' -f2 | tr -d '\r')
    MYSQL_PASSWORD=$(grep '^MYSQL_PASSWORD=' /app/.env | cut -d'=' -f2 | tr -d '\r')
    MYSQL_DB=$(grep '^MYSQL_DB=' /app/.env | cut -d'=' -f2 | tr -d '\r')
    echo "✅ Variables MySQL cargadas desde .env"
else
    echo "❌ Archivo .env no encontrado"
    exit 1
fi

# Usar variables del .env pero ajustar puerto para conexión interna de Docker
MYSQL_HOST="mysql_db"
MYSQL_PORT="3306"  # Puerto interno del contenedor (Docker network)
# MYSQL_USER ya está cargado desde .env  
# MYSQL_PASSWORD ya está cargado desde .env
MYSQL_DATABASE="${MYSQL_DB:-proyectosDB}"

echo "📋 Configuración de conexión:"
echo "   Host: $MYSQL_HOST"
echo "   Port: $MYSQL_PORT (puerto interno Docker - el 3308 es externo)"
echo "   Database: $MYSQL_DATABASE"
echo "   User: $MYSQL_USER"

# Intentar conexión usando el puerto interno de Docker (sin SSL)
if mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --ssl=0 -e "SELECT 1;" "$MYSQL_DATABASE" >/dev/null 2>&1; then
    echo "✅ Conexión a la base de datos exitosa"
    
    # Crear un backup de prueba para verificar que todo funciona
    echo "🧪 Creando backup de prueba..."
    BACKUP_FILE="/app/backups/test_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if mysqldump -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --ssl=0 "$MYSQL_DATABASE" > "$BACKUP_FILE" 2>/dev/null; then
        echo "✅ Backup de prueba creado exitosamente"
        echo "   Archivo: $BACKUP_FILE"
        echo "   Tamaño: $(du -h $BACKUP_FILE | cut -f1)"
        
        # Eliminar el backup de prueba
        rm "$BACKUP_FILE"
        echo "🧹 Backup de prueba eliminado"
    else
        echo "❌ Error creando backup de prueba"
    fi
else
    echo "❌ Error conectando a la base de datos"
    echo "🔧 Verificar configuración de red Docker"
fi

echo "🎉 Configuración de backups completada"