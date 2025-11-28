#!/usr/bin/env python3
"""
Script para crear la tabla actividad_proyecto en la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def create_actividad_proyecto_table():
    """Crear la tabla actividad_proyecto"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar si la tabla ya existe
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'actividad_proyecto'
            """))
            
            table_exists = result.fetchone()[0] > 0
            
            if table_exists:
                print("✅ La tabla actividad_proyecto ya existe")
                return True
            
            # Crear la tabla
            create_sql = """
            CREATE TABLE actividad_proyecto (
                id INT AUTO_INCREMENT PRIMARY KEY,
                requerimiento_id INT NOT NULL,
                edt VARCHAR(50) NOT NULL,
                nombre_tarea VARCHAR(500) NOT NULL,
                nivel_esquema INT NOT NULL DEFAULT 1,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                duracion INT NOT NULL,
                dias_corridos INT NULL,
                predecesoras TEXT NULL,
                recursos TEXT NULL,
                progreso DECIMAL(5,2) NOT NULL DEFAULT 0.00,
                datos_adicionales JSON NULL,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (requerimiento_id) REFERENCES requerimiento(id) ON DELETE CASCADE,
                UNIQUE KEY uq_actividad_proyecto_edt (requerimiento_id, edt),
                INDEX idx_actividad_proyecto_requerimiento (requerimiento_id),
                INDEX idx_actividad_proyecto_fecha_inicio (fecha_inicio),
                INDEX idx_actividad_proyecto_fecha_fin (fecha_fin)
            )
            """
            
            print("🔧 Creando tabla actividad_proyecto...")
            db.session.execute(text(create_sql))
            db.session.commit()
            
            print("✅ Tabla actividad_proyecto creada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al crear la tabla: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_actividad_proyecto_table()
    if success:
        print("🎉 Migración completada exitosamente")
    else:
        print("💥 Migración falló")
        sys.exit(1)
