"""
Sistema de Caching y Optimización de Performance
Redis + Memory Cache + Database Query Optimization
"""
import redis
import json
import pickle
from functools import wraps
from datetime import datetime, timedelta
import time
import hashlib
from flask import current_app, request, g
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor centralizado de cache con múltiples backends"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.memory_cache = {}  # Cache en memoria para desarrollo
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar el sistema de cache con la app Flask"""
        self.app = app
        
        # Configurar Redis si está disponible
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # Test connection
            logger.info("Cache Redis conectado exitosamente")
        except Exception as e:
            logger.warning(f"Redis no disponible, usando cache en memoria: {e}")
            self.redis_client = None
    
    def _generate_key(self, key_parts):
        """Generar clave única para cache"""
        if isinstance(key_parts, (list, tuple)):
            key_string = ":".join(str(part) for part in key_parts)
        else:
            key_string = str(key_parts)
        
        # Agregar prefijo de la aplicación
        app_prefix = self.app.config.get('CACHE_KEY_PREFIX', 'flask_app')
        return f"{app_prefix}:{key_string}"
    
    def get(self, key, default=None):
        """Obtener valor del cache"""
        cache_key = self._generate_key(key)
        
        try:
            # Intentar Redis primero
            if self.redis_client:
                value = self.redis_client.get(cache_key)
                if value is not None:
                    self.cache_stats['hits'] += 1
                    return json.loads(value)
            
            # Fallback a cache en memoria
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if entry['expires'] > datetime.now():
                    self.cache_stats['hits'] += 1
                    return entry['value']
                else:
                    # Expirado, eliminar
                    del self.memory_cache[cache_key]
            
            self.cache_stats['misses'] += 1
            return default
            
        except Exception as e:
            logger.error(f"Error getting cache key {cache_key}: {e}")
            self.cache_stats['misses'] += 1
            return default
    
    def set(self, key, value, timeout=300):
        """Establecer valor en cache"""
        cache_key = self._generate_key(key)
        
        try:
            # Redis
            if self.redis_client:
                serialized_value = json.dumps(value, default=str)
                self.redis_client.setex(cache_key, timeout, serialized_value)
            
            # Memory cache
            expires_at = datetime.now() + timedelta(seconds=timeout)
            self.memory_cache[cache_key] = {
                'value': value,
                'expires': expires_at
            }
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {cache_key}: {e}")
            return False
    
    def delete(self, key):
        """Eliminar clave del cache"""
        cache_key = self._generate_key(key)
        
        try:
            # Redis
            if self.redis_client:
                self.redis_client.delete(cache_key)
            
            # Memory cache
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            self.cache_stats['deletes'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache key {cache_key}: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Limpiar claves que coincidan con un patrón"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(self._generate_key(pattern))
                if keys:
                    self.redis_client.delete(*keys)
            
            # Memory cache - buscar por patrón
            pattern_key = self._generate_key(pattern)
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern_key in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
                
            return True
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return False
    
    def get_stats(self):
        """Obtener estadísticas de cache"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            'hit_rate': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache),
            'redis_connected': self.redis_client is not None
        }

# Instancia global
cache = CacheManager()

def cached(timeout=300, key_func=None):
    """
    Decorator para cachear resultados de funciones
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Clave por defecto basada en función y parámetros
                func_name = f"{func.__module__}.{func.__name__}"
                params_hash = hashlib.md5(str((args, sorted(kwargs.items()))).encode()).hexdigest()
                cache_key = f"func:{func_name}:{params_hash}"
            
            # Intentar obtener del cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Solo cachear si la ejecución tomó tiempo significativo
            if execution_time > 0.01:  # 10ms
                cache.set(cache_key, result, timeout)
                logger.debug(f"Cached result for {cache_key} (execution: {execution_time:.3f}s)")
            
            return result
        return wrapper
    return decorator

def cache_database_query(timeout=600):
    """Decorator específico para queries de base de datos"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Incluir información del usuario para cache personalizado
            user_id = getattr(g, 'current_user_id', 'anonymous')
            
            # Generar clave incluyendo usuario
            func_name = f"{func.__module__}.{func.__name__}"
            params_str = str((args, sorted(kwargs.items())))
            cache_key = f"db_query:{func_name}:{user_id}:{hashlib.md5(params_str.encode()).hexdigest()}"
            
            # Verificar cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar query
            result = func(*args, **kwargs)
            
            # Cachear resultado
            cache.set(cache_key, result, timeout)
            return result
            
        return wrapper
    return decorator

def invalidate_cache_on_change(cache_patterns):
    """
    Decorator para invalidar cache cuando hay cambios en datos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidar patrones de cache especificados
            for pattern in cache_patterns:
                cache.clear_pattern(pattern)
                logger.info(f"Invalidated cache pattern: {pattern}")
            
            return result
        return wrapper
    return decorator

class QueryOptimizer:
    """Utilidades para optimizar queries de SQLAlchemy"""
    
    @staticmethod
    def add_eager_loading(query, relationships):
        """Agregar eager loading a un query"""
        from sqlalchemy.orm import joinedload
        
        for relationship in relationships:
            query = query.options(joinedload(relationship))
        return query
    
    @staticmethod
    def paginate_efficiently(query, page, per_page, max_per_page=100):
        """Paginación eficiente con límites"""
        per_page = min(per_page, max_per_page)
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
            max_per_page=max_per_page
        )
    
    @staticmethod
    def count_efficiently(query):
        """Contar registros de forma eficiente"""
        from sqlalchemy import func
        return query.with_entities(func.count()).scalar()

def monitor_query_performance(func):
    """Decorator para monitorear performance de queries"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log queries lentas
        if execution_time > 1.0:  # 1 segundo
            logger.warning(f"Slow query detected: {func.__name__} took {execution_time:.3f}s")
        
        # Métricas de performance
        from app.logging_config import log_performance_metric
        log_performance_metric(
            'database_query_time',
            execution_time,
            {'function': func.__name__, 'module': func.__module__}
        )
        
        return result
    return wrapper

def setup_performance_monitoring(app):
    """Configurar monitoreo de performance"""
    
    @app.before_request
    def before_request():
        g.request_start_time = time.time()
        g.current_user_id = getattr(request, 'current_user_id', 'anonymous')
    
    @app.after_request
    def after_request(response):
        # Calcular tiempo total de request
        if hasattr(g, 'request_start_time'):
            total_time = time.time() - g.request_start_time
            
            # Log requests lentos
            if total_time > 2.0:  # 2 segundos
                logger.warning(f"Slow request: {request.endpoint} took {total_time:.3f}s")
            
            # Agregar header de tiempo
            response.headers['X-Response-Time'] = f"{total_time:.3f}s"
        
        return response
    
    # Endpoint para estadísticas de cache
    @app.route('/admin/cache-stats')
    def cache_stats():
        from flask_login import login_required, current_user
        
        @login_required
        def _cache_stats():
            if not current_user.is_superadmin():
                return {'error': 'Unauthorized'}, 403
            
            return cache.get_stats()
        
        return _cache_stats()