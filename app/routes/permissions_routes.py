"""
Gestión de Permisos por Página y Rol - Nueva Versión con Base de Datos
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.routes.auth_routes import admin_required
from app.models import db, Category, Page, PagePermission, UserRole, CustomRole
from app.services.menu_service import menu_service
import json
import os
import logging

# Configurar logger
logger = logging.getLogger(__name__)

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
                            'roles': [perm.role_name for perm in page.permissions]
                        })
            
            return categories_dict
            
        except Exception as e:
            logger.error(f"Error al obtener páginas por categoría: {str(e)}")
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
            logger.error(f"Error al verificar permiso: {str(e)}")
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
            logger.error(f"Error al obtener páginas del usuario: {str(e)}")
            return []

# Instancia global del gestor
permission_manager = PagePermissionManager()

# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@permissions_bp.route('/')
@login_required
@admin_required
def index():
    """Página principal del gestor de permisos unificado"""
    try:
        # Obtener todas las categorías con sus páginas
        categories = Category.query.all()
        pages_by_category = []
        
        total_pages = 0
        total_permissions = 0
        
        for category in categories:
            # Obtener páginas de esta categoría
            pages = Page.query.filter_by(category_id=category.id, active=True).all()
            
            pages_data = []
            for page in pages:
                # Obtener permisos de esta página
                permissions = PagePermission.query.filter_by(page_id=page.id).all()
                page_permissions = [perm.role_name.lower() for perm in permissions]
                total_permissions += len(permissions)
                
                pages_data.append({
                    'id': page.id,
                    'name': page.name,
                    'route': page.route,
                    'permissions': page_permissions
                })
            
            if pages_data:  # Solo incluir categorías que tienen páginas
                pages_by_category.append({
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'color': category.color,
                        'description': category.description,
                        'page_count': len(pages_data)
                    },
                    'pages': pages_data
                })
            
            total_pages += len(pages_data)
        
        # Obtener todas las páginas para la tabla principal
        all_pages = Page.query.filter_by(active=True).all()
        
        # Estructurar páginas con datos completos
        pages_data = []
        for page in all_pages:
            try:
                # Obtener roles permitidos para esta página
                permissions = PagePermission.query.filter_by(page_id=page.id).all()
                allowed_roles = []
                for perm in permissions:
                    # Crear objeto simple para compatibilidad con template
                    role_obj = type('obj', (object,), {'name': perm.role_name})()
                    allowed_roles.append(role_obj)
                
                # Verificar atributos de página
                page_name = getattr(page, 'name', 'Sin nombre')
                page_route = getattr(page, 'route', '/unknown')
                page_template_path = getattr(page, 'template_path', None)
                
                # Obtener categoría de forma segura
                try:
                    category_name = page.category_obj.name if page.category_obj else 'Sin categoría'
                except AttributeError:
                    # Si no funciona category_obj, buscar por category_id
                    if hasattr(page, 'category_id') and page.category_id:
                        category = Category.query.get(page.category_id)
                        category_name = category.name if category else 'Sin categoría'
                    else:
                        category_name = 'Sin categoría'
                
                # Crear objeto página con estructura esperada por el template
                page_obj = type('obj', (object,), {
                    'name': page_name,
                    'route': page_route,
                    'template_path': page_template_path,
                    'category': category_name,
                    'allowed_roles': allowed_roles
                })()
                
                pages_data.append(page_obj)
                
            except Exception as page_error:
                logger.error(f"Error procesando página {getattr(page, 'id', 'unknown')}: {str(page_error)}")
                continue
        
        # Obtener roles disponibles
        from app.models import CustomRole
        system_roles = ['SUPERADMIN']  # Solo SUPERADMIN es rol del sistema ahora
        custom_roles = [role.name for role in CustomRole.query.filter_by(active=True).all()]
        all_role_names = system_roles + custom_roles
        
        # Crear objetos de rol para compatibilidad con template
        roles_data = []
        for role_name in all_role_names:
            role_obj = type('obj', (object,), {'name': role_name})()
            roles_data.append(role_obj)
        
        return render_template('permissions/index.html',
                             pages=pages_data,
                             categories=categories,
                             roles=roles_data,
                             total_categories=len(categories),
                             total_pages=total_pages,
                             total_permissions=total_permissions)
        
    except Exception as e:
        logger.error(f"Error en index(): {str(e)}")
        flash(f'Error al cargar permisos: {str(e)}', 'error')
        return redirect(url_for('main.index'))

# ============================================================================
# APIs PARA GESTIÓN DE CATEGORÍAS
# ============================================================================

@permissions_bp.route('/api/add-category', methods=['POST'])
@login_required
@admin_required
def add_category():
    """API para agregar nueva categoría"""
    try:
        logger.debug(f"add_category() llamada por usuario: {current_user.email}")
        
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos JSON'})
        
        category_name = data.get('name', '').strip()
        category_color = data.get('color', 'primary')
        
        logger.debug(f"Categoría: '{category_name}', Color: '{category_color}'")
        
        if not category_name:
            return jsonify({'success': False, 'message': 'El nombre de la categoría es requerido'})
        
        # Verificar si la categoría ya existe
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            return jsonify({'success': False, 'message': 'La categoría ya existe'})
        
        logger.debug(f"✅ Categoría '{category_name}' es válida")
        
        # Crear la nueva categoría
        new_category = Category(
            name=category_name,
            color=category_color,
            description=f'Categoría {category_name} creada desde la interfaz web'
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        # Limpiar cache del menú para reflejar cambios inmediatamente
        menu_service.clear_cache()
        
        logger.debug(f"Categoría '{category_name}' guardada en la base de datos")
        
        return jsonify({
            'success': True, 
            'message': f'Categoría "{category_name}" creada exitosamente. Ahora puedes agregar páginas a esta categoría.',
            'category': category_name,
            'color': category_color
        })
        
    except Exception as e:
        logger.error(f"Error en add_category: {str(e)}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@permissions_bp.route('/api/update-category', methods=['POST'])
@login_required
@admin_required
def update_category():
    """API para actualizar el nombre de una categoría"""
    try:
        logger.info(f"🔄 update_category() llamada por usuario: {current_user.email}")
        
        data = request.get_json()
        logger.info(f"📋 Datos recibidos: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos JSON'})
        
        category_id = data.get('categoryId')
        old_name = data.get('oldName', '').strip()
        new_name = data.get('newName', '').strip()
        
        logger.info(f"📝 Actualización: ID={category_id}, '{old_name}' → '{new_name}'")
        
        if not category_id or not new_name:
            return jsonify({'success': False, 'message': 'ID de categoría y nuevo nombre son requeridos'})
        
        # Buscar la categoría por ID
        category = Category.query.get(category_id)
        if not category:
            logger.warning(f"❌ Categoría con ID {category_id} no encontrada")
            return jsonify({'success': False, 'message': 'Categoría no encontrada'})
        
        # Verificar si el nuevo nombre ya existe en otra categoría
        existing_category = Category.query.filter(
            Category.name == new_name,
            Category.id != category_id
        ).first()
        
        if existing_category:
            logger.warning(f"❌ Ya existe una categoría con el nombre '{new_name}'")
            return jsonify({'success': False, 'message': f'Ya existe una categoría con el nombre "{new_name}"'})
        
        # Actualizar el nombre
        old_category_name = category.name
        category.name = new_name
        
        db.session.commit()
        menu_service.clear_cache()
        
        logger.info(f"✅ Categoría actualizada: '{old_category_name}' → '{new_name}'")
        
        return jsonify({
            'success': True, 
            'message': f'Categoría actualizada de "{old_category_name}" a "{new_name}" exitosamente',
            'oldName': old_category_name,
            'newName': new_name
        })
        
    except Exception as e:
        logger.error(f"❌ Error en update_category: {str(e)}")
        db.session.rollback()
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
        category_id = data.get('id')
        
        if not category_id:
            return jsonify({'success': False, 'message': 'ID de categoría requerido'})
        
        # Buscar la categoría por ID
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'success': False, 'message': 'La categoría no existe'})
        
        # Verificar que no tenga páginas
        page_count = Page.query.filter_by(category_id=category.id, active=True).count()
        if page_count > 0:
            return jsonify({'success': False, 'message': f'No se puede eliminar una categoría que tiene {page_count} páginas asignadas'})
        
        category_name = category.name  # Guardar el nombre antes de eliminar
        
        # Eliminar la categoría
        db.session.delete(category)
        db.session.commit()
        
        # Limpiar cache del menú para reflejar cambios inmediatamente
        menu_service.clear_cache()
        
        return jsonify({
            'success': True, 
            'message': f'Categoría "{category_name}" eliminada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al eliminar categoría: {str(e)}'})

@permissions_bp.route('/api/update-category', methods=['POST'])
@login_required
@admin_required
def get_category():
    """API para obtener datos de una categoría"""
    try:
        category_name = request.args.get('name')
        if not category_name:
            return jsonify({'success': False, 'message': 'Nombre de categoría requerido'})
        
        # Buscar la categoría
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            return jsonify({'success': False, 'message': 'Categoría no encontrada'})
        
        return jsonify({
            'success': True,
            'category': category.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al obtener categoría: {str(e)}'})

# ============================================================================
# APIs PARA GESTIÓN DE PÁGINAS
# ============================================================================

@permissions_bp.route('/api/add-page', methods=['POST'])
@login_required
@admin_required
def add_page():
    """API para agregar nueva página con permisos"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        route = data.get('route', '').strip()
        category_name = data.get('category', '').strip()
        roles = data.get('roles', [])
        new_category_data = data.get('new_category')
        template_path = data.get('template_path')  # Nuevo campo
        
        logger.debug(f"add_page() - Datos recibidos: {data}")
        
        if not all([name, route, category_name, roles]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        # Verificar que no exista ya la página
        existing_page = Page.query.filter_by(route=route).first()
        if existing_page:
            return jsonify({'success': False, 'message': 'Ya existe una página con esa ruta'})
        
        # Crear nueva categoría si es necesario
        category_id = None
        if new_category_data:
            new_category = Category(
                name=new_category_data['name'],
                color=new_category_data['color'],
                description=f"Categoría creada automáticamente para {name}"
            )
            db.session.add(new_category)
            db.session.flush()  # Para obtener el ID
            category_id = new_category.id
            logger.debug(f"Nueva categoría creada: {new_category_data['name']}")
        else:
            # Buscar categoría existente
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                return jsonify({'success': False, 'message': f'Categoría "{category_name}" no encontrada'})
            category_id = category.id
        
        # Crear la nueva página
        new_page = Page(
            name=name,
            route=route,
            category_id=category_id,
            description=f"Página {name}",
            active=True,
            template_path=template_path  # Agregar el template_path
        )
        
        db.session.add(new_page)
        db.session.flush()  # Para obtener el ID
        
        # Crear permisos para los roles seleccionados
        permissions_created = 0
        for role_str in roles:
            try:
                role = UserRole(role_str.lower())
                permission = PagePermission(
                    page_id=new_page.id,
                    role=role
                )
                db.session.add(permission)
                permissions_created += 1
            except ValueError:
                logger.warning(f"Rol inválido: {role_str}")
                continue
        
        db.session.commit()
        
        # Limpiar cache del menú para reflejar cambios inmediatamente
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': f'Página "{name}" creada exitosamente con {permissions_created} permisos'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en add_page(): {str(e)}")
        return jsonify({'success': False, 'message': f'Error al crear página: {str(e)}'})

@permissions_bp.route('/api/get-page', methods=['GET'])
@login_required
@admin_required
def get_page():
    """API para obtener datos de una página"""
    try:
        page_route = request.args.get('route')
        if not page_route:
            return jsonify({'success': False, 'message': 'Ruta de página requerida'})
        
        # Buscar la página
        page = Page.query.filter_by(route=page_route).first()
        if not page:
            return jsonify({'success': False, 'message': 'Página no encontrada'})
        
        return jsonify({
            'success': True,
            'page': page.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al obtener página: {str(e)}'})

@permissions_bp.route('/api/update-page', methods=['POST'])
@login_required
@admin_required
def update_page():
    """API para actualizar una página"""
    try:
        data = request.get_json()
        
        logger.debug(f"update_page() - Datos recibidos: {data}")
        
        original_route = data.get('originalRoute')
        new_route = data.get('route', '').strip()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip() or f"Página {name}"  # Valor por defecto
        category_name = data.get('category', '').strip()
        roles = data.get('roles', [])
        template_path = data.get('template_path')  # Nuevo campo
        
        logger.debug(f"Campos procesados - originalRoute: {original_route}, newRoute: {new_route}, name: {name}, category: {category_name}")
        
        if not all([original_route, new_route, name, category_name]):
            missing_fields = []
            if not original_route: missing_fields.append('originalRoute')
            if not new_route: missing_fields.append('route')
            if not name: missing_fields.append('name')
            if not category_name: missing_fields.append('category')
            
            error_msg = f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            logger.error(f"{error_msg}")
            return jsonify({'success': False, 'message': error_msg})
        
        # Buscar la página
        page = Page.query.filter_by(route=original_route).first()
        if not page:
            logger.error(f"Página no encontrada con ruta: {original_route}")
            return jsonify({'success': False, 'message': 'Página no encontrada'})
        
        # Buscar o crear la categoría
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            logger.error(f"Categoría no encontrada: {category_name}")
            return jsonify({'success': False, 'message': f'Categoría "{category_name}" no existe'})
        
        logger.debug(f"Validaciones pasadas, actualizando página...")
        
        # Actualizar página
        page.route = new_route
        page.name = name
        page.description = description
        page.category_id = category.id
        if template_path is not None:  # Permitir None para mantener el valor actual
            page.template_path = template_path
        
        # Eliminar permisos existentes
        PagePermission.query.filter_by(page_id=page.id).delete()
        
        # Agregar nuevos permisos
        for role_str in roles:
            try:
                role_enum = UserRole(role_str.lower())
                permission = PagePermission(page_id=page.id, role=role_enum)
                db.session.add(permission)
            except ValueError:
                pass  # Ignorar roles no válidos
        
        db.session.commit()
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': f'Página "{name}" actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al actualizar página: {str(e)}'})

@permissions_bp.route('/api/delete-page', methods=['POST'])
@login_required
@admin_required
def delete_page():
    """Eliminar página y todos sus permisos asociados"""
    try:
        data = request.get_json()
        route = data.get('route')
        
        if not route:
            return jsonify({'success': False, 'message': 'Ruta de la página es requerida'})
        
        # Buscar la página
        page = Page.query.filter_by(route=route).first()
        if not page:
            return jsonify({'success': False, 'message': 'Página no encontrada'})
        
        page_name = page.name
        
        # Eliminar primero todos los permisos asociados a la página
        permissions_deleted = PagePermission.query.filter_by(page_id=page.id).delete()
        
        # Eliminar la página
        db.session.delete(page)
        db.session.commit()
        
        # Limpiar cache del menú para reflejar cambios inmediatamente
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': f'Página "{page_name}" eliminada exitosamente (con {permissions_deleted} permisos asociados)'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al eliminar página: {str(e)}'})

@permissions_bp.route('/api/add-role', methods=['POST'])
@login_required
@admin_required
def add_role():
    """Agregar nuevo rol personalizado al sistema"""
    try:
        data = request.get_json()
        role_name = data.get('name', '').strip().upper()
        
        if not role_name:
            return jsonify({'success': False, 'message': 'Nombre del rol es requerido'})
        
        # Verificar que no sea un rol del sistema
        system_roles = ['SUPERADMIN']  # Solo SUPERADMIN es rol del sistema ahora
        if role_name in system_roles:
            return jsonify({'success': False, 'message': 'Este rol ya existe en el sistema'})
        
        # Verificar que no exista ya en roles personalizados
        from app.models import CustomRole
        existing_role = CustomRole.query.filter_by(name=role_name).first()
        if existing_role:
            return jsonify({'success': False, 'message': 'Este rol personalizado ya existe'})
        
        # Crear el nuevo rol personalizado
        new_role = CustomRole(name=role_name, description=f'Rol personalizado: {role_name}')
        db.session.add(new_role)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Rol "{role_name}" agregado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al agregar rol: {str(e)}'})

@permissions_bp.route('/api/edit-role', methods=['POST'])
@login_required
@admin_required
def edit_role():
    """Editar rol personalizado del sistema"""
    try:
        data = request.get_json()
        original_name = data.get('original_name', '').strip().upper()
        new_name = data.get('name', '').strip().upper()
        
        if not original_name or not new_name:
            return jsonify({'success': False, 'message': 'Nombres del rol son requeridos'})
        
        # Verificar que no sean roles del sistema
        system_roles = ['SUPERADMIN']  # Solo SUPERADMIN es rol del sistema ahora
        if original_name in system_roles:
            return jsonify({'success': False, 'message': 'No se pueden editar los roles del sistema'})
        
        if new_name in system_roles:
            return jsonify({'success': False, 'message': 'No se puede usar un nombre de rol del sistema'})
        
        # Buscar el rol personalizado a editar
        from app.models import CustomRole
        role = CustomRole.query.filter_by(name=original_name).first()
        if not role:
            return jsonify({'success': False, 'message': 'Rol personalizado no encontrado'})
        
        # Verificar que el nuevo nombre no exista ya (si es diferente)
        if original_name != new_name:
            existing_role = CustomRole.query.filter_by(name=new_name).first()
            if existing_role:
                return jsonify({'success': False, 'message': 'Ya existe un rol con ese nombre'})
        
        # Actualizar el rol
        role.name = new_name
        role.description = f'Rol personalizado: {new_name}'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Rol editado de "{original_name}" a "{new_name}" exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al editar rol: {str(e)}'})

@permissions_bp.route('/api/toggle-permission', methods=['POST'])
@login_required
@admin_required
def toggle_permission():
    """Alternar permisos de página para un rol específico (sistema + personalizados)"""
    try:
        data = request.get_json()
        logger.info(f"🔄 Toggle permission - Datos recibidos: {data}")
        
        page_route = data.get('route', '').strip()
        role_name = data.get('role', '').strip().upper()
        enabled = data.get('enabled', False)
        
        logger.info(f"📋 Procesando: route={page_route}, role={role_name}, enabled={enabled}")
        
        if not page_route or not role_name:
            return jsonify({'success': False, 'message': 'Datos incompletos'})
        
        # Buscar la página
        from app.models import Page, PagePermission, UserRole, CustomRole
        page = Page.query.filter_by(route=page_route).first()
        logger.info(f"🔍 Página encontrada: {page.name if page else 'No encontrada'}")
        
        if not page:
            logger.warning(f"❌ Página no encontrada para ruta: {page_route}")
            return jsonify({'success': False, 'message': 'Página no encontrada'})
        
        # Verificar si es un rol del sistema o personalizado
        is_system_role = role_name in ['SUPERADMIN']  # Solo SUPERADMIN es rol del sistema ahora
        logger.info(f"🔐 Tipo de rol: {'Sistema' if is_system_role else 'Personalizado'}")
        
        if enabled:
            # Agregar permiso si no existe
            existing_permission = PagePermission.query.filter_by(
                page_id=page.id, 
                role_name=role_name
            ).first()
            
            logger.info(f"📝 Permiso existente: {'Sí' if existing_permission else 'No'}")
            
            if not existing_permission:
                new_permission = PagePermission(page_id=page.id)
                
                if is_system_role:
                    # Rol del sistema
                    try:
                        system_role = UserRole[role_name]
                        new_permission.system_role = system_role
                        new_permission.role_name = role_name
                        new_permission.custom_role_id = None
                        logger.info(f"✅ Creando permiso para rol del sistema: {role_name}")
                    except KeyError:
                        logger.error(f"❌ Rol del sistema no válido: {role_name}")
                        return jsonify({'success': False, 'message': 'Rol del sistema no válido'})
                else:
                    # Rol personalizado
                    custom_role = CustomRole.query.filter_by(name=role_name, active=True).first()
                    if not custom_role:
                        logger.error(f"❌ Rol personalizado no encontrado: {role_name}")
                        return jsonify({'success': False, 'message': 'Rol personalizado no encontrado'})
                    
                    new_permission.system_role = None
                    new_permission.custom_role_id = custom_role.id
                    new_permission.role_name = role_name
                    logger.info(f"✅ Creando permiso para rol personalizado: {role_name}")
                
                db.session.add(new_permission)
                logger.info(f"💾 Permiso agregado a la sesión")
            else:
                logger.info(f"ℹ️ Permiso ya existe, no se requiere acción para habilitar")
        else:
            # Eliminar permiso si existe
            permission = PagePermission.query.filter_by(
                page_id=page.id, 
                role_name=role_name
            ).first()
            
            logger.info(f"🗑️ Permiso a eliminar: {'Encontrado' if permission else 'No encontrado'}")
            
            if permission:
                db.session.delete(permission)
                logger.info(f"💾 Permiso eliminado de la sesión")
            else:
                logger.info(f"ℹ️ Permiso no existe, no se requiere acción para deshabilitar")
        
        # Commit antes del mensaje de éxito
        db.session.commit()
        logger.info(f"✅ Cambios confirmados en la base de datos")
        
        # Limpiar cache del menú para reflejar cambios inmediatamente
        menu_service.clear_cache()
        
        action = "habilitado" if enabled else "deshabilitado"
        role_type = "del sistema" if is_system_role else "personalizado"
        success_message = f'Permiso {action} para rol {role_type} {role_name} en {page.name}'
        
        logger.info(f"🎉 Operación exitosa: {success_message}")
        
        return jsonify({
            'success': True, 
            'message': success_message
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en toggle_permission: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error al cambiar permiso: {str(e)}'})

# ============================================================================
# GESTIÓN DE TEMPLATES
# ============================================================================

@permissions_bp.route('/api/get-templates', methods=['GET'])
@login_required
def get_templates():
    """Obtener lista de templates disponibles"""
    try:
        import os
        templates = []
        
        # Buscar en carpeta templates
        template_dir = os.path.join(current_app.root_path, 'templates')
        
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                # Excluir carpetas especiales
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__']]
                
                for file in files:
                    if file.endswith(('.html', '.htm')):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, template_dir)
                        
                        # Obtener carpeta relativa
                        folder = os.path.dirname(relative_path) if os.path.dirname(relative_path) else 'templates'
                        
                        # Leer preview del archivo (primeras líneas)
                        preview = ''
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                preview = f.read(200) + '...'
                        except:
                            preview = 'No se pudo leer el archivo'
                        
                        templates.append({
                            'name': file,
                            'path': relative_path.replace('\\', '/'),
                            'folder': folder,
                            'preview': preview
                        })
        
        # Ordenar por carpeta y nombre
        templates.sort(key=lambda x: (x['folder'], x['name']))
        
        return jsonify({
            'success': True,
            'templates': templates,
            'message': f'{len(templates)} templates encontrados'
        })
        
    except Exception as e:
        logger.error(f"Error en get_templates: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al cargar templates: {str(e)}'})

@permissions_bp.route('/api/upload-template', methods=['POST'])
@login_required
def upload_template():
    """Subir un nuevo template HTML"""
    try:
        if 'template_file' not in request.files:
            return jsonify({'success': False, 'message': 'No se encontró archivo'})
        
        file = request.files['template_file']
        template_name = request.form.get('template_name', '').strip()
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No se seleccionó archivo'})
        
        if not template_name:
            template_name = file.filename
        
        # Validar extensión
        if not template_name.lower().endswith(('.html', '.htm')):
            template_name += '.html'
        
        # Validar nombre de archivo
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+\.html?$', template_name):
            return jsonify({'success': False, 'message': 'Nombre de archivo inválido'})
        
        # Guardar archivo
        import os
        template_dir = os.path.join(current_app.root_path, 'templates')
        file_path = os.path.join(template_dir, template_name)
        
        # Verificar si existe
        if os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Ya existe un template con ese nombre'})
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar archivo
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Template {template_name} subido exitosamente',
            'template_path': template_name
        })
        
    except Exception as e:
        logger.error(f"Error en upload_template: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al subir template: {str(e)}'})

@permissions_bp.route('/api/create-dynamic-route', methods=['POST'])
@login_required
def create_dynamic_route():
    """Crear ruta dinámica para un template"""
    try:
        data = request.get_json()
        
        route_path = data.get('route', '').strip()
        template_path = data.get('template', '').strip()
        page_name = data.get('name', '').strip()
        
        if not all([route_path, template_path, page_name]):
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'})
        
        # Validar que el template existe
        import os
        full_template_path = os.path.join(current_app.root_path, 'templates', template_path)
        if not os.path.exists(full_template_path):
            return jsonify({'success': False, 'message': 'El template especificado no existe'})
        
        # Crear ruta dinámica en el registry
        from app.utils.dynamic_routes import register_dynamic_route
        success = register_dynamic_route(route_path, template_path, page_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Ruta {route_path} creada exitosamente',
                'route': route_path,
                'template': template_path
            })
        else:
            return jsonify({'success': False, 'message': 'Error al crear la ruta dinámica'})
        
    except Exception as e:
        logger.error(f"Error en create_dynamic_route: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al crear ruta: {str(e)}'})

# ============================================================================
# RUTAS PARA DATOS DINÁMICOS DE LA TABLA
# ============================================================================

@permissions_bp.route('/api/permissions-data', methods=['GET'])
@login_required
@admin_required
def get_permissions_data():
    """Obtener datos completos para la tabla de permisos (páginas + roles)"""
    try:
        # Obtener todas las páginas activas
        pages = Page.query.filter_by(active=True).all()
        
        # Obtener todos los roles (sistema + personalizados)
        system_roles = ['SUPERADMIN']  # Solo SUPERADMIN es rol del sistema ahora
        custom_roles = [role.name for role in CustomRole.query.filter_by(active=True).all()]
        all_roles = system_roles + custom_roles
        
        # Preparar datos de páginas
        pages_data = []
        for page in pages:
            try:
                # Obtener permisos de esta página
                permissions = PagePermission.query.filter_by(page_id=page.id).all()
                # Normalizar roles a mayúsculas para consistencia
                page_permissions = [perm.role_name.upper() for perm in permissions]
                
                # Obtener categoría
                category_name = page.category_obj.name if page.category_obj else 'Sin categoría'
                
                page_data = {
                    'id': page.id,
                    'name': page.name,
                    'route': page.route,
                    'category': category_name,
                    'permissions': page_permissions
                }
                
                pages_data.append(page_data)
                
            except Exception as page_error:
                logger.error(f"Error procesando página {page.id}: {str(page_error)}")
                continue
        
        return jsonify({
            'success': True,
            'pages': pages_data,
            'roles': all_roles
        })
        
    except Exception as e:
        logger.error(f"Error al obtener datos de permisos: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al obtener datos: {str(e)}'})

# ============================================================================
# RUTAS PARA GESTIÓN DE ROLES PERSONALIZADOS
# ============================================================================

@permissions_bp.route('/api/roles', methods=['GET'])
@login_required
@admin_required
def get_roles():
    """Obtener todos los roles (sistema y personalizados)"""
    try:
        # Roles del sistema
        system_roles = []
        for role in UserRole:
            system_roles.append({
                'id': f'system_{role.name}',
                'name': role.name,
                'display_name': role.display_name,
                'type': 'system',
                'deletable': False,
                'active': True,
                'description': f'Rol del sistema: {role.display_name}'
            })
        
        # Roles personalizados
        custom_roles = CustomRole.query.all()
        custom_roles_data = []
        for role in custom_roles:
            custom_roles_data.append({
                'id': role.id,
                'name': role.name,
                'display_name': role.name,
                'type': 'custom',
                'deletable': True,
                'active': role.active,
                'description': role.description or f'Rol personalizado: {role.name}',
                'created_at': role.created_at.isoformat() if role.created_at else None
            })
        
        # Combinar ambos tipos
        all_roles = system_roles + custom_roles_data
        
        return jsonify({
            'success': True,
            'roles': all_roles,
            'system_count': len(system_roles),
            'custom_count': len(custom_roles_data)
        })
        
    except Exception as e:
        logger.error(f"Error al obtener roles: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al obtener roles: {str(e)}'})

@permissions_bp.route('/api/roles', methods=['POST'])
@login_required
@admin_required  
def add_custom_role():
    """Agregar nuevo rol personalizado"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip().upper()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'El nombre del rol es requerido'})
        
        # Validar que no sea un rol del sistema
        system_role_names = [role.name for role in UserRole]
        if name in system_role_names:
            return jsonify({'success': False, 'message': 'No se puede crear un rol con el nombre de un rol del sistema'})
        
        # Verificar que no exista
        existing_role = CustomRole.query.filter_by(name=name).first()
        if existing_role:
            return jsonify({'success': False, 'message': 'Ya existe un rol con ese nombre'})
        
        # Crear nuevo rol
        new_role = CustomRole(
            name=name,
            description=description,
            active=True
        )
        
        db.session.add(new_role)
        db.session.commit()
        
        logger.info(f"Rol personalizado creado: {name} por usuario {current_user.nombre}")
        
        return jsonify({
            'success': True,
            'message': f'Rol {name} creado exitosamente',
            'role': new_role.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear rol: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al crear rol: {str(e)}'})

@permissions_bp.route('/api/roles/<int:role_id>', methods=['PUT'])
@login_required
@admin_required
def update_role(role_id):
    """Actualizar rol personalizado"""
    try:
        data = request.get_json()
        
        role = CustomRole.query.get_or_404(role_id)
        
        new_name = data.get('name', '').strip().upper()
        new_description = data.get('description', '').strip()
        
        if not new_name:
            return jsonify({'success': False, 'message': 'El nombre del rol es requerido'})
        
        # Validar que no sea un rol del sistema
        system_role_names = [role.name for role in UserRole]
        if new_name in system_role_names:
            return jsonify({'success': False, 'message': 'No se puede usar el nombre de un rol del sistema'})
        
        # Verificar que no exista otro rol con ese nombre
        existing_role = CustomRole.query.filter(
            CustomRole.name == new_name,
            CustomRole.id != role_id
        ).first()
        if existing_role:
            return jsonify({'success': False, 'message': 'Ya existe otro rol con ese nombre'})
        
        old_name = role.name
        
        # Actualizar el rol
        role.name = new_name
        role.description = new_description
        
        # Actualizar el role_name en los permisos si cambió el nombre
        if old_name != new_name:
            permissions = PagePermission.query.filter_by(custom_role_id=role.id).all()
            for permission in permissions:
                permission.role_name = new_name
        
        db.session.commit()
        
        logger.info(f"Rol personalizado actualizado: {old_name} -> {new_name} por usuario {current_user.nombre}")
        
        return jsonify({
            'success': True,
            'message': f'Rol {new_name} actualizado exitosamente',
            'role': role.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar rol {role_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al actualizar rol: {str(e)}'})

@permissions_bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_role(role_id):
    """Eliminar rol personalizado"""
    try:
        role = CustomRole.query.get_or_404(role_id)
        
        # Verificar si el rol tiene permisos asignados
        permissions_count = PagePermission.query.filter_by(custom_role_id=role.id).count()
        
        if permissions_count > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar el rol {role.name} porque tiene {permissions_count} permisos asignados. Elimine primero los permisos.'
            })
        
        # Verificar si hay usuarios con este rol (si se implementa en el futuro)
        # usuarios_count = Trabajador.query.filter_by(custom_role_id=role.id).count()
        # if usuarios_count > 0:
        #     return jsonify({
        #         'success': False,
        #         'message': f'No se puede eliminar el rol {role.name} porque hay {usuarios_count} usuarios asignados.'
        #     })
        
        role_name = role.name
        db.session.delete(role)
        db.session.commit()
        
        logger.info(f"Rol personalizado eliminado: {role_name} por usuario {current_user.nombre}")
        
        return jsonify({
            'success': True,
            'message': f'Rol {role_name} eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar rol {role_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al eliminar rol: {str(e)}'})

@permissions_bp.route('/api/roles/<int:role_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_role_status(role_id):
    """Activar/desactivar rol personalizado"""
    try:
        role = CustomRole.query.get_or_404(role_id)
        
        role.active = not role.active
        db.session.commit()
        
        status = "activado" if role.active else "desactivado"
        logger.info(f"Rol personalizado {status}: {role.name} por usuario {current_user.nombre}")
        
        return jsonify({
            'success': True,
            'message': f'Rol {role.name} {status} exitosamente',
            'active': role.active
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al cambiar estado del rol {role_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al cambiar estado del rol: {str(e)}'})

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def init_app(app):
    """Inicializar el módulo de permisos"""
    app.register_blueprint(permissions_bp)

# ============================================================================
# RUTAS DE ORGANIZACIÓN DE MENÚ
# ============================================================================

@permissions_bp.route('/api/menu/categories/reorder', methods=['POST'])
@login_required
@admin_required
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
        
        # Limpiar cache del menú
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Orden de categorías actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reordenando categorías: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@permissions_bp.route('/api/menu/pages/reorder', methods=['POST'])
@login_required
@admin_required
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
        
        # Limpiar cache del menú
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Orden de páginas actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reordenando páginas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@permissions_bp.route('/api/menu/category/<int:category_id>/icon', methods=['PUT'])
@login_required
@admin_required
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
        
        # Limpiar cache del menú
        menu_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Icono actualizado correctamente',
            'category': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando icono de categoría: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@permissions_bp.route('/api/menu/page/<int:page_id>/icon', methods=['PUT'])
@login_required
@admin_required
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
        logger.error(f"Error actualizando icono de página: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@permissions_bp.route('/api/menu/category/<int:category_id>/visibility', methods=['PUT'])
@login_required
@admin_required
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
        logger.error(f"Error cambiando visibilidad de categoría: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@permissions_bp.route('/api/menu/page/<int:page_id>/visibility', methods=['PUT'])
@login_required
@admin_required
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
        logger.error(f"Error cambiando visibilidad de página: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@permissions_bp.route('/api/menu/icons', methods=['GET'])
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

@permissions_bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories_api():
    """Obtener lista de categorías para organización de menú"""
    try:
        categories = Category.query.order_by(Category.display_order.asc()).all()
        
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'description': category.description,
                'display_order': category.display_order,
                'icon': category.icon,
                'is_visible': category.is_visible
            })
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@permissions_bp.route('/api/categories/<int:category_id>/pages', methods=['GET'])
@login_required
def get_category_pages_api(category_id):
    """Obtener páginas de una categoría específica"""
    try:
        pages = Page.query.filter_by(category_id=category_id).order_by(Page.display_order.asc()).all()
        
        pages_data = []
        for page in pages:
            pages_data.append({
                'id': page.id,
                'name': page.name,
                'route': page.route,
                'description': page.description,
                'display_order': page.display_order,
                'icon': page.icon,
                'is_visible': page.is_visible,
                'active': page.active,
                'category_id': page.category_id
            })
        
        return jsonify({
            'success': True,
            'pages': pages_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo páginas de categoría {category_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
