#!/usr/bin/env python3
"""
Script para corregir y actualizar los roles personalizados en la base de datos
"""

import sys
import os
from sqlalchemy import text

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import CustomRole

def main():
    print("🚀 Iniciando corrección de roles personalizados")
    
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        try:
            if update_custom_roles():
                if assign_correct_custom_roles():
                    print("\n✅ Corrección exitosa. Los roles personalizados están actualizados.")
                    return 0
                else:
                    print("\n❌ Falló la asignación de roles personalizados.")
                    return 1
            else:
                print("\n❌ Falló la corrección de roles personalizados.")
                return 1
        except Exception as e:
            print(f"\n❌ Error general: {e}")
            return 1

def update_custom_roles():
    """Actualizar roles personalizados con los nombres correctos"""
    print("\n🔄 Actualizando roles personalizados...")
    
    try:
        # Definir los roles correctos
        correct_roles = [
            {
                'name': 'ADMIN',
                'description': 'Administrador General con permisos completos de gestión',
                'active': True
            },
            {
                'name': 'ADMIN_AREA',
                'description': 'Control de Proyectos con permisos de supervisión y control',
                'active': True
            },
            {
                'name': 'USUARIO', 
                'description': 'Usuario Operativo con acceso a funcionalidades básicas',
                'active': True
            },
            {
                'name': 'SOLICITANTE',
                'description': 'Solicitante Externo con permisos de solicitud y consulta',
                'active': True
            }
        ]
        
        # Listar roles actuales
        current_roles = db.session.execute(text("SELECT id, name, description FROM custom_roles")).fetchall()
        print(f"📋 Roles actuales en la base de datos:")
        for role in current_roles:
            print(f"   • ID {role[0]}: {role[1]} - {role[2]}")
        
        # Desactivar todos los roles actuales
        print(f"\n🔄 Desactivando roles existentes...")
        db.session.execute(text("UPDATE custom_roles SET active = FALSE"))
        
        # Crear o actualizar roles correctos
        print(f"\n🔄 Creando/actualizando roles correctos...")
        for role_data in correct_roles:
            existing_role = CustomRole.query.filter_by(name=role_data['name']).first()
            
            if existing_role:
                # Actualizar role existente
                existing_role.description = role_data['description']
                existing_role.active = role_data['active']
                print(f"✅ Actualizado: {role_data['name']}")
            else:
                # Crear nuevo role
                new_role = CustomRole(**role_data)
                db.session.add(new_role)
                print(f"✅ Creado: {role_data['name']}")
        
        db.session.commit()
        
        # Verificar roles finales
        print(f"\n📋 Roles finales:")
        final_roles = db.session.execute(text("SELECT id, name, description, active FROM custom_roles WHERE active = TRUE")).fetchall()
        for role in final_roles:
            print(f"   • ID {role[0]}: {role[1]} - {role[2]} (Activo: {role[3]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando roles personalizados: {e}")
        try:
            db.session.rollback()
        except:
            pass  # Ignorar errores de rollback si estamos fuera de contexto
        return False

def assign_correct_custom_roles():
    """Asignar roles personalizados correctos a usuarios existentes"""
    print("\n🔄 Asignando roles personalizados correctos...")
    
    try:
        # Mapeo de emails a roles personalizados
        email_role_mapping = {
            'admin@sistema.local': None,  # Mantener como SUPERADMIN del sistema
            'administrador@sistema.local': 'ADMIN',
            'control@sistema.local': 'ADMIN_AREA', 
            'usuario@sistema.local': 'USUARIO',
            'solicitante@sistema.local': 'SOLICITANTE'
        }
        
        # Obtener roles personalizados activos
        active_roles = {}
        for role in CustomRole.query.filter_by(active=True).all():
            active_roles[role.name] = role.id
        
        print(f"📋 Roles disponibles: {list(active_roles.keys())}")
        
        for email, target_role in email_role_mapping.items():
            user_query = """
            SELECT id FROM trabajador WHERE email = :email
            """
            user_result = db.session.execute(text(user_query), {'email': email}).fetchone()
            
            if not user_result:
                print(f"⚠️ Usuario {email} no encontrado")
                continue
            
            user_id = user_result[0]
            
            if target_role is None:
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
                if target_role in active_roles:
                    custom_role_id = active_roles[target_role]
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
                else:
                    print(f"❌ {email}: Rol personalizado {target_role} no encontrado")
        
        db.session.commit()
        
        # Verificar asignaciones finales
        print(f"\n📋 Asignaciones finales:")
        final_users = db.session.execute(text("""
            SELECT t.email, t.rol, cr.name as custom_role
            FROM trabajador t
            LEFT JOIN custom_roles cr ON t.custom_role_id = cr.id
            ORDER BY t.email
        """)).fetchall()
        
        for user in final_users:
            if user[1]:  # Si tiene rol del sistema
                print(f"   • {user[0]}: Sistema: {user[1]}")
            else:  # Si tiene rol personalizado
                print(f"   • {user[0]}: Personalizado: {user[2]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error asignando roles: {e}")
        try:
            db.session.rollback()
        except:
            pass  # Ignorar errores de rollback si estamos fuera de contexto
        return False

if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        print("\n🎉 ¡Corrección de roles completada exitosamente!")
        print("📝 Ahora puedes probar la aplicación:")
        print("   • Aplicación: http://localhost:5050/")
        print("   • Permisos: http://localhost:5050/permissions/")
    else:
        print("\n❌ Falló la corrección de roles.")
    exit(exit_code)
