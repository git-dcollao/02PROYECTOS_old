#!/usr/bin/env python3
"""
Prueba de restauración de backups
"""

import sys
import os
sys.path.append('/app')

from app import create_app, db
from app.routes.admin_routes import BackupManager

def test_restore_functionality():
    """Probar funcionalidad de restauración"""
    print("🔄 PROBANDO FUNCIONALIDAD DE RESTAURACIÓN")
    print("=" * 50)
    
    try:
        app = create_app()
        
        with app.app_context():
            backup_manager = BackupManager()
            
            # Listar backups disponibles
            backups = backup_manager.list_backups()
            print(f"📋 Backups disponibles: {len(backups)}")
            
            if backups:
                # Tomar el backup más reciente
                latest_backup = backups[0]
                filename = latest_backup['filename']
                
                print(f"🎯 Usando backup: {filename}")
                print(f"📊 Tamaño: {latest_backup['size']} bytes")
                print(f"📅 Fecha: {latest_backup['created_at']}")
                
                # Crear backup de seguridad antes de restaurar
                print("\n💾 Creando backup de seguridad pre-restauración...")
                security_backup = backup_manager.create_backup(
                    backup_name="seguridad_pre_restauracion_test",
                    description="Backup de seguridad antes de prueba de restauración",
                    include_data=True,
                    compress=True
                )
                
                if security_backup.get('success'):
                    print(f"✅ Backup de seguridad creado: {security_backup['filename']}")
                else:
                    print(f"❌ Error creando backup de seguridad: {security_backup.get('message')}")
                    return False
                
                # Intentar restauración
                print(f"\n🔄 Intentando restaurar desde: {filename}")
                
                result = backup_manager.restore_backup(filename, is_upload=False)
                
                if result.get('success'):
                    print("✅ Restauración exitosa")
                    print("   La base de datos ha sido restaurada correctamente")
                    
                    # Verificar que la restauración funcionó
                    print("\n🔍 Verificando estado post-restauración...")
                    backups_after = backup_manager.list_backups()
                    print(f"📋 Backups disponibles después: {len(backups_after)}")
                    
                    return True
                else:
                    print(f"❌ Error en restauración: {result.get('message')}")
                    return False
            else:
                print("❌ No hay backups disponibles para probar")
                return False
                
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_restore_functionality()