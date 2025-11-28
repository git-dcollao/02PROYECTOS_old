#!/usr/bin/env python3
"""
Script para corregir el enum UserRole en la base de datos
"""

from app import create_app, db
from sqlalchemy import text

def fix_enum_values():
    """Corregir valores del enum de minúscula a mayúscula"""
    
    app = create_app()
    with app.app_context():
        print('🔧 Corrigiendo enum de roles en la base de datos...')
        
        try:
            # Paso 1: Cambiar la columna temporalmente a VARCHAR
            print('   1. Convirtiendo enum a varchar temporalmente...')
            db.session.execute(text('ALTER TABLE page_permissions MODIFY COLUMN system_role VARCHAR(20)'))
            
            # Paso 2: Actualizar los valores a mayúsculas
            print('   2. Actualizando valores a mayúsculas...')
            db.session.execute(text('UPDATE page_permissions SET system_role = UPPER(system_role) WHERE system_role IS NOT NULL'))
            
            # Paso 3: Cambiar de vuelta a enum con valores en mayúsculas
            print('   3. Recreando enum con valores correctos...')
            sql_alter = "ALTER TABLE page_permissions MODIFY COLUMN system_role ENUM('SUPERADMIN','ADMIN','SUPERVISOR','USUARIO') NULL"
            db.session.execute(text(sql_alter))
            
            db.session.commit()
            print('✅ Enum corregido exitosamente')
            
            # Verificar los cambios
            result = db.session.execute(text('''
                SELECT system_role, COUNT(*) as count
                FROM page_permissions 
                WHERE system_role IS NOT NULL
                GROUP BY system_role
            ''')).fetchall()
            
            print('\n📋 Valores corregidos:')
            for row in result:
                print(f'   - {row.system_role}: {row.count} permisos')
            
            # Verificar la nueva definición del enum
            enum_info = db.session.execute(text('''
                SELECT COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'page_permissions' 
                AND COLUMN_NAME = 'system_role'
                AND TABLE_SCHEMA = DATABASE()
            ''')).fetchone()
            
            print(f'\n🔍 Nueva definición del enum: {enum_info.COLUMN_TYPE}')
            return True
            
        except Exception as e:
            print(f'❌ Error: {e}')
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = fix_enum_values()
    if success:
        print('\n🎉 ¡Corrección completada! Ahora la página debería cargar sin errores.')
    else:
        print('\n❌ La corrección falló. Revisa los errores.')
        exit(1)
