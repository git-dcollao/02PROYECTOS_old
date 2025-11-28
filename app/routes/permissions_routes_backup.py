"""
Gestión de Permisos por Página y Rol
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.routes.auth_routes import admin_required
from app.models import db, Category, Page, PagePermission, UserRole
import json
import os

permissions_bp = Blueprint('permissions', __name__, url_prefix='/permissions')

class PagePermissionManager:
    """Gestor de permisos por página usando base de datos"""
    
    def __init__(self, app=None):
        # Ya no usamos archivo JSON, todo se maneja con la BD
        pass
    
    def get_pages_by_category(self):
        """Obtener páginas organizadas por categoría desde la BD"""
        try:
            categories_dict = {}
            
            # Obtener todas las categorías con sus páginas
            categories = Category.query.all()
            
            for category in categories:
                category_name = category.name
                categories_dict[category_name] = []
                
                for page in category.pages:
                    if page.active:  # Solo páginas activas
                        categories_dict[category_name].append({
                            'route': page.route,
                            'name': page.name,
                            'description': page.description,
                            'roles': [perm.role.name for perm in page.permissions]
                        })
            
            return categories_dict
            
        except Exception as e:
            print(f"💥 Error al obtener páginas por categoría: {str(e)}")
            return {}
    
    def has_permission(self, user_role, page_route):
        """Verificar si un rol tiene permiso para acceder a una página"""
        try:
            if not user_role:
                return False
            
            # Convertir string a enum si es necesario
            if isinstance(user_role, str):
                try:
                    user_role = UserRole(user_role.lower())
                except ValueError:
                    return False
            
            # Buscar la página
            page = Page.query.filter_by(route=page_route, active=True).first()
            if not page:
                return False
            
            # Verificar si el rol tiene permiso
            permission = PagePermission.query.filter_by(
                page_id=page.id,
                role=user_role
            ).first()
            
            return permission is not None
            
        except Exception as e:
            print(f"💥 Error al verificar permiso: {str(e)}")
            return False
    
    def get_user_pages(self, user_role):
        """Obtener todas las páginas accesibles para un rol"""
        try:
            if isinstance(user_role, str):
                try:
                    user_role = UserRole(user_role.lower())
                except ValueError:
                    return []
            
            # Obtener permisos del rol
            permissions = PagePermission.query.filter_by(role=user_role).all()
            
            accessible_pages = []
            for permission in permissions:
                if permission.page.active:
                    accessible_pages.append({
                        'route': permission.page.route,
                        'name': permission.page.name,
                        'category': permission.page.category_obj.name,
                        'description': permission.page.description
                    })
            
            return accessible_pages
            
        except Exception as e:
            print(f"💥 Error al obtener páginas del usuario: {str(e)}")
            return []
            'auth.create_user': {
                'name': 'Crear Usuario',
                'category': 'Usuarios',
                'roles': ['SUPERADMIN', 'ADMIN'],
                'description': 'Formulario para crear nuevos usuarios'
            },
            'auth.edit_user': {
                'name': 'Editar Usuario',
                'category': 'Usuarios',
                'roles': ['SUPERADMIN', 'ADMIN'],
                'description': 'Modificar datos de usuarios existentes'
            },
            'auth.delete_user': {
                'name': 'Eliminar Usuario',
                'category': 'Usuarios',
                'roles': ['SUPERADMIN'],
                'description': 'Eliminar usuarios del sistema'
            },
            
            # Proyectos
            'proyectos.list_projects': {
                'name': 'Lista de Proyectos',
                'category': 'Proyectos',
                'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR'],
                'description': 'Ver todos los proyectos'
            },
            'proyectos.create_project': {
                'name': 'Crear Proyecto',
                'category': 'Proyectos',
                'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR'],
                'description': 'Formulario para crear nuevos proyectos'
            },
            'proyectos.edit_project': {
                'name': 'Editar Proyecto',
                'category': 'Proyectos',
                'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR'],
                'description': 'Modificar datos de proyectos'
            },
            'proyectos.view_gantt': {
                'name': 'Diagrama Gantt',
                'category': 'Proyectos',
                'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR'],
                'description': 'Ver cronograma de proyectos'
            },
            
            # Reportes
            'reportes.financial': {
                'name': 'Reportes Financieros',
                'category': 'Reportes',
                'roles': ['SUPERADMIN', 'ADMIN'],
                'description': 'Informes financieros y presupuestos'
            },
            'reportes.progress': {
                'name': 'Reportes de Avance',
                'category': 'Reportes',
                'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR'],
                'description': 'Reportes de progreso de proyectos'
            },
            'reportes.export': {
                'name': 'Exportar Datos',
                'category': 'Reportes',
                'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR'],
                'description': 'Exportar información del sistema'
            },
            
            # Configuración
            'config.system': {
                'name': 'Configuración Sistema',
                'category': 'Configuración',
                'roles': ['SUPERADMIN'],
                'description': 'Configuraciones generales del sistema'
            },
            'config.backup': {
                'name': 'Respaldos',
                'category': 'Configuración',
                'roles': ['SUPERADMIN', 'ADMIN'],
                'description': 'Gestión de respaldos de datos'
            }
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar con la aplicación Flask"""
        app.page_permissions = self
        
        # Crear archivo de permisos si no existe
        if not os.path.exists(self.permissions_file):
            self.save_permissions(self.default_permissions)
    
    def load_permissions(self):
        """Cargar permisos desde archivo"""
        try:
            with open(self.permissions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.default_permissions.copy()
        except json.JSONDecodeError:
            return self.default_permissions.copy()
    
    def save_permissions(self, permissions):
        """Guardar permisos en archivo"""
        try:
            with open(self.permissions_file, 'w', encoding='utf-8') as f:
                json.dump(permissions, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando permisos: {e}")
            return False
    
    def can_access_page(self, user_role, page_route):
        """Verificar si un rol puede acceder a una página"""
        permissions = self.load_permissions()
        
        if page_route not in permissions:
            # Si la página no está definida, permitir solo a SUPERADMIN
            return user_role == 'SUPERADMIN'
        
        return user_role in permissions[page_route]['roles']
    
    def get_pages_by_category(self):
        """Obtener páginas organizadas por categoría"""
        permissions = self.load_permissions()
        categories = {}
        
        for page_route, page_data in permissions.items():
            category = page_data.get('category', 'Sin Categoría')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                'route': page_route,
                **page_data
            })
        
        return categories

# Instancia global del gestor
permission_manager = PagePermissionManager()

@permissions_bp.route('/')
@login_required
@admin_required
def index():
    """Página principal de gestión de permisos"""
    categories = permission_manager.get_pages_by_category()
    # Calcular total de páginas desde las categorías
    total_pages = sum(len(pages) for pages in categories.values())
    roles = ['USUARIO', 'SUPERVISOR', 'ADMIN', 'SUPERADMIN']
    
    return render_template('permissions/index.html', 
                         categories=categories, 
                         total_pages=total_pages,
                         roles=roles)

@permissions_bp.route('/api/update', methods=['POST'])
@login_required
@admin_required
def update_permissions():
    """API para actualizar permisos"""
    try:
        data = request.get_json()
        page_route = data.get('page_route')
        new_roles = data.get('roles', [])
        
        if not page_route:
            return jsonify({'success': False, 'message': 'Ruta de página requerida'})
        
        # Cargar permisos actuales
        permissions = permission_manager.load_permissions()
        
        if page_route not in permissions:
            return jsonify({'success': False, 'message': 'Página no encontrada'})
        
        # Actualizar roles
        permissions[page_route]['roles'] = new_roles
        
        # Guardar cambios
        if permission_manager.save_permissions(permissions):
            return jsonify({
                'success': True, 
                'message': f'Permisos actualizados para {permissions[page_route]["name"]}'
            })
        else:
            return jsonify({'success': False, 'message': 'Error al guardar cambios'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@permissions_bp.route('/api/add-page', methods=['POST'])
@login_required
@admin_required
def add_page():
    """API para agregar nueva página"""
    try:
        data = request.get_json()
        
        required_fields = ['route', 'name', 'category', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} requerido'})
        
        # Cargar permisos actuales
        permissions = permission_manager.load_permissions()
        
        # Verificar si la ruta ya existe
        if data['route'] in permissions:
            return jsonify({'success': False, 'message': 'La ruta ya existe'})
        
        # Agregar nueva página
        permissions[data['route']] = {
            'name': data['name'],
            'category': data['category'],
            'description': data['description'],
            'roles': data.get('roles', ['SUPERADMIN'])
        }
        
        # Guardar cambios
        if permission_manager.save_permissions(permissions):
            return jsonify({
                'success': True,
                'message': f'Página "{data["name"]}" agregada exitosamente'
            })
        else:
            return jsonify({'success': False, 'message': 'Error al guardar cambios'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@permissions_bp.route('/api/delete-page', methods=['POST'])
@login_required
@admin_required
def delete_page():
    """API para eliminar página"""
    try:
        data = request.get_json()
        page_route = data.get('page_route')
        
        if not page_route:
            return jsonify({'success': False, 'message': 'Ruta de página requerida'})
        
        # Cargar permisos actuales
        permissions = permission_manager.load_permissions()
        
        if page_route not in permissions:
            return jsonify({'success': False, 'message': 'Página no encontrada'})
        
        # Eliminar página
        page_name = permissions[page_route]['name']
        del permissions[page_route]
        
        # Guardar cambios
        if permission_manager.save_permissions(permissions):
            return jsonify({
                'success': True,
                'message': f'Página "{page_name}" eliminada exitosamente'
            })
        else:
            return jsonify({'success': False, 'message': 'Error al guardar cambios'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

def check_page_permission(page_route):
    """Decorador para verificar permisos de página usando el sistema dinámico"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión para acceder', 'error')
                return redirect(url_for('auth.login'))
            
            user_role = current_user.rol.name
            
            if not permission_manager.can_access_page(user_role, page_route):
                flash('No tiene permisos para acceder a esta página', 'error')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Función auxiliar para usar en templates
def can_access_page(user_role, page_route):
    """Función auxiliar para verificar acceso desde templates"""
    return permission_manager.can_access_page(user_role, page_route)

# Registrar función en el contexto de templates
@permissions_bp.app_context_processor  
def inject_permission_functions():
    """Inyectar funciones de permisos en todos los templates"""
    return dict(
        can_access_page=can_access_page,
        permission_manager=permission_manager
    )

@permissions_bp.route('/api/add-category', methods=['POST'])
@login_required
@admin_required
def add_category():
    """API para agregar nueva categoría"""
    try:
        print(f"🔧 add_category() llamada por usuario: {current_user.email}")
        
        data = request.get_json()
        print(f"📝 Datos recibidos: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos JSON'})
        
        category_name = data.get('name', '').strip()
        category_color = data.get('color', 'primary')
        
        print(f"🏷️ Categoría: '{category_name}', Color: '{category_color}'")
        
        if not category_name:
            return jsonify({'success': False, 'message': 'El nombre de la categoría es requerido'})
        
        # Verificar si la categoría ya existe
        categories = permission_manager.get_pages_by_category()
        print(f"📂 Categorías existentes: {list(categories.keys())}")
        
        if category_name in categories:
            return jsonify({'success': False, 'message': 'La categoría ya existe'})
        
        print(f"✅ Categoría '{category_name}' es válida")
        
        return jsonify({
            'success': True, 
            'message': f'Categoría "{category_name}" creada exitosamente. Ahora puedes agregar páginas a esta categoría.',
            'category': category_name,
            'color': category_color
        })
        
    except Exception as e:
        print(f"💥 Error en add_category: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@permissions_bp.route('/api/delete-category', methods=['POST'])
@login_required
@admin_required
def delete_category():
    """API para eliminar categoría vacía"""
    try:
        data = request.get_json()
        category_name = data.get('category', '')
        
        if not category_name:
            return jsonify({'success': False, 'message': 'Nombre de categoría requerido'})
        
        categories = permission_manager.get_pages_by_category()
        
        if category_name not in categories:
            return jsonify({'success': False, 'message': 'La categoría no existe'})
        
        if len(categories[category_name]) > 0:
            return jsonify({'success': False, 'message': 'No se puede eliminar una categoría que tiene páginas'})
        
        # Como la categoría no tiene páginas, no hay nada que eliminar del JSON
        # Las categorías se crean automáticamente cuando se asignan páginas
        return jsonify({'success': True, 'message': f'Categoría "{category_name}" eliminada'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@permissions_bp.route('/api/update-page', methods=['POST'])
@login_required  
@admin_required
def update_page():
    """API para actualizar una página existente"""
    try:
        data = request.get_json()
        original_route = data.get('original_route', '')
        new_route = data.get('route', '').strip()
        name = data.get('name', '').strip()
        category = data.get('category', '').strip()
        new_category = data.get('new_category', '').strip()
        description = data.get('description', '').strip()
        roles = data.get('roles', [])
        
        if not all([original_route, new_route, name, description]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        if not roles:
            return jsonify({'success': False, 'message': 'Debe seleccionar al menos un rol'})
        
        # Usar nueva categoría si se especificó
        if category == 'NUEVA' and new_category:
            category = new_category
        elif category == 'NUEVA':
            return jsonify({'success': False, 'message': 'Debe especificar el nombre de la nueva categoría'})
        
        permissions = permission_manager.load_permissions()
        
        # Verificar que la página original existe
        if original_route not in permissions:
            return jsonify({'success': False, 'message': 'La página original no existe'})
        
        # Si cambió la ruta, verificar que la nueva no exista
        if new_route != original_route and new_route in permissions:
            return jsonify({'success': False, 'message': 'Ya existe una página con esa ruta'})
        
        # Actualizar la página
        page_data = {
            'name': name,
            'category': category,
            'roles': roles,
            'description': description
        }
        
        # Si cambió la ruta, eliminar la antigua y crear la nueva
        if new_route != original_route:
            del permissions[original_route]
            permissions[new_route] = page_data
        else:
            permissions[original_route] = page_data
        
        if permission_manager.save_permissions(permissions):
            return jsonify({
                'success': True,
                'message': f'Página "{name}" actualizada exitosamente',
                'page': {
                    'route': new_route,
                    **page_data
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Error al guardar los cambios'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@permissions_bp.route('/api/get-page', methods=['GET'])
@login_required
@admin_required
def get_page():
    """API para obtener datos de una página específica"""
    try:
        page_route = request.args.get('route', '')
        
        if not page_route:
            return jsonify({'success': False, 'message': 'Ruta de página requerida'})
        
        permissions = permission_manager.load_permissions()
        
        if page_route not in permissions:
            return jsonify({'success': False, 'message': 'La página no existe'})
        
        page_data = permissions[page_route]
        page_data['route'] = page_route
        
        return jsonify({
            'success': True,
            'page': page_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
