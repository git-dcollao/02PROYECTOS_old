#!/usr/bin/env python3
"""
Test del Sistema de Restauración Completa con Limpieza de BD
===========================================================

Script para probar la nueva funcionalidad de restauración con limpieza completa.
"""

import os
import sys
import time

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backup_service():
    """Test del servicio de backup con limpieza"""
    print("🧪 === TESTING BACKUP SERVICE CON LIMPIEZA ===")
    
    try:
        # Importar servicio
        from app.services.backup_service import enhanced_backup_service
        print("✅ Servicio importado correctamente")
        
        # Verificar que el método existe
        if hasattr(enhanced_backup_service, 'restore_backup_enhanced'):
            print("✅ Método restore_backup_enhanced encontrado")
            
            # Obtener signature del método
            import inspect
            sig = inspect.signature(enhanced_backup_service.restore_backup_enhanced)
            print(f"✅ Signature del método: {sig}")
            
            # Verificar parámetros
            params = list(sig.parameters.keys())
            print(f"📋 Parámetros: {params}")
            
            if 'clean_database' in params:
                print("✅ Parámetro 'clean_database' encontrado")
            else:
                print("❌ Parámetro 'clean_database' NO encontrado")
                
        else:
            print("❌ Método restore_backup_enhanced NO encontrado")
            
        # Verificar método de limpieza
        if hasattr(enhanced_backup_service, '_clear_all_database_tables'):
            print("✅ Método _clear_all_database_tables encontrado")
        else:
            print("❌ Método _clear_all_database_tables NO encontrado")
            
    except Exception as e:
        print(f"❌ Error importando servicio: {e}")
        import traceback
        traceback.print_exc()

def test_database_connection():
    """Test de conexión a base de datos"""
    print("\n🔌 === TESTING CONEXIÓN A BD ===")
    
    try:
        from config import Config
        import pymysql
        
        # Configuración de BD
        config = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'charset': 'utf8mb4'
        }
        
        print(f"📋 Configuración: {config['host']}:{config['port']}")
        
        # Conectar
        connection = pymysql.connect(**config)
        print("✅ Conexión establecida")
        
        # Obtener lista de tablas
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📊 Total de tablas: {len(tables)}")
            print(f"📋 Primeras 5 tablas: {tables[:5]}")
        
        connection.close()
        print("✅ Conexión cerrada")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_frontend_files():
    """Test de archivos frontend"""
    print("\n🎨 === TESTING ARCHIVOS FRONTEND ===")
    
    # Verificar enhanced-backup-manager.js
    js_file = "app/static/js/enhanced-backup-manager.js"
    if os.path.exists(js_file):
        print("✅ enhanced-backup-manager.js encontrado")
        
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar funciones
        if 'showRestoreOptions' in content:
            print("✅ Función showRestoreOptions encontrada")
        else:
            print("❌ Función showRestoreOptions NO encontrada")
            
        if 'executeRestore' in content:
            print("✅ Función executeRestore encontrada")
        else:
            print("❌ Función executeRestore NO encontrada")
            
        if 'clean_database' in content:
            print("✅ Parámetro clean_database en AJAX encontrado")
        else:
            print("❌ Parámetro clean_database NO encontrado")
            
    else:
        print("❌ enhanced-backup-manager.js NO encontrado")

def main():
    """Función principal"""
    print("🚀 === TEST SISTEMA RESTAURACIÓN COMPLETA ===")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"⏰ Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar tests
    test_backup_service()
    test_database_connection()
    test_frontend_files()
    
    print("\n✅ === TESTS COMPLETADOS ===")

if __name__ == "__main__":
    main()