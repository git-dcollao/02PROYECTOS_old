#!/usr/bin/env python3
"""
Script para diagnosticar el problema del menú "Configuración"
mostrando "ID Nombre" en lugar del contenido correcto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, Category, Page, PagePermission
from app.services.menu_service import MenuService

def diagnosticar_menu_configuracion():
    app = create_app()
    
    with app.app_context():
        print("=== DIAGNÓSTICO MENÚ CONFIGURACIÓN ===")
        
        # 1. Verificar usuarios de prueba
        admin = Trabajador.query.filter_by(email='admin@sistema.local').first()
        administrador = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        
        print(f"👤 Usuarios encontrados:")
        if admin:
            print(f"   SUPERADMIN: {admin.email}")
        if administrador:
            print(f"   ADMINISTRADOR: {administrador.email}")
        
        # 2. Verificar categoría "Configuración"
        print(f"\n📁 CATEGORÍAS EN LA BASE DE DATOS:")
        categorias = Category.query.order_by(Category.display_order.asc()).all()
        for cat in categorias:
            print(f"   ID {cat.id}: {cat.name} (orden: {cat.display_order}, visible: {cat.is_visible})")
            if 'configuración' in cat.name.lower() or 'config' in cat.name.lower():
                print(f"      🔍 CATEGORÍA CONFIGURACIÓN ENCONTRADA")
                print(f"         Icono: {cat.icon}")
                print(f"         Color: {cat.color}")
                print(f"         Parent ID: {cat.parent_id}")
        
        # 3. Verificar páginas de configuración
        print(f"\n📄 PÁGINAS DE CONFIGURACIÓN:")
        config_categories = Category.query.filter(
            Category.name.ilike('%configuración%') | 
            Category.name.ilike('%config%') |
            Category.name.ilike('%administración%') |
            Category.name.ilike('%admin%')
        ).all()
        
        for cat in config_categories:
            print(f"\n   Categoría: {cat.name}")
            paginas = Page.query.filter_by(category_id=cat.id).all()
            print(f"   Páginas ({len(paginas)}):")
            for page in paginas:
                print(f"      ID {page.id}: {page.name}")
                print(f"         Ruta: {page.route}")
                print(f"         Activa: {page.active}")
                print(f"         Visible: {page.is_visible}")
                print(f"         Descripción: {page.description}")
        
        # 4. Verificar permisos para estas páginas
        print(f"\n🔐 PERMISOS PARA PÁGINAS DE CONFIGURACIÓN:")
        for cat in config_categories:
            paginas = Page.query.filter_by(category_id=cat.id).all()
            for page in paginas:
                permisos = PagePermission.query.filter_by(page_id=page.id).all()
                print(f"\n   Página {page.name} (ID: {page.id}):")
                print(f"      Permisos ({len(permisos)}):")
                for perm in permisos:
                    print(f"         Role: {perm.role_name or 'N/A'}")
                    print(f"         Custom Role ID: {perm.custom_role_id or 'N/A'}")
        
        # 5. Probar servicio de menú con usuarios específicos
        print(f"\n🔧 PRUEBA SERVICIO DE MENÚ:")
        menu_service = MenuService()
        
        for usuario in [admin, administrador]:
            if not usuario:
                continue
                
            print(f"\n   Usuario: {usuario.email}")
            menu = menu_service.get_user_menu(usuario)
            print(f"   Categorías en menú: {len(menu)}")
            
            for categoria in menu:
                print(f"      📁 {categoria['category']} ({categoria['count']} páginas)")
                if 'configuración' in categoria['category'].lower() or 'config' in categoria['category'].lower():
                    print(f"         🔍 CATEGORIA DE CONFIGURACIÓN:")
                    print(f"            Icono: {categoria.get('icon', 'N/A')}")
                    print(f"            Color: {categoria.get('color', 'N/A')}")
                    print(f"            Páginas:")
                    for page in categoria.get('pages', []):
                        print(f"               - {page.get('name', 'SIN NOMBRE')}: {page.get('url', 'SIN URL')}")
        
        # 6. Verificar datos problemáticos que podrían mostrar "ID Nombre"
        print(f"\n🚨 BUSCAR DATOS PROBLEMÁTICOS:")
        
        # Buscar páginas sin nombre
        paginas_sin_nombre = Page.query.filter(
            (Page.name == None) | 
            (Page.name == '') | 
            (Page.name == 'ID Nombre') |
            (Page.name.like('%ID%Nombre%'))
        ).all()
        
        print(f"   Páginas con nombres problemáticos: {len(paginas_sin_nombre)}")
        for page in paginas_sin_nombre:
            print(f"      ID {page.id}: '{page.name}' - Ruta: {page.route}")
        
        # Buscar categorías sin nombre
        categorias_sin_nombre = Category.query.filter(
            (Category.name == None) | 
            (Category.name == '') | 
            (Category.name == 'ID Nombre') |
            (Category.name.like('%ID%Nombre%'))
        ).all()
        
        print(f"   Categorías con nombres problemáticos: {len(categorias_sin_nombre)}")
        for cat in categorias_sin_nombre:
            print(f"      ID {cat.id}: '{cat.name}'")

        print(f"\n✅ DIAGNÓSTICO COMPLETADO")

if __name__ == '__main__':
    diagnosticar_menu_configuracion()