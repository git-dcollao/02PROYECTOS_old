"""
Sistema de Logging Avanzado para Aplicación Flask
Configuración centralizada con diferentes niveles y formatters
"""
import logging
import logging.handlers
import os
import json
from datetime import datetime
from flask import request, g, current_user
from functools import wraps

class FlaskRequestFormatter(logging.Formatter):
    """Formatter personalizado que incluye contexto de Flask"""
    
    def format(self, record):
        # Información básica del request
        if hasattr(g, 'request_id'):
            record.request_id = g.request_id
        else:
            record.request_id = 'N/A'
            
        # Usuario actual si está disponible
        try:
            if current_user and hasattr(current_user, 'email'):
                record.user_email = current_user.email
                record.user_id = getattr(current_user, 'id', 'N/A')
                record.is_superadmin = getattr(current_user, 'is_superadmin', lambda: False)()
            else:
                record.user_email = 'Anonymous'
                record.user_id = 'N/A'
                record.is_superadmin = False
        except:
            record.user_email = 'Unknown'
            record.user_id = 'N/A'
            record.is_superadmin = False
            
        # Información del request
        try:
            if request:
                record.endpoint = request.endpoint or 'N/A'
                record.method = request.method
                record.url = request.url
                record.remote_addr = request.remote_addr
            else:
                record.endpoint = 'N/A'
                record.method = 'N/A'
                record.url = 'N/A'
                record.remote_addr = 'N/A'
        except:
            record.endpoint = 'N/A'
            record.method = 'N/A'
            record.url = 'N/A'
            record.remote_addr = 'N/A'
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """Formatter JSON para logs estructurados"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Agregar contexto de Flask si está disponible
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'user_email'):
            log_entry['user'] = {
                'email': record.user_email,
                'id': record.user_id,
                'is_superadmin': record.is_superadmin
            }
        if hasattr(record, 'endpoint'):
            log_entry['request'] = {
                'endpoint': record.endpoint,
                'method': record.method,
                'url': record.url,
                'remote_addr': record.remote_addr
            }
        
        # Agregar información adicional si existe
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(app):
    """
    Configurar sistema de logging para la aplicación Flask
    """
    # Crear directorio de logs si no existe
    log_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuración según ambiente
    if app.config.get('FLASK_ENV') == 'production':
        log_level = logging.WARNING
    elif app.config.get('FLASK_ENV') == 'testing':
        log_level = logging.ERROR
    else:
        log_level = logging.DEBUG
    
    # Logger principal de la aplicación
    app_logger = logging.getLogger('app')
    app_logger.setLevel(log_level)
    
    # Handler para archivo principal (rotativo)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_formatter = FlaskRequestFormatter(
        '%(asctime)s [%(levelname)s] %(request_id)s - %(user_email)s - %(endpoint)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Handler para errores (archivo separado)
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=10*1024*1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Handler JSON para análisis automatizado
    json_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.json.log'),
        maxBytes=50*1024*1024,  # 50MB
        backupCount=3
    )
    json_handler.setLevel(log_level)
    json_handler.setFormatter(JSONFormatter())
    
    # Handler para consola (desarrollo)
    if app.config.get('FLASK_ENV') != 'production':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = FlaskRequestFormatter(
            '%(asctime)s [%(levelname)s] %(user_email)s@%(endpoint)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        app_logger.addHandler(console_handler)
    
    # Agregar handlers
    app_logger.addHandler(file_handler)
    app_logger.addHandler(error_handler)
    app_logger.addHandler(json_handler)
    
    # Logger específico para seguridad
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    security_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'security.log'),
        maxBytes=20*1024*1024,
        backupCount=10
    )
    security_handler.setFormatter(file_formatter)
    security_logger.addHandler(security_handler)
    
    # Logger para performance
    perf_logger = logging.getLogger('performance')
    perf_logger.setLevel(logging.INFO)
    perf_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'performance.log'),
        maxBytes=20*1024*1024,
        backupCount=5
    )
    perf_handler.setFormatter(JSONFormatter())
    perf_logger.addHandler(perf_handler)
    
    # Configurar niveles para librerías externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    app.logger.info("Sistema de logging configurado correctamente")

def log_security_event(event_type, details=None, user=None):
    """Registrar eventos de seguridad"""
    security_logger = logging.getLogger('security')
    
    extra_data = {
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'details': details or {}
    }
    
    if user:
        extra_data['user'] = {
            'id': getattr(user, 'id', None),
            'email': getattr(user, 'email', None),
            'is_superadmin': getattr(user, 'is_superadmin', lambda: False)()
        }
    
    security_logger.info(f"SECURITY_EVENT: {event_type}", extra={'extra_data': extra_data})

def log_performance_metric(metric_name, value, details=None):
    """Registrar métricas de performance"""
    perf_logger = logging.getLogger('performance')
    
    extra_data = {
        'metric': metric_name,
        'value': value,
        'timestamp': datetime.now().isoformat(),
        'details': details or {}
    }
    
    perf_logger.info(f"PERFORMANCE_METRIC: {metric_name}={value}", extra={'extra_data': extra_data})

def log_endpoint_access(func):
    """Decorator para registrar acceso a endpoints"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger = logging.getLogger('app')
        
        logger.info(f"Accessing endpoint: {request.endpoint}")
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            log_performance_metric(
                'endpoint_duration',
                duration,
                {'endpoint': request.endpoint, 'method': request.method}
            )
            
            logger.info(f"Endpoint completed successfully in {duration:.3f}s")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Endpoint failed after {duration:.3f}s: {str(e)}", exc_info=True)
            raise
            
    return wrapper