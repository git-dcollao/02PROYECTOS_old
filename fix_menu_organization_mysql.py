#!/usr/bin/env python3
"""
Script para corregir la migración de organización de menú con sintaxis MySQL compatible
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_menu_organization_migration():
    """Ejecuta las correcciones necesarias para MySQL"""
    
    print("🔧 Corrigiendo migración de organización de menú para MySQL...")
    
    try:
        # Lista de comandos SQL compatibles con MySQL
        sql_commands = [
            # Crear índices para categories (sin IF NOT EXISTS)
            """
            CREATE INDEX idx_categories_display_order ON categories(display_order);
            """,
            """
            CREATE INDEX idx_categories_visible ON categories(is_visible);
            """,
            """
            CREATE INDEX idx_categories_parent ON categories(parent_id);
            """,
            
            # Crear índices para pages (sin IF NOT EXISTS)
            """
            CREATE INDEX idx_pages_display_order ON pages(display_order);
            """,
            """
            CREATE INDEX idx_pages_visible ON pages(is_visible);
            """,
            """
            CREATE INDEX idx_pages_parent ON pages(parent_page_id);
            """,
            """
            CREATE INDEX idx_pages_menu_group ON pages(menu_group);
            """,
            
            # Insertar configuración predeterminada (MySQL compatible)
            """
            INSERT IGNORE INTO menu_configuration (id, sidebar_collapsed, theme, menu_style, show_icons, show_badges)
            VALUES (1, FALSE, 'light', 'vertical', TRUE, TRUE);
            """,
            
            # Actualizar orden de categorías existentes
            """
            UPDATE categories 
            SET display_order = CASE 
                WHEN name = 'Dashboard' THEN 1
                WHEN name = 'Proyectos' THEN 2
                WHEN name = 'Trabajadores' THEN 3
                WHEN name = 'Administración' THEN 4
                WHEN name = 'Reportes' THEN 5
                WHEN name = 'Sistema' THEN 6
                ELSE 99
            END
            WHERE display_order IS NULL OR display_order = 0;
            """,
            
            # Actualizar iconos de categorías
            """
            UPDATE categories 
            SET icon = CASE 
                WHEN name = 'Dashboard' THEN 'fas fa-tachometer-alt'
                WHEN name = 'Proyectos' THEN 'fas fa-project-diagram'
                WHEN name = 'Trabajadores' THEN 'fas fa-users'
                WHEN name = 'Administración' THEN 'fas fa-cogs'
                WHEN name = 'Reportes' THEN 'fas fa-chart-bar'
                WHEN name = 'Sistema' THEN 'fas fa-tools'
                ELSE 'fas fa-folder'
            END
            WHERE icon IS NULL OR icon = '';
            """,
            
            # Actualizar orden de páginas existentes
            """
            UPDATE pages p
            JOIN categories c ON p.category_id = c.id
            SET p.display_order = CASE 
                WHEN p.name = 'Dashboard' THEN 1
                WHEN p.name = 'Proyectos' THEN 1
                WHEN p.name = 'Trabajadores' THEN 1
                WHEN p.name = 'Permisos' THEN 1
                WHEN p.name = 'Categorías' THEN 2
                WHEN p.name = 'Usuarios' THEN 2
                ELSE 10
            END
            WHERE p.display_order IS NULL OR p.display_order = 0;
            """,
            
            # Actualizar iconos de páginas
            """
            UPDATE pages 
            SET icon = CASE 
                WHEN name = 'Dashboard' THEN 'fas fa-home'
                WHEN name = 'Proyectos' THEN 'fas fa-project-diagram'
                WHEN name = 'Trabajadores' THEN 'fas fa-users'
                WHEN name = 'Permisos' THEN 'fas fa-shield-alt'
                WHEN name = 'Categorías' THEN 'fas fa-tags'
                WHEN name = 'Usuarios' THEN 'fas fa-user-friends'
                ELSE 'fas fa-file'
            END
            WHERE icon IS NULL OR icon = '';
            """
        ]
        
        # Ejecutar comandos uno por uno
        for i, command in enumerate(sql_commands):
            try:
                db.session.execute(text(command.strip()))
                print(f"✅ Comando {i+1}/{len(sql_commands)} ejecutado correctamente")
            except Exception as e:
                error_msg = str(e)
                # Ignorar errores de índices duplicados
                if "Duplicate key name" in error_msg or "already exists" in error_msg:
                    print(f"⚠️  Comando {i+1}/{len(sql_commands)} - índice ya existe, continuando...")
                else:
                    print(f"❌ Error en comando {i+1}/{len(sql_commands)}: {error_msg}")
        
        # Confirmar cambios
        db.session.commit()
        print("✅ Migración corregida exitosamente")
        
        # Verificar resultados
        print("\n📊 Verificando resultados:")
        
        # Verificar categorías
        result = db.session.execute(text("SELECT name, display_order, icon, is_visible FROM categories ORDER BY display_order"))
        categories = result.fetchall()
        print(f"Categorías actualizadas: {len(categories)}")
        for cat in categories:
            print(f"  - {cat[0]}: orden={cat[1]}, icono={cat[2]}, visible={cat[3]}")
        
        # Verificar páginas
        result = db.session.execute(text("SELECT p.name, p.display_order, p.icon, p.is_visible, c.name as category FROM pages p JOIN categories c ON p.category_id = c.id ORDER BY c.display_order, p.display_order"))
        pages = result.fetchall()
        print(f"\nPáginas actualizadas: {len(pages)}")
        for page in pages:
            print(f"  - {page[0]} ({page[4]}): orden={page[1]}, icono={page[2]}, visible={page[3]}")
            
        # Verificar configuración del menú
        result = db.session.execute(text("SELECT * FROM menu_configuration WHERE id = 1"))
        config = result.fetchone()
        if config:
            print(f"\nConfiguración del menú: {config}")
        else:
            print("\n⚠️  No se encontró configuración del menú")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error general en la migración: {e}")
        return False

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        success = fix_menu_organization_migration()
        if success:
            print("\n🎉 Migración completada exitosamente")
        else:
            print("\n💥 La migración falló")
