#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir privilegios de administrador
Asigna el rol correcto al usuario administrador@sistema.local
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Trabajador, CustomRole
from sqlalchemy import text

def verificar_y_corregir_admin():
    """Verificar y corregir el rol del administrador"""
    
    print("🔍 VERIFICANDO USUARIO ADMINISTRADOR...")
    print("=" * 60)
    
    # Buscar el usuario administrador@sistema.local
    admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
    
    if not admin_user:
        print("❌ Usuario 'administrador@sistema.local' no encontrado")
        return False
    
    print(f"👤 Usuario encontrado:")
    print(f"   ID: {admin_user.id}")
    print(f"   Nombre: {admin_user.nombre}")
    print(f"   Email: {admin_user.email}")
    print(f"   Rol actual: {admin_user.rol.name if admin_user.rol else 'Sin rol'}")
    print(f"   Es admin: {admin_user.is_admin}")
    print(f"   Activo: {admin_user.activo}")
    
    # Verificar roles disponibles
    print("\n🎭 ROLES DISPONIBLES:")
    roles = CustomRole.query.all()
    for role in roles:
        print(f"   - {role.name}: {role.descripcion}")
    
    # Buscar el rol ADMINISTRADOR
    admin_role = CustomRole.query.filter_by(name='ADMINISTRADOR').first()
    
    if not admin_role:
        print("\n❌ Rol ADMINISTRADOR no encontrado, creando...")
        admin_role = CustomRole(
            name='ADMINISTRADOR',
            descripcion='Administrador del sistema con permisos de gestión'
        )
        db.session.add(admin_role)
        db.session.flush()
        print(f"✅ Rol ADMINISTRADOR creado con ID: {admin_role.id}")
    
    # Asignar el rol correcto al usuario
    print(f"\n🔧 CORRIGIENDO PERMISOS...")
    
    # Actualizar el rol
    admin_user.rol = admin_role
    admin_user.is_admin = True
    admin_user.activo = True
    
    try:
        db.session.commit()
        print("✅ Permisos actualizados correctamente")
        
        # Verificar cambios
        admin_user = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        print(f"\n🎯 ESTADO FINAL:")
        print(f"   Nombre: {admin_user.nombre}")
        print(f"   Email: {admin_user.email}")
        print(f"   Rol: {admin_user.rol.name}")
        print(f"   Es admin: {admin_user.is_admin}")
        print(f"   Activo: {admin_user.activo}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al actualizar permisos: {e}")
        return False

def listar_todos_los_usuarios():
    """Listar todos los usuarios del sistema con sus roles"""
    
    print("\n" + "=" * 60)
    print("📋 TODOS LOS USUARIOS DEL SISTEMA")
    print("=" * 60)
    
    usuarios = Trabajador.query.all()
    
    print(f"{'ID':<5} {'Nombre':<25} {'Email':<30} {'Rol':<15} {'Admin':<7}")
    print("-" * 85)
    
    for user in usuarios:
        rol_name = user.rol.name if user.rol else 'Sin rol'
        is_admin = 'Sí' if user.is_admin else 'No'
        
        print(f"{user.id:<5} {user.nombre[:24]:<25} {user.email[:29]:<30} {rol_name:<15} {is_admin:<7}")

def crear_admin_adicional():
    """Crear un usuario administrador adicional"""
    
    print("\n" + "=" * 60)
    print("➕ CREANDO ADMINISTRADOR ADICIONAL")
    print("=" * 60)
    
    # Verificar si ya existe
    existing_admin = Trabajador.query.filter_by(email='admin@maho.cl').first()
    if existing_admin:
        print("⚠️ Ya existe un usuario admin@maho.cl")
        return existing_admin
    
    # Buscar rol ADMINISTRADOR
    admin_role = CustomRole.query.filter_by(name='ADMINISTRADOR').first()
    if not admin_role:
        print("❌ Rol ADMINISTRADOR no encontrado")
        return None
    
    # Crear nuevo administrador
    nuevo_admin = Trabajador(
        nombre='Administrador Maho',
        email='admin@maho.cl',
        password='admin123',  # Se hasheará automáticamente
        rol=admin_role,
        is_admin=True,
        activo=True,
        profesion='Administrador Sistema'
    )
    
    try:
        db.session.add(nuevo_admin)
        db.session.commit()
        
        print(f"✅ Nuevo administrador creado:")
        print(f"   Email: admin@maho.cl")
        print(f"   Contraseña: admin123")
        print(f"   Rol: {admin_role.name}")
        
        return nuevo_admin
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando administrador: {e}")
        return None

def main():
    """Función principal"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 SCRIPT DE CORRECCIÓN DE PRIVILEGIOS ADMINISTRATIVOS")
        print("=" * 60)
        
        try:
            # Verificar conexión a BD
            db.session.execute(text('SELECT 1'))
            print("✅ Conexión a base de datos OK")
            
            # Corregir el administrador principal
            success = verificar_y_corregir_admin()
            
            # Listar todos los usuarios
            listar_todos_los_usuarios()
            
            # Crear administrador adicional si se necesita
            print(f"\n{'='*60}")
            respuesta = input("¿Desea crear un administrador adicional? (s/n): ").lower().strip()
            if respuesta == 's':
                crear_admin_adicional()
            
            if success:
                print(f"\n🎉 CORRECCIÓN COMPLETADA")
                print(f"✅ El usuario 'administrador@sistema.local' ahora tiene permisos de ADMINISTRADOR")
                print(f"🔑 Puede iniciar sesión y ver el menú correspondiente")
            else:
                print(f"\n❌ Hubo problemas en la corrección")
                
        except Exception as e:
            print(f"❌ Error general: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()