"""
Script para agregar la columna id_area a la tabla requerimiento
"""
from app import create_app
from app.models import db, Requerimiento, Area
from sqlalchemy import text

def migrate_add_area_to_requerimiento():
    app = create_app()
    with app.app_context():
        try:
            print("🔄 Iniciando migración: Agregar columna id_area a requerimiento...")
            
            # Verificar si la columna ya existe
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'requerimiento' 
                AND COLUMN_NAME = 'id_area'
                AND TABLE_SCHEMA = DATABASE()
            """)).fetchone()
            
            if result[0] > 0:
                print("✅ La columna id_area ya existe en la tabla requerimiento")
                return
            
            # Agregar la columna
            print("📝 Agregando columna id_area...")
            db.session.execute(text("""
                ALTER TABLE requerimiento 
                ADD COLUMN id_area INT NULL,
                ADD CONSTRAINT fk_requerimiento_area 
                FOREIGN KEY (id_area) REFERENCES area(id) ON DELETE RESTRICT
            """))
            
            print("📊 Asignando áreas por defecto a requerimientos existentes...")
            
            # Obtener ID del área SECOPLAC para asignar por defecto
            area_secoplac = Area.query.filter_by(nombre='SECOPLAC').first()
            if area_secoplac:
                # Asignar SECOPLAC a todos los requerimientos existentes sin área
                db.session.execute(text("""
                    UPDATE requerimiento 
                    SET id_area = :area_id 
                    WHERE id_area IS NULL
                """), {'area_id': area_secoplac.id})
                
                print(f"✅ Asignada área SECOPLAC a requerimientos existentes")
            else:
                print("⚠️ Área SECOPLAC no encontrada, requerimientos quedarán sin área")
            
            db.session.commit()
            print("✅ Migración completada exitosamente")
            
            # Verificar resultado
            total_reqs = Requerimiento.query.count()
            reqs_con_area = Requerimiento.query.filter(Requerimiento.id_area.isnot(None)).count()
            print(f"📊 Resultado: {reqs_con_area}/{total_reqs} requerimientos con área asignada")
            
        except Exception as e:
            print(f"❌ Error en migración: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    migrate_add_area_to_requerimiento()
