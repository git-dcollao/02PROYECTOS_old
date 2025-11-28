#!/usr/bin/env python3
"""
Script para crear la tabla de áreas y modificar trabajadores
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Area, Trabajador
from sqlalchemy import text, inspect
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ejecutar_migracion():
    """Ejecuta la migración para agregar áreas"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar conexión
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("✅ Conectado a la base de datos")
            
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            logger.info(f"📋 Tablas existentes: {tablas_existentes}")
            
            # 1. Crear tabla de áreas si no existe
            if 'area' not in tablas_existentes:
                logger.info("🔨 Creando tabla de áreas...")
                
                crear_tabla_areas = text("""
                CREATE TABLE area (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    descripcion TEXT,
                    activo BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_area_nombre (nombre)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
                
                with db.engine.connect() as connection:
                    connection.execute(crear_tabla_areas)
                    connection.commit()
                logger.info("✅ Tabla 'area' creada exitosamente")
            else:
                logger.info("ℹ️ Tabla 'area' ya existe")
            
            # 2. Verificar si la columna area_id ya existe en trabajador
            columnas_trabajador = [col['name'] for col in inspector.get_columns('trabajador')]
            
            if 'area_id' not in columnas_trabajador:
                logger.info("🔨 Agregando columna area_id a tabla trabajador...")
                
                agregar_columna = text("""
                ALTER TABLE trabajador 
                ADD COLUMN area_id INT NULL,
                ADD INDEX idx_trabajador_area (area_id),
                ADD CONSTRAINT fk_trabajador_area 
                    FOREIGN KEY (area_id) REFERENCES area(id) ON DELETE SET NULL;
                """)
                
                with db.engine.connect() as connection:
                    connection.execute(agregar_columna)
                    connection.commit()
                logger.info("✅ Columna area_id agregada a trabajador")
            else:
                logger.info("ℹ️ Columna area_id ya existe en trabajador")
            
            # 3. Insertar áreas predefinidas
            logger.info("📝 Insertando áreas predefinidas...")
            
            areas_predefinidas = [
                {'nombre': 'Administración', 'descripcion': 'Personal administrativo y de gestión'},
                {'nombre': 'Ingeniería', 'descripcion': 'Profesionales de ingeniería y técnicos'},
                {'nombre': 'Operaciones', 'descripcion': 'Personal operativo y de campo'},
                {'nombre': 'Finanzas', 'descripcion': 'Área financiera y contable'},
                {'nombre': 'Recursos Humanos', 'descripcion': 'Gestión del talento humano'},
                {'nombre': 'Tecnología', 'descripcion': 'Área de sistemas y tecnología'},
                {'nombre': 'Calidad', 'descripcion': 'Control y aseguramiento de calidad'},
                {'nombre': 'Seguridad', 'descripcion': 'Seguridad ocupacional y prevención'}
            ]
            
            with db.engine.connect() as connection:
                for area_data in areas_predefinidas:
                    # Verificar si ya existe
                    area_existente = connection.execute(
                        text("SELECT id FROM area WHERE nombre = :nombre"), 
                        {'nombre': area_data['nombre']}
                    ).fetchone()
                    
                    if not area_existente:
                        insertar_area = text("""
                        INSERT INTO area (nombre, descripcion, activo, created_at, updated_at)
                        VALUES (:nombre, :descripcion, TRUE, NOW(), NOW())
                        """)
                        
                        connection.execute(insertar_area, area_data)
                        logger.info(f"✅ Área '{area_data['nombre']}' creada")
                    else:
                        logger.info(f"ℹ️ Área '{area_data['nombre']}' ya existe")
                
                connection.commit()
            
            logger.info("✅ Migración completada exitosamente")
            
            # 5. Verificar resultados
            with db.engine.connect() as connection:
                areas_count = connection.execute(text("SELECT COUNT(*) as count FROM area")).fetchone()
                logger.info(f"📊 Total de áreas en la base de datos: {areas_count.count}")
            
        except Exception as e:
            logger.error(f"❌ Error durante la migración: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando migración de áreas...")
    
    if ejecutar_migracion():
        print("✅ Migración completada exitosamente")
    else:
        print("❌ La migración falló")
        sys.exit(1)
