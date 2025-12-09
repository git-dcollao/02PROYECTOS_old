"""
Script para agregar columnas de validación a las tablas
Ejecutar: docker-compose exec proyectos_app python agregar_columnas_validacion.py
"""

from app import create_app, db
from sqlalchemy import text

def agregar_columnas():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*80)
        print("🔧 AGREGANDO COLUMNAS DE VALIDACIÓN")
        print("="*80 + "\n")
        
        try:
            # 1. Agregar columna a actividad_proyecto
            print("📋 Agregando porcentaje_avance_validado a actividad_proyecto...")
            try:
                db.session.execute(text("""
                    ALTER TABLE actividad_proyecto 
                    ADD COLUMN porcentaje_avance_validado DECIMAL(5,2) DEFAULT 0.00 NOT NULL 
                    COMMENT 'Porcentaje validado por supervisor' 
                    AFTER progreso
                """))
                db.session.commit()
                print("✅ Columna porcentaje_avance_validado agregada")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("⚠️  Columna porcentaje_avance_validado ya existe")
                    db.session.rollback()
                else:
                    raise
            
            # 2. Agregar columnas a historial_avance_actividad
            print("\n📋 Agregando columnas de validación a historial_avance_actividad...")
            
            columnas = [
                ("validado", "BOOLEAN DEFAULT FALSE NOT NULL COMMENT 'Si el avance ha sido validado'"),
                ("validado_por_id", "INT NULL COMMENT 'ID del supervisor que validó'"),
                ("fecha_validacion", "DATETIME NULL COMMENT 'Fecha de validación'"),
                ("comentario_validacion", "TEXT NULL COMMENT 'Comentarios del supervisor'")
            ]
            
            for nombre, definicion in columnas:
                try:
                    db.session.execute(text(f"""
                        ALTER TABLE historial_avance_actividad 
                        ADD COLUMN {nombre} {definicion}
                    """))
                    db.session.commit()
                    print(f"✅ Columna {nombre} agregada")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print(f"⚠️  Columna {nombre} ya existe")
                        db.session.rollback()
                    else:
                        raise
            
            # 3. Agregar foreign key para validado_por_id
            print("\n📋 Agregando foreign key para validado_por_id...")
            try:
                db.session.execute(text("""
                    ALTER TABLE historial_avance_actividad 
                    ADD CONSTRAINT fk_historial_validado_por 
                    FOREIGN KEY (validado_por_id) 
                    REFERENCES trabajador(id) 
                    ON DELETE SET NULL
                """))
                db.session.commit()
                print("✅ Foreign key agregada")
            except Exception as e:
                if "Duplicate foreign key" in str(e) or "already exists" in str(e):
                    print("⚠️  Foreign key ya existe")
                    db.session.rollback()
                else:
                    raise
            
            print("\n" + "="*80)
            print("🎉 COLUMNAS AGREGADAS EXITOSAMENTE")
            print("="*80 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    agregar_columnas()
