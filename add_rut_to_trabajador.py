#!/usr/bin/env python3
"""
Script de migración para agregar campo RUT a la tabla trabajador
Ejecutar con: python add_rut_to_trabajador.py
"""

import sys
import os

# Agregar la raíz del proyecto al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador
from sqlalchemy import text

def agregar_campo_rut():
    """Agregar campo RUT a la tabla trabajador"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Verificando estructura actual de la tabla trabajador...")
            
            # Verificar si la columna RUT ya existe
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'trabajador' 
                AND COLUMN_NAME = 'rut'
                AND TABLE_SCHEMA = DATABASE()
            """))
            
            if result.fetchone():
                print("✅ La columna 'rut' ya existe en la tabla trabajador")
                
                # Verificar si hay trabajadores sin RUT válido
                result = db.session.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM trabajador 
                    WHERE rut IS NULL OR rut = '' OR rut = '00.000.000-0'
                """))
                trabajadores_sin_rut = result.fetchone()[0]
                
                if trabajadores_sin_rut > 0:
                    print(f"🔄 Encontrados {trabajadores_sin_rut} trabajadores sin RUT válido, asignando RUTs temporales...")
                    
                    # Obtener trabajadores sin RUT válido
                    result = db.session.execute(text("""
                        SELECT id FROM trabajador 
                        WHERE rut IS NULL OR rut = '' OR rut = '00.000.000-0'
                        ORDER BY id
                    """))
                    trabajadores_ids = [row[0] for row in result.fetchall()]
                    
                    # Asignar RUTs temporales únicos
                    for i, trabajador_id in enumerate(trabajadores_ids, 1):
                        rut_temporal = f"{i:02d}.000.00{i % 10}-{i % 10}"
                        db.session.execute(text("""
                            UPDATE trabajador 
                            SET rut = :rut_temporal 
                            WHERE id = :trabajador_id
                        """), {"rut_temporal": rut_temporal, "trabajador_id": trabajador_id})
                    
                    db.session.commit()
                    print(f"✅ RUTs temporales asignados a {len(trabajadores_ids)} trabajadores")
                
                # Verificar trabajadores existentes
                trabajadores = Trabajador.query.all()
                print(f"📊 Se encontraron {len(trabajadores)} trabajadores en total")
                
                if trabajadores:
                    print("⚠️  IMPORTANTE: Los trabajadores existentes tienen RUTs temporales únicos")
                    print("   Será necesario actualizar manualmente los RUTs reales desde la interfaz web")
                    
                    print("\n📋 Trabajadores que requieren actualización de RUT:")
                    for trabajador in trabajadores:
                        print(f"   - ID {trabajador.id}: {trabajador.nombre} (RUT temporal: {trabajador.rut})")
                
                print("\n🎉 Migración completada exitosamente!")
                print("💡 Ahora puedes usar la funcionalidad de RUT en la página de trabajadores")
                return True
            
            print("📝 Agregando columna 'rut' a la tabla trabajador...")
            
            # Primero, obtener el número de trabajadores existentes
            result = db.session.execute(text("SELECT COUNT(*) as count FROM trabajador"))
            trabajadores_count = result.fetchone()[0]
            
            # Agregar la columna RUT como nullable primero
            db.session.execute(text("""
                ALTER TABLE trabajador 
                ADD COLUMN rut VARCHAR(12) NULL
            """))
            
            # Asignar RUTs únicos temporales a trabajadores existentes
            if trabajadores_count > 0:
                print(f"🔄 Asignando RUTs temporales únicos a {trabajadores_count} trabajadores existentes...")
                
                # Obtener todos los trabajadores
                result = db.session.execute(text("SELECT id FROM trabajador ORDER BY id"))
                trabajadores_ids = [row[0] for row in result.fetchall()]
                
                # Asignar RUTs temporales únicos
                for i, trabajador_id in enumerate(trabajadores_ids, 1):
                    rut_temporal = f"{i:02d}.000.00{i % 10}-{i % 10}"
                    db.session.execute(text("""
                        UPDATE trabajador 
                        SET rut = :rut_temporal 
                        WHERE id = :trabajador_id
                    """), {"rut_temporal": rut_temporal, "trabajador_id": trabajador_id})
            
            # Ahora hacer la columna NOT NULL
            db.session.execute(text("""
                ALTER TABLE trabajador 
                MODIFY COLUMN rut VARCHAR(12) NOT NULL
            """))
            
            # Agregar índice único para RUT
            db.session.execute(text("""
                CREATE UNIQUE INDEX uq_trabajador_rut ON trabajador (rut)
            """))
            
            # Agregar índice regular para búsquedas
            db.session.execute(text("""
                CREATE INDEX idx_trabajador_rut ON trabajador (rut)
            """))
            
            db.session.commit()
            print("✅ Campo RUT agregado exitosamente con índices")
            
            # Verificar trabajadores existentes
            trabajadores = Trabajador.query.all()
            print(f"📊 Se encontraron {len(trabajadores)} trabajadores existentes")
            
            if trabajadores:
                print("⚠️  IMPORTANTE: Los trabajadores existentes tienen RUTs temporales únicos")
                print("   Será necesario actualizar manualmente los RUTs reales desde la interfaz web")
                
                print("\n📋 Trabajadores que requieren actualización de RUT:")
                for trabajador in trabajadores:
                    print(f"   - ID {trabajador.id}: {trabajador.nombre} (RUT temporal: {trabajador.rut})")
            
            print("\n🎉 Migración completada exitosamente!")
            print("💡 Ahora puedes usar la funcionalidad de RUT en la página de trabajadores")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante la migración: {e}")
            return False
        
        return True

if __name__ == "__main__":
    print("🚀 Iniciando migración para agregar campo RUT...")
    success = agregar_campo_rut()
    
    if success:
        print("\n✅ Migración completada exitosamente")
        print("🔗 Puedes abrir http://localhost:5050/trabajadores para probar la funcionalidad")
    else:
        print("\n❌ La migración falló")
        sys.exit(1)
