#!/usr/bin/env python3
"""
Script para probar la función de restauración directamente
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append('/app')

from app import create_app
from routes.admin_routes import restore_backup_internal

def test_direct_restore():
    """Prueba la restauración directa"""
    print("🔧 Probando restauración directa...")
    
    # Crear la aplicación
    app = create_app()
    
    backup_file = 'uploaded_BD_V3_20251023_192653_20251023_211103.sql'
    
    with app.app_context():
        print(f"📤 Iniciando restauración de {backup_file}...")
        try:
            result = restore_backup_internal(backup_file)
            print(f"✅ Resultado: {result}")
        except Exception as e:
            print(f"❌ Error en restauración: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_direct_restore()