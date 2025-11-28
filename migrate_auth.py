"""
Script para migrar el modelo Trabajador a la nueva estructura con autenticación
Agrega nuevas columnas necesarias para el sistema de autenticación
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging
from config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_trabajador_table():
    """Migrar la tabla trabajador para añadir campos de autenticación"""
    
    # Crear instancia de Flask y SQLAlchemy
    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy(app)
    
    with app.app_context():
        try:
            # Verificar si ya existe la estructura nueva
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'trabajador' 
                AND COLUMN_NAME IN ('password_hash', 'rol', 'ultimo_acceso', 'intentos_fallidos', 'bloqueado_hasta')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Migrar columna password a password_hash
            if 'password_hash' not in existing_columns:
                logger.info("Añadiendo columna password_hash...")
                db.session.execute(text("""
                    ALTER TABLE trabajador 
                    ADD COLUMN password_hash VARCHAR(255) NULL
                """))
                
                # Copiar datos de password existente a password_hash (si existe)
                try:
                    db.session.execute(text("""
                        UPDATE trabajador 
                        SET password_hash = password 
                        WHERE password IS NOT NULL
                    """))
                    logger.info("Datos de contraseña copiados a password_hash")
                except Exception as e:
                    logger.warning(f"No se pudieron copiar las contraseñas existentes: {e}")
                
                logger.info("Columna password_hash añadida")
            else:
                logger.info("Columna password_hash ya existe")
            
            # Añadir campo rol (enum)
            if 'rol' not in existing_columns:
                logger.info("Añadiendo columna rol...")
                db.session.execute(text("""
                    ALTER TABLE trabajador 
                    ADD COLUMN rol ENUM('superadmin', 'admin', 'supervisor', 'usuario') 
                    DEFAULT 'usuario' NOT NULL
                """))
                logger.info("Columna rol añadida")
            else:
                logger.info("Columna rol ya existe")
            
            # Añadir campo ultimo_acceso
            if 'ultimo_acceso' not in existing_columns:
                logger.info("Añadiendo columna ultimo_acceso...")
                db.session.execute(text("""
                    ALTER TABLE trabajador 
                    ADD COLUMN ultimo_acceso DATETIME NULL
                """))
                logger.info("Columna ultimo_acceso añadida")
            else:
                logger.info("Columna ultimo_acceso ya existe")
            
            # Añadir campo intentos_fallidos
            if 'intentos_fallidos' not in existing_columns:
                logger.info("Añadiendo columna intentos_fallidos...")
                db.session.execute(text("""
                    ALTER TABLE trabajador 
                    ADD COLUMN intentos_fallidos INT DEFAULT 0 NOT NULL
                """))
                logger.info("Columna intentos_fallidos añadida")
            else:
                logger.info("Columna intentos_fallidos ya existe")
            
            # Añadir campo bloqueado_hasta
            if 'bloqueado_hasta' not in existing_columns:
                logger.info("Añadiendo columna bloqueado_hasta...")
                db.session.execute(text("""
                    ALTER TABLE trabajador 
                    ADD COLUMN bloqueado_hasta DATETIME NULL
                """))
                logger.info("Columna bloqueado_hasta añadida")
            else:
                logger.info("Columna bloqueado_hasta ya existe")
            
            # Migrar datos de es_admin existentes a rol (si es_admin existe)
            try:
                result = db.session.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'trabajador' 
                    AND COLUMN_NAME = 'es_admin'
                """))
                
                if result.fetchone():
                    logger.info("Migrando datos de es_admin a rol...")
                    db.session.execute(text("""
                        UPDATE trabajador 
                        SET rol = CASE 
                            WHEN es_admin = TRUE THEN 'admin'
                            ELSE 'usuario'
                        END
                        WHERE rol = 'usuario' OR rol IS NULL
                    """))
                    logger.info("Datos migrados de es_admin a rol")
            except Exception as e:
                logger.warning(f"No se pudo migrar datos de es_admin: {e}")
            
            # Verificar si ya existe constraint único para email
            result = db.session.execute(text("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'trabajador' 
                AND CONSTRAINT_TYPE = 'UNIQUE'
                AND CONSTRAINT_NAME = 'uq_trabajador_email'
            """))
            
            if not result.fetchone():
                try:
                    logger.info("Añadiendo constraint único para email...")
                    db.session.execute(text("""
                        ALTER TABLE trabajador 
                        ADD CONSTRAINT uq_trabajador_email UNIQUE (email)
                    """))
                    logger.info("Constraint único para email añadido")
                except Exception as e:
                    logger.warning(f"No se pudo añadir constraint único para email: {e}")
            else:
                logger.info("Constraint único para email ya existe")
            
            # Verificar índices
            try:
                logger.info("Creando índices adicionales...")
                
                # Verificar si el índice ya existe
                result = db.session.execute(text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.STATISTICS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'trabajador'
                    AND INDEX_NAME = 'idx_trabajador_email'
                """)).fetchone()
                
                if result.count == 0:
                    # Crear índice para email
                    db.session.execute(text("""
                        CREATE INDEX idx_trabajador_email ON trabajador(email)
                    """))
                    logger.info("Índice idx_trabajador_email creado")
                else:
                    logger.info("Índice idx_trabajador_email ya existe")
                
                # Confirmar cambios
                db.session.commit()
                logger.info("Migración completada exitosamente")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error creando índices: {e}")
                raise
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error durante la migración: {e}")
            raise

def create_admin_user():
    """Crear usuario administrador inicial"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy(app)
    
    with app.app_context():
        try:
            from app.models import Trabajador
            
            # Verificar si ya existe un admin
            admin = db.session.execute(text("""
                SELECT * FROM trabajador WHERE rol = 'superadmin' LIMIT 1
            """)).fetchone()
            
            if not admin:
                # Buscar admin existente por es_admin o email
                admin = db.session.execute(text("""
                    SELECT * FROM trabajador 
                    WHERE email = 'admin@sistema.com' 
                    OR (es_admin = TRUE AND rol != 'superadmin')
                    LIMIT 1
                """)).fetchone()
                
                if admin:
                    # Actualizar trabajador existente como superadmin
                    db.session.execute(text("""
                        UPDATE trabajador 
                        SET rol = 'superadmin', activo = TRUE
                        WHERE id = :id
                    """), {'id': admin.id})
                    
                    # Actualizar contraseña si no la tiene
                    from app.models import Trabajador
                    trabajador = Trabajador.query.get(admin.id)
                    if not trabajador.password_hash:
                        trabajador.password = 'admin123'
                        
                    db.session.commit()
                    logger.info(f"Usuario {admin.nombre} actualizado como Super Administrador")
                else:
                    # Crear nuevo super admin
                    db.session.execute(text("""
                        INSERT INTO trabajador (nombre, email, profesion, rol, activo, password_hash, created_at, updated_at)
                        VALUES ('Super Administrador', 'admin@sistema.com', 'Super Administrador del Sistema', 
                                'superadmin', TRUE, NULL, NOW(), NOW())
                    """))
                    
                    # Obtener el ID del usuario recién creado y establecer contraseña
                    admin_result = db.session.execute(text("""
                        SELECT id FROM trabajador WHERE email = 'admin@sistema.com'
                    """)).fetchone()
                    
                    if admin_result:
                        from app.models import Trabajador
                        admin = Trabajador.query.get(admin_result.id)
                        admin.password = 'admin123'
                        
                    db.session.commit()
                    logger.info("Super Administrador creado con:")
                    logger.info("  Email: admin@sistema.com")
                    logger.info("  Contraseña: admin123")
                    logger.warning("¡IMPORTANTE! Cambie la contraseña después del primer login")
            else:
                logger.info("Ya existe un Super Administrador en el sistema")
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando usuario administrador: {e}")
            raise

if __name__ == '__main__':
    logger.info("Iniciando migración de tabla trabajador...")
    
    try:
        # Ejecutar migración
        migrate_trabajador_table()
        logger.info("Migración de tabla completada")
        
        # Crear usuario admin
        create_admin_user()
        logger.info("Configuración de usuario administrador completada")
        
        logger.info("¡Migración completada exitosamente!")
        logger.info("Puede ahora ejecutar la aplicación con el sistema de autenticación")
        logger.info("Usuario admin: admin@sistema.com")
        logger.info("Contraseña temporal: admin123")
        
    except Exception as e:
        logger.error(f"Error durante la migración: {e}")
        logger.error("Verifique la conexión a la base de datos y vuelva a intentar")
