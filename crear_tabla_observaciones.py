#!/usr/bin/env python3
"""
Script para crear la tabla de observaciones de requerimientos
"""

from app import create_app
from app.models import db, ObservacionRequerimiento
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crear_tabla_observaciones():
    """Crear la tabla de observaciones de requerimientos"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🔧 Iniciando creación de tabla observacion_requerimiento...")
            
            # Verificar si la tabla ya existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'observacion_requerimiento' in inspector.get_table_names():
                logger.warning("⚠️  La tabla 'observacion_requerimiento' ya existe")
                return True
            
            # Crear la tabla
            logger.info("📋 Creando tabla observacion_requerimiento...")
            db.create_all()
            
            # Verificar que se creó correctamente
            if 'observacion_requerimiento' in inspector.get_table_names():
                logger.info("✅ Tabla 'observacion_requerimiento' creada exitosamente")
                
                # Mostrar estructura de la tabla
                columns = inspector.get_columns('observacion_requerimiento')
                logger.info("📊 Estructura de la tabla:")
                for column in columns:
                    logger.info(f"   - {column['name']}: {column['type']}")
                
                return True
            else:
                logger.error("❌ Error: La tabla no se creó correctamente")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al crear la tabla: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    logger.info("🚀 Ejecutando script de migración...")
    success = crear_tabla_observaciones()
    
    if success:
        logger.info("🎉 Migración completada exitosamente")
        print("\n" + "="*50)
        print("✅ MIGRACIÓN COMPLETADA")
        print("="*50)
        print("La tabla 'observacion_requerimiento' está lista para usar.")
        print("Ahora las observaciones se guardarán como historial.")
        print("="*50)
    else:
        logger.error("💥 La migración falló")
        print("\n" + "="*50)
        print("❌ MIGRACIÓN FALLIDA")  
        print("="*50)
        print("Revise los logs para más detalles.")
        print("="*50)