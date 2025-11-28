"""
Sistema de Permisos por Área - Utilidades (VERSIÓN AVANZADA)
Funciones helper para manejo de permisos basados en área con soporte many-to-many
"""
from functools import wraps
from flask import abort, request, current_app
from flask_login import current_user
from app.models import UserRole, Area, Trabajador, db, trabajador_areas

def area_permission_required(allowed_roles=None):
    """
    Decorador para proteger rutas basado en permisos de área
    
    Args:
        allowed_roles: Lista de roles permitidos ['superadmin', 'admin']
    """
    if allowed_roles is None:
        allowed_roles = ['superadmin', 'admin']
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            user_role = current_user.rol.value if hasattr(current_user.rol, 'value') else str(current_user.rol)
            
            # Superadmin siempre tiene acceso
            if user_role == 'superadmin':
                return f(*args, **kwargs)
            
            # Admin general tiene acceso si está en allowed_roles
            if user_role == 'admin' and 'admin' in allowed_roles:
                return f(*args, **kwargs)
            
            # Sin permisos suficientes
            abort(403)
        
        return decorated_function
    return decorator

def get_trabajadores_por_area(user):
    """
    Obtiene los trabajadores que el usuario tiene permiso de ver
    VERSION TEMPORAL usando area_id
    
    Args:
        user: Usuario actual (current_user)
    
    Returns:
        Query de trabajadores filtrados según permisos
    """
    user_role = user.rol.value if hasattr(user.rol, 'value') else str(user.rol)
    
    # Superadmin ve todos
    if user_role == 'superadmin':
        return Trabajador.query
    
    # Admin general: comportamiento según especificaciones
    if user_role == 'admin':
        if user.area_id:  # Temporal: usando area_id
            # Admin con área específica: solo trabajadores de su área
            return Trabajador.query.filter_by(area_id=user.area_id)
        else:
            # Admin sin área: ve todos (backward compatibility)
            return Trabajador.query
    
        # Otros roles: sin acceso
    return Trabajador.query.filter(False)  # Query vacío

def get_areas_permitidas(user):
    """
    Obtiene las áreas que el usuario puede administrar
    VERSION TEMPORAL usando area_id
    
    Args:
        user: Usuario actual
        
    Returns:
        Lista de áreas permitidas
    """
    user_role = user.rol.value if hasattr(user.rol, 'value') else str(user.rol)
    
    # Superadmin ve todas las áreas
    if user_role == 'superadmin':
        return Area.query.filter_by(activo=True).all()
    
    # Admin general con área específica
    if user_role == 'admin':
        if user.area_id:  # Temporal: usando area_id
            return [user.area] if user.area and user.area.activo else []
        else:
            # Admin sin área: puede ver todas (backward compatibility)
            return Area.query.filter_by(activo=True).all()
    
    # Control: sus áreas asignadas
    if user_role == 'control':
        if user.area_id:  # Temporal: usando area_id
            return [user.area] if user.area and user.area.activo else []
    
    return []

def puede_editar_trabajador(user, trabajador):
    """
    Verifica si el usuario puede editar un trabajador específico
    VERSION TEMPORAL usando area_id
    
    Args:
        user: Usuario actual
        trabajador: Trabajador a verificar
        
    Returns:
        Boolean indicando si puede editar
    """
    # Obtener el valor del rol para compatibilidad con el resto de la función
    user_role = user.rol.value if hasattr(user.rol, 'value') else str(user.rol)
    
    # Obtener el nombre del rol del enum
    rol_name = user.rol.name if (hasattr(user, 'rol') and user.rol and hasattr(user.rol, 'name')) else None
    
    # Verificar si tiene permisos administrativos (SUPERADMIN o custom role ADMINISTRADOR)
    has_admin_permissions = (
        (rol_name and rol_name == 'SUPERADMIN') or
        (hasattr(user, 'custom_role_id') and user.custom_role_id and 
         user.custom_role and user.custom_role.name.upper() in ['ADMINISTRADOR', 'ADMIN', 'SUPERADMIN'])
    )
    
    # Usuarios con permisos administrativos pueden editar todos
    if has_admin_permissions:
        return True
    
    # Admin general - verificar tanto área como recinto
    if user_role == 'admin':
        # Verificar por recinto (nueva lógica)
        if user.recinto_id and trabajador.recinto_id:
            return trabajador.recinto_id == user.recinto_id
        
        # Verificar por área (lógica existente)
        if user.area_id:  # Temporal: usando area_id
            return trabajador.area_id == user.area_id
        
        # Admin sin área ni recinto específico: puede editar todos (backward compatibility)
        return True
    
    # Control: puede editar trabajadores de sus áreas
    if user_role == 'control':
        return trabajador.area_id == user.area_id
    
    return False

def puede_crear_trabajador_en_area(user, area_id):
    """
    Verifica si el usuario puede crear trabajadores en un área específica
    VERSION TEMPORAL usando area_id
    
    Args:
        user: Usuario actual
        area_id: ID del área donde se quiere crear el trabajador
        
    Returns:
        Boolean indicando si puede crear
    """
    # Obtener el valor del rol para compatibilidad con el resto de la función
    user_role = user.rol.value if hasattr(user.rol, 'value') else str(user.rol)
    
    # Obtener el nombre del rol del enum
    rol_name = user.rol.name if (hasattr(user, 'rol') and user.rol and hasattr(user.rol, 'name')) else None
    
    # Verificar si tiene permisos administrativos (SUPERADMIN o custom role ADMINISTRADOR)
    has_admin_permissions = (
        (rol_name and rol_name == 'SUPERADMIN') or
        (hasattr(user, 'custom_role_id') and user.custom_role_id and 
         user.custom_role and user.custom_role.name.upper() in ['ADMINISTRADOR', 'ADMIN', 'SUPERADMIN'])
    )
    
    # Usuarios con permisos administrativos pueden crear en cualquier área
    if has_admin_permissions:
        return True
    
    # Admin general
    if user_role == 'admin':
        if user.area_id:  # Temporal: usando area_id
            return user.area_id == area_id
        else:
            # Admin sin área: puede crear en cualquier área (backward compatibility)
            return True
    
    # Control: puede crear en sus áreas
    if user_role == 'control':
        return user.area_id == area_id
    
    return False

def get_estadisticas_area(user):
    """
    Obtiene estadísticas de trabajadores por área según permisos del usuario
    VERSION TEMPORAL usando area_id
    
    Args:
        user: Usuario actual
        
    Returns:
        Dict con estadísticas
    """
    trabajadores_query = get_trabajadores_por_area(user)
    areas_permitidas = get_areas_permitidas(user)
    
    total_trabajadores = trabajadores_query.count()
    trabajadores_con_area = trabajadores_query.filter(Trabajador.area_id.isnot(None)).count()  # Temporal: usando area_id
    trabajadores_sin_area = total_trabajadores - trabajadores_con_area
    
    estadisticas_por_area = {}
    for area in areas_permitidas:
        # Contar trabajadores con esta área
        count = trabajadores_query.filter_by(area_id=area.id).count()  # Temporal: usando area_id
        estadisticas_por_area[area.nombre] = count
    
    return {
        'total_trabajadores': total_trabajadores,
        'trabajadores_con_area': trabajadores_con_area,
        'trabajadores_sin_area': trabajadores_sin_area,
        'areas_permitidas': len(areas_permitidas),
        'por_area': estadisticas_por_area
    }

def puede_asignar_rol(user, rol_destino):
    """
    Verifica si el usuario puede asignar un rol específico
    
    Args:
        user: Usuario actual
        rol_destino: Rol que se quiere asignar (string)
        
    Returns:
        Boolean indicando si puede asignar el rol
    """
    user_role = user.rol.value if hasattr(user.rol, 'value') else str(user.rol)
    
    # Solo SUPERADMIN puede asignar CONTROL
    if rol_destino == 'control':
        return user_role == 'superadmin'
    
    # SUPERADMIN puede asignar cualquier rol
    if user_role == 'superadmin':
        return True
    
    # ADMIN puede asignar roles básicos
    if user_role == 'admin':
        return rol_destino in ['usuario', 'supervisor']
    
    # CONTROL puede asignar solo usuario
    if user_role == 'control':
        return rol_destino == 'usuario'
    
    return False

def puede_editar_trabajador_recinto(user, trabajador):
    """
    Verifica si el usuario puede editar un trabajador específico basado en recinto
    
    Args:
        user: Usuario actual
        trabajador: Trabajador a verificar
        
    Returns:
        Boolean indicando si puede editar
    """
    # Obtener el nombre del rol del enum
    rol_name = user.rol.name if (hasattr(user, 'rol') and user.rol and hasattr(user.rol, 'name')) else None
    
    # Verificar si tiene permisos administrativos (SUPERADMIN o custom role ADMINISTRADOR)
    has_admin_permissions = (
        (rol_name and rol_name == 'SUPERADMIN') or
        (hasattr(user, 'custom_role_id') and user.custom_role_id and 
         user.custom_role and user.custom_role.name.upper() in ['ADMINISTRADOR', 'ADMIN', 'SUPERADMIN'])
    )
    
    # Usuarios con permisos administrativos pueden editar todos
    if has_admin_permissions:
        return True
    
    # Verificar por recinto - administradores de recinto pueden gestionar trabajadores de su recinto
    if user.recinto_id and trabajador.recinto_id:
        return trabajador.recinto_id == user.recinto_id
    
    return False

def puede_crear_trabajador_en_recinto(user, recinto_id):
    """
    Verifica si el usuario puede crear trabajadores en un recinto específico
    
    Args:
        user: Usuario actual
        recinto_id: ID del recinto donde se quiere crear el trabajador
        
    Returns:
        Boolean indicando si puede crear
    """
    # Obtener el nombre del rol del enum
    rol_name = user.rol.name if (hasattr(user, 'rol') and user.rol and hasattr(user.rol, 'name')) else None
    
    # Verificar si tiene permisos administrativos (SUPERADMIN o custom role ADMINISTRADOR)
    has_admin_permissions = (
        (rol_name and rol_name == 'SUPERADMIN') or
        (hasattr(user, 'custom_role_id') and user.custom_role_id and 
         user.custom_role and user.custom_role.name.upper() in ['ADMINISTRADOR', 'ADMIN', 'SUPERADMIN'])
    )
    
    # Usuarios con permisos administrativos pueden crear en cualquier recinto
    if has_admin_permissions:
        return True
    
    # Administradores de recinto pueden crear trabajadores en su recinto
    if user.recinto_id:
        return user.recinto_id == recinto_id
    
    return False
