"""
Nuevas rutas API para organización de menú
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
from app import db
from app.models import Category, Page, MenuConfiguration
from app.services.menu_service import menu_service
from app.decorators import check_permissions

# Blueprint para organización de menú
menu_organization_bp = Blueprint('menu_organization', __name__, url_prefix='/api/menu')

@menu_organization_bp.route('/categories/reorder', methods=['POST'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def reorder_categories():
    """Reordenar categorías mediante drag and drop"""
    try:
        data = request.get_json()
        category_orders = data.get('categories', [])
        
        for item in category_orders:
            category_id = item.get('id')
            new_order = item.get('order')
            
            category = Category.query.get(category_id)
            if category:
                category.display_order = new_order
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Orden de categorías actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/pages/reorder', methods=['POST'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def reorder_pages():
    """Reordenar páginas dentro de una categoría"""
    try:
        data = request.get_json()
        page_orders = data.get('pages', [])
        category_id = data.get('category_id')
        
        for item in page_orders:
            page_id = item.get('id')
            new_order = item.get('order')
            
            page = Page.query.get(page_id)
            if page and page.category_id == category_id:
                page.display_order = new_order
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Orden de páginas actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/category/<int:category_id>/icon', methods=['PUT'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def update_category_icon(category_id):
    """Actualizar icono de una categoría"""
    try:
        data = request.get_json()
        new_icon = data.get('icon')
        
        if not new_icon:
            return jsonify({
                'success': False,
                'error': 'Icono es requerido'
            }), 400
        
        category = Category.query.get_or_404(category_id)
        category.icon = new_icon
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Icono actualizado correctamente',
            'category': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/page/<int:page_id>/icon', methods=['PUT'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def update_page_icon(page_id):
    """Actualizar icono de una página"""
    try:
        data = request.get_json()
        new_icon = data.get('icon')
        
        if not new_icon:
            return jsonify({
                'success': False,
                'error': 'Icono es requerido'
            }), 400
        
        page = Page.query.get_or_404(page_id)
        page.icon = new_icon
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Icono actualizado correctamente',
            'page': page.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/category/<int:category_id>/visibility', methods=['PUT'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def toggle_category_visibility(category_id):
    """Cambiar visibilidad de una categoría"""
    try:
        data = request.get_json()
        is_visible = data.get('is_visible', True)
        
        category = Category.query.get_or_404(category_id)
        category.is_visible = is_visible
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': f'Categoría {"mostrada" if is_visible else "ocultada"} correctamente',
            'category': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/page/<int:page_id>/visibility', methods=['PUT'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def toggle_page_visibility(page_id):
    """Cambiar visibilidad de una página"""
    try:
        data = request.get_json()
        is_visible = data.get('is_visible', True)
        
        page = Page.query.get_or_404(page_id)
        page.is_visible = is_visible
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': f'Página {"mostrada" if is_visible else "ocultada"} correctamente',
            'page': page.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/configuration', methods=['GET'])
@login_required
def get_menu_configuration():
    """Obtener configuración del menú"""
    try:
        config = MenuConfiguration.get_default_config()
        return jsonify({
            'success': True,
            'configuration': config.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/configuration', methods=['PUT'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def update_menu_configuration():
    """Actualizar configuración del menú"""
    try:
        data = request.get_json()
        
        config = MenuConfiguration.get_default_config()
        
        # Actualizar campos permitidos
        allowed_fields = ['sidebar_collapsed', 'theme', 'menu_style', 'show_icons', 'show_badges', 'custom_css']
        
        for field in allowed_fields:
            if field in data:
                setattr(config, field, data[field])
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Configuración actualizada correctamente',
            'configuration': config.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/preview', methods=['GET'])
@login_required
@check_permissions('ADMIN', 'SUPERADMIN')
def preview_menu():
    """Obtener vista previa del menú organizado"""
    try:
        # Obtener menú actual del usuario
        menu = menu_service.get_user_menu()
        
        return jsonify({
            'success': True,
            'menu': menu
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@menu_organization_bp.route('/icons', methods=['GET'])
@login_required
def get_available_icons():
    """Obtener lista de iconos disponibles"""
    # Lista de iconos Font Awesome más comunes para el sistema
    icons = [
        # Navegación
        'fas fa-home', 'fas fa-tachometer-alt', 'fas fa-bars', 'fas fa-folder', 'fas fa-folder-open',
        
        # Usuarios y permisos
        'fas fa-users', 'fas fa-user', 'fas fa-user-friends', 'fas fa-shield-alt', 'fas fa-key', 
        'fas fa-lock', 'fas fa-unlock', 'fas fa-user-shield',
        
        # Proyectos y tareas
        'fas fa-project-diagram', 'fas fa-tasks', 'fas fa-clipboard-list', 'fas fa-calendar',
        'fas fa-calendar-alt', 'fas fa-clock', 'fas fa-hourglass', 'fas fa-stopwatch',
        
        # Administración
        'fas fa-cogs', 'fas fa-cog', 'fas fa-wrench', 'fas fa-tools', 'fas fa-sliders-h',
        'fas fa-server', 'fas fa-database', 'fas fa-hdd',
        
        # Reportes y estadísticas
        'fas fa-chart-bar', 'fas fa-chart-line', 'fas fa-chart-pie', 'fas fa-analytics',
        'fas fa-file-alt', 'fas fa-file-excel', 'fas fa-file-pdf',
        
        # Documentos y archivos
        'fas fa-file', 'fas fa-file-text', 'fas fa-download', 'fas fa-upload',
        'fas fa-paperclip', 'fas fa-archive',
        
        # Comunicación
        'fas fa-envelope', 'fas fa-bell', 'fas fa-comment', 'fas fa-comments',
        'fas fa-phone', 'fas fa-fax',
        
        # Estados y alertas
        'fas fa-check', 'fas fa-times', 'fas fa-exclamation-triangle', 'fas fa-info-circle',
        'fas fa-question-circle', 'fas fa-plus', 'fas fa-minus', 'fas fa-edit',
        
        # Otros
        'fas fa-globe', 'fas fa-map', 'fas fa-building', 'fas fa-industry',
        'fas fa-search', 'fas fa-filter', 'fas fa-sort'
    ]
    
    return jsonify({
        'success': True,
        'icons': icons
    })

# Registrar el blueprint en la aplicación
def register_menu_organization_routes(app):
    """Registrar las rutas de organización de menú"""
    app.register_blueprint(menu_organization_bp)
