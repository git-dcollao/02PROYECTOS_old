#!/usr/bin/env python3
"""
Script para verificar y corregir la estructura de la tabla trabajador
"""

import sys
import os
from sqlalchemy import text

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def main():
    print("🔍 Verificando estructura de la tabla trabajador")
    
    # Crear la aplicación
    app = create_app()
    
    with app.app_context():
        check_table_structure()
        fix_table_structure()
    
    return 0

def check_table_structure():
    """Verificar la estructura actual de la tabla trabajador"""
    print("\n📋 Estructura actual de la tabla trabajador:")
    
    try:
        result = db.session.execute(text("DESCRIBE trabajador")).fetchall()
        
        for row in result:
            field, type_info, null, key, default, extra = row
            print(f"   • {field}: {type_info} (NULL: {null}, Key: {key}, Default: {default})")
            
            # Verificar específicamente la columna rol
            if field == 'rol':
                if null == 'NO':
                    print(f"   ⚠️ PROBLEMA: La columna 'rol' no permite NULL")
                    return False
                else:
                    print(f"   ✅ La columna 'rol' permite NULL")
                    return True
                    
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False
    
    return True

def fix_table_structure():
    """Corregir la estructura de la tabla para permitir NULL en rol"""
    print("\n🔧 Corrigiendo estructura de la tabla trabajador...")
    
    try:
        # Modificar la columna rol para permitir NULL
        alter_query = """
        ALTER TABLE trabajador 
        MODIFY COLUMN rol ENUM('SUPERADMIN') NULL
        """
        
        db.session.execute(text(alter_query))
        db.session.commit()
        
        print("✅ Columna 'rol' modificada para permitir NULL")
        
        # Verificar el cambio
        print("\n📋 Verificando cambio:")
        check_table_structure()
        
        return True
        
    except Exception as e:
        print(f"❌ Error modificando estructura: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return False

if __name__ == "__main__":
    exit(main())
