#!/usr/bin/env python3
"""
Script para agregar la columna 'proyecto' a la tabla 'requerimiento'
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import DevelopmentConfig
from app import create_app
from app.models import db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_proyecto_column():
    """Agregar la columna 'proyecto' a la tabla requerimiento"""
    try:
        app = create_app(DevelopmentConfig)
        
        with app.app_context():
            # Ejecutar la migración SQL directamente usando text()
            from sqlalchemy import text
            
            sql_commands = [
                # Agregar la columna proyecto
                "ALTER TABLE requerimiento ADD COLUMN proyecto VARCHAR(100) NULL;",
                
                # Agregar índice para la nueva columna
                "CREATE INDEX idx_requerimiento_proyecto ON requerimiento(proyecto);",
            ]
            
            logger.info("🚀 Iniciando migración de base de datos...")
            
            for i, sql in enumerate(sql_commands, 1):
                try:
                    logger.info(f"📋 Ejecutando comando {i}/{len(sql_commands)}: {sql[:50]}...")
                    # Usar la conexión directa con text()
                    with db.engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    logger.info(f"✅ Comando {i} ejecutado exitosamente")
                except Exception as e:
                    # Si el error es que la columna ya existe, continuamos
                    if "Duplicate column name" in str(e) or "already exists" in str(e):
                        logger.info(f"⚠️  Comando {i}: La columna/índice ya existe, saltando...")
                        continue
                    else:
                        logger.error(f"❌ Error en comando {i}: {e}")
                        raise
            
            logger.info("🎉 Migración completada exitosamente")
            
            # Verificar que la columna se agregó correctamente
            with db.engine.connect() as conn:
                result = conn.execute(text("DESCRIBE requerimiento;"))
                columns = [row[0] for row in result.fetchall()]
            
            if 'proyecto' in columns:
                logger.info("✅ Verificación exitosa: La columna 'proyecto' existe en la tabla")
            else:
                logger.error("❌ Error: La columna 'proyecto' no se agregó correctamente")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Script de migración de base de datos")
    print("=" * 50)
    
    success = add_proyecto_column()
    
    if success:
        print("\n🎉 ¡Migración completada exitosamente!")
        print("✅ La columna 'proyecto' ha sido agregada a la tabla 'requerimiento'")
        print("🚀 Ahora puedes reiniciar la aplicación Flask")
    else:
        print("\n❌ La migración falló")
        print("🔍 Revisa los logs para más detalles")
        sys.exit(1)
