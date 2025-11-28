#!/usr/bin/env python3
"""
Diagnóstico específico para el problema del menú del usuario superadmin
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Trabajador, PagePermission, Page, Category, UserRole
from app.services.menu_service import menu_service
from flask_login import login_user

def diagnose_superadmin_menu():
    """Diagnosticar el problema del menú del superadmin"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DIAGNÓSTICO DEL MENÚ SUPERADMIN")
        print("=" * 50)
        
        # 1. Buscar usuario superadmin
        print("\n1. 🔍 BUSCAR USUARIO SUPERADMIN")
        superadmin = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if not superadmin:
            print("❌ No se encontró usuario administrador@sistema.local")
            return
        
        print(f"✅ Usuario encontrado: {superadmin.nombre} ({superadmin.email})")
        print(f"   📊 ID: {superadmin.id}")
        print(f"   🔑 Rol: {superadmin.rol}")
        print(f"   🎭 Custom Role ID: {superadmin.custom_role_id}")
        print(f"   🏢 Recinto ID: {superadmin.recinto_id}")
        print(f"   ✅ Activo: {superadmin.activo}")
        print(f"   🔐 is_superadmin(): {superadmin.is_superadmin()}")
        
        # 2. Verificar permisos del usuario
        print(f"\n2. 🔍 VERIFICAR PERMISOS DEL USUARIO")
        
        # Buscar permisos por rol del sistema
        if superadmin.rol:
            role_name = superadmin.rol.name if hasattr(superadmin.rol, 'name') else str(superadmin.rol).upper()
            print(f"   🔍 Buscando permisos por rol del sistema: {role_name}")
            
            system_permissions = PagePermission.query.join(Page).join(Category).filter(
                PagePermission.role_name == role_name,
                Page.active == True,
                Page.is_visible == True,
                Category.is_visible == True
            ).all()
            
            print(f"   📊 Permisos encontrados por rol del sistema: {len(system_permissions)}")
            for perm in system_permissions[:5]:  # Mostrar solo los primeros 5
                print(f"      - {perm.page.name} ({perm.page.route})")
            if len(system_permissions) > 5:
                print(f"      ... y {len(system_permissions) - 5} más")
        
        # Buscar permisos por custom role
        if superadmin.custom_role_id:
            print(f"   🔍 Buscando permisos por custom role: {superadmin.custom_role_id}")
            
            custom_permissions = PagePermission.query.join(Page).join(Category).filter(
                PagePermission.custom_role_id == superadmin.custom_role_id,
                Page.active == True,
                Page.is_visible == True,
                Category.is_visible == True
            ).all()
            
            print(f"   📊 Permisos encontrados por custom role: {len(custom_permissions)}")
            for perm in custom_permissions[:5]:  # Mostrar solo los primeros 5
                print(f"      - {perm.page.name} ({perm.page.route})")
            if len(custom_permissions) > 5:
                print(f"      ... y {len(custom_permissions) - 5} más")
        
        # 3. Obtener menú usando el servicio
        print(f"\n3. 🔍 OBTENER MENÚ USANDO EL SERVICIO")
        try:
            menu = menu_service.get_user_menu(superadmin)
            print(f"   📊 Menú generado: {type(menu)}")
            print(f"   📊 Número de categorías: {len(menu) if menu else 0}")
            
            if menu:
                for i, category in enumerate(menu):
                    print(f"   📂 Categoría {i+1}: {category.get('category', 'Sin nombre')}")
                    print(f"      🎨 Icono: {category.get('icon', 'Sin icono')}")
                    print(f"      📄 Páginas: {category.get('count', 0)}")
                    
                    pages = category.get('pages', [])
                    for j, page in enumerate(pages[:3]):  # Mostrar solo las primeras 3
                        print(f"         {j+1}. {page.get('name')} -> {page.get('url')}")
                    if len(pages) > 3:
                        print(f"         ... y {len(pages) - 3} páginas más")
            else:
                print("   ❌ Menú vacío o None")
                
        except Exception as e:
            print(f"   ❌ Error generando menú: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Verificar páginas totales disponibles
        print(f"\n4. 🔍 PÁGINAS TOTALES EN EL SISTEMA")
        total_pages = Page.query.filter_by(active=True, is_visible=True).count()
        total_categories = Category.query.filter_by(is_visible=True).count()
        total_permissions = PagePermission.query.count()
        
        print(f"   📊 Total páginas activas y visibles: {total_pages}")
        print(f"   📊 Total categorías visibles: {total_categories}")
        print(f"   📊 Total permisos en sistema: {total_permissions}")
        
        # 5. Verificar UserRole enum
        print(f"\n5. 🔍 VERIFICAR ENUM USERROLE")
        try:
            print(f"   📊 UserRole disponibles:")
            for role in UserRole:
                print(f"      - {role.name}: {role.value}")
                
            # Verificar si el rol del superadmin está en el enum
            if superadmin.rol:
                if isinstance(superadmin.rol, UserRole):
                    print(f"   ✅ Rol del superadmin ({superadmin.rol.name}) está en UserRole enum")
                else:
                    print(f"   ⚠️ Rol del superadmin ({superadmin.rol}) NO es un UserRole enum")
                    
        except Exception as e:
            print(f"   ❌ Error verificando UserRole: {e}")
        
        # 6. Verificar permisos específicos para SUPERADMIN
        print(f"\n6. 🔍 VERIFICAR PERMISOS ESPECÍFICOS PARA SUPERADMIN")
        superadmin_permissions = PagePermission.query.filter_by(role_name='SUPERADMIN').all()
        print(f"   📊 Permisos encontrados para role_name='SUPERADMIN': {len(superadmin_permissions)}")
        
        for perm in superadmin_permissions[:10]:  # Mostrar primeros 10
            print(f"      - {perm.page.name} ({perm.page.route}) - Categoría: {perm.page.category_obj.name}")
        
        if len(superadmin_permissions) > 10:
            print(f"      ... y {len(superadmin_permissions) - 10} más")

if __name__ == "__main__":
    diagnose_superadmin_menu()