#!/usr/bin/env python3
"""
Script para recrear el usuario admin con contraseña correctamente hasheada
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador
from config import Config

def recrear_usuario_admin():
    """Recrear usuario admin con hash correcto"""
    print("🔐 Recreando usuario admin con hash Argon2 correcto...")
    
    app = create_app(Config)
    
    with app.app_context():
        try:
            # Buscar usuario admin existente
            admin_user = Trabajador.query.filter_by(email='admin@sistema.com').first()
            
            if admin_user:
                print(f"👤 Usuario admin encontrado: {admin_user.email}")
                print(f"📊 Hash actual: {admin_user.password_hash[:50]}...")
                
                # Actualizar la contraseña correctamente
                admin_user.password = 'admin123'  # Esto activará el setter que hashea con Argon2
                db.session.commit()
                print("✅ Contraseña actualizada correctamente")
                
                # Probar la verificación
                if admin_user.verify_password('admin123'):
                    print("✅ Verificación de contraseña exitosa")
                else:
                    print("❌ Error en verificación de contraseña")
            else:
                print("👤 Usuario admin no encontrado, creando nuevo...")
                # Crear nuevo usuario admin
                admin_user = Trabajador(
                    nombre='Administrador',
                    email='admin@sistema.com',
                    rol='admin',
                    activo=True
                )
                admin_user.password = 'admin123'  # Hash con Argon2
                
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Usuario admin creado exitosamente")
                
                # Verificar
                if admin_user.verify_password('admin123'):
                    print("✅ Verificación de contraseña exitosa")
                else:
                    print("❌ Error en verificación de contraseña")
            
            print(f"🎯 Nuevo hash: {admin_user.password_hash[:50]}...")
            print("✅ Usuario admin listo para usar")
            print("📧 Email: admin@sistema.com")
            print("🔑 Contraseña: admin123")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    recrear_usuario_admin()
