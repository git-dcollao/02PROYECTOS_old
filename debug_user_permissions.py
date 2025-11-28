#!/usr/bin/env python3
"""
Script para diagnosticar y corregir permisos de usuario para crear trabajadores
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Trabajador, Sector, Recinto, TipoRecinto, CustomRole, UserRole
from flask_login import login_user

def diagnosticar_usuario():
    """Diagnosticar el estado del usuario actual y sus permisos"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DIAGNÓSTICO DE PERMISOS DE USUARIO")
        print("=" * 50)
        
        # Obtener todos los usuarios con email (potenciales usuarios de login)
        usuarios_con_email = Trabajador.query.filter(Trabajador.email.isnot(None)).all()
        
        print(f"\n📋 USUARIOS CON CREDENCIALES DE ACCESO:")
        print("-" * 40)
        
        for i, user in enumerate(usuarios_con_email, 1):
            print(f"\n{i}. Usuario: {user.nombre}")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            
            # Verificar rol
            if user.rol:
                print(f"   Rol Sistema: {user.rol.name} ({user.rol.display_name})")
                is_superadmin = user.rol.name == 'SUPERADMIN'
            else:
                is_superadmin = False
                print(f"   Rol Sistema: Ninguno")
            
            # Verificar rol personalizado
            if user.custom_role:
                print(f"   Rol Personalizado: {user.custom_role.name}")
                is_administrador = user.custom_role.name.upper() == 'ADMINISTRADOR'
            else:
                is_administrador = False
                print(f"   Rol Personalizado: Ninguno")
            
            # Verificar sector y recinto
            print(f"   Sector: {user.sector.nombre if user.sector else 'NO ASIGNADO'}")
            print(f"   Recinto: {user.recinto.nombre if user.recinto else 'NO ASIGNADO'}")
            
            # Determinar permisos
            print(f"\n   📊 ANÁLISIS DE PERMISOS:")
            if is_superadmin:
                print(f"   ✅ SUPERADMIN - Puede crear trabajadores en cualquier lugar")
            elif is_administrador and user.recinto_id:
                print(f"   ✅ ADMINISTRADOR con recinto - Puede crear trabajadores")
            elif user.recinto_id:
                print(f"   ✅ Usuario con recinto - Puede crear trabajadores en su recinto")
            else:
                print(f"   ❌ SIN PERMISOS - No tiene recinto asignado")
                print(f"   💡 SOLUCIÓN: Asignar recinto o convertir en SUPERADMIN")
        
        return usuarios_con_email

def corregir_permisos():
    """Permite seleccionar un usuario y corregir sus permisos"""
    app = create_app()
    
    with app.app_context():
        usuarios = diagnosticar_usuario()
        
        print(f"\n🛠️ CORRECCIÓN DE PERMISOS")
        print("=" * 30)
        
        try:
            user_choice = int(input("\n¿Qué usuario quieres corregir? (número): ")) - 1
            
            if 0 <= user_choice < len(usuarios):
                usuario = usuarios[user_choice]
                print(f"\n👤 Trabajando con: {usuario.nombre} ({usuario.email})")
                
                print(f"\nOpciones de corrección:")
                print(f"1. Convertir en SUPERADMIN (acceso total)")
                print(f"2. Asignar recinto existente")
                print(f"3. Mostrar recintos disponibles")
                print(f"4. Crear nuevo recinto y asignar")
                
                opcion = input("\nSelecciona opción (1-4): ")
                
                if opcion == "1":
                    # Convertir en SUPERADMIN
                    from app.models import UserRole
                    
                    # Verificar si ya existe el rol SUPERADMIN
                    superadmin_role = UserRole.query.filter_by(name='SUPERADMIN').first()
                    if not superadmin_role:
                        superadmin_role = UserRole(
                            name='SUPERADMIN',
                            display_name='Super Administrador'
                        )
                        from app import db
                        db.session.add(superadmin_role)
                        db.session.commit()
                        print("✅ Rol SUPERADMIN creado")
                    
                    usuario.rol = superadmin_role
                    from app import db
                    db.session.commit()
                    print(f"✅ {usuario.nombre} ahora es SUPERADMIN")
                
                elif opcion == "2":
                    # Mostrar recintos y asignar
                    recintos = Recinto.query.all()
                    if recintos:
                        print(f"\n📍 RECINTOS DISPONIBLES:")
                        for i, recinto in enumerate(recintos, 1):
                            sector = recinto.tiporecinto.sector.nombre if recinto.tiporecinto and recinto.tiporecinto.sector else "Sin sector"
                            print(f"{i}. {recinto.nombre} (Sector: {sector})")
                        
                        try:
                            recinto_choice = int(input("Selecciona recinto (número): ")) - 1
                            if 0 <= recinto_choice < len(recintos):
                                recinto_seleccionado = recintos[recinto_choice]
                                usuario.recinto_id = recinto_seleccionado.id
                                
                                # También asignar el sector correspondiente
                                if recinto_seleccionado.tiporecinto:
                                    usuario.sector_id = recinto_seleccionado.tiporecinto.id_sector
                                
                                from app import db
                                db.session.commit()
                                print(f"✅ {usuario.nombre} asignado al recinto: {recinto_seleccionado.nombre}")
                            else:
                                print("❌ Selección inválida")
                        except ValueError:
                            print("❌ Entrada inválida")
                    else:
                        print("❌ No hay recintos disponibles")
                
                elif opcion == "3":
                    # Solo mostrar recintos
                    recintos = Recinto.query.all()
                    if recintos:
                        print(f"\n📍 RECINTOS DISPONIBLES:")
                        for recinto in recintos:
                            sector = recinto.tiporecinto.sector.nombre if recinto.tiporecinto and recinto.tiporecinto.sector else "Sin sector"
                            tipo = recinto.tiporecinto.nombre if recinto.tiporecinto else "Sin tipo"
                            print(f"• {recinto.nombre} (Tipo: {tipo}, Sector: {sector})")
                    else:
                        print("❌ No hay recintos disponibles")
                
                elif opcion == "4":
                    print("⚠️ Crear recinto requiere configuración adicional de sectores y tipos")
                    print("💡 Recomendación: Usar opción 1 (SUPERADMIN) para acceso inmediato")
                
            else:
                print("❌ Selección inválida")
                
        except ValueError:
            print("❌ Entrada inválida")
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada")

if __name__ == "__main__":
    print("🏥 SISTEMA DE GESTIÓN DE PERMISOS")
    print("=" * 40)
    
    try:
        corregir_permisos()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()