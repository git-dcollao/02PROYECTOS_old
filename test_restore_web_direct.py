#!/usr/bin/env python3
"""
Script para probar la restauración directamente desde dentro del contenedor
simulando el request POST de la interfaz web
"""
import requests
import time
from flask import Flask

def test_restore_endpoint():
    """Prueba el endpoint de restauración directamente"""
    print("🔧 Probando endpoint de restauración...")
    
    # Datos para el POST request
    data = {
        'backup_file': 'uploaded_BD_V3_20251023_192653_20251023_211103.sql'
    }
    
    try:
        # Como estamos dentro del contenedor, usamos la IP interna
        print("📤 Enviando request POST...")
        
        # Intentar conectarse directamente al proceso Flask
        response = requests.post(
            'http://127.0.0.1:5050/admin/restore_backup',
            data=data,
            timeout=360,  # 6 minutos de timeout
            allow_redirects=False
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Response:", response.text[:500])
        elif response.status_code in [301, 302]:
            print(f"↩️  Redirección a: {response.headers.get('Location', 'Unknown')}")
        else:
            print(f"❌ Error Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La restauración puede estar tomando mucho tiempo")
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_backup_manager_direct():
    """Prueba el BackupManager directamente importando las clases"""
    print("\n🔧 Probando BackupManager directamente...")
    
    import sys
    sys.path.insert(0, '/app')
    
    try:
        # Importar desde admin_routes
        from routes.admin_routes import BackupManager
        
        # Crear instancia
        backup_manager = BackupManager()
        
        # Configuración de DB
        db_config = {
            'host': 'mysql_db',
            'port': 3306,
            'user': 'proyectos_admin', 
            'password': '123456!#Td',
            'database': 'proyectosDB'
        }
        
        backup_file = 'uploaded_BD_V3_20251023_192653_20251023_211103.sql'
        
        print(f"📤 Iniciando restauración de {backup_file}...")
        result = backup_manager.restore_backup(backup_file, is_upload=False, db_config=db_config)
        
        if result.get('success'):
            print("✅ Restauración exitosa!")
            print(f"Mensaje: {result.get('message')}")
        else:
            print("❌ Restauración falló!")
            print(f"Error: {result.get('message')}")
            
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
    except Exception as e:
        print(f"❌ Error en restauración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando tests de restauración...")
    test_restore_endpoint()
    test_backup_manager_direct()
    print("🏁 Tests completados")