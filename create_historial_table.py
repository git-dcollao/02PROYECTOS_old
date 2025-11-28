"""
Script para crear la tabla historial_avance_actividad
Ejecutar este script para crear la nueva tabla de historial de avances
"""

from app import create_app
from app.models import db, HistorialAvanceActividad

def crear_tabla_historial():
    """Crear la tabla de historial de avances"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Creando tabla historial_avance_actividad...")
            
            # Crear la tabla
            db.create_all()
            
            print("✅ Tabla historial_avance_actividad creada exitosamente")
            
            # Verificar que la tabla existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            
            if 'historial_avance_actividad' in tablas:
                print("✅ Tabla verificada correctamente en la base de datos")
                
                # Mostrar la estructura de la tabla
                columnas = inspector.get_columns('historial_avance_actividad')
                print("📋 Estructura de la tabla:")
                for columna in columnas:
                    print(f"  - {columna['name']}: {columna['type']}")
            else:
                print("❌ Error: La tabla no se encontró en la base de datos")
                
        except Exception as e:
            print(f"❌ Error al crear la tabla: {str(e)}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    crear_tabla_historial()
