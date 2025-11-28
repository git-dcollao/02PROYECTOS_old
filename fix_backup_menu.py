#!/usr/bin/env python3
"""
Script para arreglar el problema de páginas y permisos de backup
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Page, PagePermission, UserRole, Category

def main():
    """Arreglar configuración de backup"""
    app = create_app()
    
    with app.app_context():
        from app import db
        
        print("🔧 Arreglando configuración de backup...")
        
        # 1. Buscar páginas duplicadas de backup
        backup_pages = Page.query.filter(Page.route.like('%backup%')).all()
        
        print(f"\n📋 Páginas de backup encontradas: {len(backup_pages)}")
        for page in backup_pages:
            print(f"  - ID: {page.id}, Nombre: {page.name}, Ruta: {page.route}")
        
        # 2. Si existe la página pero sin permisos para SUPERADMIN, agregarlos
        if backup_pages:
            backup_page = backup_pages[0]  # Usar la primera página encontrada
            
            # Verificar si ya tiene permisos para SUPERADMIN
            existing_permission = PagePermission.query.filter_by(
                page_id=backup_page.id,
                role_name='SUPERADMIN'
            ).first()
            
            if not existing_permission:
                print(f"🔧 Agregando permisos de SUPERADMIN para: {backup_page.name}")
                
                new_permission = PagePermission(
                    page_id=backup_page.id,
                    system_role=UserRole.SUPERADMIN,
                    role_name='SUPERADMIN'
                )
                
                db.session.add(new_permission)
                db.session.commit()
                
                print("✅ Permisos agregados exitosamente")
            else:
                print("✅ Los permisos ya existen para esta página")
        
        else:
            # 3. Si no existe la página, crearla
            print("🔧 Creando página de backup...")
            
            # Buscar categoría de Administración
            admin_category = Category.query.filter_by(name='Administración').first()
            
            if not admin_category:
                print("❌ No se encontró la categoría de Administración")
                return
            
            # Crear la página
            backup_page = Page(
                route='/admin/backup',
                name='Gestión de Backups',
                description='Crear y restaurar copias de seguridad de la base de datos',
                category_id=admin_category.id,
                display_order=8,
                icon='fas fa-database',
                is_visible=True,
                active=True
            )
            
            db.session.add(backup_page)
            db.session.flush()  # Para obtener el ID
            
            # Crear permiso para SUPERADMIN
            backup_permission = PagePermission(
                page_id=backup_page.id,
                system_role=UserRole.SUPERADMIN,
                role_name='SUPERADMIN'
            )
            
            db.session.add(backup_permission)
            db.session.commit()
            
            print("✅ Página y permisos de backup creados exitosamente")
        
        # 4. Verificar resultado final
        print("\n🔍 Verificación final...")
        
        final_backup_pages = Page.query.filter(Page.route.like('%backup%')).all()
        print(f"📋 Páginas de backup: {len(final_backup_pages)}")
        
        for page in final_backup_pages:
            permissions = PagePermission.query.filter_by(
                page_id=page.id,
                role_name='SUPERADMIN'
            ).all()
            print(f"  - {page.name}: {len(permissions)} permisos para SUPERADMIN")
        
        print("\n🎉 Configuración de backup completada")

if __name__ == "__main__":
    main()