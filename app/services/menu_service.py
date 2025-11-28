"""
Servicio para generar menús dinámicos basados en permisos de usuario
"""

from flask_login import current_user
from app.models import Page, Category, PagePermission, UserRole, CustomRole, MenuConfiguration
from collections import defaultdict

class MenuService:
    """Servicio para generar menús dinámicos según permisos del usuario"""
    
    def __init__(self):
        self.menu_cache = {}
    
    def get_user_menu(self, user=None):
        """Obtener menú personalizado para el usuario actual"""
        if not user:
            user = current_user
        
        if not user or not user.is_authenticated:
            return self._get_public_menu()
        
        # Cache key basado en usuario, rol del sistema y custom role
        role_part = user.rol.value if hasattr(user, 'rol') and user.rol else 'none'
        custom_role_part = str(user.custom_role_id) if hasattr(user, 'custom_role_id') and user.custom_role_id else 'none'
        cache_key = f"{user.id}_{role_part}_{custom_role_part}"
        
        if cache_key in self.menu_cache:
            return self.menu_cache[cache_key]
        
        menu = self._build_user_menu(user)
        self.menu_cache[cache_key] = menu
        
        return menu
    
    def _build_user_menu(self, user):
        """Construir menú basado en permisos del usuario"""
        
        # Obtener rol del usuario (puede ser rol del sistema o custom role)
        user_role = user.rol if hasattr(user, 'rol') else None
        custom_role_id = user.custom_role_id if hasattr(user, 'custom_role_id') else None
        
        # Si no tiene ni rol del sistema ni custom role, mostrar menú público
        if not user_role and not custom_role_id:
            return self._get_public_menu()
        
        # Obtener páginas permitidas para este usuario
        allowed_pages = self._get_user_allowed_pages(user_role, custom_role_id)
        
        # Agrupar por categorías
        menu_by_category = defaultdict(list)
        
        for page_data in allowed_pages:
            category_name = page_data['category']['name']
            menu_by_category[category_name].append(page_data)
        
        # Construir estructura final del menú con organización
        menu_structure = []
        
        # Obtener categorías ordenadas y visibles
        categories = Category.query.filter_by(is_visible=True).order_by(Category.display_order.asc(), Category.name.asc()).all()
        
        for category in categories:
            pages = menu_by_category.get(category.name, [])
            if pages:  # Solo incluir categorías con páginas
                # Ordenar páginas por display_order
                sorted_pages = sorted(pages, key=lambda x: (x.get('display_order', 0), x['name']))
                
                menu_structure.append({
                    'category': category.name,
                    'icon': category.icon,
                    'color': category.color,
                    'display_order': category.display_order,
                    'parent_id': category.parent_id,
                    'pages': self._format_pages_for_menu(sorted_pages),
                    'count': len(sorted_pages)
                })
        
        return menu_structure
    
    def _get_user_allowed_pages(self, user_role, custom_role_id=None):
        """Obtener páginas permitidas para un rol específico (sistema o personalizado)"""
        allowed_pages = []
        
        try:
            permissions = []
            
            # Buscar permisos por rol del sistema si existe
            if user_role:
                # Determinar el nombre del rol para la consulta
                if isinstance(user_role, UserRole):
                    role_name = user_role.name  # ADMIN, SUPERVISOR, etc.
                else:
                    role_name = str(user_role).upper()
                
                # Buscar permisos por role_name con páginas visibles
                system_permissions = PagePermission.query.join(Page).join(Category).filter(
                    PagePermission.role_name == role_name,
                    Page.active == True,
                    Page.is_visible == True,
                    Category.is_visible == True
                ).all()
                
                permissions.extend(system_permissions)
            
            # Buscar permisos por custom_role_id si existe
            if custom_role_id:
                custom_permissions = PagePermission.query.join(Page).join(Category).filter(
                    PagePermission.custom_role_id == custom_role_id,
                    Page.active == True,
                    Page.is_visible == True,
                    Category.is_visible == True
                ).all()
                
                permissions.extend(custom_permissions)
            
            # Procesar permisos encontrados
            for permission in permissions:
                page = permission.page
                if page and page.active and page.is_visible:
                    page_data = {
                        'id': page.id,
                        'route': page.route,
                        'name': page.name,
                        'description': page.description,
                        'icon': page.icon,
                        'display_order': page.display_order,
                        'parent_page_id': page.parent_page_id,
                        'menu_group': page.menu_group,
                        'external_url': page.external_url,
                        'target_blank': page.target_blank,
                        'category': {
                            'id': page.category_obj.id,
                            'name': page.category_obj.name,
                            'icon': page.category_obj.icon,
                            'color': page.category_obj.color,
                            'display_order': page.category_obj.display_order
                        }
                    }
                    
                    # Evitar duplicados (si un usuario tiene ambos tipos de permisos)
                    if not any(p['id'] == page.id for p in allowed_pages):
                        allowed_pages.append(page_data)
            
        except Exception as e:
            print(f"Error obteniendo páginas permitidas: {e}")
        
        return allowed_pages
    
    def _format_pages_for_menu(self, pages):
        """Formatear páginas para el menú con jerarquía"""
        formatted_pages = []
        
        # Separar páginas padre e hijas
        parent_pages = [p for p in pages if not p.get('parent_page_id')]
        child_pages = [p for p in pages if p.get('parent_page_id')]
        
        # Procesar páginas padre
        for page in parent_pages:
            formatted_page = {
                'name': page['name'],
                'url': page.get('external_url') or page['route'],
                'icon': page['icon'],
                'description': page.get('description', ''),
                'target_blank': page.get('target_blank', False),
                'is_external': bool(page.get('external_url')),
                'menu_group': page.get('menu_group'),
                'children': []
            }
            
            # Buscar páginas hijas
            for child in child_pages:
                if child.get('parent_page_id') == page.get('id'):
                    formatted_page['children'].append({
                        'name': child['name'],
                        'url': child.get('external_url') or child['route'],
                        'icon': child['icon'],
                        'description': child.get('description', ''),
                        'target_blank': child.get('target_blank', False),
                        'is_external': bool(child.get('external_url'))
                    })
            
            formatted_pages.append(formatted_page)
        
        return formatted_pages
    
    def _get_public_menu(self):
        """Menú para usuarios no autenticados"""
        return [
            {
                'category': 'Público',
                'icon': 'fas fa-globe',
                'color': 'primary',
                'display_order': 1,
                'parent_id': None,
                'pages': [
                    {
                        'name': 'Iniciar Sesión',
                        'url': '/auth/login',
                        'icon': 'fas fa-sign-in-alt',
                        'description': 'Acceder al sistema',
                        'target_blank': False,
                        'is_external': False,
                        'children': []
                    }
                ],
                'count': 1
            }
        ]
    
    def get_menu_configuration(self):
        """Obtener configuración global del menú"""
        return MenuConfiguration.get_default_config()
    
    def clear_cache(self):
        """Limpiar cache del menú (útil cuando cambian permisos)"""
        self.menu_cache.clear()
    
    def get_breadcrumbs(self, current_route):
        """Generar breadcrumbs para la ruta actual"""
        try:
            page = Page.query.filter_by(route=current_route, active=True).first()
            if not page:
                return []
            
            breadcrumbs = []
            
            # Agregar categoría
            if page.category_obj:
                breadcrumbs.append({
                    'name': page.category_obj.name,
                    'url': None,
                    'icon': page.category_obj.icon
                })
            
            # Agregar página padre si existe
            if page.parent_page_id:
                parent = Page.query.get(page.parent_page_id)
                if parent:
                    breadcrumbs.append({
                        'name': parent.name,
                        'url': parent.route,
                        'icon': parent.icon
                    })
            
            # Agregar página actual
            breadcrumbs.append({
                'name': page.name,
                'url': page.route,
                'icon': page.icon,
                'current': True
            })
            
            return breadcrumbs
            
        except Exception as e:
            print(f"Error generando breadcrumbs: {e}")
            return []

# Instancia global del servicio
menu_service = MenuService()
