#!/usr/bin/env python3
"""
Script para crear el usuario administrador correcto
"""
from app import create_app, db
from app.models import Trabajador, UserRole
from datetime import datetime

def crear_admin_correcto():
    """Crear el usuario administrador con los datos correctos"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Configurando usuario administrador...")
        
        try:
            # Buscar si ya existe el usuario admin por nombre
            admin_existing = Trabajador.query.filter_by(nombre='Admin').first()
            
            if admin_existing:
                # Actualizar el usuario existente
                print("📝 Actualizando usuario Admin existente...")
                admin_existing.email = 'admin@sistema.com'
                admin_existing.rol = UserRole.ADMIN
                admin_existing.password = 'admin123'
                admin_existing.activo = True
                admin_existing.profesion = 'Administrador del Sistema'
                admin_existing.nombrecorto = 'admin'
                admin_existing.intentos_fallidos = 0
                admin_existing.bloqueado_hasta = None
                
                db.session.commit()
                print("✅ Usuario Admin actualizado exitosamente")
                
            else:
                # Crear nuevo usuario admin
                print("🆕 Creando nuevo usuario Admin...")
                admin = Trabajador(
                    nombre='Admin',
                    email='admin@sistema.com',
                    profesion='Administrador del Sistema',
                    nombrecorto='admin',
                    rol=UserRole.ADMIN,
                    activo=True
                )
                admin.password = 'admin123'
                
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario Admin creado exitosamente")
            
            # Verificar que el usuario fue creado/actualizado correctamente
            admin_check = Trabajador.query.filter_by(email='admin@sistema.com').first()
            if admin_check:
                print(f"✅ Verificación exitosa:")
                print(f"   - ID: {admin_check.id}")
                print(f"   - Nombre: {admin_check.nombre}")
                print(f"   - Email: {admin_check.email}")
                print(f"   - Rol: {admin_check.rol.value}")
                print(f"   - Activo: {admin_check.activo}")
                
                # Probar verificación de contraseña
                if admin_check.verify_password('admin123'):
                    print("✅ Contraseña verificada correctamente")
                else:
                    print("❌ Error en verificación de contraseña")
                
                return True
            else:
                print("❌ Error: No se pudo verificar la creación del usuario")
                return False
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear/actualizar usuario admin: {e}")
            return False

def mostrar_usuarios_actuales():
    """Mostrar todos los usuarios actuales en la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("👥 Usuarios actuales en la base de datos:")
        usuarios = Trabajador.query.all()
        
        for usuario in usuarios:
            print(f"   - ID: {usuario.id}")
            print(f"     Nombre: {usuario.nombre}")
            print(f"     Email: {usuario.email or 'Sin email'}")
            print(f"     Rol: {usuario.rol.value if usuario.rol else 'Sin rol'}")
            print(f"     Activo: {usuario.activo}")
            print("     ---")

if __name__ == '__main__':
    print("🚀 Iniciando configuración del usuario administrador...")
    
    # Mostrar estado actual
    print("\n📋 Estado actual:")
    mostrar_usuarios_actuales()
    
    # Crear/actualizar admin
    print("\n🔧 Configurando admin...")
    if crear_admin_correcto():
        print("\n✅ Estado después de la configuración:")
        mostrar_usuarios_actuales()
        print("\n🎉 Configuración completada exitosamente!")
        print("📌 Credenciales de acceso:")
        print("   Email: admin@sistema.com")
        print("   Contraseña: admin123")
    else:
        print("\n❌ Error en la configuración")
