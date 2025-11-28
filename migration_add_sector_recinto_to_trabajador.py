#!/usr/bin/env python3
"""
Migración: Agregar sector_id y recinto_id a tabla trabajador
Fecha: 2025-09-23
Descripción: Agregar campos para asociar trabajadores con sectores y recintos en lugar de áreas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db, create_app
from sqlalchemy import text

def run_migration():
    """Ejecutar migración para agregar sector_id y recinto_id a trabajador"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Iniciando migración: Agregar sector_id y recinto_id a trabajador")
            
            # Verificar si las columnas ya existen
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'trabajador' 
                AND TABLE_SCHEMA = DATABASE()
                AND COLUMN_NAME IN ('sector_id', 'recinto_id')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'sector_id' in existing_columns and 'recinto_id' in existing_columns:
                print("✅ Las columnas sector_id y recinto_id ya existen en la tabla trabajador")
                return True
            
            # Agregar sector_id si no existe
            if 'sector_id' not in existing_columns:
                print("📝 Agregando columna sector_id...")
                db.session.execute(text("""
                    ALTER TABLE trabajador 
                    ADD COLUMN sector_id INT NULL,
                    ADD CONSTRAINT fk_trabajador_sector 
                        FOREIGN KEY (sector_id) REFERENCES sector(id) ON DELETE SET NULL
                """))
                print("✅ Columna sector_id agregada correctamente")
            
            # Agregar recinto_id si no existe  
            if 'recinto_id' not in existing_columns:
                print("📝 Agregando columna recinto_id...")
                db.session.execute(text("""
                    ALTER TABLE trabajador 
                    ADD COLUMN recinto_id INT NULL,
                    ADD CONSTRAINT fk_trabajador_recinto 
                        FOREIGN KEY (recinto_id) REFERENCES recinto(id) ON DELETE SET NULL
                """))
                print("✅ Columna recinto_id agregada correctamente")
            
            # Agregar índices para optimización
            print("📝 Agregando índices...")
            try:
                db.session.execute(text("CREATE INDEX idx_trabajador_sector ON trabajador(sector_id)"))
                print("✅ Índice idx_trabajador_sector creado")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("⚠️  Índice idx_trabajador_sector ya existe")
                else:
                    raise e
            
            try:
                db.session.execute(text("CREATE INDEX idx_trabajador_recinto ON trabajador(recinto_id)"))
                print("✅ Índice idx_trabajador_recinto creado")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("⚠️  Índice idx_trabajador_recinto ya existe")
                else:
                    raise e
            
            # Confirmar cambios
            db.session.commit()
            print("✅ Migración completada exitosamente")
            
            # Mostrar estadísticas
            print("\n📊 Estadísticas después de la migración:")
            result = db.session.execute(text("SELECT COUNT(*) FROM trabajador"))
            total_trabajadores = result.scalar()
            print(f"   - Total trabajadores: {total_trabajadores}")
            
            result = db.session.execute(text("SELECT COUNT(*) FROM trabajador WHERE sector_id IS NOT NULL"))
            con_sector = result.scalar()
            print(f"   - Con sector asignado: {con_sector}")
            
            result = db.session.execute(text("SELECT COUNT(*) FROM trabajador WHERE recinto_id IS NOT NULL"))
            con_recinto = result.scalar()
            print(f"   - Con recinto asignado: {con_recinto}")
            
            print("\n💡 Próximos pasos:")
            print("   1. Actualizar controladores para usar sectores y recintos")
            print("   2. Modificar templates para mostrar nueva información")
            print("   3. Asignar sectores y recintos a trabajadores existentes")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante la migración: {e}")
            return False

def rollback_migration():
    """Revertir migración (eliminar columnas sector_id y recinto_id)"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Iniciando rollback: Eliminar sector_id y recinto_id de trabajador")
            
            # Eliminar índices
            try:
                db.session.execute(text("DROP INDEX idx_trabajador_sector ON trabajador"))
                print("✅ Índice idx_trabajador_sector eliminado")
            except Exception as e:
                print(f"⚠️  Error eliminando índice sector: {e}")
            
            try:
                db.session.execute(text("DROP INDEX idx_trabajador_recinto ON trabajador"))
                print("✅ Índice idx_trabajador_recinto eliminado")
            except Exception as e:
                print(f"⚠️  Error eliminando índice recinto: {e}")
            
            # Eliminar foreign keys y columnas
            db.session.execute(text("""
                ALTER TABLE trabajador 
                DROP FOREIGN KEY fk_trabajador_sector,
                DROP COLUMN sector_id,
                DROP FOREIGN KEY fk_trabajador_recinto,
                DROP COLUMN recinto_id
            """))
            
            db.session.commit()
            print("✅ Rollback completado exitosamente")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante rollback: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migración de base de datos para trabajadores')
    parser.add_argument('--rollback', action='store_true', 
                       help='Revertir la migración (eliminar columnas)')
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1)