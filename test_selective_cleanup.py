#!/usr/bin/env python3
"""
🧪 TEST: Limpieza Selectiva de Tabla Trabajador
============================================

Script para validar que la limpieza selectiva funciona correctamente
preservando usuarios SUPERADMIN y usuario actual.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_selective_cleanup_logic():
    """Test de la lógica de limpieza selectiva"""
    print("🧪 TEST: Limpieza Selectiva de Tabla Trabajador")
    print("=" * 50)
    
    try:
        from app.models import Trabajador
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Obtener usuarios actuales
            users = Trabajador.query.all()
            
            print(f"👥 Total usuarios en sistema: {len(users)}")
            print("")
            
            print("📋 Lista de usuarios:")
            for i, user in enumerate(users, 1):
                role_info = f"Rol: {user.role}" if hasattr(user, 'role') else "Sin rol"
                print(f"   {i:2d}. {user.email:25} | {role_info}")
            
            print("")
            
            # Simular qué usuarios se preservarían
            superadmin_users = [u for u in users if hasattr(u, 'role') and u.role == 'SUPERADMIN']
            current_user_email = 'admin@sistema.local'  # Usuario de prueba
            
            preserved_users = []
            deleted_users = []
            
            for user in users:
                preserve = False
                
                # Preservar SUPERADMIN
                if hasattr(user, 'role') and user.role == 'SUPERADMIN':
                    preserved_users.append((user, 'SUPERADMIN'))
                    preserve = True
                
                # Preservar usuario actual
                elif user.email == current_user_email:
                    preserved_users.append((user, 'Usuario Actual'))
                    preserve = True
                
                if not preserve:
                    deleted_users.append(user)
            
            print("✅ RESULTADOS DE LIMPIEZA SELECTIVA:")
            print("")
            print(f"🛡️  PRESERVADOS ({len(preserved_users)}):")
            for user, reason in preserved_users:
                print(f"   • {user.email:25} | Razón: {reason}")
            
            print("")
            print(f"🗑️  SE ELIMINARÍAN ({len(deleted_users)}):")
            for user in deleted_users:
                role_info = f"Rol: {user.role}" if hasattr(user, 'role') else "Sin rol definido"
                print(f"   • {user.email:25} | {role_info}")
            
            print("")
            print("📊 RESUMEN:")
            print(f"   • Total usuarios: {len(users)}")
            print(f"   • Preservados: {len(preserved_users)}")
            print(f"   • A eliminar: {len(deleted_users)}")
            print(f"   • % Preservado: {(len(preserved_users)/len(users)*100):.1f}%")
            
            # Verificaciones de seguridad
            print("")
            print("🔍 VERIFICACIONES DE SEGURIDAD:")
            
            # ¿Hay al menos un SUPERADMIN preservado?
            superadmin_preserved = any(reason == 'SUPERADMIN' for _, reason in preserved_users)
            print(f"   ✅ SUPERADMIN preservado: {'SÍ' if superadmin_preserved else '❌ NO'}")
            
            # ¿Se preserva acceso al sistema?
            access_preserved = len(preserved_users) > 0
            print(f"   ✅ Acceso al sistema: {'SÍ' if access_preserved else '❌ NO'}")
            
            # ¿No se eliminan todos los usuarios?
            safe_operation = len(deleted_users) < len(users)
            print(f"   ✅ Operación segura: {'SÍ' if safe_operation else '❌ NO'}")
            
            # SQL que se ejecutaría
            print("")
            print("🔧 SQL QUE SE EJECUTARÍA:")
            preserve_conditions = []
            
            if superadmin_users:
                preserve_conditions.append("role = 'SUPERADMIN'")
            
            preserve_conditions.append(f"email = '{current_user_email}'")
            
            where_clause = " AND ".join([f"NOT ({cond})" for cond in preserve_conditions])
            sql = f"DELETE FROM trabajador WHERE {where_clause}"
            
            print(f"   {sql}")
            
            print("")
            if superadmin_preserved and access_preserved and safe_operation:
                print("🎉 ¡LIMPIEZA SELECTIVA ES SEGURA!")
            else:
                print("⚠️ ADVERTENCIA: Revisar lógica de preservación")
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_selective_cleanup_logic()