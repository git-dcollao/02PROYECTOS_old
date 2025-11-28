#!/usr/bin/env python3
"""
Script para limpiar y migrar datos existentes de la tabla trabajador
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
import traceback

def fix_existing_user_roles():
    """Corregir roles existentes en la base de datos"""
    print("🔄 Corrigiendo roles existentes en la base de datos")
    
    try:
        # Paso 1: Ver qué roles existen actualmente
        check_roles_query = """
        SELECT rol, COUNT(*) as count 
        FROM trabajador 
        GROUP BY rol
        """
        
        existing_roles = db.session.execute(text(check_roles_query)).fetchall()
        print("📋 Roles actuales en la base de datos:")
        for role, count in existing_roles:
            print(f"   • {role}: {count} usuarios")
        
        # Paso 2: Actualizar todos los roles inválidos a SUPERADMIN temporalmente
        # para que puedan ser leídos por SQLAlchemy
        invalid_roles = ['ADMIN', 'ADMIN_AREA', 'USUARIO', 'SOLICITANTE']
        
        for invalid_role in invalid_roles:
            count_query = """
            SELECT COUNT(*) FROM trabajador WHERE rol = :rol
            """
            result = db.session.execute(text(count_query), {'rol': invalid_role}).fetchone()
            
            if result[0] > 0:
                print(f"🔄 Actualizando {result[0]} usuarios con rol '{invalid_role}' a SUPERADMIN temporalmente")
                
                update_query = """
                UPDATE trabajador 
                SET rol = 'SUPERADMIN' 
                WHERE rol = :rol
                """
                db.session.execute(text(update_query), {'rol': invalid_role})
        
        db.session.commit()
        print("✅ Roles temporalmente corregidos")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error corrigiendo roles: {e}")
        traceback.print_exc()
        return False

def assign_custom_roles():
    """Asignar roles personalizados basados en el email del usuario"""
    print("\n🔄 Asignando roles personalizados...")
    
    try:
        # Mapeo de emails a roles personalizados
        email_role_mapping = {
            'admin@sistema.local': 'SUPERADMIN',  # Mantener como SUPERADMIN
            'administrador@sistema.local': 'ADMIN',
            'control@sistema.local': 'ADMIN_AREA', 
            'usuario@sistema.local': 'USUARIO',
            'solicitante@sistema.local': 'SOLICITANTE'
        }
        
        # Obtener roles personalizados disponibles
        custom_roles_query = """
        SELECT id, name FROM custom_roles WHERE active = TRUE
        """
        custom_roles = db.session.execute(text(custom_roles_query)).fetchall()
        custom_roles_dict = {name: id for id, name in custom_roles}
        
        print(f"📋 Roles personalizados disponibles: {list(custom_roles_dict.keys())}")
        
        updated_count = 0
        
        for email, target_role in email_role_mapping.items():
            # Verificar si el usuario existe
            user_query = """
            SELECT id FROM trabajador WHERE email = :email
            """
            user_result = db.session.execute(text(user_query), {'email': email}).fetchone()
            
            if not user_result:
                print(f"⚠️ Usuario {email} no encontrado")
                continue
            
            user_id = user_result[0]
            
            if target_role == 'SUPERADMIN':
                # Mantener como SUPERADMIN del sistema
                update_query = """
                UPDATE trabajador 
                SET rol = 'SUPERADMIN', custom_role_id = NULL 
                WHERE id = :user_id
                """
                db.session.execute(text(update_query), {'user_id': user_id})
                print(f"✅ {email}: Configurado como SUPERADMIN del sistema")
                
            else:
                # Asignar rol personalizado
                if target_role in custom_roles_dict:
                    custom_role_id = custom_roles_dict[target_role]
                    update_query = """
                    UPDATE trabajador 
                    SET rol = NULL, custom_role_id = :custom_role_id 
                    WHERE id = :user_id
                    """
                    db.session.execute(text(update_query), {
                        'custom_role_id': custom_role_id,
                        'user_id': user_id
                    })
                    print(f"✅ {email}: Asignado rol personalizado {target_role}")
                    updated_count += 1
                else:
                    print(f"⚠️ {email}: Rol personalizado {target_role} no encontrado")
        
        db.session.commit()
        print(f"✅ {updated_count} usuarios actualizados con roles personalizados")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error asignando roles personalizados: {e}")
        traceback.print_exc()
        return False

def verify_migration():
    """Verificar que la migración fue exitosa"""
    print("\n🔍 Verificando migración...")
    
    try:
        verification_query = """
        SELECT 
            t.email,
            t.rol as system_role,
            cr.name as custom_role_name,
            CASE 
                WHEN t.rol IS NOT NULL THEN CONCAT('Sistema: ', t.rol)
                WHEN t.custom_role_id IS NOT NULL THEN CONCAT('Personalizado: ', cr.name)
                ELSE 'Sin rol'
            END as effective_role
        FROM trabajador t
        LEFT JOIN custom_roles cr ON t.custom_role_id = cr.id
        ORDER BY t.email
        """
        
        results = db.session.execute(text(verification_query)).fetchall()
        
        print("📋 Estado final de usuarios:")
        for email, system_role, custom_role, effective_role in results:
            print(f"   • {email}: {effective_role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando limpieza y migración de datos de usuario")
    
    app = create_app()
    
    with app.app_context():
        # Paso 1: Corregir roles existentes
        if not fix_existing_user_roles():
            print("❌ Falló la corrección de roles existentes")
            return False
        
        # Paso 2: Asignar roles personalizados
        if not assign_custom_roles():
            print("❌ Falló la asignación de roles personalizados")
            return False
        
        # Paso 3: Verificar migración
        if not verify_migration():
            print("❌ Falló la verificación")
            return False
        
        print("\n🎉 ¡Migración de datos completada exitosamente!")
        return True

if __name__ == "__main__":
    if main():
        print("\n✅ Migración exitosa. Los usuarios están listos con el nuevo sistema de roles.")
        sys.exit(0)
    else:
        print("\n❌ Migración falló. Revisa los errores anteriores.")
        sys.exit(1)
