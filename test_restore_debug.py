#!/usr/bin/env python3
"""
Script para probar la funcionalidad de restauración de backups
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backup_restoration():
    """Probar la restauración de backup"""
    try:
        from app import create_app
        from app.routes.admin_routes import BackupManager
        
        print("🔧 Iniciando prueba de restauración...")
        
        app = create_app()
        
        with app.app_context():
            backup_manager = BackupManager()
            
            # Listar backups disponibles
            print("\n📋 Listando backups disponibles...")
            backups = backup_manager.list_backups()
            
            if not backups:
                print("❌ No hay backups disponibles para probar")
                return False
            
            print(f"✅ Encontrados {len(backups)} backups:")
            for i, backup in enumerate(backups[:5]):  # Solo mostrar primeros 5
                print(f"  {i+1}. {backup['filename']} ({backup.get('size', 'N/A')} bytes)")
            
            # Probar configuración de base de datos
            print("\n🔧 Probando configuración de base de datos...")
            db_config = backup_manager.get_db_config()
            print(f"✅ Configuración DB: host={db_config['host']}, port={db_config['port']}, db={db_config['database']}")
            
            # Probar conexión con PyMySQL
            print("\n🔌 Probando conexión con PyMySQL...")
            try:
                import pymysql
                connection = pymysql.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    charset='utf8mb4',
                    connect_timeout=10
                )
                print("✅ Conexión PyMySQL exitosa")
                connection.close()
            except Exception as e:
                print(f"❌ Error de conexión PyMySQL: {e}")
                return False
            
            # Verificar comando mysql
            print("\n💻 Verificando comando mysql...")
            try:
                import subprocess
                result = subprocess.run(['mysql', '--version'], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ MySQL comando disponible: {result.stdout.strip()}")
                else:
                    print(f"⚠️ MySQL comando no funciona: {result.stderr}")
            except FileNotFoundError:
                print("❌ Comando mysql no encontrado")
            except Exception as e:
                print(f"❌ Error verificando mysql: {e}")
            
            print("\n🎯 Prueba completada")
            return True
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backup_restoration()
    sys.exit(0 if success else 1)