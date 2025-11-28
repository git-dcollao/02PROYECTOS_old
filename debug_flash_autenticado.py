"""
Debug de mensajes flash duplicados en proyecto-llenar
Inspecciona la página con usuario autenticado
"""
import requests
from bs4 import BeautifulSoup
import re

def test_authenticated_access():
    print("🔍 DEBUGGING MENSAJES FLASH DUPLICADOS - CON AUTENTICACIÓN")
    print("="*60)
    
    base_url = "http://localhost:5050"
    login_url = f"{base_url}/auth/login"
    proyecto_url = f"{base_url}/proyecto-llenar"
    
    session = requests.Session()
    
    try:
        # 1. Obtener página de login para extraer CSRF token
        print("1️⃣ Obteniendo página de login...")
        login_page = session.get(login_url)
        if login_page.status_code != 200:
            print(f"❌ Error obteniendo login: {login_page.status_code}")
            return
        
        print(f"   ✅ Login page status: {login_page.status_code}")
        
        # Extraer CSRF token
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if not csrf_input:
            # Buscar en meta tag
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            csrf_token = csrf_meta.get('content') if csrf_meta else None
        else:
            csrf_token = csrf_input.get('value')
        
        print(f"   🔑 CSRF Token: {csrf_token[:20]}..." if csrf_token else "   ❌ No CSRF token found")
        
        # 2. Hacer login
        print("\n2️⃣ Realizando login...")
        login_data = {
            'email': 'administrador@sistema.local',
            'password': 'Admin#2024'
        }
        
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(login_url, data=login_data, allow_redirects=True)
        print(f"   ✅ Login response: {login_response.status_code}")
        print(f"   🔗 URL después de login: {login_response.url}")
        
        # Verificar si el login fue exitoso
        if 'login' in login_response.url:
            print("   ❌ Login falló - aún en página de login")
            # Buscar mensajes de error
            soup = BeautifulSoup(login_response.text, 'html.parser')
            alerts = soup.find_all('div', class_='alert')
            for alert in alerts:
                print(f"      Error: {alert.get_text().strip()}")
            return
        else:
            print("   ✅ Login exitoso")
        
        # 3. Acceder a proyecto-llenar
        print("\n3️⃣ Accediendo a proyecto-llenar con usuario autenticado...")
        proyecto_response = session.get(proyecto_url, allow_redirects=True)
        print(f"   ✅ Response: {proyecto_response.status_code}")
        print(f"   🔗 URL final: {proyecto_response.url}")
        
        # 4. Analizar flash messages en la página autenticada
        html = proyecto_response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        print("\n4️⃣ Analizando flash messages en página autenticada...")
        
        # Buscar todos los elementos con clase alert
        alerts = soup.find_all('div', class_='alert')
        print(f"   📊 Total de alerts encontrados: {len(alerts)}")
        
        if alerts:
            print("   ⚠️ MENSAJES FLASH ENCONTRADOS:")
            for i, alert in enumerate(alerts):
                alert_text = alert.get_text().strip()
                alert_classes = ' '.join(alert.get('class', []))
                print(f"      {i+1}. [{alert_classes}] {alert_text}")
                
                # Verificar si es duplicado comparando texto
                if i > 0:
                    prev_alerts = [a.get_text().strip() for a in alerts[:i]]
                    if alert_text in prev_alerts:
                        print(f"          ⚠️  DUPLICADO detectado!")
        
        # 5. Buscar patrones específicos de texto duplicado
        print("\n5️⃣ Buscando patrones de mensajes duplicados...")
        
        # Buscar texto específico que podría estar duplicado
        patterns = [
            r'Bienvenido[^<]*',
            r'[Ss]esión[^<]*',
            r'correctamente[^<]*',
            r'exitosamente[^<]*'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            if len(matches) > 1:
                print(f"   🔍 Patrón '{pattern}' encontrado {len(matches)} veces:")
                for match in matches[:5]:  # Mostrar solo las primeras 5
                    print(f"      - {match.strip()}")
        
        # 6. Guardar HTML para análisis manual
        with open('debug_proyecto_llenar_autenticado.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n💾 HTML autenticado guardado en: debug_proyecto_llenar_autenticado.html")
        
        # 7. Verificar estructura del template flash messages
        print("\n6️⃣ Verificando estructura del template...")
        if 'get_flashed_messages' in html:
            print("   🎯 Template contiene bloque de flash messages")
        
        # Buscar múltiples bloques de flash messages
        flash_blocks = html.count('get_flashed_messages')
        if flash_blocks > 1:
            print(f"   ⚠️  PROBLEMA: {flash_blocks} bloques de flash messages encontrados!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_authenticated_access()