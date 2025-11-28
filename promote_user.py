#!/usr/bin/env python3
"""
Script para promover un usuario existente a administrador
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, UserRole

def promote_user_to_admin():
    """Promover un usuario existente a administrador"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 PROMOCIÓN DE USUARIO A ADMINISTRADOR")
            print("=" * 50)
            
            # Mostrar todos los usuarios disponibles
            users = Trabajador.query.all()
            
            if not users:
                print("❌ No se encontraron usuarios en el sistema")
                return
            
            print("👥 Usuarios disponibles:")
            for i, user in enumerate(users, 1):
                status = "✅ Activo" if user.activo else "❌ Inactivo"
                email = user.email if user.email else "Sin email"
                print(f"{i}. {user.nombre} - {email} ({user.rol_display}) - {status}")
            
            # Solicitar selección
            print()
            choice = input("Selecciona el número del usuario a promover (1-{}): ".format(len(users)))
            
            try:
                user_index = int(choice) - 1
                if user_index < 0 or user_index >= len(users):
                    print("❌ Selección inválida")
                    return
                
                selected_user = users[user_index]
                
                print(f"\n👤 Usuario seleccionado: {selected_user.nombre}")
                print(f"📧 Email actual: {selected_user.email or 'Sin email'}")
                print(f"🔑 Rol actual: {selected_user.rol_display}")
                
                # Confirmar promoción
                confirm = input("\n¿Confirmas la promoción a SUPERADMIN? (s/N): ")
                if confirm.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
                    print("❌ Promoción cancelada")
                    return
                
                # Actualizar email si no tiene uno
                if not selected_user.email:
                    new_email = input("👍 El usuario no tiene email. Ingresa uno: ").strip()
                    if new_email:
                        selected_user.email = new_email
                    else:
                        print("❌ Email es requerido para acceder al sistema")
                        return
                
                # Realizar la promoción
                selected_user.rol = UserRole.SUPERADMIN
                selected_user.activo = True
                selected_user.intentos_fallidos = 0
                selected_user.bloqueado_hasta = None
                
                db.session.commit()
                
                print("\n✅ Usuario promovido exitosamente:")
                print(f"   👤 Nombre: {selected_user.nombre}")
                print(f"   📧 Email: {selected_user.email}")
                print(f"   🔑 Nuevo rol: {selected_user.rol_display}")
                print(f"   🛡️ Puede gestionar usuarios: {selected_user.can_manage_users()}")
                print(f"   📁 Puede gestionar proyectos: {selected_user.can_manage_projects()}")
                
                print("\n🎉 ¡Listo! Ahora puedes iniciar sesión con este usuario para acceder a la gestión de permisos.")
                
            except ValueError:
                print("❌ Entrada inválida. Debe ser un número.")
            
        except Exception as e:
            print(f"💥 Error al promover usuario: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    promote_user_to_admin()
