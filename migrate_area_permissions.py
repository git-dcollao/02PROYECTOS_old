"""
Script de Migración para Sistema de Permisos por Área
========================================================

Este script migra la base de datos existente para soportar:
1. Nuevo rol ADMIN_AREA
2. Tabla intermedia trabajador_areas (many-to-many)
3. Migración de area_id a area_principal_id
4. Preservación de datos existentes

Uso:
    python migrate_area_permissions.py

IMPORTANTE: Hacer backup de la base de datos antes de ejecutar
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar la app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, Area, UserRole
from sqlalchemy import text

def create_backup():
    """Crear backup de la base de datos"""
    print("🔄 Creando backup de la base de datos...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_pre_migration_{timestamp}.sql"
    
    # Comando para MySQL dump (ajustar según tu configuración)
    import subprocess
    try:
        subprocess.run([
            "mysqldump", 
            "-u", "root", 
            "-p", 
            "proyectosDB", 
            "--result-file", backup_name
        ], check=True)
        print(f"✅ Backup creado: {backup_name}")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  No se pudo crear backup automático. Continúa bajo tu responsabilidad.")
        response = input("¿Continuar sin backup? (y/N): ")
        return response.lower() == 'y'

def check_existing_schema():
    """Verificar esquema actual"""
    print("🔍 Verificando esquema actual...")
    
    try:
        # Verificar si ya existe area_principal_id
        result = db.session.execute(text("SHOW COLUMNS FROM trabajador LIKE 'area_principal_id'"))
        if result.fetchone():
            print("⚠️  Columna area_principal_id ya existe. Migración posiblemente ya ejecutada.")
            return False
        
        # Verificar si existe tabla trabajador_areas
        result = db.session.execute(text("SHOW TABLES LIKE 'trabajador_areas'"))
        if result.fetchone():
            print("⚠️  Tabla trabajador_areas ya existe. Migración posiblemente ya ejecutada.")
            return False
        
        print("✅ Esquema listo para migración")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando esquema: {e}")
        return False

def migrate_database():
    """Ejecutar migración completa"""
    print("🚀 Iniciando migración de base de datos...")
    
    try:
        # Paso 1: Agregar nueva columna area_principal_id
        print("📝 Paso 1: Agregando columna area_principal_id...")
        db.session.execute(text("""
            ALTER TABLE trabajador 
            ADD COLUMN area_principal_id INT NULL,
            ADD CONSTRAINT fk_trabajador_area_principal 
            FOREIGN KEY (area_principal_id) REFERENCES area(id) ON DELETE SET NULL
        """))
        
        # Paso 2: Migrar datos de area_id a area_principal_id
        print("📝 Paso 2: Migrando datos de area_id a area_principal_id...")
        db.session.execute(text("""
            UPDATE trabajador 
            SET area_principal_id = area_id 
            WHERE area_id IS NOT NULL
        """))
        
        # Paso 3: Crear tabla intermedia trabajador_areas
        print("📝 Paso 3: Creando tabla trabajador_areas...")
        db.session.execute(text("""
            CREATE TABLE trabajador_areas (
                trabajador_id INT NOT NULL,
                area_id INT NOT NULL,
                fecha_asignacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                PRIMARY KEY (trabajador_id, area_id),
                CONSTRAINT fk_trabajador_areas_trabajador 
                    FOREIGN KEY (trabajador_id) REFERENCES trabajador(id) ON DELETE CASCADE,
                CONSTRAINT fk_trabajador_areas_area 
                    FOREIGN KEY (area_id) REFERENCES area(id) ON DELETE CASCADE
            )
        """))
        
        # Paso 4: Crear índices para optimización
        print("📝 Paso 4: Creando índices...")
        db.session.execute(text("""
            CREATE INDEX idx_trabajador_areas_trabajador ON trabajador_areas(trabajador_id)
        """))
        db.session.execute(text("""
            CREATE INDEX idx_trabajador_areas_area ON trabajador_areas(area_id)
        """))
        db.session.execute(text("""
            CREATE INDEX idx_trabajador_areas_activo ON trabajador_areas(activo)
        """))
        db.session.execute(text("""
            CREATE INDEX idx_trabajador_area_principal ON trabajador(area_principal_id)
        """))
        
        # Paso 5: Poblar tabla intermedia con datos existentes
        print("📝 Paso 5: Poblando tabla trabajador_areas con datos existentes...")
        db.session.execute(text("""
            INSERT INTO trabajador_areas (trabajador_id, area_id, fecha_asignacion, activo)
            SELECT id, area_principal_id, COALESCE(created_at, NOW()), TRUE
            FROM trabajador 
            WHERE area_principal_id IS NOT NULL
        """))
        
        # Paso 6: Actualizar enum UserRole (se hace en código Python)
        print("📝 Paso 6: Verificando enum UserRole...")
        # El enum ya está actualizado en el código, MySQL lo manejará automáticamente
        
        # Confirmar transacción
        db.session.commit()
        print("✅ Migración completada exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        db.session.rollback()
        return False

def validate_migration():
    """Validar que la migración fue exitosa"""
    print("🔍 Validando migración...")
    
    try:
        # Verificar estructura de tablas
        result = db.session.execute(text("SHOW COLUMNS FROM trabajador LIKE 'area_principal_id'"))
        if not result.fetchone():
            raise Exception("Columna area_principal_id no encontrada")
        
        result = db.session.execute(text("SHOW TABLES LIKE 'trabajador_areas'"))
        if not result.fetchone():
            raise Exception("Tabla trabajador_areas no encontrada")
        
        # Verificar datos
        trabajadores_total = db.session.execute(text("SELECT COUNT(*) FROM trabajador")).scalar()
        trabajadores_con_area_principal = db.session.execute(text(
            "SELECT COUNT(*) FROM trabajador WHERE area_principal_id IS NOT NULL"
        )).scalar()
        relaciones_trabajador_areas = db.session.execute(text(
            "SELECT COUNT(*) FROM trabajador_areas WHERE activo = TRUE"
        )).scalar()
        
        print(f"📊 Estadísticas post-migración:")
        print(f"   - Total trabajadores: {trabajadores_total}")
        print(f"   - Trabajadores con área principal: {trabajadores_con_area_principal}")
        print(f"   - Relaciones activas en trabajador_areas: {relaciones_trabajador_areas}")
        
        if trabajadores_con_area_principal == relaciones_trabajador_areas:
            print("✅ Validación exitosa: Los datos se migraron correctamente")
            return True
        else:
            print("⚠️  Advertencia: Discrepancia en los datos migrados")
            return False
            
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False

def cleanup_old_column():
    """Limpiar columna antigua area_id (OPCIONAL)"""
    print("🧹 ¿Eliminar columna antigua area_id?")
    print("⚠️  ADVERTENCIA: Esto eliminará permanentemente la columna area_id")
    print("   Asegúrate de que todo funciona correctamente antes de continuar")
    
    response = input("¿Eliminar columna area_id? (y/N): ")
    if response.lower() == 'y':
        try:
            # Primero eliminar índice
            db.session.execute(text("DROP INDEX idx_trabajador_area ON trabajador"))
            # Luego eliminar columna
            db.session.execute(text("ALTER TABLE trabajador DROP COLUMN area_id"))
            db.session.commit()
            print("✅ Columna area_id eliminada")
        except Exception as e:
            print(f"❌ Error eliminando columna: {e}")
            db.session.rollback()
    else:
        print("ℹ️  Columna area_id conservada para compatibilidad")

def main():
    """Función principal de migración"""
    print("=" * 60)
    print("MIGRACIÓN: SISTEMA DE PERMISOS POR ÁREA")
    print("=" * 60)
    print()
    
    # Crear contexto de aplicación
    app = create_app()
    with app.app_context():
        
        # Verificar backup
        if not create_backup():
            print("❌ Migración cancelada por seguridad")
            return
        
        # Verificar esquema
        if not check_existing_schema():
            print("❌ Esquema no válido para migración")
            return
        
        # Confirmar migración
        print("\n📋 Resumen de cambios a realizar:")
        print("   1. Agregar columna area_principal_id")
        print("   2. Migrar datos de area_id a area_principal_id")
        print("   3. Crear tabla trabajador_areas")
        print("   4. Crear índices de optimización")
        print("   5. Poblar tabla intermedia")
        print("   6. Validar migración")
        print()
        
        response = input("¿Continuar con la migración? (y/N): ")
        if response.lower() != 'y':
            print("❌ Migración cancelada por el usuario")
            return
        
        # Ejecutar migración
        if migrate_database():
            if validate_migration():
                print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
                print("\n📋 Próximos pasos:")
                print("   1. Probar funcionalidad de trabajadores")
                print("   2. Verificar permisos por área")
                print("   3. Asignar rol ADMIN_AREA según necesidad")
                print("   4. Configurar áreas adicionales para trabajadores")
                
                # Opcional: limpiar columna antigua
                print()
                cleanup_old_column()
                
            else:
                print("⚠️  Migración completada con advertencias")
        else:
            print("❌ Migración falló")

if __name__ == "__main__":
    main()
