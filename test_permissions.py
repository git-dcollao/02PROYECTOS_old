#!/usr/bin/env python3
"""
Script para probar el sistema de permisos
Verifica que todos los componentes estén correctamente configurados
"""

from app import create_app, db
from app.models import Page, Category, PagePermission, UserRole, CustomRole
import json

def test_permissions_system():
    app = create_app()
    
    with app.app_context():
        print("🔍 VERIFICANDO SISTEMA DE PERMISOS")
        print("=" * 60)
        
        # 1. Verificar categorías
        categories = Category.query.all()
        print(f"📁 Categorías: {len(categories)}")
        for cat in categories:
            print(f"  - {cat.name} (color: {cat.color})")
        
        print()
        
        # 2. Verificar páginas
        pages = Page.query.all()
        print(f"📄 Páginas: {len(pages)}")
        for page in pages:
            print(f"  - {page.route} ({page.name}) - Categoría: {page.category_obj.name}")
        
        print()
        
        # 3. Verificar permisos actuales
        permissions = PagePermission.query.all()
        print(f"🔐 Permisos actuales: {len(permissions)}")
        
        # Agrupar permisos por página
        pages_permissions = {}
        for perm in permissions:
            page_route = perm.page.route
            if page_route not in pages_permissions:
                pages_permissions[page_route] = []
            pages_permissions[page_route].append(perm.role.value)
        
        for page_route, roles in pages_permissions.items():
            print(f"  - {page_route}: {', '.join(roles)}")
        
        print()
        
        # 4. Verificar roles personalizados
        custom_roles = CustomRole.query.filter_by(active=True).all()
        print(f"👥 Roles personalizados: {len(custom_roles)}")
        for role in custom_roles:
            print(f"  - {role.name}")
        
        print()
        
        # 5. Verificar estructura de datos para el template
        print("📊 DATOS PARA TEMPLATE:")
        print("-" * 30)
        
        # Simular la estructura de datos que se pasa al template
        system_roles = ['USUARIO', 'SUPERVISOR', 'ADMIN', 'SUPERADMIN']
        custom_role_names = [role.name for role in custom_roles]
        available_roles = system_roles + custom_role_names
        
        print(f"Roles disponibles: {available_roles}")
        
        # Crear estructura de páginas por categoría
        pages_by_category = []
        for category in categories:
            category_pages = Page.query.filter_by(category_id=category.id, active=True).all()
            if category_pages:
                pages_data = []
                for page in category_pages:
                    page_permissions = [perm.role.value for perm in page.permissions]
                    pages_data.append({
                        'route': page.route,
                        'name': page.name,
                        'permissions': page_permissions
                    })
                
                pages_by_category.append({
                    'category': {
                        'name': category.name,
                        'color': category.color
                    },
                    'pages': pages_data
                })
        
        print(f"\nEstructura de páginas por categoría:")
        for cat_data in pages_by_category:
            print(f"  📁 {cat_data['category']['name']}:")
            for page in cat_data['pages']:
                print(f"    - {page['route']}: {page['permissions']}")
        
        print("\n✅ VERIFICACIÓN COMPLETADA")
        
        return {
            'categories_count': len(categories),
            'pages_count': len(pages),
            'permissions_count': len(permissions),
            'custom_roles_count': len(custom_roles),
            'available_roles': available_roles,
            'pages_by_category': pages_by_category
        }

if __name__ == "__main__":
    result = test_permissions_system()
    print(f"\n🎯 RESUMEN:")
    print(f"  - {result['categories_count']} categorías")
    print(f"  - {result['pages_count']} páginas") 
    print(f"  - {result['permissions_count']} permisos")
    print(f"  - {result['custom_roles_count']} roles personalizados")
    print(f"  - {len(result['available_roles'])} roles totales")
