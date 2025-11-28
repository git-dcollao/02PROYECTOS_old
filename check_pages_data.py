#!/usr/bin/env python3
"""
Script para verificar el estado de páginas y categorías en la base de datos
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Page, PagePermission, UserRole

def check_pages_and_categories():
    """Verificar páginas y categorías en la base de datos"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 VERIFICANDO PÁGINAS Y CATEGORÍAS")
            print("=" * 50)
            
            # Verificar categorías
            categories = Category.query.all()
            print(f"📂 Total de categorías: {len(categories)}")
            
            if categories:
                print("\n📂 CATEGORÍAS EXISTENTES:")
                for cat in categories:
                    page_count = Page.query.filter_by(category_id=cat.id, active=True).count()
                    print(f"   • {cat.name} (Color: {cat.color}) - {page_count} páginas")
            else:
                print("❌ No hay categorías en la base de datos")
            
            # Verificar páginas
            pages = Page.query.filter_by(active=True).all()
            print(f"\n📄 Total de páginas activas: {len(pages)}")
            
            if pages:
                print("\n📄 PÁGINAS EXISTENTES:")
                for page in pages:
                    category_name = page.category_obj.name if page.category_obj else "Sin categoría"
                    permissions = PagePermission.query.filter_by(page_id=page.id).all()
                    roles = [perm.role.value for perm in permissions]
                    print(f"   • {page.name} ({page.route})")
                    print(f"     Categoría: {category_name}")
                    print(f"     Roles: {', '.join(roles) if roles else 'Sin permisos'}")
                    print()
            else:
                print("❌ No hay páginas en la base de datos")
            
            # Verificar permisos
            permissions = PagePermission.query.all()
            print(f"🔐 Total de permisos: {len(permissions)}")
            
            return len(categories) > 0 or len(pages) > 0
            
        except Exception as e:
            print(f"💥 Error al verificar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def create_sample_data():
    """Crear datos de ejemplo para probar la interfaz"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🌱 CREANDO DATOS DE EJEMPLO")
            print("=" * 50)
            
            # Crear categorías de ejemplo
            categories_data = [
                {"name": "Sistema", "color": "#007bff", "description": "Páginas del sistema"},
                {"name": "Administración", "color": "#28a745", "description": "Páginas administrativas"},
                {"name": "Proyectos", "color": "#ffc107", "description": "Gestión de proyectos"},
                {"name": "Reportes", "color": "#6f42c1", "description": "Páginas de reportes"}
            ]
            
            created_categories = []
            for cat_data in categories_data:
                existing = Category.query.filter_by(name=cat_data["name"]).first()
                if not existing:
                    category = Category(**cat_data)
                    db.session.add(category)
                    db.session.flush()
                    created_categories.append(category)
                    print(f"✅ Categoría creada: {cat_data['name']}")
                else:
                    created_categories.append(existing)
                    print(f"⚠️ Categoría ya existe: {cat_data['name']}")
            
            # Crear páginas de ejemplo
            pages_data = [
                {
                    "name": "Dashboard Principal",
                    "route": "/dashboard",
                    "category_name": "Sistema",
                    "description": "Página principal del dashboard",
                    "roles": [UserRole.USUARIO, UserRole.SUPERVISOR, UserRole.ADMIN, UserRole.SUPERADMIN]
                },
                {
                    "name": "Gestión de Usuarios",
                    "route": "/auth/users",
                    "category_name": "Administración",
                    "description": "Administración de usuarios del sistema",
                    "roles": [UserRole.ADMIN, UserRole.SUPERADMIN]
                },
                {
                    "name": "Lista de Proyectos",
                    "route": "/projects",
                    "category_name": "Proyectos",
                    "description": "Listado de todos los proyectos",
                    "roles": [UserRole.SUPERVISOR, UserRole.ADMIN, UserRole.SUPERADMIN]
                },
                {
                    "name": "Crear Proyecto",
                    "route": "/projects/create",
                    "category_name": "Proyectos",
                    "description": "Crear nuevo proyecto",
                    "roles": [UserRole.ADMIN, UserRole.SUPERADMIN]
                },
                {
                    "name": "Reportes de Estado",
                    "route": "/reports/status",
                    "category_name": "Reportes",
                    "description": "Reportes de estado de proyectos",
                    "roles": [UserRole.SUPERVISOR, UserRole.ADMIN, UserRole.SUPERADMIN]
                },
                {
                    "name": "Gestión de Permisos",
                    "route": "/permissions",
                    "category_name": "Administración",
                    "description": "Gestión de permisos del sistema",
                    "roles": [UserRole.ADMIN, UserRole.SUPERADMIN]
                }
            ]
            
            created_pages = 0
            for page_data in pages_data:
                # Buscar la categoría
                category = Category.query.filter_by(name=page_data["category_name"]).first()
                if not category:
                    print(f"❌ No se encontró la categoría: {page_data['category_name']}")
                    continue
                
                # Verificar si ya existe
                existing_page = Page.query.filter_by(route=page_data["route"]).first()
                if existing_page:
                    print(f"⚠️ Página ya existe: {page_data['name']} ({page_data['route']})")
                    continue
                
                # Crear la página
                page = Page(
                    name=page_data["name"],
                    route=page_data["route"],
                    category_id=category.id,
                    description=page_data["description"],
                    active=True
                )
                
                db.session.add(page)
                db.session.flush()
                
                # Crear permisos
                for role in page_data["roles"]:
                    permission = PagePermission(
                        page_id=page.id,
                        role=role
                    )
                    db.session.add(permission)
                
                created_pages += 1
                roles_str = ', '.join([role.value for role in page_data["roles"]])
                print(f"✅ Página creada: {page_data['name']} - Roles: {roles_str}")
            
            db.session.commit()
            print(f"\n🎉 Datos de ejemplo creados: {len(created_categories)} categorías, {created_pages} páginas")
            return True
            
        except Exception as e:
            print(f"💥 Error al crear datos de ejemplo: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE PÁGINAS Y CATEGORÍAS")
    print("=" * 60)
    
    # Verificar estado actual
    has_data = check_pages_and_categories()
    
    if not has_data:
        print("\n❌ No hay datos suficientes para la interfaz")
        response = input("¿Deseas crear datos de ejemplo? (s/N): ")
        
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            if create_sample_data():
                print("\n✅ Datos de ejemplo creados exitosamente")
                print("🔄 Verificando datos creados...")
                check_pages_and_categories()
            else:
                print("\n❌ Error al crear datos de ejemplo")
        else:
            print("❌ Sin datos de ejemplo, la interfaz aparecerá vacía")
    else:
        print("\n✅ Hay datos disponibles en la base de datos")
    
    print("\n💡 NOTA: Actualiza la página web después de ejecutar este script")
