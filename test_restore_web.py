#!/usr/bin/env python3
"""
Script para probar la restauración vía endpoint web
"""
import requests
import time
from pathlib import Path
import os

def test_restore():
    """Prueba la restauración de backup vía web"""
    print("🔧 Probando restauración vía endpoint web...")
    
    # URL del endpoint
    url = "http://localhost:5000/admin/restore_backup"
    
    # Datos del formulario
    data = {
        'backup_file': 'uploaded_BD_V3_20251023_192653_20251023_211103.sql'
    }
    
    try:
        print("📤 Enviando solicitud de restauración...")
        response = requests.post(url, data=data, timeout=300)  # 5 minutos de timeout
        
        print(f"📊 Código de respuesta: {response.status_code}")
        print(f"📋 Contenido de respuesta: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Restauración completada exitosamente")
        else:
            print(f"❌ Error en restauración: {response.status_code}")
            print(f"Contenido completo: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout en la solicitud (5 minutos)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_restore()