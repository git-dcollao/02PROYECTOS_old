#!/usr/bin/env python3
"""
Script de inicialización mínima para el sistema
Solo crea lo esencial para que funcione el menú y el sistema de backup
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import text

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar el entorno antes de importar app
os.environ['FLASK_ENV'] = 'development'

def init_minimal_system():
    """Inicializar solo los datos mínimos necesarios"""
    try:
        from app import create_app, db
        from app.models import Page, PagePermission, Category, Trabajador, UserRole
        from werkzeug.security import generate_password_hash
        
        print("🚀 Iniciando inicialización mínima del sistema...")
        
        app = create_app()
        
        with app.app_context():
            try:
                # 1. LIMPIAR DATOS DUPLICADOS O PROBLEMÁTICOS
                print("\n📋 Paso 1: Limpiando datos problemáticos...")
                
                # Limpiar datos problemáticos de forma segura
                # Primero eliminar permisos relacionados con páginas duplicadas
                db.session.execute(text("DELETE FROM page_permissions WHERE page_id IN (SELECT id FROM pages WHERE route = '/admin/backup')"))
                # Luego eliminar las páginas duplicadas
                db.session.execute(text("DELETE FROM pages WHERE route = '/admin/backup'"))
                # Finalmente limpiar todos los permisos para recrear
                db.session.execute(text("DELETE FROM page_permissions"))
                db.session.commit()
                print("✅ Limpieza completada")
                
                # 2. CREAR/VERIFICAR CATEGORÍAS ESENCIALES
                print("\n📋 Paso 2: Creando categorías esenciales...")
                
                categorias_esenciales = [
                    {"name": "Sistema", "description": "Funciones del sistema", "display_order": 1, "is_visible": True},
                    {"name": "Administración", "description": "Herramientas de administración", "display_order": 2, "is_visible": True}
                ]
                
                for cat_data in categorias_esenciales:
                    categoria = Category.query.filter_by(name=cat_data["name"]).first()
                    if not categoria:
                        categoria = Category(
                            name=cat_data["name"],
                            description=cat_data["description"],
                            display_order=cat_data["display_order"],
                            is_visible=cat_data["is_visible"]
                        )
                        db.session.add(categoria)
                        print(f"   ✅ Categoría creada: {cat_data['name']}")
                    else:
                        print(f"   ✅ Categoría existe: {cat_data['name']}")
                
                db.session.commit()
                
                # 3. CREAR PÁGINAS ESENCIALES
                print("\n📋 Paso 3: Creando páginas esenciales...")
                
                # Obtener IDs de categorías
                cat_sistema = Category.query.filter_by(name="Sistema").first()
                cat_administracion = Category.query.filter_by(name="Administración").first()
                
                if not cat_sistema or not cat_administracion:
                    raise Exception("No se pudieron crear las categorías esenciales")
                
                paginas_esenciales = [
                    {
                        "route": "/",
                        "name": "Inicio",
                        "description": "Página principal del sistema",
                        "category_id": cat_sistema.id,
                        "display_order": 1,
                        "icon": "fas fa-home",
                        "is_visible": True,
                        "active": True
                    },
                    {
                        "route": "/admin/backup",
                        "name": "Gestión de Backups",
                        "description": "Sistema de backup y restauración",
                        "category_id": cat_administracion.id,
                        "display_order": 2,
                        "icon": "fas fa-database",
                        "is_visible": True,
                        "active": True
                    }
                ]
                
                for pagina_data in paginas_esenciales:
                    pagina = Page.query.filter_by(route=pagina_data["route"]).first()
                    if not pagina:
                        pagina = Page(
                            route=pagina_data["route"],
                            name=pagina_data["name"],
                            description=pagina_data["description"],
                            category_id=pagina_data["category_id"],
                            display_order=pagina_data["display_order"],
                            icon=pagina_data["icon"],
                            is_visible=pagina_data["is_visible"],
                            active=pagina_data["active"],
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        db.session.add(pagina)
                        print(f"   ✅ Página creada: {pagina_data['name']}")
                    else:
                        print(f"   ✅ Página existe: {pagina_data['name']}")
                
                db.session.commit()
                
                # 4. VERIFICAR/CREAR USUARIO SUPERADMIN
                print("\n📋 Paso 4: Verificando usuario superadmin...")
                
                admin_user = Trabajador.query.filter_by(email="admin@sistema.local").first()
                if not admin_user:
                    # Crear usuario admin
                    admin_user = Trabajador(
                        rut="11111111-1",
                        nombres="Administrador",
                        apellidos="Sistema",
                        email="admin@sistema.local",
                        password_hash=generate_password_hash("admin123"),
                        rol=UserRole.SUPERADMIN,
                        activo=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    print("   ✅ Usuario superadmin creado")
                else:
                    # Asegurar que tiene el rol correcto
                    if admin_user.rol != UserRole.SUPERADMIN:
                        admin_user.rol = UserRole.SUPERADMIN
                        db.session.commit()
                    print(f"   ✅ Usuario superadmin verificado: {admin_user.email}")
                
                # 5. CREAR PERMISOS ESENCIALES PARA SUPERADMIN
                print("\n📋 Paso 5: Creando permisos esenciales...")
                
                todas_las_paginas = Page.query.filter_by(active=True).all()
                print(f"   📄 Páginas activas encontradas: {len(todas_las_paginas)}")
                
                permisos_creados = 0
                for pagina in todas_las_paginas:
                    permiso_existente = PagePermission.query.filter_by(
                        page_id=pagina.id,
                        system_role=UserRole.SUPERADMIN,
                        role_name='SUPERADMIN'
                    ).first()
                    
                    if not permiso_existente:
                        permiso = PagePermission(
                            page_id=pagina.id,
                            system_role=UserRole.SUPERADMIN,
                            role_name='SUPERADMIN',
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        db.session.add(permiso)
                        permisos_creados += 1
                        print(f"   ✅ Permiso creado para: {pagina.name}")
                    else:
                        print(f"   ✅ Permiso existe para: {pagina.name}")
                
                db.session.commit()
                print(f"   📊 Total permisos: {permisos_creados}")
                
                # 6. VERIFICACIÓN FINAL
                print("\n📋 Paso 6: Verificación final...")
                
                paginas_count = Page.query.filter_by(active=True, is_visible=True).count()
                permisos_count = PagePermission.query.filter_by(
                    system_role=UserRole.SUPERADMIN,
                    role_name='SUPERADMIN'
                ).count()
                categorias_count = Category.query.filter_by(is_visible=True).count()
                
                print(f"   📄 Páginas activas: {paginas_count}")
                print(f"   🔐 Permisos SUPERADMIN: {permisos_count}")
                print(f"   📂 Categorías: {categorias_count}")
                
                print("\n🎉 ¡Inicialización mínima completada exitosamente!")
                print("=" * 50)
                print("🚀 SISTEMA LISTO PARA USAR")
                print("=" * 50)
                print(f"👤 Usuario: admin@sistema.local")
                print(f"🔑 Contraseña: admin123")
                print(f"🌐 URL: http://localhost:5050")
                print(f"💾 Backup: http://localhost:5050/admin/backup")
                print("=" * 50)
                
                return True
                
            except Exception as e:
                print(f"❌ Error durante la inicialización: {e}")
                db.session.rollback()
                raise e
                
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_minimal_system()
    sys.exit(0 if success else 1)