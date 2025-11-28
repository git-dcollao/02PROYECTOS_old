#!/usr/bin/env python3
"""
Script para actualizar el rol del usuario admin
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, UserRole
from config import Config

def actualizar_usuario_admin():
    """Actualizar el rol y datos del usuario admin"""
    print("🔧 Actualizando usuario admin con rol correcto...")
    
    app = create_app(Config)
    
    with app.app_context():
        try:
            # Buscar usuario admin
            admin_user = Trabajador.query.filter_by(email='admin@sistema.com').first()
            
            if admin_user:
                print(f"👤 Usuario encontrado: {admin_user.email}")
                print(f"📊 Rol actual: {admin_user.rol}")
                print(f"📊 Nombre actual: {admin_user.nombre}")
                
                # Actualizar los datos
                admin_user.rol = UserRole.ADMIN  # Cambiar a ADMIN
                admin_user.nombre = 'Administrador del Sistema'
                admin_user.password = 'admin123'  # Rehash la contraseña
                admin_user.activo = True
                
                db.session.commit()
                
                print(f"✅ Usuario actualizado:")
                print(f"👤 Nombre: {admin_user.nombre}")
                print(f"📧 Email: {admin_user.email}")
                print(f"🎭 Rol: {admin_user.rol}")
                print(f"📝 Rol display: {admin_user.rol_display}")
                print(f"✅ Activo: {admin_user.activo}")
                
                # Verificar contraseña
                if admin_user.verify_password('admin123'):
                    print("✅ Contraseña verificada correctamente")
                else:
                    print("❌ Error en verificación de contraseña")
                
                # Verificar permisos de administrador
                print(f"🔐 Es admin: {admin_user.is_admin()}")
                print(f"👥 Puede gestionar usuarios: {admin_user.can_manage_users()}")
                print(f"📊 Puede gestionar proyectos: {admin_user.can_manage_projects()}")
                
            else:
                print("❌ Usuario admin no encontrado")
                return False
                
            print(f"\n🎯 CREDENCIALES FINALES:")
            print(f"📧 Email: admin@sistema.com")
            print(f"🔑 Contraseña: admin123")
            print(f"🎭 Rol: Administrador")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    actualizar_usuario_admin()
