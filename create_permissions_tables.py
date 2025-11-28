#!/usr/bin/env python3
"""
Script para crear las tablas del sistema de permisos y migrar datos del JSON
"""
import sys
import os
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Category, Page, PagePermission, UserRole

def create_permissions_tables():
    """Crear las tablas del sistema de permisos"""
    print("🔧 Creando tablas del sistema de permisos...")
    
    # Crear todas las tablas
    db.create_all()
    
    print("✅ Tablas creadas exitosamente")

def migrate_from_json():
    """Migrar datos del archivo JSON a la base de datos"""
    json_file = 'page_permissions.json'
    
    if not os.path.exists(json_file):
        print(f"❌ No se encontró el archivo {json_file}")
        return
    
    print(f"📁 Migrando datos desde {json_file}...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            permissions_data = json.load(f)
        
        print(f"📊 Encontradas {len(permissions_data)} páginas en el JSON")
        
        # Extraer categorías únicas
        categories = {}
        for route, page_data in permissions_data.items():
            category_name = page_data.get('category', 'General')
            if category_name not in categories:
                categories[category_name] = {
                    'name': category_name,
                    'color': 'primary',  # Color por defecto
                    'pages': []
                }
            categories[category_name]['pages'].append((route, page_data))
        
        print(f"🏷️ Encontradas {len(categories)} categorías: {list(categories.keys())}")
        
        # Crear categorías
        category_objects = {}
        for cat_name, cat_data in categories.items():
            # Verificar si la categoría ya existe
            existing_category = Category.query.filter_by(name=cat_name).first()
            if existing_category:
                print(f"⚠️ Categoría '{cat_name}' ya existe, usando la existente")
                category_objects[cat_name] = existing_category
            else:
                category = Category(
                    name=cat_name,
                    color=cat_data['color'],
                    description=f'Categoría para páginas de {cat_name}'
                )
                db.session.add(category)
                db.session.flush()  # Para obtener el ID
                category_objects[cat_name] = category
                print(f"✅ Categoría '{cat_name}' creada")
        
        # Crear páginas y permisos
        pages_created = 0
        permissions_created = 0
        
        for cat_name, cat_data in categories.items():
            category = category_objects[cat_name]
            
            for route, page_data in cat_data['pages']:
                # Verificar si la página ya existe
                existing_page = Page.query.filter_by(route=route).first()
                if existing_page:
                    print(f"⚠️ Página '{route}' ya existe, saltando")
                    continue
                
                # Crear página
                page = Page(
                    route=route,
                    name=page_data.get('name', route),
                    description=page_data.get('description', ''),
                    category_id=category.id
                )
                db.session.add(page)
                db.session.flush()  # Para obtener el ID
                pages_created += 1
                
                # Crear permisos
                roles = page_data.get('roles', [])
                for role_str in roles:
                    try:
                        # Convertir string a enum
                        role_enum = UserRole(role_str.lower())
                        
                        permission = PagePermission(
                            page_id=page.id,
                            role=role_enum
                        )
                        db.session.add(permission)
                        permissions_created += 1
                        
                    except ValueError:
                        print(f"⚠️ Rol desconocido: {role_str} para página {route}")
                
                print(f"✅ Página '{route}' creada con {len(roles)} permisos")
        
        # Confirmar cambios
        db.session.commit()
        
        print(f"\n🎉 Migración completada:")
        print(f"   📁 {len(categories)} categorías")
        print(f"   📄 {pages_created} páginas creadas")
        print(f"   🔐 {permissions_created} permisos creados")
        
        # Crear respaldo del JSON
        backup_file = f"page_permissions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.rename(json_file, backup_file)
        print(f"📦 JSON original respaldado como: {backup_file}")
        
    except Exception as e:
        print(f"💥 Error durante la migración: {str(e)}")
        db.session.rollback()
        raise

def verify_migration():
    """Verificar que la migración fue exitosa"""
    print("\n🔍 Verificando migración...")
    
    categories_count = Category.query.count()
    pages_count = Page.query.count()
    permissions_count = PagePermission.query.count()
    
    print(f"📊 Resultados:")
    print(f"   🏷️ Categorías: {categories_count}")
    print(f"   📄 Páginas: {pages_count}")
    print(f"   🔐 Permisos: {permissions_count}")
    
    # Mostrar algunas categorías de ejemplo
    print(f"\n📋 Categorías existentes:")
    for category in Category.query.all():
        pages_count = len(category.pages)
        print(f"   - {category.name}: {pages_count} páginas")

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("🚀 Iniciando migración del sistema de permisos...")
        print("=" * 60)
        
        try:
            # Paso 1: Crear tablas
            create_permissions_tables()
            
            # Paso 2: Migrar datos
            migrate_from_json()
            
            # Paso 3: Verificar
            verify_migration()
            
            print("\n" + "=" * 60)
            print("🎉 ¡Migración completada exitosamente!")
            print("💡 Ahora puedes usar el sistema de permisos basado en base de datos")
            
        except Exception as e:
            print(f"\n💥 Error durante la migración: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
