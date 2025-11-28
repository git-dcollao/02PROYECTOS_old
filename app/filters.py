from datetime import datetime
import logging
from flask_login import current_user
from flask import has_request_context

logger = logging.getLogger(__name__)

def init_filters(app):
    """Inicializar filtros personalizados para plantillas"""
    
    # Importar el servicio de menú aquí para evitar imports circulares
    from app.services.menu_service import menu_service
    
    # FUNCIONES GLOBALES DE MENÚ
    @app.template_global()
    def get_current_user():
        """Obtener usuario actual para templates"""
        try:
            if not has_request_context() or not hasattr(current_user, 'is_authenticated'):
                return None
            return current_user if current_user.is_authenticated else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario actual: {e}")
            return None
    
    @app.template_global()
    def get_user_menu():
        """Obtener menú del usuario actual para templates"""
        try:
            # Verificar si tenemos contexto de request y usuario autenticado
            if not has_request_context() or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                return []
            return menu_service.get_user_menu(current_user)
        except Exception as e:
            logger.error(f"Error obteniendo menú: {e}")
            return []

    @app.template_global()
    def get_menu_item_count():
        """Obtener conteo total de elementos del menú"""
        try:
            # Verificar si tenemos contexto de request y usuario autenticado
            if not has_request_context() or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                return 0
            menu = menu_service.get_user_menu(current_user)
            return sum(category.get('count', 0) for category in menu)
        except Exception as e:
            logger.error(f"Error obteniendo conteo del menú: {e}")
            return 0

    @app.template_global()
    def has_menu_access(route):
        """Verificar si el usuario actual tiene acceso a una ruta específica"""
        try:
            # Verificar si tenemos contexto de request y usuario autenticado
            if not has_request_context() or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                return False
            menu = menu_service.get_user_menu(current_user)
            for category in menu:
                for page in category.get('pages', []):
                    if page.get('url') == route:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error verificando acceso a ruta {route}: {e}")
            return False
    
    @app.template_filter('datetime')
    def datetime_filter(value, format='%Y-%m-%d %H:%M:%S'):
        """Formatear datetime para plantillas"""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return value
        return value.strftime(format)
    
    @app.template_filter('date')
    def date_filter(value, format='%Y-%m-%d'):
        """Formatear fecha para plantillas"""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                return value
        return value.strftime(format)
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Formatear moneda"""
        if value is None:
            return "$0"
        try:
            return f"${value:,.2f}"
        except:
            return str(value)
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """Formatear números como porcentaje"""
        try:
            return f"{value:.1f}%"
        except (ValueError, TypeError):
            return value
    
    @app.template_filter('safe_html')
    def safe_html_filter(value):
        """Marcar contenido como HTML seguro"""
        if value is None:
            return ''
        return value  # Markup importado solo si usas Jinja2 Markup
    
    @app.template_filter('truncate_words')
    def truncate_words_filter(value, length=50):
        """Truncar texto a un número específico de caracteres"""
        if value is None:
            return ''
        if len(str(value)) <= length:
            return value
        return str(value)[:length] + '...'
    
    @app.template_filter('format_date')
    def format_date_filter(value, format='%d-%m-%Y'):
        """Formatear fechas"""
        if value is None:
            return ''
        try:
            if hasattr(value, 'strftime'):
                return value.strftime(format)
            return str(value)
        except (ValueError, AttributeError):
            return str(value)
    
    @app.template_filter('capitalize_first')
    def capitalize_first_filter(value):
        """Capitalizar solo la primera letra"""
        if value is None:
            return ''
        str_value = str(value)
        if len(str_value) == 0:
            return ''
        return str_value[0].upper() + str_value[1:]

    logger.info("Filtros de plantilla inicializados correctamente")