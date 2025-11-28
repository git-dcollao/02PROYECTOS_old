#!/usr/bin/env python3
"""
Script Rápido de Gestión de Usuarios
Uso: python quick_user_admin.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, UserRole

def show_users():
    """Mostrar usuarios actuales"""
    print("\n" + "="*60)
    print("👥 **USUARIOS DEL SISTEMA**")
    print("="*60)
    
    trabajadores = Trabajador.query.filter_by(activo=True).all()
    
    if not trabajadores:
        print("❌ No hay usuarios activos")
        return
    
    print(f"{'ID':>3} | {'EMAIL':20} | {'NOMBRE':20} | {'ROL':15}")
    print("-" * 63)
    
    for t in trabajadores:
        print(f"{t.id:>3} | {t.email:20} | {t.nombre[:20]:20} | {t.rol.display_name:15}")

def quick_role_change():
    """Cambio rápido de rol"""
    print("\n🔧 **CAMBIO RÁPIDO DE ROL**")
    print("="*40)
    
    show_users()
    
    try:
        user_id = input("\n🆔 ID del usuario: ").strip()
        if not user_id:
            return
        
        user_id = int(user_id)
        user = Trabajador.query.get(user_id)
        
        if not user:
            print("❌ Usuario no encontrado")
            return
        
        print(f"\n📧 Usuario: {user.email}")
        print(f"📝 Nombre: {user.nombre}")
        print(f"👤 Rol actual: {user.rol.display_name}")
        
        print("\n🎯 Roles disponibles:")
        print("1️⃣  Usuario")
        print("2️⃣  Supervisor") 
        print("3️⃣  Administrador")
        print("4️⃣  Super Administrador")
        
        choice = input("\n🔢 Nuevo rol (1-4): ").strip()
        
        role_map = {
            '1': UserRole.USUARIO,
            '2': UserRole.SUPERVISOR,
            '3': UserRole.ADMIN,
            '4': UserRole.SUPERADMIN
        }
        
        if choice not in role_map:
            print("❌ Opción inválida")
            return
        
        old_role = user.rol.display_name
        user.rol = role_map[choice]
        db.session.commit()
        
        print(f"\n✅ **ROL ACTUALIZADO**")
        print(f"   {old_role} ➡️  {user.rol.display_name}")
        
    except ValueError:
        print("❌ Ingrese un número válido")
    except Exception as e:
        print(f"❌ Error: {e}")

def create_user():
    """Crear un nuevo usuario"""
    print("\n👤 **CREAR NUEVO USUARIO**")
    print("="*40)
    
    try:
        email = input("📧 Email: ").strip()
        if not email:
            print("❌ Email es requerido")
            return
        
        # Verificar si ya existe
        if Trabajador.query.filter_by(email=email).first():
            print("❌ El email ya existe")
            return
        
        nombre = input("📝 Nombre: ").strip()
        if not nombre:
            print("❌ Nombre es requerido")
            return
        
        password = input("🔒 Contraseña: ").strip()
        if not password:
            print("❌ Contraseña es requerida")
            return
        
        print("\n🎯 Seleccione rol:")
        print("1️⃣  Usuario")
        print("2️⃣  Supervisor") 
        print("3️⃣  Administrador")
        print("4️⃣  Super Administrador")
        
        choice = input("\n🔢 Rol (1-4): ").strip()
        
        role_map = {
            '1': UserRole.USUARIO,
            '2': UserRole.SUPERVISOR,
            '3': UserRole.ADMIN,
            '4': UserRole.SUPERADMIN
        }
        
        if choice not in role_map:
            print("❌ Opción inválida")
            return
        
        # Crear usuario
        trabajador = Trabajador(
            email=email,
            nombre=nombre,
            profesion="Usuario Sistema",
            telefono="000000000",
            rol=role_map[choice],
            activo=True
        )
        trabajador.set_password(password)
        
        db.session.add(trabajador)
        db.session.commit()
        
        print(f"\n✅ **USUARIO CREADO**")
        print(f"   📧 Email: {email}")
        print(f"   📝 Nombre: {nombre}")
        print(f"   👤 Rol: {role_map[choice].display_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Menú principal simplificado"""
    app = create_app()
    with app.app_context():
        while True:
            print("\n" + "="*50)
            print("⚡ **GESTIÓN RÁPIDA DE USUARIOS**")
            print("="*50)
            print("1️⃣  👀 Ver usuarios")
            print("2️⃣  🔧 Cambiar rol")
            print("3️⃣  👤 Crear usuario")
            print("4️⃣  🚪 Salir")
            
            choice = input("\n🔢 Opción (1-4): ").strip()
            
            if choice == '1':
                show_users()
            elif choice == '2':
                quick_role_change()
            elif choice == '3':
                create_user()
            elif choice == '4':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
            
            input("\n⏎ Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
