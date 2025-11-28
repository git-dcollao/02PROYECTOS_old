#!/usr/bin/env python3
"""
Script para corregir completamente el sistema de menú y permisos
Limpia y recrea las páginas, permisos y menú para garantizar funcionamiento correcto
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

try:
    from app import create_app, db
    from app.models import Page, PagePermission, Category, Trabajador, UserRole
    from werkzeug.security import generate_password_hash
    
    print("🔧 Iniciando corrección completa del sistema de menú...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. LIMPIAR DATOS DUPLICADOS O CORRUPTOS
            print("\n📋 Paso 1: Limpiando datos duplicados...")
            
            # Eliminar permisos huérfanos
            db.session.execute(text("DELETE FROM page_permissions WHERE page_id NOT IN (SELECT id FROM pages)"))
            
            # Eliminar páginas duplicadas de backup
            db.session.execute(text("DELETE FROM pages WHERE route = '/admin/backup'"))
            
            # Limpiar permisos
            db.session.execute(text("DELETE FROM page_permissions"))
            
            db.session.commit()
            print("✅ Datos duplicados eliminados")
            
            # 2. VERIFICAR CATEGORÍAS
            print("\n📋 Paso 2: Verificando categorías...")
            
            categorias_requeridas = [
                {"name": "Sistema", "description": "Configuración del sistema", "display_order": 1, "is_visible": True},
                {"name": "Requerimiento", "description": "Gestión de requerimientos", "display_order": 2, "is_visible": True},
                {"name": "Usuarios", "description": "Gestión de usuarios", "display_order": 3, "is_visible": True},
                {"name": "Configuración", "description": "Configuración general", "display_order": 4, "is_visible": True},
                {"name": "Administración", "description": "Herramientas de administración", "display_order": 5, "is_visible": True}
            ]
            
            for cat_data in categorias_requeridas:
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
            
            # 3. CREAR PÁGINAS PRINCIPALES
            print("\n📋 Paso 3: Creando páginas principales...")
            
            # Obtener IDs de categorías
            cat_sistema = Category.query.filter_by(name="Sistema").first()
            cat_usuarios = Category.query.filter_by(name="Usuarios").first()
            cat_administracion = Category.query.filter_by(name="Administración").first()
            
            paginas_principales = [
                {
                    "route": "/",
                    "name": "Dashboard",
                    "description": "Panel principal del sistema",
                    "category_id": cat_sistema.id,
                    "display_order": 1,
                    "icon": "fas fa-tachometer-alt",
                    "is_visible": True,
                    "active": True
                },
                {
                    "route": "/admin",
                    "name": "Administración",
                    "description": "Panel de administración",
                    "category_id": cat_administracion.id,
                    "display_order": 2,
                    "icon": "fas fa-cogs",
                    "is_visible": True,
                    "active": True
                },
                {
                    "route": "/admin/users",
                    "name": "Gestión de Usuarios",
                    "description": "Administrar usuarios del sistema",
                    "category_id": cat_usuarios.id,
                    "display_order": 3,
                    "icon": "fas fa-users",
                    "is_visible": True,
                    "active": True
                },
                {
                    "route": "/admin/backup",
                    "name": "Gestión de Backups",
                    "description": "Crear y restaurar copias de seguridad de la base de datos",
                    "category_id": cat_administracion.id,
                    "display_order": 4,
                    "icon": "fas fa-database",
                    "is_visible": True,
                    "active": True
                }
            ]
            
            for pagina_data in paginas_principales:
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
                    # Actualizar página existente
                    pagina.name = pagina_data["name"]
                    pagina.description = pagina_data["description"]
                    pagina.category_id = pagina_data["category_id"]
                    pagina.display_order = pagina_data["display_order"]
                    pagina.icon = pagina_data["icon"]
                    pagina.is_visible = pagina_data["is_visible"]
                    pagina.active = pagina_data["active"]
                    pagina.updated_at = datetime.now()
                    print(f"   ✅ Página actualizada: {pagina_data['name']}")
            
            db.session.commit()
            
            # 4. CREAR PERMISOS PARA SUPERADMIN
            print("\n📋 Paso 4: Creando permisos para rol SUPERADMIN...")
            
            # Obtener todas las páginas
            todas_las_paginas = Page.query.filter_by(active=True).all()
            print(f"   📄 Páginas encontradas: {len(todas_las_paginas)}")
            
            # Crear permisos para cada página usando el rol SUPERADMIN
            permisos_creados = 0
            for pagina in todas_las_paginas:
                # Verificar si ya existe el permiso para SUPERADMIN
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
                    # Actualizar permiso existente
                    permiso_existente.updated_at = datetime.now()
                    print(f"   ✅ Permiso existe para: {pagina.name}")
            
            db.session.commit()
            print(f"   📊 Total permisos procesados: {permisos_creados}")
            
            # Verificar el usuario admin tiene el rol correcto
            admin_user = Trabajador.query.filter_by(email="admin@sistema.local").first()
            if admin_user and admin_user.rol != UserRole.SUPERADMIN:
                admin_user.rol = UserRole.SUPERADMIN
                db.session.commit()
                print("   ✅ Rol de admin actualizado a SUPERADMIN")
            
            # 5. VERIFICACIÓN FINAL
            print("\n📋 Paso 5: Verificación final...")
            
            # Contar páginas activas
            paginas_activas = Page.query.filter_by(active=True, is_visible=True).count()
            print(f"   📄 Páginas activas y visibles: {paginas_activas}")
            
            # Contar permisos para SUPERADMIN
            permisos_admin = PagePermission.query.filter_by(
                system_role=UserRole.SUPERADMIN,
                role_name='SUPERADMIN'
            ).count()
            print(f"   🔐 Permisos para SUPERADMIN: {permisos_admin}")
            
            # Verificar usuario admin
            admin_user = Trabajador.query.filter_by(email="admin@sistema.local").first()
            if admin_user:
                print(f"   👤 Usuario admin: {admin_user.email} - Rol: {admin_user.rol}")
            else:
                print("   ❌ Usuario admin no encontrado")
            
            # Contar categorías
            categorias_activas = Category.query.filter_by(is_visible=True).count()
            print(f"   📂 Categorías activas: {categorias_activas}")
            
            # 6. PROBAR GENERACIÓN DEL MENÚ
            print("\n📋 Paso 6: Probando generación del menú...")
            
            try:
                from app.services.menu_service import get_user_menu
                admin_user = Trabajador.query.filter_by(email="admin@sistema.local").first()
                if admin_user:
                    menu_data = get_user_menu(admin_user.id)
                    print(f"   ✅ Menú generado: {len(menu_data)} categorías")
                    
                    for categoria in menu_data:
                        print(f"      - {categoria['name']}: {len(categoria['pages'])} páginas")
                else:
                    print("   ❌ Usuario admin no encontrado para prueba de menú")
                    
            except Exception as e:
                print(f"   ❌ Error generando menú: {e}")
            
            print("\n🎉 ¡Corrección del sistema de menú completada!")
            print("=" * 50)
            print("📊 RESUMEN:")
            print(f"   📄 Páginas activas: {paginas_activas}")
            print(f"   🔐 Permisos para SUPERADMIN: {permisos_admin}")
            print(f"   📂 Categorías: {categorias_activas}")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error durante la corrección: {e}")
            db.session.rollback()
            raise e
            
except Exception as e:
    print(f"❌ Error crítico: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)