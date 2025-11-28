#!/usr/bin/env python3
"""
Migración para soportar roles personalizados en el sistema de permisos
"""

from app import create_app, db
from app.models import PagePermission, UserRole, CustomRole, Page
from sqlalchemy import text
import traceback

def migrate_permissions():
    """Migrar la estructura de permisos para soportar roles personalizados"""
    print("🔄 Iniciando migración de permisos para roles personalizados...")
    
    app = create_app()
    with app.app_context():
        try:
            # 1. Verificar estructura actual
            print("\n📊 Verificando estructura actual...")
            current_permissions = PagePermission.query.count()
            print(f"   Permisos existentes: {current_permissions}")
            
            # 2. Agregar las nuevas columnas si no existen
            print("\n🏗️  Modificando estructura de tabla...")
            
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('page_permissions')]
            
            needs_migration = False
            
            if 'custom_role_id' not in columns:
                print("   Agregando columna custom_role_id...")
                db.engine.execute(text('ALTER TABLE page_permissions ADD COLUMN custom_role_id INTEGER'))
                needs_migration = True
            
            if 'role_name' not in columns:
                print("   Agregando columna role_name...")
                db.engine.execute(text('ALTER TABLE page_permissions ADD COLUMN role_name VARCHAR(50)'))
                needs_migration = True
            
            # 3. Renombrar la columna role a system_role si es necesario
            if 'role' in columns and 'system_role' not in columns:
                print("   Renombrando columna role a system_role...")
                db.engine.execute(text('ALTER TABLE page_permissions CHANGE COLUMN role system_role ENUM("superadmin", "admin", "supervisor", "usuario")'))
                needs_migration = True
            
            if needs_migration:
                # 4. Migrar datos existentes
                print("\n📋 Migrando datos existentes...")
                
                # Actualizar role_name para permisos existentes
                existing_permissions = db.session.execute(text("""
                    SELECT id, system_role FROM page_permissions 
                    WHERE role_name IS NULL OR role_name = ''
                """)).fetchall()
                
                for perm in existing_permissions:
                    role_name = perm.system_role.upper() if perm.system_role else 'UNKNOWN'
                    db.session.execute(text("""
                        UPDATE page_permissions 
                        SET role_name = :role_name 
                        WHERE id = :id
                    """), {"role_name": role_name, "id": perm.id})
                
                print(f"   ✅ Actualizados {len(existing_permissions)} permisos existentes")
            
            # 5. Agregar foreign key constraint para custom_role_id
            if 'custom_role_id' not in [fk['constrained_columns'][0] for fk in inspector.get_foreign_keys('page_permissions')]:
                print("   Agregando constraint de foreign key...")
                db.engine.execute(text("""
                    ALTER TABLE page_permissions 
                    ADD CONSTRAINT fk_page_permissions_custom_role 
                    FOREIGN KEY (custom_role_id) REFERENCES custom_roles(id)
                """))
            
            # 6. Actualizar constraint unique
            try:
                db.engine.execute(text('ALTER TABLE page_permissions DROP INDEX uq_page_permission'))
                print("   Eliminando constraint único anterior...")
            except:
                pass  # Puede que no exista
            
            try:
                db.engine.execute(text("""
                    ALTER TABLE page_permissions 
                    ADD CONSTRAINT uq_page_permission_name 
                    UNIQUE (page_id, role_name)
                """))
                print("   Agregando nuevo constraint único...")
            except Exception as e:
                print(f"   ⚠️ Error al agregar constraint: {e}")
            
            # 7. Agregar check constraint
            try:
                db.engine.execute(text("""
                    ALTER TABLE page_permissions 
                    ADD CONSTRAINT ck_permission_role_type 
                    CHECK ((system_role IS NOT NULL AND custom_role_id IS NULL) OR 
                           (system_role IS NULL AND custom_role_id IS NOT NULL))
                """))
                print("   Agregando constraint de validación...")
            except Exception as e:
                print(f"   ⚠️ Error al agregar check constraint: {e}")
            
            db.session.commit()
            print("\n✅ Migración completada exitosamente!")
            
            # 8. Verificar resultado
            print("\n📊 Verificando resultado...")
            final_permissions = PagePermission.query.count()
            custom_roles = CustomRole.query.filter_by(active=True).count()
            
            print(f"   Permisos totales: {final_permissions}")
            print(f"   Roles personalizados activos: {custom_roles}")
            
            # Mostrar algunos ejemplos
            print("\n📋 Ejemplos de permisos:")
            sample_permissions = PagePermission.query.limit(5).all()
            for perm in sample_permissions:
                role_type = "Sistema" if perm.system_role else "Personalizado"
                print(f"   - {perm.page.route}: {perm.role_name} ({role_type})")
            
            return True
            
        except Exception as e:
            print(f"\n💥 Error durante la migración: {e}")
            db.session.rollback()
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = migrate_permissions()
    if success:
        print("\n🎉 ¡Migración completada con éxito!")
        print("   Los roles personalizados ahora pueden usarse en el sistema de permisos.")
    else:
        print("\n❌ La migración falló. Revisa los errores arriba.")
        exit(1)
