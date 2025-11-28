#!/usr/bin/env python3
"""
Script para corregir los nombres de roles personalizados en la base de datos
"""

import sys
import os
from sqlalchemy import text

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import CustomRole

def main():
    print("🔧 Corrigiendo nombres de roles personalizados")
    
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        if fix_role_names():
            print("\n✅ Nombres de roles corregidos exitosamente.")
        else:
            print("\n❌ Falló la corrección de nombres de roles.")
            return 1
    
    return 0

def fix_role_names():
    """Corregir nombres de roles personalizados"""
    print("\n🔄 Verificando y corrigiendo nombres de roles...")
    
    try:
        # Mapeo de nombres incorrectos a nombres correctos
        role_mapping = {
            'ADMINISTRADOR': 'ADMIN',
            'CONTROL': 'ADMIN_AREA'
            # USUARIO y SOLICITANTE ya están correctos
        }
        
        # Mostrar roles actuales
        current_roles = CustomRole.query.filter_by(active=True).all()
        print(f"📋 Roles actuales:")
        for role in current_roles:
            print(f"   • {role.name}: {role.description}")
        
        # Aplicar correcciones
        corrected_count = 0
        for old_name, new_name in role_mapping.items():
            role = CustomRole.query.filter_by(name=old_name, active=True).first()
            if role:
                print(f"🔄 Cambiando '{old_name}' → '{new_name}'")
                role.name = new_name
                corrected_count += 1
            else:
                print(f"⚠️ Rol '{old_name}' no encontrado")
        
        if corrected_count > 0:
            db.session.commit()
            print(f"✅ {corrected_count} roles corregidos")
        else:
            print("ℹ️ No se requieren correcciones")
        
        # Mostrar roles finales
        print(f"\n📋 Roles finales:")
        final_roles = CustomRole.query.filter_by(active=True).all()
        for role in final_roles:
            print(f"   • {role.name}: {role.description}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error corrigiendo nombres de roles: {e}")
        return False

if __name__ == "__main__":
    exit(main())
