#!/bin/bash

# Configuración de colores y logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S')${NC} $1"
}

error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') SUCCESS:${NC} $1"
}

warning() {
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') WARNING:${NC} $1"
}

# Función para verificar archivos requeridos
check_requirements() {
    log "🔍 Verificando archivos requeridos..."
    
    local required_files=(".env" "docker-compose.yml" "Dockerfile" "requirements.txt")
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        error "Archivos faltantes: ${missing_files[*]}"
        return 1
    fi
    
    success "Todos los archivos requeridos están presentes"
    return 0
}

# Función para verificar variables de entorno
check_env_vars() {
    log "🔍 Verificando variables de entorno..."
    
    if [ ! -f .env ]; then
        error "Archivo .env no encontrado"
        return 1
    fi
    
    # Cargar variables del .env
    set -a
    source .env
    set +a
    
    local required_vars=("DATABASE_URL" "SECRET_KEY" "MYSQL_DB" "MYSQL_USER" "MYSQL_PW")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        error "Variables de entorno faltantes: ${missing_vars[*]}"
        return 1
    fi
    
    success "Variables de entorno verificadas"
    return 0
}

# Función para limpiar contenedores
cleanup_containers() {
    log "🧹 Limpiando contenedores existentes..."
    
    # Detener contenedores
    docker-compose down -v --remove-orphans 2>/dev/null || true
    
    # Limpiar imágenes huérfanas
    docker image prune -f 2>/dev/null || true
    
    success "Contenedores limpiados"
}

# Función para construir servicios
build_services() {
    log "🔨 Construyendo servicios..."
    
    if ! docker-compose build --no-cache; then
        error "Error al construir servicios"
        return 1
    fi
    
    success "Servicios construidos exitosamente"
    return 0
}

# Función para iniciar base de datos
start_database() {
    log "🎯 Iniciando base de datos..."
    
    if ! docker-compose up -d proyectos_db; then
        error "Error al iniciar base de datos"
        return 1
    fi
    
    # Esperar a que la base de datos esté lista
    log "⏳ Esperando que MySQL esté listo..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T proyectos_db mysqladmin ping -h localhost -u root -p"$MYSQL_PW" 2>/dev/null; then
            success "Base de datos lista"
            return 0
        fi
        
        log "Intento $attempt/$max_attempts - Esperando MySQL..."
        sleep 2
        ((attempt++))
    done
    
    error "Base de datos no respondió después de $max_attempts intentos"
    return 1
}

# Función para verificar conectividad
test_connectivity() {
    log "🔗 Verificando conectividad..."
    
    if ! python check_db.py; then
        error "Error de conectividad con la base de datos"
        return 1
    fi
    
    success "Conectividad verificada"
    return 0
}

# Función para iniciar aplicación
start_application() {
    log "🚀 Iniciando aplicación..."
    
    # Iniciar aplicación en modo detached primero para verificar
    if ! docker-compose up -d proyectos_app; then
        error "Error al iniciar aplicación"
        return 1
    fi
    
    # Esperar un momento y verificar estado
    sleep 5
    
    if ! docker-compose ps proyectos_app | grep -q "Up"; then
        error "La aplicación no se inició correctamente"
        docker-compose logs proyectos_app
        return 1
    fi
    
    success "Aplicación iniciada en modo background"
    
    # Preguntar si mostrar logs en tiempo real
    echo ""
    read -p "¿Deseas ver los logs en tiempo real? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "📋 Mostrando logs (Ctrl+C para salir)..."
        docker-compose logs -f proyectos_app
    fi
    
    return 0
}

# Función principal
main() {
    echo "🚀 Iniciando sistema de proyectos..."
    echo "======================================="
    
    # Verificaciones previas
    check_requirements || exit 1
    check_env_vars || exit 1
    
    # Proceso de inicio
    cleanup_containers
    build_services || exit 1
    start_database || exit 1
    test_connectivity || exit 1
    start_application || exit 1
    
    echo ""
    success "✅ Sistema iniciado exitosamente!"
    echo "🌐 Aplicación disponible en: http://localhost:${APP_PORT:-5050}"
    echo "🗄️  Adminer disponible en: http://localhost:8080 (perfil development)"
    echo ""
    echo "Comandos útiles:"
    echo "  docker-compose logs -f proyectos_app  # Ver logs"
    echo "  docker-compose down                   # Detener servicios"
    echo "  docker-compose ps                     # Ver estado"
}

# Manejo de errores
set -e
trap 'error "Script interrumpido"; exit 1' INT TERM

# Ejecutar función principal
main "$@"
