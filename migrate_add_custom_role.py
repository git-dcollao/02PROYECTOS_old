#!/usr/bin/env python3
"""
Script de migración para agregar la columna custom_role_id a la tabla trabajador
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
import traceback

def migrate_add_custom_role_column():
    """Agregar la columna custom_role_id a la tabla trabajador"""
    print("🔄 Iniciando migración: Agregar columna custom_role_id a tabla trabajador")
    
    try:
        # Verificar si la columna ya existe
        check_column_query = """
        SELECT COUNT(*) as column_exists 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'trabajador' 
        AND COLUMN_NAME = 'custom_role_id'
        """
        
        result = db.session.execute(text(check_column_query)).fetchone()
        
        if result[0] > 0:
            print("✅ La columna custom_role_id ya existe en la tabla trabajador")
            return True
        
        print("📋 Agregando columna custom_role_id a tabla trabajador...")
        
        # Agregar la columna custom_role_id
        alter_query = """
        ALTER TABLE trabajador 
        ADD COLUMN custom_role_id INT NULL,
        ADD CONSTRAINT fk_trabajador_custom_role 
        FOREIGN KEY (custom_role_id) REFERENCES custom_roles(id)
        """
        
        db.session.execute(text(alter_query))
        
        # Crear índice para mejor performance
        index_query = """
        CREATE INDEX idx_trabajador_custom_role ON trabajador(custom_role_id)
        """
        
        db.session.execute(text(index_query))
        
        db.session.commit()
        print("✅ Columna custom_role_id agregada exitosamente")
        
        # Verificar que la migración fue exitosa
        verify_query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'trabajador' 
        AND COLUMN_NAME = 'custom_role_id'
        """
        
        verification = db.session.execute(text(verify_query)).fetchone()
        if verification:
            print(f"✅ Verificación exitosa: {verification[0]} ({verification[1]}, nullable: {verification[2]})")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error durante la migración: {e}")
        traceback.print_exc()
        return False

def migrate_update_existing_users():
    """Actualizar usuarios existentes para usar el nuevo sistema de roles"""
    print("\n🔄 Actualizando usuarios existentes...")
    
    try:
        from app.models import Trabajador, CustomRole, UserRole
        
        # Obtener todos los trabajadores
        trabajadores = Trabajador.query.all()
        print(f"📋 Encontrados {len(trabajadores)} trabajadores para actualizar")
        
        updated_count = 0
        
        for trabajador in trabajadores:
            # Si ya tiene custom_role_id, saltarlo
            if trabajador.custom_role_id is not None:
                continue
                
            # Si es SUPERADMIN, mantenerlo como está
            if trabajador.rol == UserRole.SUPERADMIN:
                trabajador.custom_role_id = None
                print(f"✅ {trabajador.email}: Mantenido como SUPERADMIN")
                continue
            
            # Para otros casos, necesitamos determinar qué rol asignar
            # Por ahora, asignar rol USUARIO por defecto
            default_role = CustomRole.query.filter_by(name='USUARIO', active=True).first()
            if default_role:
                trabajador.rol = None  # Limpiar el rol del sistema
                trabajador.custom_role_id = default_role.id
                updated_count += 1
                print(f"✅ {trabajador.email}: Asignado rol personalizado USUARIO")
            else:
                print(f"⚠️ {trabajador.email}: No se pudo asignar rol (rol USUARIO no encontrado)")
        
        if updated_count > 0:
            db.session.commit()
            print(f"✅ {updated_count} trabajadores actualizados exitosamente")
        else:
            print("ℹ️ No se requirieron actualizaciones")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error actualizando usuarios: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal de migración"""
    print("🚀 Iniciando proceso de migración para sistema de roles personalizado")
    
    app = create_app()
    
    with app.app_context():
        # Paso 1: Agregar columna custom_role_id
        if not migrate_add_custom_role_column():
            print("❌ Falló la migración de la columna custom_role_id")
            return False
        
        # Paso 2: Actualizar usuarios existentes
        if not migrate_update_existing_users():
            print("❌ Falló la actualización de usuarios existentes")
            return False
        
        print("\n🎉 ¡Migración completada exitosamente!")
        print("✅ Sistema de roles personalizado configurado")
        print("✅ Usuarios existentes actualizados")
        
        return True

if __name__ == "__main__":
    if main():
        print("\n✅ Migración exitosa. La aplicación está lista para usar.")
        sys.exit(0)
    else:
        print("\n❌ Migración falló. Revisa los errores anteriores.")
        sys.exit(1)
