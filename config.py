import os
import logging
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
# Buscar primero el archivo .env.local si existe (para desarrollo local)
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
    print("📋 Cargando configuración desde .env.local (desarrollo local)")
else:
    load_dotenv()
    print("📋 Cargando configuración desde .env (contenedor Docker)")

class Config:
    """Configuración base con validaciones y mejores prácticas"""
    
    # Validar variables críticas
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY == 'dev-secret-key-change-in-production':
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError("SECRET_KEY debe ser configurada en producción")
        SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'echo': False,
        'pool_timeout': 60,  # Aumentado para backups
        'connect_args': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'connect_timeout': 120,   # 2 minutos para conectar
            'read_timeout': 1800,     # 30 minutos para leer (backups grandes)
            'write_timeout': 1800,    # 30 minutos para escribir (restore)
            'autocommit': False,      # Control manual de transacciones
            'sql_mode': 'TRADITIONAL'  # Modo estricto para mejor compatibilidad
        }
    }
    
    # Configuración MySQL para backups
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql_db')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'proyectos_admin')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '123456!#Td')
    MYSQL_DATABASE = os.environ.get('MYSQL_DB', 'proyectosDB')
    
    # Configuraciones de Flask
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False  # Permitir caracteres Unicode en JSON
    JSONIFY_PRETTYPRINT_REGULAR = True
    RESTFUL_JSON = {'ensure_ascii': False}  # No escapar caracteres Unicode
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', 16)) * 1024 * 1024
    
    # Seguridad
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.environ.get('SESSION_LIFETIME_HOURS', 1)))
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Aplicación
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'csv'}
    
    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))
    
    @staticmethod
    def init_app(app):
        """Inicialización específica de la aplicación"""
        # Crear directorios necesarios
        for directory in [app.config.get('UPLOAD_FOLDER'), 'logs', 'tmp']:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, app.config['LOG_LEVEL']),
            format='%(asctime)s %(levelname)s %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(app.config['LOG_FILE']),
                logging.StreamHandler()
            ]
        )

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'echo': os.environ.get('SQL_ECHO', 'True').lower() == 'true'
    }
    
    LOG_LEVEL = 'DEBUG'
    
    # Cache deshabilitada en desarrollo
    CACHE_TYPE = 'null'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Configuraciones específicas de desarrollo
        app.logger.info("🔧 Aplicación iniciada en modo DESARROLLO")

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_T") or 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'echo': False
    }
    
    # Configuraciones para tests
    SKIP_DB_INIT = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info("🧪 Aplicación iniciada en modo TESTING")

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_P") or Config.SQLALCHEMY_DATABASE_URI
    
    # Seguridad reforzada
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    # Logging optimizado
    LOG_LEVEL = 'WARNING'
    
    # Cache habilitada
    CACHE_TYPE = 'redis'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Logging a syslog en producción
        import logging
        from logging.handlers import SysLogHandler, RotatingFileHandler
        
        # Handler rotativo para archivos
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'], 
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
        
        app.logger.info("🚀 Aplicación iniciada en modo PRODUCCIÓN")

class DockerConfig(DevelopmentConfig):
    """Configuración específica para Docker"""
    
    @staticmethod
    def init_app(app):
        DevelopmentConfig.init_app(app)
        
        # Configuraciones específicas de Docker
        import logging
        root = logging.getLogger()
        root.handlers = []
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtener la configuración actual basada en el entorno"""
    env = os.getenv('FLASK_ENV', 'default')
    config_class = config.get(env, DevelopmentConfig)
    
    # Validar configuración
    if hasattr(config_class, 'validate'):
        config_class.validate()
    
    return config_class

