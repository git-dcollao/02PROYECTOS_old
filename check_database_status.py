#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos después de ejecutar seeds
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, UserRole, CustomRole, Page, Category, PagePermission

def check_database_status():
    """Verificar el estado completo de la base de datos"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 VERIFICACIÓN DEL ESTADO DE LA BASE DE DATOS")
        print("=" * 60)
        
        # 1. Verificar usuarios SUPERADMIN
        print("\n1️⃣ USUARIOS SUPERADMIN:")
        superadmin_users = Trabajador.query.filter_by(rol=UserRole.SUPERADMIN).all()
        print(f"   Total usuarios SUPERADMIN: {len(superadmin_users)}")
        for user in superadmin_users:
            nombre = getattr(user, 'nombre_completo', getattr(user, 'nombre', 'Sin nombre'))
            print(f"   - {user.email} ({nombre}) - Activo: {user.activo}")
        
        # 2. Verificar categorías
        print("\n2️⃣ CATEGORÍAS:")
        categories = Category.query.filter_by(is_visible=True).order_by(Category.display_order).all()
        print(f"   Total categorías visibles: {len(categories)}")
        for cat in categories:
            print(f"   - {cat.name} (Orden: {cat.display_order}, Visible: {cat.is_visible})")
        
        # 3. Verificar páginas
        print("\n3️⃣ PÁGINAS:")
        pages = Page.query.filter_by(active=True, is_visible=True).order_by(Page.name).all()
        print(f"   Total páginas activas y visibles: {len(pages)}")
        for page in pages[:10]:  # Mostrar solo las primeras 10
            print(f"   - {page.name} ({page.route}) - Categoría: {page.category_obj.name if page.category_obj else 'Sin categoría'}")
        if len(pages) > 10:
            print(f"   ... y {len(pages) - 10} páginas más")
        
        # 4. Verificar permisos para SUPERADMIN
        print("\n4️⃣ PERMISOS SUPERADMIN:")
        superadmin_permissions = PagePermission.query.filter_by(role_name='SUPERADMIN').all()
        print(f"   Total permisos para SUPERADMIN: {len(superadmin_permissions)}")
        
        # Verificar si SUPERADMIN tiene acceso a todas las páginas
        total_pages = Page.query.filter_by(active=True, is_visible=True).count()
        print(f"   Páginas totales activas/visibles: {total_pages}")
        print(f"   Permisos SUPERADMIN: {len(superadmin_permissions)}")
        
        if len(superadmin_permissions) < total_pages:
            print("   ⚠️  PROBLEMA: SUPERADMIN no tiene permisos para todas las páginas")
            
            # Mostrar páginas sin permisos para SUPERADMIN
            permitted_page_ids = [p.page_id for p in superadmin_permissions]
            missing_pages = Page.query.filter(
                Page.active == True,
                Page.is_visible == True,
                ~Page.id.in_(permitted_page_ids)
            ).all()
            
            print(f"   Páginas sin permisos para SUPERADMIN: {len(missing_pages)}")
            for page in missing_pages:
                print(f"     - {page.name} (ID: {page.id})")
        else:
            print("   ✅ SUPERADMIN tiene permisos para todas las páginas")
        
        # 5. Verificar estructura del menú para SUPERADMIN
        print("\n5️⃣ ESTRUCTURA DEL MENÚ PARA SUPERADMIN:")
        
        # Simular la lógica del menu_service
        from app.services.menu_service import MenuService
        menu_service = MenuService()
        
        # Obtener primer usuario SUPERADMIN para prueba
        if superadmin_users:
            test_user = superadmin_users[0]
            print(f"   Probando menú para: {test_user.email}")
            
            try:
                menu = menu_service.get_user_menu(test_user)
                print(f"   Categorías en el menú: {len(menu)}")
                
                total_pages_in_menu = 0
                for category in menu:
                    page_count = len(category.get('pages', []))
                    total_pages_in_menu += page_count
                    print(f"   - {category['category']}: {page_count} páginas")
                
                print(f"   Total páginas en el menú: {total_pages_in_menu}")
                
                if total_pages_in_menu == 0:
                    print("   ❌ PROBLEMA: El menú está vacío para SUPERADMIN")
                else:
                    print("   ✅ El menú tiene contenido")
                    
            except Exception as e:
                print(f"   ❌ ERROR generando menú: {e}")
        else:
            print("   ❌ No hay usuarios SUPERADMIN para probar")
        
        # 6. Verificar roles personalizados
        print("\n6️⃣ ROLES PERSONALIZADOS:")
        custom_roles = CustomRole.query.all()
        print(f"   Total roles personalizados: {len(custom_roles)}")
        for role in custom_roles:
            permissions_count = PagePermission.query.filter_by(custom_role_id=role.id).count()
            print(f"   - {role.name}: {permissions_count} permisos")
        
        print("\n" + "=" * 60)
        print("✅ Verificación completada")

if __name__ == '__main__':
    check_database_status()