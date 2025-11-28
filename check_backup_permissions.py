#!/usr/bin/env python3
"""
Script para verificar permisos de backup en el sistema
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Page, PagePermission, UserRole, Trabajador

def main():
    """Verificar configuración de permisos de backup"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Verificando configuración de backup...")
        
        # Buscar páginas de backup
        backup_pages = Page.query.filter(Page.route.like('%backup%')).all()
        
        print(f"\n📋 Páginas de backup encontradas: {len(backup_pages)}")
        for page in backup_pages:
            print(f"  - {page.name} ({page.route}) - Visible: {page.is_visible} - Activa: {page.active}")
            if page.category_obj:
                print(f"    Categoría: {page.category_obj.name}")
        
        # Buscar permisos para SUPERADMIN
        superadmin_permissions = PagePermission.query.filter_by(role_name='SUPERADMIN').all()
        backup_permissions = []
        
        for perm in superadmin_permissions:
            if perm.page and 'backup' in perm.page.route.lower():
                backup_permissions.append(perm)
        
        print(f"\n🔐 Permisos de backup para SUPERADMIN: {len(backup_permissions)}")
        for perm in backup_permissions:
            if perm.page:
                print(f"  - {perm.page.name} ({perm.page.route})")
        
        # Buscar usuario admin
        admin_user = Trabajador.query.filter_by(email='admin@sistema.local').first()
        if admin_user:
            print(f"\n👤 Usuario admin encontrado:")
            print(f"  - Nombre: {admin_user.nombre}")
            print(f"  - Email: {admin_user.email}")
            print(f"  - Rol: {admin_user.rol}")
            print(f"  - Activo: {admin_user.activo}")
        else:
            print("\n❌ Usuario admin no encontrado")
        
        # Verificar total de páginas con permisos para SUPERADMIN
        total_permissions = len(superadmin_permissions)
        print(f"\n📊 Total de permisos para SUPERADMIN: {total_permissions}")
        
        if total_permissions == 0:
            print("⚠️ No hay permisos configurados para SUPERADMIN")
            print("💡 Esto podría indicar que los datos iniciales no se crearon correctamente")

if __name__ == "__main__":
    main()