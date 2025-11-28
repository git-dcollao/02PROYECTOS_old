"""
Script para crear usuario administrador inicial
Versión simplificada sin dependencias de Flask-Login
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging
from config import Config
from argon2 import PasswordHasher

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_simple():
    """Crear usuario administrador usando SQL directo"""
    
    # Crear instancia de Flask y SQLAlchemy
    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy(app)
    
    with app.app_context():
        try:
            # Verificar si ya existe un superadmin
            result = db.session.execute(text("""
                SELECT * FROM trabajador WHERE rol = 'superadmin' LIMIT 1
            """)).fetchone()
            
            if not result:
                # Hash de la contraseña usando Argon2
                ph = PasswordHasher()
                password_hash = ph.hash('admin123')
                
                # Verificar si existe usuario admin
                admin = db.session.execute(text("""
                    SELECT * FROM trabajador WHERE email = 'admin@sistema.com' LIMIT 1
                """)).fetchone()
                
                if admin:
                    # Actualizar usuario existente
                    db.session.execute(text("""
                        UPDATE trabajador 
                        SET rol = 'superadmin', 
                            activo = TRUE, 
                            password_hash = :password_hash,
                            updated_at = NOW()
                        WHERE id = :id
                    """), {'id': admin.id, 'password_hash': password_hash})
                    
                    logger.info(f"Usuario {admin.nombre} actualizado como Super Administrador")
                else:
                    # Crear nuevo super admin
                    db.session.execute(text("""
                        INSERT INTO trabajador 
                        (nombre, email, profesion, rol, activo, password_hash, 
                         intentos_fallidos, created_at, updated_at)
                        VALUES 
                        ('Super Administrador', 'admin@sistema.com', 
                         'Super Administrador del Sistema', 'superadmin', TRUE, 
                         :password_hash, 0, NOW(), NOW())
                    """), {'password_hash': password_hash})
                    
                    logger.info("Super Administrador creado con:")
                    logger.info("  Email: admin@sistema.com")
                    logger.info("  Contraseña: admin123")
                
                db.session.commit()
                logger.info("✅ Super Administrador configurado correctamente")
                logger.warning("⚠️  ¡IMPORTANTE! Cambie la contraseña después del primer login")
                
            else:
                logger.info("Ya existe un Super Administrador en el sistema")
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando usuario administrador: {e}")
            raise

if __name__ == '__main__':
    logger.info("Creando Super Administrador...")
    
    try:
        create_admin_simple()
        logger.info("✅ Configuración completada exitosamente!")
        logger.info("Puede ahora iniciar la aplicación y usar:")
        logger.info("  Usuario: admin@sistema.com")
        logger.info("  Contraseña: admin123")
        
    except Exception as e:
        logger.error(f"❌ Error durante la configuración: {e}")
        logger.error("Verifique la conexión a la base de datos")
