#!/usr/bin/env python3
"""
Script para agregar la columna id_grupo a la tabla requerimiento
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
import logging

def add_grupo_column():
    """Agregar columna id_grupo a la tabla requerimiento"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la columna ya existe
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('requerimiento')]
            
            if 'id_grupo' in columns:
                print("✅ La columna 'id_grupo' ya existe en la tabla 'requerimiento'")
                return True
            
            print("🔄 Agregando columna 'id_grupo' a la tabla 'requerimiento'...")
            
            # Agregar la columna usando SQL directo con la sintaxis correcta
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE requerimiento 
                    ADD COLUMN id_grupo INT NULL
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE requerimiento 
                    ADD CONSTRAINT fk_requerimiento_grupo 
                    FOREIGN KEY (id_grupo) REFERENCES grupo(id) ON DELETE RESTRICT
                """))
                
                conn.commit()
            
            print("✅ Columna 'id_grupo' agregada exitosamente")
            
            # Verificar que la columna se agregó correctamente
            inspector = db.inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('requerimiento')]
            
            if 'id_grupo' in columns:
                print("✅ Verificación exitosa: La columna 'id_grupo' está presente")
                return True
            else:
                print("❌ Error: La columna 'id_grupo' no se agregó correctamente")
                return False
                
        except Exception as e:
            print(f"❌ Error al agregar columna: {str(e)}")
            return False

if __name__ == "__main__":
    if add_grupo_column():
        print("🎉 Migración completada exitosamente")
    else:
        print("💥 Migración fallida")
        sys.exit(1)
