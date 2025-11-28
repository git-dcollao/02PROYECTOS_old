#!/usr/bin/env python3
"""
Script para crear la tabla historial_control en la base de datos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import HistorialControl

def create_historial_control_table():
    """Crea la tabla historial_control en la base de datos"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Iniciando creación de tabla historial_control...")
            
            # Crear la tabla
            db.create_all()
            
            print("✅ Tabla historial_control creada exitosamente")
            
            # Verificar que la tabla se creó
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'historial_control' in tables:
                print("🔍 Tabla historial_control confirmada en la base de datos")
                
                # Obtener columnas de la tabla
                columns = inspector.get_columns('historial_control')
                print(f"📋 Columnas encontradas ({len(columns)}):")
                for column in columns:
                    print(f"   - {column['name']}: {column['type']}")
                    
            else:
                print("❌ Error: La tabla historial_control no fue encontrada")
                
        except Exception as e:
            print(f"❌ Error al crear la tabla: {str(e)}")
            return False
            
    return True

if __name__ == '__main__':
    if create_historial_control_table():
        print("🎉 Proceso completado exitosamente")
    else:
        print("💥 Proceso falló")
        sys.exit(1)
