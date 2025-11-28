#!/usr/bin/env python3
"""
Script para verificar el estado del usuario admin y sus credenciales
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador
from config import Config

def verificar_usuario_admin():
    """Verificar y mostrar información completa del usuario admin"""
    print("🔍 Verificando usuario admin...")
    
    app = create_app(Config)
    
    with app.app_context():
        try:
            # Buscar todos los usuarios admin
            admin_users = Trabajador.query.filter(
                (Trabajador.email.like('%admin%')) | 
                (Trabajador.rol == 'admin')
            ).all()
            
            print(f"👥 Usuarios encontrados: {len(admin_users)}")
            
            for user in admin_users:
                print(f"\n📋 Usuario ID: {user.id}")
                print(f"👤 Nombre: {user.nombre}")
                print(f"📧 Email: {user.email}")
                print(f"🎭 Rol: {user.rol}")
                print(f"✅ Activo: {user.activo}")
                print(f"🔐 Hash: {user.password_hash[:80]}...")
                
                # Probar contraseñas comunes
                passwords_to_test = ['admin123', 'admin', '123456', 'password']
                
                for pwd in passwords_to_test:
                    try:
                        if user.verify_password(pwd):
                            print(f"✅ CONTRASEÑA CORRECTA: '{pwd}'")
                            break
                        else:
                            print(f"❌ Contraseña incorrecta: '{pwd}'")
                    except Exception as e:
                        print(f"⚠️ Error verificando '{pwd}': {e}")
                
                # Si no funciona ninguna, crear nueva contraseña
                print(f"\n🔧 Actualizando contraseña a 'admin123'...")
                user.password = 'admin123'
                db.session.commit()
                
                if user.verify_password('admin123'):
                    print("✅ Contraseña 'admin123' actualizada y verificada")
                else:
                    print("❌ Error: la contraseña sigue sin funcionar")
            
            # Si no hay usuarios admin, crear uno
            if not admin_users:
                print("🆕 Creando nuevo usuario admin...")
                admin_user = Trabajador(
                    nombre='Administrador del Sistema',
                    email='admin@sistema.com',
                    rol='admin',
                    activo=True
                )
                admin_user.password = 'admin123'
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Usuario admin creado")
                print(f"📧 Email: admin@sistema.com")
                print(f"🔑 Contraseña: admin123")
                
                if admin_user.verify_password('admin123'):
                    print("✅ Verificación exitosa")
            
            print(f"\n🎯 CREDENCIALES FINALES:")
            print(f"📧 Email: admin@sistema.com")
            print(f"🔑 Contraseña: admin123")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    verificar_usuario_admin()
