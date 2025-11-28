#!/usr/bin/env python3
"""
Script para probar específicamente qué está mostrando el menú del usuario administrador
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, CustomRole
from app.services.menu_service import MenuService

def probar_menu_administrador_detallado():
    app = create_app()
    
    with app.app_context():
        print("=== PRUEBA DETALLADA MENÚ ADMINISTRADOR ===")
        
        # Obtener usuario administrador
        admin = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if not admin:
            print("❌ Usuario administrador no encontrado")
            return
            
        print(f"👤 Usuario: {admin.nombre}")
        print(f"   Email: {admin.email}")
        print(f"   Rol sistema: {admin.rol}")
        print(f"   Custom role ID: {admin.custom_role_id}")
        
        # Verificar custom role
        if admin.custom_role_id:
            custom_role = CustomRole.query.get(admin.custom_role_id)
            if custom_role:
                print(f"   Custom role: {custom_role.name}")
        
        # Obtener menú usando el servicio
        menu_service = MenuService()
        menu = menu_service.get_user_menu(admin)
        
        print(f"\n📋 MENÚ GENERADO ({len(menu)} categorías):")
        
        for i, categoria in enumerate(menu):
            print(f"\n{i+1}. 📁 {categoria['category']}")
            print(f"   Icono: {categoria.get('icon', 'N/A')}")
            print(f"   Count: {categoria.get('count', 0)}")
            print(f"   Display order: {categoria.get('display_order', 'N/A')}")
            
            pages = categoria.get('pages', [])
            print(f"   Páginas ({len(pages)}):")
            
            if len(pages) == 0:
                print("      ❌ SIN PÁGINAS")
            else:
                for j, page in enumerate(pages[:5]):  # Mostrar solo las primeras 5
                    print(f"      {j+1}. {page.get('name', '❌ SIN NOMBRE')} → {page.get('url', '❌ SIN URL')}")
                if len(pages) > 5:
                    print(f"      ... y {len(pages) - 5} más")
        
        # Buscar específicamente la categoría "Configuración"
        print(f"\n🔍 ANÁLISIS ESPECÍFICO CATEGORÍA 'CONFIGURACIÓN':")
        config_cat = None
        for cat in menu:
            if 'configuración' in cat['category'].lower() or 'config' in cat['category'].lower():
                config_cat = cat
                break
        
        if config_cat:
            print(f"✅ Categoría encontrada: {config_cat['category']}")
            print(f"   Datos completos:")
            for key, value in config_cat.items():
                if key != 'pages':
                    print(f"      {key}: {value}")
            
            print(f"\n   📄 PÁGINAS DETALLADAS:")
            pages = config_cat.get('pages', [])
            for page in pages:
                print(f"      📄 {page.get('name', '❌ SIN NOMBRE')}")
                print(f"         URL: {page.get('url', '❌ SIN URL')}")
                print(f"         Icon: {page.get('icon', 'N/A')}")
                print(f"         Description: {page.get('description', 'N/A')}")
                print()
        else:
            print("❌ Categoría 'Configuración' NO encontrada en el menú")
        
        # Verificar si hay algo raro en la estructura del menú
        print(f"\n🔍 VERIFICACIÓN DE INTEGRIDAD DEL MENÚ:")
        for cat in menu:
            # Verificar que las claves esenciales existan
            required_keys = ['category', 'pages']
            missing_keys = [key for key in required_keys if key not in cat]
            if missing_keys:
                print(f"⚠️ Categoría '{cat.get('category', 'SIN NOMBRE')}' falta: {missing_keys}")
            
            # Verificar páginas
            pages = cat.get('pages', [])
            for i, page in enumerate(pages):
                required_page_keys = ['name', 'url']
                missing_page_keys = [key for key in required_page_keys if key not in page or not page[key]]
                if missing_page_keys:
                    print(f"⚠️ Página {i+1} en '{cat['category']}' falta: {missing_page_keys}")
                    print(f"     Página completa: {page}")

if __name__ == '__main__':
    probar_menu_administrador_detallado()