#!/usr/bin/env python3
"""
Script para agregar campos de organización de menú a las tablas existentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from sqlalchemy import text

def add_menu_organization_fields():
    """Agregar campos para organización avanzada del menú"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Agregando campos de organización de menú...")
            
            # Agregar campos a la tabla categories
            category_fields = [
                "ALTER TABLE categories ADD COLUMN display_order INTEGER DEFAULT 0;",
                "ALTER TABLE categories ADD COLUMN icon VARCHAR(100) DEFAULT 'fas fa-folder';",
                "ALTER TABLE categories ADD COLUMN is_visible BOOLEAN DEFAULT TRUE;",
                "ALTER TABLE categories ADD COLUMN parent_id INTEGER REFERENCES categories(id);",
                "CREATE INDEX IF NOT EXISTS idx_categories_display_order ON categories(display_order);",
                "CREATE INDEX IF NOT EXISTS idx_categories_visible ON categories(is_visible);",
                "CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);"
            ]
            
            # Agregar campos a la tabla pages
            page_fields = [
                "ALTER TABLE pages ADD COLUMN display_order INTEGER DEFAULT 0;",
                "ALTER TABLE pages ADD COLUMN icon VARCHAR(100) DEFAULT 'fas fa-file';",
                "ALTER TABLE pages ADD COLUMN is_visible BOOLEAN DEFAULT TRUE;",
                "ALTER TABLE pages ADD COLUMN parent_page_id INTEGER REFERENCES pages(id);",
                "ALTER TABLE pages ADD COLUMN menu_group VARCHAR(100);",
                "ALTER TABLE pages ADD COLUMN external_url VARCHAR(500);",
                "ALTER TABLE pages ADD COLUMN target_blank BOOLEAN DEFAULT FALSE;",
                "CREATE INDEX IF NOT EXISTS idx_pages_display_order ON pages(display_order);",
                "CREATE INDEX IF NOT EXISTS idx_pages_visible ON pages(is_visible);",
                "CREATE INDEX IF NOT EXISTS idx_pages_parent ON pages(parent_page_id);",
                "CREATE INDEX IF NOT EXISTS idx_pages_menu_group ON pages(menu_group);"
            ]
            
            # Ejecutar alteraciones para categories
            for sql in category_fields:
                try:
                    db.session.execute(text(sql))
                    print(f"✅ Ejecutado: {sql[:50]}...")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print(f"⚠️  Campo ya existe: {sql[:50]}...")
                    else:
                        print(f"❌ Error: {sql[:50]}... -> {e}")
            
            # Ejecutar alteraciones para pages
            for sql in page_fields:
                try:
                    db.session.execute(text(sql))
                    print(f"✅ Ejecutado: {sql[:50]}...")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print(f"⚠️  Campo ya existe: {sql[:50]}...")
                    else:
                        print(f"❌ Error: {sql[:50]}... -> {e}")
            
            # Crear tabla para configuración de menú global
            menu_config_table = """
            CREATE TABLE IF NOT EXISTS menu_configuration (
                id INTEGER PRIMARY KEY,
                sidebar_collapsed BOOLEAN DEFAULT FALSE,
                theme VARCHAR(50) DEFAULT 'light',
                menu_style VARCHAR(50) DEFAULT 'vertical',
                show_icons BOOLEAN DEFAULT TRUE,
                show_badges BOOLEAN DEFAULT TRUE,
                auto_close_categories BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            db.session.execute(text(menu_config_table))
            print("✅ Tabla menu_configuration creada")
            
            # Insertar configuración por defecto
            default_config = """
            INSERT OR IGNORE INTO menu_configuration (id, sidebar_collapsed, theme, menu_style, show_icons, show_badges)
            VALUES (1, FALSE, 'light', 'vertical', TRUE, TRUE);
            """
            
            db.session.execute(text(default_config))
            print("✅ Configuración por defecto insertada")
            
            # Actualizar orden de categorías existentes
            update_category_order = """
            UPDATE categories SET 
                display_order = CASE name
                    WHEN 'Sistema' THEN 1
                    WHEN 'Dashboard' THEN 2
                    WHEN 'Proyectos' THEN 3
                    WHEN 'Usuarios' THEN 4
                    WHEN 'Administración' THEN 5
                    WHEN 'Permisos' THEN 6
                    WHEN 'Reportes' THEN 7
                    WHEN 'Configuración' THEN 8
                    ELSE 99
                END,
                icon = CASE name
                    WHEN 'Sistema' THEN 'fas fa-server'
                    WHEN 'Dashboard' THEN 'fas fa-tachometer-alt'
                    WHEN 'Proyectos' THEN 'fas fa-project-diagram'
                    WHEN 'Usuarios' THEN 'fas fa-users'
                    WHEN 'Administración' THEN 'fas fa-cogs'
                    WHEN 'Permisos' THEN 'fas fa-shield-alt'
                    WHEN 'Reportes' THEN 'fas fa-chart-line'
                    WHEN 'Configuración' THEN 'fas fa-wrench'
                    ELSE 'fas fa-folder'
                END
            WHERE display_order = 0;
            """
            
            db.session.execute(text(update_category_order))
            print("✅ Orden de categorías actualizado")
            
            # Actualizar iconos de páginas comunes
            update_page_icons = """
            UPDATE pages SET 
                icon = CASE 
                    WHEN route LIKE '%dashboard%' THEN 'fas fa-home'
                    WHEN route LIKE '%users%' OR route LIKE '%trabajadores%' THEN 'fas fa-user-friends'
                    WHEN route LIKE '%permissions%' THEN 'fas fa-key'
                    WHEN route LIKE '%projects%' OR route LIKE '%proyectos%' THEN 'fas fa-tasks'
                    WHEN route LIKE '%reports%' THEN 'fas fa-file-alt'
                    WHEN route LIKE '%settings%' OR route LIKE '%config%' THEN 'fas fa-cog'
                    WHEN route LIKE '%especialidades%' THEN 'fas fa-user-tag'
                    WHEN route LIKE '%estados%' THEN 'fas fa-flag'
                    WHEN route LIKE '%equipos%' THEN 'fas fa-users-cog'
                    WHEN route LIKE '%fases%' THEN 'fas fa-step-forward'
                    WHEN route LIKE '%financiamientos%' THEN 'fas fa-dollar-sign'
                    WHEN route LIKE '%prioridades%' THEN 'fas fa-sort-amount-up'
                    WHEN route LIKE '%tipologias%' THEN 'fas fa-tags'
                    WHEN route LIKE '%tipoproyectos%' THEN 'fas fa-project-diagram'
                    WHEN route LIKE '%areas%' THEN 'fas fa-map'
                    WHEN route LIKE '%sectores%' THEN 'fas fa-sitemap'
                    WHEN route LIKE '%recintos%' THEN 'fas fa-building'
                    WHEN route LIKE '%etapas%' THEN 'fas fa-list-ol'
                    ELSE 'fas fa-file'
                END,
                display_order = CASE 
                    WHEN route = '/' OR route LIKE '%dashboard%' THEN 1
                    WHEN route LIKE '%list%' OR route LIKE '%index%' THEN 2
                    WHEN route LIKE '%create%' OR route LIKE '%new%' THEN 3
                    WHEN route LIKE '%edit%' THEN 4
                    WHEN route LIKE '%delete%' THEN 5
                    ELSE 99
                END
            WHERE icon = 'fas fa-file' AND display_order = 0;
            """
            
            db.session.execute(text(update_page_icons))
            print("✅ Iconos y orden de páginas actualizados")
            
            db.session.commit()
            print("🎉 Campos de organización de menú agregados exitosamente!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error agregando campos de organización: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = add_menu_organization_fields()
    if success:
        print("\n✅ Migración completada. Ahora puedes usar la funcionalidad de organización de menú.")
    else:
        print("\n❌ Error en la migración. Revisa los logs arriba.")
