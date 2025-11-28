"""
Script para crear páginas de ejemplo y poblar el sistema de menús
"""

from app import create_app, db
from app.models import Page, Category, PagePermission, UserRole
import sys

def create_sample_pages():
    """Crear páginas de ejemplo para el sistema de menús"""
    
    app = create_app()
    with app.app_context():
        
        print("🚀 Creando páginas de ejemplo para el sistema de menús...")
        
        # Crear categorías
        categories_data = [
            {'name': 'Dashboard', 'description': 'Página principal y resúmenes'},
            {'name': 'Proyectos', 'description': 'Gestión de proyectos'},
            {'name': 'Usuarios', 'description': 'Administración de usuarios'},
            {'name': 'Administración', 'description': 'Configuración del sistema'},
            {'name': 'Reportes', 'description': 'Informes y estadísticas'},
            {'name': 'Configuración', 'description': 'Configuración personal'}
        ]
        
        created_categories = {}
        
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                print(f"  ✅ Categoría creada: {cat_data['name']}")
            else:
                print(f"  ⚡ Categoría existente: {cat_data['name']}")
            
            created_categories[cat_data['name']] = category
        
        db.session.flush()  # Para obtener IDs
        
        # Crear páginas
        pages_data = [
            # Dashboard
            {'name': 'Dashboard Principal', 'route': '/dashboard', 'category': 'Dashboard', 
             'description': 'Panel principal con resumen general'},
            
            # Proyectos
            {'name': 'Lista de Proyectos', 'route': '/projects', 'category': 'Proyectos',
             'description': 'Ver todos los proyectos'},
            {'name': 'Crear Proyecto', 'route': '/projects/create', 'category': 'Proyectos',
             'description': 'Crear nuevo proyecto'},
            {'name': 'Gantt', 'route': '/projects/gantt', 'category': 'Proyectos',
             'description': 'Vista de diagrama de Gantt'},
            
            # Usuarios
            {'name': 'Lista de Usuarios', 'route': '/auth/users', 'category': 'Usuarios',
             'description': 'Gestión de usuarios del sistema'},
            {'name': 'Crear Usuario', 'route': '/auth/users/create', 'category': 'Usuarios',
             'description': 'Crear nuevo usuario'},
            {'name': 'Trabajadores', 'route': '/workers', 'category': 'Usuarios',
             'description': 'Gestión de trabajadores'},
            
            # Administración
            {'name': 'Gestión de Permisos', 'route': '/permissions', 'category': 'Administración',
             'description': 'Configurar permisos de páginas'},
            {'name': 'Roles Personalizados', 'route': '/custom-roles', 'category': 'Administración',
             'description': 'Gestión de roles personalizados'},
            {'name': 'Estados', 'route': '/estados', 'category': 'Administración',
             'description': 'Gestión de estados'},
            {'name': 'Tipologías', 'route': '/tipologias', 'category': 'Administración',
             'description': 'Gestión de tipologías'},
            
            # Reportes
            {'name': 'Reportes de Proyectos', 'route': '/reports/projects', 'category': 'Reportes',
             'description': 'Informes sobre proyectos'},
            {'name': 'Estadísticas', 'route': '/reports/stats', 'category': 'Reportes',
             'description': 'Estadísticas generales'},
            
            # Configuración
            {'name': 'Mi Perfil', 'route': '/profile', 'category': 'Configuración',
             'description': 'Editar perfil personal'},
            {'name': 'Configuración', 'route': '/settings', 'category': 'Configuración',
             'description': 'Configuración del sistema'}
        ]
        
        created_pages = []
        
        for page_data in pages_data:
            page = Page.query.filter_by(route=page_data['route']).first()
            if not page:
                category_obj = created_categories[page_data['category']]
                page = Page(
                    name=page_data['name'],
                    route=page_data['route'],
                    description=page_data['description'],
                    category_id=category_obj.id,
                    active=True
                )
                db.session.add(page)
                created_pages.append(page)
                print(f"  ✅ Página creada: {page_data['name']} -> {page_data['route']}")
            else:
                created_pages.append(page)
                print(f"  ⚡ Página existente: {page_data['name']} -> {page_data['route']}")
        
        db.session.flush()  # Para obtener IDs de páginas
        
        # Configurar permisos por rol
        permissions_config = {
            'ADMIN': {  # Administradores tienen acceso a todo
                'pages': [p.route for p in created_pages]
            },
            'SUPERVISOR': {  # Supervisores pueden ver proyectos y algunos reportes
                'pages': [
                    '/dashboard', '/projects', '/projects/gantt', 
                    '/workers', '/reports/projects', '/reports/stats', '/profile'
                ]
            },
            'USUARIO': {  # Usuarios básicos acceso limitado
                'pages': ['/dashboard', '/projects', '/profile']
            }
        }
        
        # Crear permisos
        for role_name, config in permissions_config.items():
            for page_route in config['pages']:
                page = next((p for p in created_pages if p.route == page_route), None)
                if page:
                    # Verificar si ya existe el permiso
                    existing_permission = PagePermission.query.filter_by(
                        page_id=page.id, 
                        role_name=role_name
                    ).first()
                    
                    if not existing_permission:
                        permission = PagePermission(
                            page_id=page.id,
                            role_name=role_name
                        )
                        db.session.add(permission)
                        print(f"  🔑 Permiso creado: {role_name} -> {page.name}")
        
        # Guardar cambios
        db.session.commit()
        
        print("\n✨ ¡Páginas de ejemplo creadas exitosamente!")
        print("\n📊 Resumen:")
        
        # Mostrar estadísticas
        total_categories = Category.query.count()
        total_pages = Page.query.count()
        total_permissions = PagePermission.query.count()
        
        print(f"  📁 Categorías: {total_categories}")
        print(f"  📄 Páginas: {total_pages}")
        print(f"  🔐 Permisos: {total_permissions}")
        
        # Mostrar permisos por rol
        print("\n🎭 Permisos por rol:")
        for role in ['ADMIN', 'SUPERVISOR', 'USUARIO']:
            count = PagePermission.query.filter_by(role_name=role).count()
            print(f"  • {role}: {count} permisos")
        
        return True

if __name__ == "__main__":
    try:
        success = create_sample_pages()
        if success:
            print("\n🎉 ¡Proceso completado exitosamente!")
            print("\n🌐 Ahora puedes acceder al sistema y ver el menú dinámico en acción:")
            print("  • http://localhost:5050/")
            print("  • Credenciales: admin@test.com / admin123")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")
        sys.exit(1)
