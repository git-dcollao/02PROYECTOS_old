from markupsafe import Markup
from flask_login import current_user
from app.services.menu_service import menu_service

def nl2br(value):
    """
    Convierte saltos de línea en etiquetas <br>
    """
    if not value:
        return ""
    return Markup(value.replace('\n', '<br>'))

def get_user_menu():
    """
    Obtener menú del usuario actual para templates
    """
    try:
        return menu_service.get_user_menu(current_user)
    except Exception as e:
        print(f"Error obteniendo menú: {e}")
        return []

def get_menu_item_count():
    """
    Obtener conteo total de elementos del menú
    """
    try:
        menu = menu_service.get_user_menu(current_user)
        return sum(category.get('count', 0) for category in menu)
    except:
        return 0

def has_menu_access(route):
    """
    Verificar si el usuario actual tiene acceso a una ruta específica
    """
    try:
        menu = menu_service.get_user_menu(current_user)
        for category in menu:
            for page in category.get('pages', []):
                if page.get('url') == route:
                    return True
        return False
    except:
        return False

def register_filters(app):
    """
    Registra todos los filtros personalizados para Jinja2
    """
    app.jinja_env.filters['nl2br'] = nl2br
    
    # Funciones de contexto global para templates
    app.jinja_env.globals['get_user_menu'] = get_user_menu
    app.jinja_env.globals['get_menu_item_count'] = get_menu_item_count
    app.jinja_env.globals['has_menu_access'] = has_menu_access
