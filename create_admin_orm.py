#!/usr/bin/env python3
"""
Script para crear el usuario admin usando el ORM de la aplicación
"""

from app import create_app, db
from app.models import Trabajador
from argon2 import PasswordHasher
import sys

def create_admin_user():
    """Crea el usuario admin"""
    
    app = create_app()
    with app.app_context():
        try:
            # Verificar si el usuario admin ya existe
            existing_admin = Trabajador.query.filter_by(email='admin@sistema.com').first()
            
            if existing_admin:
                print("✅ El usuario admin ya existe")
                print(f"   Email: {existing_admin.email}")
                print(f"   Nombre: {existing_admin.nombre}")
                return True
            
            # Crear hash de la contraseña
            ph = PasswordHasher()
            password_hash = ph.hash('admin123')
            
            # Crear el usuario admin
            admin_user = Trabajador(
                nombre='Administrador del Sistema',
                nombrecorto='admin',
                email='admin@sistema.com',
                password_hash=password_hash,
                rol='admin',
                activo=True,
                profesion='Administrador'
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("🎉 Usuario admin creado exitosamente!")
            print("   Email: admin@sistema.com")
            print("   Contraseña: admin123")
            print("   Rol: admin")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al crear usuario admin: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Creando usuario admin...")
    if create_admin_user():
        print("\n✅ ¡Usuario admin listo para usar!")
        sys.exit(0)
    else:
        print("\n❌ Error al crear usuario admin")
        sys.exit(1)
