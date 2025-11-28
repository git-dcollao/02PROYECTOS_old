#!/usr/bin/env python3
"""
Migración SQL para soportar roles personalizados en el sistema de permisos
"""

from app import create_app, db
from sqlalchemy import text
import traceback

def migrate_permissions_sql():
    """Migrar la estructura de permisos usando SQL directo"""
    print("🔄 Iniciando migración SQL de permisos para roles personalizados...")
    
    app = create_app()
    with app.app_context():
        try:
            # 1. Verificar estructura actual con SQL directo
            print("\n📊 Verificando estructura actual...")
            
            result = db.session.execute(text("SELECT COUNT(*) as count FROM page_permissions")).fetchone()
            current_permissions = result.count if result else 0
            print(f"   Permisos existentes: {current_permissions}")
            
            # 2. Verificar si las columnas ya existen
            print("\n🔍 Verificando estructura de tabla...")
            
            columns_result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'page_permissions'
            """)).fetchall()
            
            existing_columns = [row.COLUMN_NAME for row in columns_result]
            print(f"   Columnas existentes: {existing_columns}")
            
            needs_migration = False
            
            # 3. Agregar las nuevas columnas si no existen
            print("\n🏗️  Modificando estructura de tabla...")
            
            if 'custom_role_id' not in existing_columns:
                print("   ➕ Agregando columna custom_role_id...")
                db.session.execute(text('ALTER TABLE page_permissions ADD COLUMN custom_role_id INTEGER NULL'))
                needs_migration = True
            else:
                print("   ✅ Columna custom_role_id ya existe")
            
            if 'role_name' not in existing_columns:
                print("   ➕ Agregando columna role_name...")
                db.session.execute(text('ALTER TABLE page_permissions ADD COLUMN role_name VARCHAR(50) NOT NULL DEFAULT ""'))
                needs_migration = True
            else:
                print("   ✅ Columna role_name ya existe")
            
            # 4. Renombrar la columna role a system_role si es necesario
            if 'role' in existing_columns and 'system_role' not in existing_columns:
                print("   🔄 Renombrando columna role a system_role...")
                db.session.execute(text('ALTER TABLE page_permissions CHANGE COLUMN role system_role ENUM("superadmin", "admin", "supervisor", "usuario") NULL'))
                needs_migration = True
            elif 'system_role' in existing_columns:
                print("   ✅ Columna system_role ya existe")
            elif 'role' not in existing_columns:
                print("   ➕ Agregando columna system_role...")
                db.session.execute(text('ALTER TABLE page_permissions ADD COLUMN system_role ENUM("superadmin", "admin", "supervisor", "usuario") NULL'))
                needs_migration = True
            
            if needs_migration:
                # 5. Migrar datos existentes
                print("\n📋 Migrando datos existentes...")
                
                # Actualizar role_name para permisos existentes donde esté vacío
                result = db.session.execute(text("""
                    UPDATE page_permissions 
                    SET role_name = UPPER(system_role)
                    WHERE (role_name IS NULL OR role_name = '') AND system_role IS NOT NULL
                """))
                
                updated_rows = result.rowcount if hasattr(result, 'rowcount') else 0
                print(f"   ✅ Actualizados {updated_rows} permisos existentes")
                
                # 6. Agregar foreign key constraint para custom_role_id si no existe
                print("   🔗 Verificando foreign key constraints...")
                
                fk_result = db.session.execute(text("""
                    SELECT CONSTRAINT_NAME 
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'page_permissions' 
                    AND COLUMN_NAME = 'custom_role_id'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """)).fetchall()
                
                if not fk_result:
                    print("   ➕ Agregando foreign key constraint...")
                    db.session.execute(text("""
                        ALTER TABLE page_permissions 
                        ADD CONSTRAINT fk_page_permissions_custom_role 
                        FOREIGN KEY (custom_role_id) REFERENCES custom_roles(id) ON DELETE CASCADE
                    """))
                else:
                    print("   ✅ Foreign key constraint ya existe")
                
                # 7. Actualizar constraint unique
                print("   🔧 Actualizando constraints únicos...")
                
                # Eliminar constraint único anterior si existe
                try:
                    db.session.execute(text('ALTER TABLE page_permissions DROP INDEX uq_page_permission'))
                    print("   ✅ Eliminado constraint único anterior")
                except Exception as e:
                    print(f"   ℹ️ Constraint anterior no existía o ya fue eliminado: {e}")
                
                # Agregar nuevo constraint único
                try:
                    db.session.execute(text("""
                        ALTER TABLE page_permissions 
                        ADD CONSTRAINT uq_page_permission_name 
                        UNIQUE (page_id, role_name)
                    """))
                    print("   ✅ Agregado nuevo constraint único")
                except Exception as e:
                    print(f"   ⚠️ Error al agregar constraint único: {e}")
                
                # 8. Agregar check constraint (MySQL puede no soportarlo completamente, pero intentamos)
                try:
                    # Para MySQL, usamos un enfoque diferente con triggers o validación en la aplicación
                    print("   ℹ️ Check constraint se manejará en la aplicación (MySQL limitado)")
                except Exception as e:
                    print(f"   ℹ️ Check constraint no agregado: {e}")
            
            db.session.commit()
            print("\n✅ Migración SQL completada exitosamente!")
            
            # 9. Verificar resultado
            print("\n📊 Verificando resultado...")
            
            # Contar permisos nuevamente
            result = db.session.execute(text("SELECT COUNT(*) as count FROM page_permissions")).fetchone()
            final_permissions = result.count if result else 0
            
            # Contar roles personalizados
            result = db.session.execute(text("SELECT COUNT(*) as count FROM custom_roles WHERE active = 1")).fetchone()
            custom_roles = result.count if result else 0
            
            print(f"   Permisos totales: {final_permissions}")
            print(f"   Roles personalizados activos: {custom_roles}")
            
            # Mostrar estructura final
            columns_result = db.session.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'page_permissions'
                ORDER BY ORDINAL_POSITION
            """)).fetchall()
            
            print("\n📋 Estructura final de page_permissions:")
            for col in columns_result:
                nullable = "NULL" if col.IS_NULLABLE == "YES" else "NOT NULL"
                print(f"   - {col.COLUMN_NAME} ({col.DATA_TYPE}) {nullable}")
            
            # Mostrar algunos ejemplos de datos
            print("\n📋 Ejemplos de permisos:")
            sample_result = db.session.execute(text("""
                SELECT pp.role_name, p.route, pp.system_role, pp.custom_role_id
                FROM page_permissions pp
                JOIN pages p ON pp.page_id = p.id
                LIMIT 5
            """)).fetchall()
            
            for perm in sample_result:
                role_type = "Sistema" if perm.system_role else "Personalizado"
                print(f"   - {perm.route}: {perm.role_name} ({role_type})")
            
            return True
            
        except Exception as e:
            print(f"\n💥 Error durante la migración: {e}")
            db.session.rollback()
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = migrate_permissions_sql()
    if success:
        print("\n🎉 ¡Migración SQL completada con éxito!")
        print("   Los roles personalizados ahora pueden usarse en el sistema de permisos.")
        print("   ⚠️ IMPORTANTE: Reinicia la aplicación para usar la nueva estructura.")
    else:
        print("\n❌ La migración SQL falló. Revisa los errores arriba.")
        exit(1)
