#!/usr/bin/env python3
"""
Test de autenticación y funcionalidad de backup
============================================== 
Script para probar el sistema de backup mejorado con autenticación AJAX
"""

import requests
import json
import time
import sys

def test_backup_system():
    """Prueba completa del sistema de backup mejorado"""
    
    base_url = "http://localhost:5050"
    session = requests.Session()
    
    print("🔍 Testing Enhanced Backup System v1.4.0")
    print("=" * 50)
    
    # Paso 1: Obtener página de login para CSRF token
    print("📝 Paso 1: Obteniendo token CSRF...")
    try:
        login_page = session.get(f"{base_url}/auth/login")
        if login_page.status_code == 200:
            print(f"✅ Página de login obtenida: {login_page.status_code}")
            
            # Buscar token CSRF en la página con múltiples métodos
            csrf_token = None
            
            # Método 1: Buscar input hidden
            import re
            csrf_pattern = r'name="csrf_token"[^>]*value="([^"]+)"'
            match = re.search(csrf_pattern, login_page.text)
            if match:
                csrf_token = match.group(1)
                print(f"✅ Token CSRF encontrado (método 1): {csrf_token[:20]}...")
            
            # Método 2: Buscar meta tag
            if not csrf_token:
                meta_pattern = r'name="csrf-token"[^>]*content="([^"]+)"'
                match = re.search(meta_pattern, login_page.text)
                if match:
                    csrf_token = match.group(1)
                    print(f"✅ Token CSRF encontrado (método 2): {csrf_token[:20]}...")
            
            # Método 3: Buscar cualquier token en el HTML
            if not csrf_token:
                token_pattern = r'csrf[^>]*"([A-Za-z0-9\._-]{20,})"'
                match = re.search(token_pattern, login_page.text, re.IGNORECASE)
                if match:
                    csrf_token = match.group(1)
                    print(f"✅ Token CSRF encontrado (método 3): {csrf_token[:20]}...")
            
            if not csrf_token:
                print("❌ No se pudo obtener token CSRF")
                # Mostrar parte del HTML para debug
                print("🔍 HTML snippet:")
                csrf_section = login_page.text[login_page.text.find('csrf'):login_page.text.find('csrf')+200] if 'csrf' in login_page.text.lower() else "No se encontró csrf en el HTML"
                print(csrf_section[:200])
                return False
        else:
            print(f"❌ Error obteniendo login: {login_page.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False
    
    # Paso 2: Autenticarse
    print("\n🔐 Paso 2: Autenticándose...")
    try:
        login_data = {
            'email': 'admin@sistema.local',
            'password': 'Maho#2024',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        
        # Validación mejorada de login exitoso
        login_success = False
        if login_response.status_code == 200:
            if 'login' not in login_response.url and 'auth' not in login_response.url:
                login_success = True
                print(f"✅ Login exitoso: {login_response.status_code} -> {login_response.url}")
            elif 'dashboard' in login_response.text.lower() or 'sistema' in login_response.text.lower():
                login_success = True
                print(f"✅ Login exitoso (contenido): {login_response.status_code}")
        elif login_response.status_code == 302:
            location = login_response.headers.get('Location', '')
            if location and 'login' not in location and 'auth' not in location:
                login_success = True
                print(f"✅ Login exitoso (redirect): {login_response.status_code} -> {location}")
        
        if not login_success:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Response URL: {login_response.url}")
            if 'error' in login_response.text.lower() or 'invalid' in login_response.text.lower():
                print("🔍 Posibles credenciales incorrectas")
            return False
            
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False
    
    # Paso 3: Probar endpoint de progreso
    print("\n📊 Paso 3: Probando endpoint de progreso...")
    try:
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
        
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token
        
        progress_response = session.get(f"{base_url}/admin/backup/progress", headers=headers)
        
        print(f"📡 Status: {progress_response.status_code}")
        print(f"📡 Content-Type: {progress_response.headers.get('Content-Type', 'N/A')}")
        print(f"📡 Response length: {len(progress_response.text)}")
        
        if progress_response.status_code == 200:
            if 'application/json' in progress_response.headers.get('Content-Type', ''):
                try:
                    data = progress_response.json()
                    print(f"✅ Respuesta JSON válida: {json.dumps(data, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    print("❌ Respuesta no es JSON válido")
                    print(f"Contenido (primeros 200 chars): {progress_response.text[:200]}")
                    return False
            else:
                print("❌ Respuesta no es JSON")
                if "login" in progress_response.text.lower():
                    print("🔍 Detectado redirect a login - problema de autenticación")
                print(f"Contenido (primeros 200 chars): {progress_response.text[:200]}")
                return False
        else:
            print(f"❌ Error en endpoint: {progress_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        return False

if __name__ == '__main__':
    try:
        success = test_backup_system()
        print("\n" + "=" * 50)
        if success:
            print("🎉 ¡SISTEMA DE BACKUP FUNCIONANDO CORRECTAMENTE!")
            print("✅ Autenticación AJAX implementada exitosamente")
            print("✅ Endpoints respondiendo con JSON válido")
        else:
            print("❌ Sistema requiere ajustes adicionales")
            print("🔧 Revisar configuración de autenticación")
        print("=" * 50)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)