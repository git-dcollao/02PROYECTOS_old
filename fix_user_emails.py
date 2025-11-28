#!/usr/bin/env python3
"""
Script para corregir usuarios sin email y asignarles emails válidos
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, UserRole

def fix_users_without_email():
    """Corregir usuarios que no tienen email asignado"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 CORRIGIENDO USUARIOS SIN EMAIL")
            print("=" * 50)
            
            # Obtener usuarios sin email
            users_without_email = Trabajador.query.filter(
                (Trabajador.email == None) | (Trabajador.email == '')
            ).all()
            
            if not users_without_email:
                print("✅ Todos los usuarios ya tienen email asignado")
                return True
            
            print(f"👥 Usuarios sin email encontrados: {len(users_without_email)}")
            print()
            
            # Mapeo de correcciones sugeridas
            email_mapping = {
                'Admin': 'admin@sistema.local',
                'Usuario Demo': 'demo@sistema.local',
                'Administrador Sistema': 'superadmin@sistema.local'
            }
            
            users_updated = 0
            
            for user in users_without_email:
                print(f"👤 Usuario: {user.nombre}")
                print(f"🔑 Rol actual: {user.rol_display}")
                
                # Buscar email sugerido
                suggested_email = email_mapping.get(user.nombre)
                
                if suggested_email:
                    # Verificar que el email no esté en uso
                    existing_user = Trabajador.query.filter_by(email=suggested_email).first()
                    if existing_user and existing_user.id != user.id:
                        suggested_email = f"{user.nombre.lower().replace(' ', '.')}@sistema.local"
                    
                    user.email = suggested_email
                    print(f"📧 Email asignado: {suggested_email}")
                else:
                    # Crear email basado en el nombre
                    base_email = user.nombre.lower().replace(' ', '.').replace('ñ', 'n')
                    email = f"{base_email}@sistema.local"
                    
                    # Verificar que no esté en uso
                    counter = 1
                    while Trabajador.query.filter_by(email=email).first():
                        email = f"{base_email}{counter}@sistema.local"
                        counter += 1
                    
                    user.email = email
                    print(f"📧 Email generado: {email}")
                
                # Asegurarse de que esté activo
                user.activo = True
                users_updated += 1
                print("✅ Usuario actualizado")
                print("-" * 30)
            
            # Guardar cambios
            db.session.commit()
            
            print(f"\n🎉 {users_updated} usuarios actualizados exitosamente")
            print("\n📋 RESUMEN DE USUARIOS ACTUALIZADOS:")
            
            # Mostrar todos los usuarios con sus emails
            all_users = Trabajador.query.all()
            for user in all_users:
                status = "✅ Activo" if user.activo else "❌ Inactivo"
                admin_status = "🛡️ Admin" if user.can_manage_users() else "👤 Usuario"
                print(f"   • {user.nombre} - {user.email} ({user.rol_display}) - {status} {admin_status}")
            
            return True
            
        except Exception as e:
            print(f"💥 Error al corregir usuarios: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

def test_login_credentials():
    """Probar las credenciales de login de los usuarios"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🔐 PROBANDO CREDENCIALES DE LOGIN")
            print("=" * 50)
            
            # Obtener usuarios activos con email
            users = Trabajador.query.filter(
                Trabajador.activo == True,
                Trabajador.email.isnot(None),
                Trabajador.email != ''
            ).all()
            
            if not users:
                print("❌ No se encontraron usuarios válidos para login")
                return False
            
            print("🔑 CREDENCIALES DISPONIBLES PARA LOGIN:")
            print()
            
            for user in users:
                print(f"👤 Nombre: {user.nombre}")
                print(f"📧 Email: {user.email}")
                print(f"🔒 Contraseña: [La contraseña del usuario]")
                print(f"🔑 Rol: {user.rol_display}")
                print(f"🛡️ Permisos admin: {'✅ Sí' if user.can_manage_users() else '❌ No'}")
                
                # Si es el usuario Admin original, mostrar la contraseña
                if user.nombre == 'Admin':
                    print(f"💡 Contraseña sugerida: Maho#2024")
                elif user.nombre == 'Usuario Demo':
                    print(f"💡 Contraseña sugerida: Demo#2024")
                elif user.email == 'admin@sistema.local' and user.nombre == 'Administrador Sistema':
                    print(f"💡 Contraseña: admin123")
                
                print("-" * 40)
            
            return True
            
        except Exception as e:
            print(f"💥 Error al probar credenciales: {str(e)}")
            return False

if __name__ == "__main__":
    print("🔧 CORRECCIÓN DE USUARIOS SIN EMAIL")
    print("=" * 60)
    
    # Corregir usuarios sin email
    if fix_users_without_email():
        print("\n✅ Corrección completada exitosamente")
        
        # Probar credenciales
        test_login_credentials()
        
        print("\n💡 INSTRUCCIONES:")
        print("1. Usa cualquiera de las credenciales mostradas arriba")
        print("2. Los usuarios con 🛡️ Admin pueden acceder a la gestión de permisos")
        print("3. Ve a http://localhost:5050/auth/login para iniciar sesión")
        print("4. Después del login, ve a http://localhost:5050/permissions/")
        
    else:
        print("\n❌ Error en la corrección de usuarios")
        sys.exit(1)
