#!/usr/bin/env python3
"""
Debug específico para verificar los datos del menú que se están pasando al template
"""
import sys
import os

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Trabajador
from app.services.menu_service import MenuService
from flask_login import login_user
import json

def debug_menu_data():
    print("🔍 DEBUG ESPECÍFICO - DATOS DEL MENÚ")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        with app.test_request_context():
            # Obtener el usuario administrador
            admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
            
            if not admin_user:
                print("❌ Usuario administrador no encontrado")
                return
            
            print(f"✅ Usuario encontrado: {admin_user.email}")
            print(f"📋 Rol: {admin_user.rol}")
            print(f"📋 Custom Role ID: {admin_user.custom_role_id}")
            
            # Login simulado para establecer current_user
            login_user(admin_user)
            
            # Obtener el menú usando el servicio
            menu_service = MenuService()
            user_menu = menu_service.get_user_menu(admin_user)
            
            print(f"\n📊 DATOS DEL MENÚ GENERADO:")
            print(f"📋 Categorías encontradas: {len(user_menu) if user_menu else 0}")
            
            if user_menu:
                for i, category in enumerate(user_menu):
                    print(f"\n📂 Categoría {i+1}: {category.get('category', 'Sin nombre')}")
                    print(f"   🎨 Icono: {category.get('icon', 'Sin icono')}")
                    print(f"   📊 Count: {category.get('count', 0)}")
                    print(f"   📄 Páginas: {len(category.get('pages', []))}")
                    
                    # Si es la categoría Configuración, mostrar detalles
                    if category.get('category') == 'Configuración':
                        print(f"\n🔍 DETALLES DE CONFIGURACIÓN:")
                        pages = category.get('pages', [])
                        for j, page in enumerate(pages):
                            print(f"   📄 Página {j+1}:")
                            print(f"      - name: '{page.get('name', 'SIN NOMBRE')}'")
                            print(f"      - url: '{page.get('url', 'SIN URL')}'")
                            print(f"      - icon: '{page.get('icon', 'SIN ICONO')}'")
                            
                            # ¡AQUÍ ESTÁ EL DEBUG CRÍTICO!
                            print(f"      - TODAS LAS CLAVES: {list(page.keys())}")
                            
                            # Verificar si hay claves extrañas
                            for key, value in page.items():
                                if key not in ['name', 'url', 'icon', 'description', 'target_blank', 'is_external', 'menu_group', 'children']:
                                    print(f"      - ⚠️ CLAVE INESPERADA: {key} = {value}")
            
            # También vamos a verificar los datos RAW de las páginas
            print(f"\n🔍 VERIFICACIÓN RAW DE PÁGINAS CONFIGURACIÓN:")
            from app.models import Page, Category
            
            config_category = Category.query.filter_by(name='Configuración').first()
            if config_category:
                config_pages = Page.query.filter_by(
                    category_id=config_category.id,
                    active=True,
                    is_visible=True
                ).all()
                
                print(f"📊 Páginas Configuración en BD: {len(config_pages)}")
                for page in config_pages[:3]:  # Solo mostrar las primeras 3
                    print(f"   📄 {page.name} → {page.route}")
                    print(f"      - ID: {page.id}")
                    print(f"      - Icono: {page.icon}")
                    print(f"      - Display Order: {page.display_order}")
            else:
                print("❌ Categoría 'Configuración' no encontrada en BD")

if __name__ == "__main__":
    debug_menu_data()