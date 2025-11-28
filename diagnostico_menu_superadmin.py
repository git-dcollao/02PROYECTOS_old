#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico del menú para usuario superadmin
Verifica permisos, páginas y configuración del menú
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, Page, Category, PagePermission, UserRole
from app.services.menu_service import menu_service
from config import DevelopmentConfig

def diagnosticar_menu_superadmin():
    """Diagnosticar configuración del menú para superadmin"""
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        print("=" * 80)
        print("🔍 DIAGNÓSTICO DE MENÚ PARA SUPERADMIN")
        print("=" * 80)
        print()
        
        # 1. Verificar usuario superadmin
        print("📋 PASO 1: Verificando usuario admin@sistema.local")
        print("-" * 80)
        
        admin = Trabajador.query.filter_by(email='admin@sistema.local').first()
        
        if not admin:
            print("❌ Usuario admin@sistema.local NO ENCONTRADO")
            return False
        
        print(f"✅ Usuario encontrado: {admin.nombre}")
        print(f"   - ID: {admin.id}")
        print(f"   - Email: {admin.email}")
        print(f"   - Rol sistema: {admin.rol}")
        print(f"   - Custom role ID: {admin.custom_role_id}")
        print(f"   - Activo: {admin.activo}")
        print(f"   - Is authenticated: {admin.is_authenticated}")
        print()
        
        # Verificar método is_superadmin
        try:
            is_super = admin.is_superadmin()
            print(f"   - is_superadmin(): {is_super}")
        except Exception as e:
            print(f"   ❌ Error llamando is_superadmin(): {e}")
        print()
        
        # 2. Verificar páginas en la base de datos
        print("📋 PASO 2: Verificando páginas en la base de datos")
        print("-" * 80)
        
        total_pages = Page.query.count()
        active_pages = Page.query.filter_by(active=True).count()
        visible_pages = Page.query.filter_by(active=True, is_visible=True).count()
        
        print(f"   Total de páginas: {total_pages}")
        print(f"   Páginas activas: {active_pages}")
        print(f"   Páginas visibles: {visible_pages}")
        print()
        
        # Listar algunas páginas importantes
        important_pages = Page.query.filter(
            Page.route.in_(['/permissions/', '/admin/trabajadores', '/dashboard'])
        ).all()
        
        print("   📄 Páginas importantes:")
        for page in important_pages:
            print(f"      - {page.name} ({page.route}) - Activa: {page.active}, Visible: {page.is_visible}")
        print()
        
        # 3. Verificar categorías
        print("📋 PASO 3: Verificando categorías")
        print("-" * 80)
        
        categories = Category.query.filter_by(is_visible=True).all()
        print(f"   Total categorías visibles: {len(categories)}")
        for cat in categories:
            pages_count = Page.query.filter_by(
                category_id=cat.id,
                active=True,
                is_visible=True
            ).count()
            print(f"      - {cat.name} (orden: {cat.display_order}) - {pages_count} páginas")
        print()
        
        # 4. Verificar permisos para SUPERADMIN
        print("📋 PASO 4: Verificando permisos para rol SUPERADMIN")
        print("-" * 80)
        
        superadmin_permissions = PagePermission.query.filter_by(
            role_name='SUPERADMIN'
        ).all()
        
        print(f"   Permisos encontrados para SUPERADMIN: {len(superadmin_permissions)}")
        
        if len(superadmin_permissions) == 0:
            print("   ❌ NO HAY PERMISOS CONFIGURADOS PARA SUPERADMIN")
            print("   ⚠️  ESTO ES EL PROBLEMA - El superadmin debe tener permisos!")
        else:
            print("   Primeros 10 permisos:")
            for i, perm in enumerate(superadmin_permissions[:10], 1):
                page = perm.page
                print(f"      {i}. {page.name} ({page.route})")
        print()
        
        # 5. Verificar menú generado
        print("📋 PASO 5: Verificando menú generado para el usuario")
        print("-" * 80)
        
        try:
            menu_service.clear_cache()
            menu = menu_service.get_user_menu(admin)
            
            print(f"   Categorías en el menú: {len(menu)}")
            
            total_items = 0
            for category in menu:
                cat_name = category.get('category', 'Sin nombre')
                pages_count = category.get('count', 0)
                total_items += pages_count
                print(f"      - {cat_name}: {pages_count} páginas")
                
                # Mostrar las páginas
                for page in category.get('pages', [])[:5]:  # Solo primeras 5
                    print(f"         · {page.get('name')} -> {page.get('url')}")
            
            print()
            print(f"   ✅ Total de items en el menú: {total_items}")
            
            # Verificar si está la página de permisos
            tiene_permisos = False
            for category in menu:
                for page in category.get('pages', []):
                    if '/permissions' in page.get('url', ''):
                        tiene_permisos = True
                        print(f"   ✅ Página de permisos ENCONTRADA en el menú")
                        break
            
            if not tiene_permisos:
                print(f"   ❌ Página de permisos NO ENCONTRADA en el menú")
            
        except Exception as e:
            print(f"   ❌ Error generando menú: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # 6. Recomendaciones
        print("=" * 80)
        print("💡 RECOMENDACIONES")
        print("=" * 80)
        
        if len(superadmin_permissions) == 0:
            print("""
⚠️  PROBLEMA DETECTADO: No hay permisos configurados para el rol SUPERADMIN

SOLUCIÓN:
1. El sistema debe configurar permisos automáticamente para SUPERADMIN
2. O bien, SUPERADMIN debe tener acceso a TODAS las páginas sin verificar permisos

Opciones para resolver:

A) Crear permisos para SUPERADMIN en todas las páginas:
   - Ejecutar script de seeds para crear permisos
   - O crear manualmente los permisos en la tabla page_permissions

B) Modificar el código para que SUPERADMIN tenga acceso total:
   - Modificar menu_service.py para dar acceso a todas las páginas si is_superadmin()
   - No depender de PagePermission para superadmin
            """)
        else:
            print("✅ El sistema tiene permisos configurados correctamente")
        
        print()
        return True

if __name__ == '__main__':
    diagnosticar_menu_superadmin()
