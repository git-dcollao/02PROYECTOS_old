#!/usr/bin/env python3
"""
Script de Gestión de Permisos y Roles de Usuario
Uso: python manage_permissions.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, UserRole

def show_all_users():
    """Mostrar todos los usuarios con sus roles"""
    print("\n🔍 **USUARIOS DEL SISTEMA**")
    print("=" * 60)
    
    trabajadores = Trabajador.query.all()
    if not trabajadores:
        print("❌ No hay usuarios en el sistema")
        return
    
    for t in trabajadores:
        status = "✅ ACTIVO" if t.activo else "❌ INACTIVO"
        print(f"ID: {t.id:2} | Email: {t.email:20} | Rol: {t.rol.display_name:12} | {status}")

def change_user_role():
    """Cambiar rol de un usuario"""
    print("\n🔧 **CAMBIAR ROL DE USUARIO**")
    print("=" * 40)
    
    # Mostrar usuarios actuales
    show_all_users()
    
    try:
        user_id = int(input("\nIngrese ID del usuario: "))
        user = Trabajador.query.get(user_id)
        
        if not user:
            print("❌ Usuario no encontrado")
            return
        
        print(f"\nUsuario seleccionado: {user.email}")
        print(f"Rol actual: {user.rol.display_name}")
        
        print("\nRoles disponibles:")
        print("1. Usuario (Acceso básico)")
        print("2. Supervisor (Gestión proyectos + reportes)")
        print("3. Administrador (Gestión usuarios + proyectos)")
        print("4. Super Administrador (Acceso completo)")
        
        choice = int(input("\nSeleccione nuevo rol (1-4): "))
        
        role_map = {
            1: UserRole.USUARIO,
            2: UserRole.SUPERVISOR,
            3: UserRole.ADMIN,
            4: UserRole.SUPERADMIN
        }
        
        if choice not in role_map:
            print("❌ Opción inválida")
            return
        
        old_role = user.rol.display_name
        user.rol = role_map[choice]
        db.session.commit()
        
        print(f"✅ Rol cambiado exitosamente:")
        print(f"   {old_role} → {user.rol.display_name}")
        
    except ValueError:
        print("❌ Ingrese un número válido")
    except Exception as e:
        print(f"❌ Error: {e}")

def create_test_users():
    """Crear usuarios de prueba con diferentes roles"""
    print("\n👥 **CREAR USUARIOS DE PRUEBA**")
    print("=" * 40)
    
    test_users = [
        ("usuario@test.com", "usuario123", UserRole.USUARIO, "Juan Usuario"),
        ("supervisor@test.com", "super123", UserRole.SUPERVISOR, "María Supervisora"),
        ("admin2@test.com", "admin123", UserRole.ADMIN, "Carlos Admin"),
    ]
    
    for email, password, role, nombre in test_users:
        # Verificar si ya existe
        existing = Trabajador.query.filter_by(email=email).first()
        if existing:
            print(f"⚠️  Ya existe: {email}")
            continue
        
        # Crear usuario
        trabajador = Trabajador(
            email=email,
            nombre=nombre,
            profesion="Test",
            telefono="123456789",
            rol=role,
            activo=True
        )
        trabajador.set_password(password)
        
        db.session.add(trabajador)
        print(f"✅ Creado: {email} ({role.display_name})")
    
    db.session.commit()
    print("\n✅ Usuarios de prueba creados exitosamente")

def show_permissions_by_role():
    """Mostrar permisos por rol"""
    print("\n🔐 **PERMISOS POR ROL**")
    print("=" * 50)
    
    # Crear un usuario temporal para cada rol para mostrar permisos
    temp_user = Trabajador(
        email="temp@test.com",
        nombre="Temp User",
        profesion="Test",
        telefono="000000000",
        activo=True
    )
    
    roles = [UserRole.USUARIO, UserRole.SUPERVISOR, UserRole.ADMIN, UserRole.SUPERADMIN]
    
    for role in roles:
        temp_user.rol = role
        print(f"\n🎯 **{role.display_name.upper()}**")
        print(f"   • Gestionar Usuarios: {'✅' if temp_user.can_manage_users() else '❌'}")
        print(f"   • Gestionar Proyectos: {'✅' if temp_user.can_manage_projects() else '❌'}")
        print(f"   • Ver Reportes: {'✅' if temp_user.can_view_reports() else '❌'}")
        print(f"   • Modificar Sistema: {'✅' if temp_user.can_modify_system() else '❌'}")

def main():
    """Menú principal"""
    app = create_app()
    with app.app_context():
        while True:
            print("\n" + "="*60)
            print("🛡️  **GESTIÓN DE PERMISOS Y ROLES**")
            print("="*60)
            print("1. 👀 Ver todos los usuarios")
            print("2. 🔧 Cambiar rol de usuario")
            print("3. 👥 Crear usuarios de prueba")
            print("4. 🔐 Ver permisos por rol")
            print("5. 🚪 Salir")
            
            choice = input("\nSeleccione opción (1-5): ")
            
            if choice == '1':
                show_all_users()
            elif choice == '2':
                change_user_role()
            elif choice == '3':
                create_test_users()
            elif choice == '4':
                show_permissions_by_role()
            elif choice == '5':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
            
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
