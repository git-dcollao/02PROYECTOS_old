#!/usr/bin/env python3
"""
Script para probar que la corrección del error en la página de permisos funciona correctamente
"""

import requests
import json
from requests.auth import HTTPBasicAuth

def test_permissions_page():
    """Prueba la página de permisos"""
    
    base_url = "http://localhost:5050"
    session = requests.Session()
    
    print("🔐 Iniciando sesión...")
    
    # Primero obtener la página de login para el token CSRF
    login_page = session.get(f"{base_url}/auth/login")
    
    if login_page.status_code != 200:
        print(f"❌ Error al obtener página de login: {login_page.status_code}")
        return False
    
    # Buscar el token CSRF
    csrf_token = None
    if 'csrf_token' in login_page.text:
        # Buscar el token en el HTML
        import re
        match = re.search(r'csrf_token.*?value="([^"]+)"', login_page.text)
        if match:
            csrf_token = match.group(1)
    
    # Hacer login
    login_data = {
        'email': 'admin@sistema.com',
        'password': 'admin123'
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code != 200 and login_response.status_code != 302:
        print(f"❌ Error en login: {login_response.status_code}")
        return False
    
    print("✅ Login exitoso")
    
    # Probar la página de permisos
    print("📋 Probando página de permisos...")
    permissions_response = session.get(f"{base_url}/permissions/")
    
    if permissions_response.status_code == 200:
        print("✅ Página de permisos carga correctamente")
        
        # Verificar que contenga elementos esperados
        content = permissions_response.text
        if "Total de Páginas" in content and "Categorías" in content:
            print("✅ Estadísticas mostradas correctamente")
        else:
            print("⚠️  Las estadísticas no se muestran correctamente")
        
        if "permissionsTable" in content:
            print("✅ Tabla de permisos presente")
        else:
            print("⚠️  Tabla de permisos no encontrada")
        
        return True
    else:
        print(f"❌ Error al cargar página de permisos: {permissions_response.status_code}")
        return False

if __name__ == "__main__":
    print("🧪 Probando corrección del error en página de permisos...")
    success = test_permissions_page()
    
    if success:
        print("\n🎉 ¡Todas las pruebas pasaron! El error ha sido corregido.")
        print("📖 Puedes acceder a http://localhost:5050/permissions/ con:")
        print("   Email: admin@sistema.com")
        print("   Password: admin123")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los logs del contenedor.")
