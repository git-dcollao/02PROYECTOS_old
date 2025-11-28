#!/usr/bin/env python3
"""
Script para diagnosticar problemas del menú
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Page, PagePermission, UserRole, Trabajador, Category
from app.services.menu_service import menu_service

def main():
    """Diagnosticar problemas del menú"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Diagnóstico del Sistema de Menú")
        print("=" * 50)
        
        # 1. Verificar usuario admin
        admin_user = Trabajador.query.filter_by(email='admin@sistema.local').first()
        if not admin_user:
            print("❌ Usuario admin no encontrado")
            return
        
        print(f"👤 Usuario: {admin_user.nombre}")
        print(f"   Email: {admin_user.email}")
        print(f"   Rol: {admin_user.rol}")
        print(f"   Activo: {admin_user.activo}")
        
        # 2. Verificar categorías
        categories = Category.query.filter_by(is_visible=True).order_by(Category.display_order).all()
        print(f"\n📂 Categorías disponibles: {len(categories)}")
        for cat in categories:
            print(f"   - {cat.name} (orden: {cat.display_order}, visible: {cat.is_visible})")
        
        # 3. Verificar páginas
        total_pages = Page.query.filter_by(active=True, is_visible=True).count()
        print(f"\n📄 Páginas activas y visibles: {total_pages}")
        
        # 4. Verificar páginas de backup específicamente
        backup_pages = Page.query.filter(Page.route.like('%backup%')).all()
        print(f"\n💾 Páginas de backup: {len(backup_pages)}")
        for page in backup_pages:
            print(f"   - {page.name} ({page.route})")
            print(f"     Activa: {page.active}, Visible: {page.is_visible}")
            if page.category_obj:
                print(f"     Categoría: {page.category_obj.name}")
        
        # 5. Verificar permisos para SUPERADMIN
        superadmin_perms = PagePermission.query.filter_by(role_name='SUPERADMIN').count()
        print(f"\n🔐 Permisos para SUPERADMIN: {superadmin_perms}")
        
        # Permisos específicos de backup
        backup_perms = 0
        for page in backup_pages:
            perm_count = PagePermission.query.filter_by(
                page_id=page.id,
                role_name='SUPERADMIN'
            ).count()
            backup_perms += perm_count
            print(f"   - {page.name}: {perm_count} permisos")
        
        # 6. Probar generación de menú para el usuario admin
        print(f"\n🧪 Probando generación de menú para usuario admin...")
        
        try:
            # Simular contexto de usuario autenticado
            from flask import Flask
            from flask_login import LoginManager
            
            # Limpiar cache del menú
            menu_service.clear_cache()
            
            # Intentar obtener menú
            user_menu = menu_service._build_user_menu(admin_user)
            
            print(f"✅ Menú generado exitosamente: {len(user_menu)} categorías")
            
            for category in user_menu:
                print(f"\n📂 Categoría: {category['category']}")
                print(f"   - Páginas: {category['count']}")
                print(f"   - Icono: {category['icon']}")
                print(f"   - Color: {category['color']}")
                
                for page in category['pages']:
                    print(f"     • {page['name']} ({page['url']})")
        
        except Exception as e:
            print(f"❌ Error generando menú: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 7. Verificar función de template
        print(f"\n🔧 Verificando funciones de template...")
        try:
            from app.jinja_filters import get_user_menu
            print("✅ Función get_user_menu disponible")
        except Exception as e:
            print(f"❌ Error con funciones de template: {str(e)}")

if __name__ == "__main__":
    main()