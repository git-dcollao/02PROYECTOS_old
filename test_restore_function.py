#!/usr/bin/env python3
"""
Script para probar la función restore_backup directamente desde el código de la app
"""
import sys
import os
import logging

# Configurar logging para ver el progreso
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Agregar el directorio de la app al path
sys.path.insert(0, '/app')

def test_restore_function():
    """Probar la función de restauración integrada"""
    print("🔧 Probando función de restauración integrada...")
    
    # Importar la clase BackupManager
    from utils.backup_utils import BackupManager
    
    # Crear instancia de BackupManager
    backup_manager = BackupManager()
    
    # Configurar la base de datos usando las variables de entorno
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'mysql_db'),
        'port': int(os.getenv('MYSQL_PORT_INTERNAL', 3306)),
        'user': os.getenv('MYSQL_USER', 'proyectos_admin'),
        'password': os.getenv('MYSQL_PASSWORD', '123456!#Td'),
        'database': os.getenv('MYSQL_DB', 'proyectosDB')
    }
    
    print(f"📊 Configuración DB: host={db_config['host']}, port={db_config['port']}, db={db_config['database']}")
    
    backup_file = 'uploaded_BD_V3_20251023_192653_20251023_211103.sql'
    
    try:
        print(f"📤 Iniciando restauración de {backup_file}...")
        result = backup_manager.restore_backup(backup_file, is_upload=False, db_config=db_config)
        
        if result['success']:
            print("✅ Restauración completada exitosamente!")
            print(f"Mensaje: {result['message']}")
        else:
            print("❌ Error en restauración!")
            print(f"Error: {result['message']}")
            
    except Exception as e:
        print(f"❌ Excepción durante restauración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_restore_function()