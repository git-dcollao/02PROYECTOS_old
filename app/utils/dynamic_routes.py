"""
Módulo para gestión de rutas dinámicas
Permite crear rutas automáticamente a partir de templates HTML
"""

from flask import current_app, render_template, redirect, url_for
from flask_login import current_user, login_required
import os
import importlib
import sys
import logging

# Registry de rutas dinámicas
dynamic_routes_registry = {}

# Configurar logger
logger = logging.getLogger(__name__)

def register_dynamic_route(route_path, template_path, page_name):
    """
    Registra una ruta dinámica que renderiza un template específico
    
    Args:
        route_path (str): Ruta de la URL (ej: '/gantt-v2')
        template_path (str): Ruta del template (ej: 'gantt-proyecto.html')
        page_name (str): Nombre de la página para contexto
        
    Returns:
        bool: True si se registró exitosamente
    """
    try:
        print(f"🔗 Registrando ruta dinámica: {route_path} -> {template_path}")
        
        # Verificar que el template existe
        full_template_path = os.path.join(current_app.root_path, 'templates', template_path)
        if not os.path.exists(full_template_path):
            print(f"❌ Template no encontrado: {full_template_path}")
            return False
        
        # Crear función de vista dinámica
        def dynamic_view():
            """Vista generada dinámicamente"""
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Contexto básico para la página
            context = {
                'user': current_user,
                'page_title': page_name,
                'page_route': route_path,
                'is_dynamic_route': True
            }
            
            return render_template(template_path, **context)
        
        # Configurar la función
        dynamic_view.__name__ = f"dynamic_{route_path.replace('/', '_').replace('-', '_')}"
        dynamic_view = login_required(dynamic_view)
        
        # Registrar en el blueprint principal
        from app.routes.main_routes import main_bp
        
        # Registrar la ruta
        main_bp.add_url_rule(
            route_path,
            endpoint=dynamic_view.__name__,
            view_func=dynamic_view,
            methods=['GET']
        )
        
        # Guardar en registry
        dynamic_routes_registry[route_path] = {
            'template': template_path,
            'name': page_name,
            'function_name': dynamic_view.__name__
        }
        
        print(f"✅ Ruta dinámica registrada: {route_path}")
        return True
        
    except Exception as e:
        print(f"💥 Error al registrar ruta dinámica: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_dynamic_routes():
    """Obtiene todas las rutas dinámicas registradas"""
    return dynamic_routes_registry.copy()

def remove_dynamic_route(route_path):
    """
    Remueve una ruta dinámica (limitado por Flask)
    Nota: Flask no permite remover rutas fácilmente una vez registradas
    """
    if route_path in dynamic_routes_registry:
        del dynamic_routes_registry[route_path]
        print(f"🗑️ Ruta {route_path} removida del registry")
        return True
    return False

def load_dynamic_routes_from_db():
    """
    Carga rutas dinámicas desde la base de datos al iniciar la aplicación
    """
    try:
        from app.models import Page
        
        print("📚 Cargando rutas dinámicas desde BD...")
        
        # Obtener páginas que tienen templates asociados
        pages = Page.query.filter(Page.template_path.isnot(None)).all()
        
        for page in pages:
            if page.template_path and page.route:
                success = register_dynamic_route(
                    page.route,
                    page.template_path,
                    page.name
                )
                if success:
                    print(f"✅ Ruta dinámica cargada: {page.route}")
                else:
                    print(f"❌ Error cargando ruta: {page.route}")
        
        print(f"📚 {len(dynamic_routes_registry)} rutas dinámicas cargadas")
        
    except Exception as e:
        print(f"💥 Error cargando rutas dinámicas: {str(e)}")

def init_dynamic_routes(app):
    """
    Inicializa el sistema de rutas dinámicas
    """
    with app.app_context():
        load_dynamic_routes_from_db()

def initialize_dynamic_routes(app):
    """
    Inicializa todas las rutas dinámicas basadas en las páginas con template_path
    """
    try:
        with app.app_context():
            from app.models import Page
            
            # Buscar todas las páginas que tienen template_path definido
            pages_with_templates = Page.query.filter(
                Page.template_path.isnot(None),
                Page.active == True
            ).all()
            
            success_count = 0
            for page in pages_with_templates:
                if register_dynamic_route_with_template(
                    app=app,
                    route_path=page.route,
                    template_path=page.template_path,
                    page_name=page.name
                ):
                    success_count += 1
            
            logger.info(f"Rutas dinámicas inicializadas: {success_count}/{len(pages_with_templates)}")
            
    except Exception as e:
        logger.error(f"Error al inicializar rutas dinámicas: {e}")

def register_dynamic_route_with_template(app, route_path, template_path, page_name):
    """
    Registra una ruta dinámica que renderiza un template desde uploads/templates
    
    Args:
        app: Instancia de Flask
        route_path: Ruta URL (ej: '/mi-pagina')
        template_path: Ruta al template HTML en uploads/templates
        page_name: Nombre de la página para el título
    
    Returns:
        bool: True si se registró exitosamente, False si hubo error
    """
    try:
        # Verificar que el template existe
        template_full_path = os.path.join(app.root_path, 'uploads', 'templates', template_path)
        if not os.path.exists(template_full_path):
            logger.error(f"Template no encontrado: {template_full_path}")
            return False
        
        # Crear función de vista dinámica
        def dynamic_view():
            """Vista dinámica generada automáticamente"""
            try:
                if not current_user.is_authenticated:
                    return redirect(url_for('auth.login'))
                
                # Leer el contenido del template
                with open(template_full_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Renderizar usando template_string para poder pasar variables
                from flask import render_template_string
                return render_template_string(template_content, page_name=page_name)
                
            except Exception as e:
                logger.error(f"Error al renderizar template dinámico {template_path}: {e}")
                return render_template('errors/500.html'), 500
        
        # Generar nombre único para la función
        endpoint_name = f"dynamic_{route_path.replace('/', '_').replace('-', '_')}"
        dynamic_view.__name__ = endpoint_name
        
        # Registrar la ruta
        app.add_url_rule(
            route_path,
            endpoint=endpoint_name,
            view_func=dynamic_view,
            methods=['GET']
        )
        
        logger.info(f"Ruta dinámica registrada: {route_path} -> {template_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error al registrar ruta dinámica {route_path}: {e}")
        return False
