#!/usr/bin/env python3
"""
Script para verificar permisos de usuario y solucionar problemas de acceso
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, UserRole

def check_user_permissions():
    """Verificar permisos de usuarios en el sistema"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 VERIFICANDO USUARIOS Y PERMISOS")
            print("=" * 50)
            
            # Obtener todos los usuarios
            users = Trabajador.query.all()
            
            if not users:
                print("❌ No se encontraron usuarios en la base de datos")
                return
            
            print(f"👥 Total de usuarios encontrados: {len(users)}")
            print()
            
            for user in users:
                print(f"📧 Email: {user.email}")
                print(f"👤 Nombre: {user.nombre}")
                print(f"🔑 Rol: {user.rol.value} ({user.rol_display})")
                print(f"✅ Activo: {'Sí' if user.activo else 'No'}")
                print(f"🛡️ Puede gestionar usuarios: {'✅' if user.can_manage_users() else '❌'}")
                print(f"📁 Puede gestionar proyectos: {'✅' if user.can_manage_projects() else '❌'}")
                print(f"📊 Puede ver reportes: {'✅' if user.can_view_reports() else '❌'}")
                
                if hasattr(user, 'bloqueado_hasta') and user.bloqueado_hasta:
                    print(f"🚫 Bloqueado hasta: {user.bloqueado_hasta}")
                if hasattr(user, 'intentos_fallidos'):
                    print(f"⚠️ Intentos fallidos: {user.intentos_fallidos}")
                
                print("-" * 30)
            
            # Verificar roles disponibles
            print("\n🎭 ROLES DISPONIBLES EN EL SISTEMA:")
            for role in UserRole:
                print(f"   • {role.value.upper()} -> {role.name}")
            
            # Sugerencias
            print("\n💡 SUGERENCIAS:")
            admin_users = [u for u in users if u.can_manage_users()]
            if not admin_users:
                print("❌ No hay usuarios con permisos de administrador")
                print("   Usa el script 'update_admin.py' para crear un admin")
            else:
                print("✅ Usuarios con permisos de administrador encontrados:")
                for admin in admin_users:
                    print(f"   • {admin.email} ({admin.rol_display})")
            
            return users
            
        except Exception as e:
            print(f"💥 Error al verificar permisos: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def create_admin_user():
    """Crear un usuario administrador de emergencia"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🆘 CREANDO USUARIO ADMINISTRADOR DE EMERGENCIA")
            print("=" * 50)
            
            # Verificar si ya existe un admin
            admin_exists = Trabajador.query.filter(
                Trabajador.rol.in_([UserRole.ADMIN, UserRole.SUPERADMIN])
            ).first()
            
            if admin_exists:
                print(f"✅ Ya existe un administrador: {admin_exists.email}")
                return
            
            # Crear admin de emergencia
            admin_user = Trabajador(
                nombre="Administrador Sistema",
                email="admin@sistema.local",
                profesion="Administrador",
                telefono="",
                rol=UserRole.SUPERADMIN,
                activo=True
            )
            admin_user.password = "admin123"  # Cambiar después del primer login
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Usuario administrador creado exitosamente:")
            print(f"   📧 Email: admin@sistema.local")
            print(f"   🔒 Contraseña: admin123")
            print(f"   🔑 Rol: SUPERADMIN")
            print("\n⚠️ IMPORTANTE: Cambia la contraseña después del primer login")
            
        except Exception as e:
            print(f"💥 Error al crear admin: {str(e)}")
            db.session.rollback()

def fix_user_permissions(email):
    """Convertir un usuario específico en administrador"""
    app = create_app()
    
    with app.app_context():
        try:
            user = Trabajador.query.filter_by(email=email).first()
            if not user:
                print(f"❌ Usuario con email '{email}' no encontrado")
                return False
            
            print(f"🔧 Actualizando permisos para {user.nombre} ({email})")
            print(f"   Rol actual: {user.rol_display}")
            
            # Promover a SUPERADMIN
            user.rol = UserRole.SUPERADMIN
            user.activo = True
            user.intentos_fallidos = 0
            user.bloqueado_hasta = None
            
            db.session.commit()
            
            print(f"✅ Usuario actualizado exitosamente:")
            print(f"   🔑 Nuevo rol: {user.rol_display}")
            print(f"   🛡️ Puede gestionar usuarios: {user.can_manage_users()}")
            
            return True
            
        except Exception as e:
            print(f"💥 Error al actualizar usuario: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🔐 DIAGNÓSTICO DE PERMISOS DEL SISTEMA")
    print("=" * 60)
    
    # Verificar usuarios existentes
    users = check_user_permissions()
    
    if not users:
        print("\n❌ No se pudieron cargar los usuarios")
        sys.exit(1)
    
    # Verificar si hay admins
    admin_users = [u for u in users if u.can_manage_users()]
    
    if not admin_users:
        print("\n🆘 NO HAY USUARIOS ADMINISTRADORES")
        response = input("¿Deseas crear un usuario admin de emergencia? (s/N): ")
        
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            create_admin_user()
    else:
        print(f"\n✅ Sistema tiene {len(admin_users)} administrador(es)")
        
        # Preguntar si quiere promover otro usuario
        response = input("\n¿Deseas promover algún usuario a administrador? (s/N): ")
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            print("\nUsuarios disponibles:")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user.email} - {user.nombre} ({user.rol_display})")
            
            try:
                choice = int(input("Selecciona el número del usuario: ")) - 1
                if 0 <= choice < len(users):
                    selected_user = users[choice]
                    fix_user_permissions(selected_user.email)
                else:
                    print("❌ Selección inválida")
            except (ValueError, IndexError):
                print("❌ Entrada inválida")
    
    print("\n✅ Diagnóstico completado")
