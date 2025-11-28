from flask import Flask, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from config import Config
import time
import threading
import os
import logging
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# Variable global para controlar la inicialización
_db_initialized = False
_init_lock = threading.Lock()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuraciones de seguridad
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
        SESSION_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600,  # 1 hora
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
        WTF_CSRF_TIME_LIMIT=None,
        JSON_SORT_KEYS=False
    )

    # Configurar puerto por defecto
    app.config['PORT'] = int(os.getenv('FLASK_RUN_PORT', 5050))

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configurar timeouts automáticamente en cada conexión de SQLAlchemy
    with app.app_context():
        from sqlalchemy import event
        
        @event.listens_for(db.engine, "connect")
        def set_mysql_timeouts(dbapi_connection, connection_record):
            """Configurar automáticamente cada nueva conexión MySQL"""
            if hasattr(dbapi_connection, 'cursor'):  # Es MySQL/PyMySQL
                try:
                    cursor = dbapi_connection.cursor()
                    
                    # Configurar charset y timeouts
                    timeout_configs = [
                        "SET NAMES 'utf8mb4'",
                        "SET CHARACTER SET utf8mb4",
                        "SET character_set_connection=utf8mb4",
                        "SET SESSION wait_timeout = 1800",
                        "SET SESSION interactive_timeout = 1800", 
                        "SET SESSION net_read_timeout = 600",
                        "SET SESSION net_write_timeout = 600",
                        "SET SESSION max_execution_time = 1800000"
                    ]
                    
                    for config_sql in timeout_configs:
                        cursor.execute(config_sql)
                    
                    cursor.close()
                    logger.debug("✅ Timeouts MySQL configurados automáticamente en nueva conexión")
                    
                except Exception as e:
                    logger.debug(f"⚠️ Error configurando timeouts en conexión: {e}")
    
    
    
    # Forzar UTF-8 y configurar timeouts en todas las conexiones MySQL
    @app.before_request
    def before_request():
        """Configurar charset UTF-8 y timeouts en cada petición"""
        try:
            db.session.execute(text("SET NAMES 'utf8mb4'"))
            db.session.execute(text("SET CHARACTER SET utf8mb4"))
            db.session.execute(text("SET character_set_connection=utf8mb4"))
            
            # Configurar timeouts para operaciones largas (backups/restore)
            db.session.execute(text("SET SESSION wait_timeout = 1800"))
            db.session.execute(text("SET SESSION interactive_timeout = 1800"))
            db.session.execute(text("SET SESSION net_read_timeout = 600"))
            db.session.execute(text("SET SESSION net_write_timeout = 600"))
            db.session.execute(text("SET SESSION max_execution_time = 1800000"))
        except Exception as e:
            # Log solo en debug, ignorar errores para mantener compatibilidad
            if app.debug:
                app.logger.debug(f"Error configurando sesión MySQL: {e}")
            pass
    
    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debe iniciar sesión para acceder a esta página'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Trabajador
        return Trabajador.query.get(int(user_id))

    # Configurar logging para la aplicación
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/proyectos.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Aplicación de proyectos iniciada')

    # Middleware de seguridad
    @app.before_request
    def security_headers():
        """Agregar headers de seguridad"""
        # Limitar métodos HTTP permitidos
        if request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            return jsonify({'error': 'Método no permitido'}), 405

    @app.after_request
    def after_request(response):
        """Agregar headers de seguridad a todas las respuestas"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Asegurar codificación UTF-8 para HTML y JSON
        if response.content_type and 'text/html' in response.content_type:
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
        elif response.content_type and 'application/json' in response.content_type:
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
        
        if app.config.get('SESSION_COOKIE_SECURE'):
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Manejadores de errores globales
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f'Página no encontrada: {request.url}')
        return jsonify({'error': 'Página no encontrada'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Error interno del servidor: {str(error)}')
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        import traceback
        logger.warning(f'Solicitud incorrecta: {str(error)}')
        logger.warning(f'URL solicitada: {request.url}')
        logger.warning(f'Método: {request.method}')
        logger.warning(f'Form data: {dict(request.form) if request.form else "Sin form data"}')
        
        # Intentar leer JSON de forma segura
        try:
            json_data = request.get_json()
            logger.warning(f'JSON data: {json_data}')
        except Exception as json_error:
            logger.warning(f'JSON data error: {str(json_error)}')
            
        logger.warning(f'Traceback: {traceback.format_exc()}')
        print(f"❌ ERROR 400 INTERCEPTADO: {str(error)} en URL: {request.url}")
        return jsonify({'error': 'Solicitud incorrecta', 'details': str(error)}), 400

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        logger.error(f'Error HTTP {e.code}: {e.description}')
        return jsonify({'error': e.description}), e.code

    # Manejador específico para errores CSRF
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        logger.warning(f'Error CSRF: {str(e)} en URL: {request.url}')
        logger.warning(f'Usuario autenticado: {current_user.is_authenticated}')
        print(f"🔒 ERROR CSRF: {str(e)} en {request.url}")
        
        # Si es una petición AJAX/API, devolver JSON
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Token CSRF inválido o expirado', 
                'csrf_error': True,
                'message': 'Por favor, recarga la página e inicia sesión nuevamente'
            }), 400
        
        # Para peticiones normales, redirigir al login
        flash('Sesión expirada. Por favor, inicia sesión nuevamente.', 'error')
        return redirect(url_for('auth.login'))

    # Registrar Blueprints
    try:
        from app.controllers import controllers_bp
        app.register_blueprint(controllers_bp)
        logger.info('Blueprints registrados correctamente')
    except ImportError as e:
        logger.error(f'Error al importar controllers: {e}')
    
    # Registrar Blueprint de requerimientos (extraído del controller principal)
    try:
        from app.controllers.requerimientos_controller import requerimientos_bp
        app.register_blueprint(requerimientos_bp)
        logger.info('Blueprint de requerimientos registrado correctamente')
    except ImportError as e:
        logger.error(f'Error al importar controller de requerimientos: {e}')
    
    # Registrar Blueprint de proyectos (gestión de proyectos en ejecución)
    try:
        from app.controllers.proyectos_controller import proyectos_bp
        app.register_blueprint(proyectos_bp)
        logger.info('Blueprint de proyectos registrado correctamente')
    except ImportError as e:
        logger.error(f'Error al importar controller de proyectos: {e}')
    
    # Registrar Blueprint de autenticación
    try:
        from app.routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp)
        logger.info('Blueprint de autenticación registrado correctamente')
    except ImportError as e:
        logger.error(f'Error al importar rutas de autenticación: {e}')
    
    # Registrar Blueprint principal
    try:
        from app.routes.main_routes import main_bp
        app.register_blueprint(main_bp)
        logger.info('Blueprint principal registrado correctamente')
    except ImportError as e:
        logger.error(f'Error al importar rutas principales: {e}')
    
    # Registrar Blueprint de permisos
    try:
        from app.routes.permissions_routes import permissions_bp
        app.register_blueprint(permissions_bp)
        logger.info('Blueprint de permisos registrado correctamente')
    except ImportError as e:
        logger.error(f'Error al importar rutas de permisos: {e}')
    
    # Registrar Blueprint de administración
    try:
        from app.routes.admin_routes import admin_bp
        app.register_blueprint(admin_bp)
        logger.info('Blueprint de administración registrado correctamente')
    except ImportError as e:
        logger.error(f'Error al importar rutas de administración: {e}')
    
    # Registrar Blueprint de emergencia
    try:
        from app.routes.emergency_routes import emergency_bp
        app.register_blueprint(emergency_bp)
        logger.info('Blueprint de emergencia registrado correctamente')
    except ImportError as e:
        logger.warning(f'No se pudo registrar blueprint de emergencia: {e}')
    
    # Inicializar rutas dinámicas después de registrar los blueprints
    try:
        from app.utils.dynamic_routes import initialize_dynamic_routes
        
        @app.before_request
        def init_dynamic_routes_once():
            """Inicializar rutas dinámicas solo una vez"""
            if not hasattr(app, '_dynamic_routes_initialized'):
                initialize_dynamic_routes(app)
                app._dynamic_routes_initialized = True
        
        logger.info('Sistema de rutas dinámicas configurado')
    except ImportError as e:
        logger.warning(f'No se pudo inicializar rutas dinámicas: {e}')
    
    # Registrar filtros de plantilla personalizados
    try:
        from app.filters import init_filters
        init_filters(app)
        logger.info('Filtros de plantilla inicializados')
    except ImportError as e:
        logger.warning(f'No se pudieron cargar filtros personalizados: {e}')

    # Agregar current_user y csrf_token al contexto global de templates
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        from flask_wtf.csrf import generate_csrf
        return dict(current_user=current_user, csrf_token=generate_csrf)

    # Función para inicializar la base de datos con reintentos
    def initialize_database_with_retries():
        global _db_initialized
        
        with _init_lock:
            if _db_initialized:
                return True
                
            max_retries = 15
            retry_delay = 5
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Intento {attempt + 1}/{max_retries} de conexión a la base de datos...")
                    
                    # Verificar conexión usando el nuevo método
                    with app.app_context():
                        # Importar modelos DESPUÉS de la inicialización de la app
                        from app.models import (
                            Requerimiento, TipoRecinto, Recinto, Sector, Trabajador,
                            Financiamiento, Especialidad,
                            Equipo, Tipologia, TipoProyecto, Estado, Prioridad, Grupo,
                            requerimiento_trabajador_especialidad, EquipoTrabajo
                        )
                        
                        # Verificar conexión usando el nuevo método de SQLAlchemy 2.0
                        with db.engine.connect() as connection:
                            connection.execute(text('SELECT 1'))
                        logger.info("Conexión a la base de datos exitosa")
                    
                        # Crear todas las tablas
                        logger.info("Creando tablas de la base de datos...")
                        db.create_all()
                        logger.info("Tablas creadas exitosamente")
                        
                        # Crear datos iniciales
                        logger.info("Iniciando creación de datos iniciales...")
                        from app.seeds import crear_datos_iniciales
                        
                        # Intentar crear datos iniciales con reintentos
                        seeds_success = False
                        for seeds_attempt in range(3):
                            try:
                                if crear_datos_iniciales():
                                    seeds_success = True
                                    break
                                else:
                                    logger.warning(f"Intento {seeds_attempt + 1} de seeds falló, reintentando...")
                            except Exception as seeds_error:
                                logger.error(f"Error en seeds intento {seeds_attempt + 1}: {seeds_error}")
                                if seeds_attempt < 2:
                                    time.sleep(2)
                        
                        if seeds_success:
                            logger.info("Datos iniciales creados exitosamente")
                        else:
                            logger.warning("No se pudieron crear todos los datos iniciales")
                        
                        logger.info("Base de datos inicializada correctamente")
                        _db_initialized = True
                        return True
                    
                except Exception as e:
                    logger.error(f"Error en intento {attempt + 1}: {str(e)}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"Reintentando en {retry_delay} segundos...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"No se pudo conectar a la base de datos después de {max_retries} intentos")
                        logger.warning("La aplicación continuará sin inicializar la base de datos")
                        return False
            
            return False

    # Crear comandos CLI
    @app.cli.command()
    def init_db():
        """Comando para inicializar la base de datos y crear datos iniciales."""
        logger.info("Inicializando base de datos...")
        with app.app_context():
            if initialize_database_with_retries():
                logger.info("Base de datos inicializada exitosamente")
            else:
                logger.error("Error al inicializar la base de datos")

    @app.cli.command()
    def reset_db():
        """Comando para resetear completamente la base de datos."""
        logger.warning("Reseteando base de datos...")
        with app.app_context():
            db.drop_all()
            db.create_all()
            from app.seeds import crear_datos_iniciales
            crear_datos_iniciales()
            logger.info("Base de datos reseteada exitosamente")

    # Inicializar la base de datos usando before_request con control de una sola vez
    @app.before_request
    def init_db_once():
        global _db_initialized
        if not _db_initialized and not app.config.get('TESTING'):
            # Ejecutar en un hilo separado para no bloquear la primera request
            thread = threading.Thread(target=initialize_database_with_retries)
            thread.daemon = True
            thread.start()

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Endpoint para verificar el estado de la aplicación"""
        try:
            # Verificar conexión a la base de datos
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'version': '1.0.0'
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 503

    # También intentar inicializar inmediatamente al crear la app
    if not app.config.get('TESTING'):
        try:
            with app.app_context():
                initialize_database_with_retries()
        except Exception as e:
            logger.warning(f"Inicialización inmediata falló: {e}")
            logger.info("Se intentará nuevamente en la primera request")

    return app