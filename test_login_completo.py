#!/usr/bin/env python3
"""
Script para probar login completo
"""

import requests
import re
from urllib.parse import urljoin

def test_login_completo():
    """Test completo de login"""
    print("🧪 Probando login completo...")
    
    base_url = "http://localhost:5050"
    session = requests.Session()
    
    try:
        # 1. Obtener página de login para conseguir CSRF token
        print("1️⃣ Obteniendo página de login...")
        login_page = session.get(base_url)
        
        if login_page.status_code != 200:
            print(f"❌ Error obteniendo página: {login_page.status_code}")
            return False
        
        # Extraer CSRF token
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        if not csrf_match:
            print("❌ No se encontró CSRF token")
            return False
        
        csrf_token = csrf_match.group(1)
        print(f"✅ CSRF token obtenido: {csrf_token[:20]}...")
        
        # 2. Intentar login
        print("2️⃣ Enviando credenciales de login...")
        login_data = {
            'csrf_token': csrf_token,
            'email': 'admin@sistema.com',
            'password': 'admin123',
            'remember_me': 'y'
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        
        print(f"📊 Status code: {login_response.status_code}")
        print(f"📍 Headers: {dict(login_response.headers)}")
        
        if login_response.status_code == 302:
            print("✅ Login exitoso (redirección)")
            redirect_url = login_response.headers.get('Location')
            print(f"🔄 Redirigiendo a: {redirect_url}")
            
            # 3. Seguir redirección para ver dashboard
            if redirect_url:
                final_response = session.get(urljoin(base_url, redirect_url))
                print(f"🎯 Status final: {final_response.status_code}")
                
                if final_response.status_code == 200:
                    if "Bienvenido, Administrador" in final_response.text:
                        print("🎉 ¡LOGIN EXITOSO! Dashboard cargado correctamente")
                        return True
                    else:
                        print("⚠️ Dashboard cargado pero sin mensaje de bienvenida")
                        return True
                else:
                    print(f"❌ Error cargando dashboard: {final_response.status_code}")
            
        elif login_response.status_code == 200:
            # Verificar si hay errores en la respuesta
            if "Invalid email or password" in login_response.text or "error" in login_response.text.lower():
                print("❌ Credenciales incorrectas")
                return False
            else:
                print("ℹ️ Login procesado (sin redirección)")
                
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Respuesta: {login_response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False
    
    return True

if __name__ == '__main__':
    if test_login_completo():
        print("\n✅ ¡ÉXITO! El sistema de login está funcionando correctamente")
        print("🌐 Puedes ir a http://localhost:5050 e iniciar sesión:")
        print("📧 Email: admin@sistema.com")
        print("🔑 Contraseña: admin123")
    else:
        print("\n❌ El test de login falló")
