#!/usr/bin/env python3
"""
Debug del menú desplegable en proyecto-llenar.html
Compara el comportamiento del menú Configuración entre páginas
"""
import requests
from requests.auth import HTTPBasicAuth
import json
import re

def test_menu_pages():
    print("🔍 DIAGNÓSTICO DEL MENÚ - PROYECTO LLENAR")
    print("=" * 60)
    
    # Configurar sesión con autenticación
    session = requests.Session()
    
    # Intentar login
    print("\n📋 1. Probando autenticación...")
    login_url = "http://localhost:5050/login"
    
    # Primero obtener el formulario de login para el CSRF token
    login_page = session.get(login_url)
    if login_page.status_code != 200:
        print(f"❌ Error al acceder a página de login: {login_page.status_code}")
        return
    
    # Buscar CSRF token en la respuesta
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
    if not csrf_match:
        print("❌ No se pudo encontrar el CSRF token")
        return
    
    csrf_token = csrf_match.group(1)
    print(f"✅ CSRF Token obtenido: {csrf_token[:20]}...")
    
    # Realizar login
    login_data = {
        'email': 'administrador@sistema.local',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    login_response = session.post(login_url, data=login_data)
    
    if login_response.status_code == 200 and 'dashboard' in login_response.url:
        print("✅ Login exitoso")
    else:
        print(f"❌ Error en login: {login_response.status_code} - {login_response.url}")
        return
    
    # 2. Probar página de prueba del menú
    print("\n📋 2. Probando página de prueba del menú...")
    prueba_url = "http://localhost:5050/prueba-menu"
    prueba_response = session.get(prueba_url)
    
    if prueba_response.status_code == 200:
        print("✅ Página prueba-menu accesible")
        
        # Buscar contenido del menú Configuración
        config_menu_pattern = r'<ul class="dropdown-menu"[^>]*>(.*?)</ul>'
        config_matches = re.findall(config_menu_pattern, prueba_response.text, re.DOTALL)
        
        if config_matches:
            print(f"📋 Encontrados {len(config_matches)} menús dropdown")
            for i, menu in enumerate(config_matches):
                if 'Configuración' in menu or 'Trabajadores' in menu:
                    print(f"\n🔍 Menú {i+1} (Configuración):")
                    # Extraer elementos del menú
                    items = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', menu)
                    for href, text in items:
                        print(f"   - {text.strip()}: {href}")
        else:
            print("❌ No se encontraron menús dropdown")
    else:
        print(f"❌ Error al acceder a prueba-menu: {prueba_response.status_code}")
    
    # 3. Probar página proyecto-llenar
    print("\n📋 3. Probando página proyecto-llenar...")
    proyecto_url = "http://localhost:5050/proyecto-llenar"
    proyecto_response = session.get(proyecto_url)
    
    if proyecto_response.status_code == 200:
        print("✅ Página proyecto-llenar accesible")
        
        # Buscar contenido del menú Configuración
        config_menu_pattern = r'<ul class="dropdown-menu"[^>]*>(.*?)</ul>'
        config_matches = re.findall(config_menu_pattern, proyecto_response.text, re.DOTALL)
        
        if config_matches:
            print(f"📋 Encontrados {len(config_matches)} menús dropdown")
            for i, menu in enumerate(config_matches):
                if 'Configuración' in menu or 'ID Nombre' in menu:
                    print(f"\n🔍 Menú {i+1} (Problema detectado):")
                    # Extraer elementos del menú
                    items = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', menu)
                    if items:
                        for href, text in items:
                            print(f"   - {text.strip()}: {href}")
                    else:
                        print(f"   - Contenido HTML: {menu.strip()}")
        else:
            print("❌ No se encontraron menús dropdown")
        
        # Buscar específicamente "ID Nombre"
        if 'ID Nombre' in proyecto_response.text:
            print("\n⚠️ PROBLEMA DETECTADO: 'ID Nombre' encontrado en la página")
            id_nombre_context = re.findall(r'.{50}ID Nombre.{50}', proyecto_response.text)
            for context in id_nombre_context[:3]:  # Mostrar solo los primeros 3
                print(f"   Contexto: {context}")
        
    else:
        print(f"❌ Error al acceder a proyecto-llenar: {proyecto_response.status_code}")
    
    # 4. Verificar carga de JavaScript
    print("\n📋 4. Verificando archivos JavaScript...")
    js_files = [
        "/static/js/bootstrap.bundle.min.js",
        "/static/js/jquery-3.6.0.min.js"
    ]
    
    for js_file in js_files:
        js_url = f"http://localhost:5050{js_file}"
        js_response = session.get(js_url)
        if js_response.status_code == 200:
            print(f"✅ {js_file} - OK")
        else:
            print(f"❌ {js_file} - Error {js_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNÓSTICO COMPLETADO")
    
    # Recomendaciones
    print("\n📋 RECOMENDACIONES:")
    print("1. Accede a las páginas manualmente y abre DevTools (F12)")
    print("2. Ve a la pestaña Console para ver los logs de debugging")
    print("3. Compara el comportamiento del menú entre /prueba-menu y /proyecto-llenar")
    print("4. Busca errores JavaScript que puedan interferir con Bootstrap")

if __name__ == "__main__":
    test_menu_pages()