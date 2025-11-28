"""
Test final - Verificar que no hay mensajes flash duplicados después del fix
"""
import requests
from bs4 import BeautifulSoup

def test_flash_fix():
    print("🔍 TEST FINAL - VERIFICACIÓN DE FIX DE MENSAJES FLASH DUPLICADOS")
    print("="*65)
    
    base_url = "http://localhost:5050"
    login_url = f"{base_url}/auth/login"
    proyecto_url = f"{base_url}/proyecto-llenar"
    
    session = requests.Session()
    
    try:
        # 1. Login
        print("1️⃣ Realizando login...")
        login_page = session.get(login_url)
        
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        csrf_token = csrf_input.get('value') if csrf_input else None
        
        login_data = {
            'email': 'administrador@sistema.local',
            'password': 'Admin#2024'
        }
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(login_url, data=login_data, allow_redirects=True)
        
        if 'login' in login_response.url:
            print("   ❌ Login falló")
            return
        else:
            print("   ✅ Login exitoso")
        
        # 2. Acceder a proyecto-llenar
        print("\n2️⃣ Accediendo a proyecto-llenar...")
        proyecto_response = session.get(proyecto_url)
        
        if proyecto_response.status_code == 200:
            print("   ✅ Página cargada correctamente")
        else:
            print(f"   ❌ Error: {proyecto_response.status_code}")
            return
        
        # 3. Contar mensajes flash específicamente
        print("\n3️⃣ Analizando mensajes flash...")
        soup = BeautifulSoup(proyecto_response.text, 'html.parser')
        
        # Buscar todos los divs con clase alert (excepto los informativos hardcodeados)
        flash_alerts = soup.find_all('div', class_=lambda x: x and 'alert' in x and ('success' in x or 'danger' in x or 'warning' in x) and 'info' not in x)
        
        print(f"   📊 Mensajes flash dinámicos encontrados: {len(flash_alerts)}")
        
        if len(flash_alerts) == 0:
            print("   ✅ PERFECTO: No hay mensajes flash duplicados")
        elif len(flash_alerts) == 1:
            alert_text = flash_alerts[0].get_text().strip()
            print(f"   ✅ Solo 1 mensaje flash: {alert_text}")
        else:
            print("   ⚠️ POSIBLE PROBLEMA: Múltiples mensajes flash:")
            for i, alert in enumerate(flash_alerts):
                print(f"      {i+1}. {alert.get_text().strip()}")
        
        # 4. Verificar mensaje informativo hardcodeado (debe existir)
        info_alerts = soup.find_all('div', class_=lambda x: x and 'alert' in x and 'info' in x)
        print(f"\n   📝 Mensajes informativos (hardcoded): {len(info_alerts)}")
        if info_alerts:
            print("   ✅ Mensaje informativo de plantilla presente (correcto)")
        
        # 5. Verificar bloque de flash messages en HTML
        html_content = proyecto_response.text
        flash_blocks = html_content.count('get_flashed_messages')
        print(f"\n4️⃣ Bloques de 'get_flashed_messages' en HTML: {flash_blocks}")
        
        if flash_blocks == 0:
            print("   ✅ PERFECTO: No hay bloques de flash messages redundantes")
        elif flash_blocks == 1:
            print("   ✅ CORRECTO: Solo 1 bloque de flash messages (desde base_layout.html)")
        else:
            print(f"   ❌ PROBLEMA: {flash_blocks} bloques de flash messages - debería ser solo 1")
        
        # 6. Resultado final
        print(f"\n🎯 RESULTADO FINAL:")
        if len(flash_alerts) <= 1 and flash_blocks <= 1:
            print("   ✅ ÉXITO: Problema de mensajes flash duplicados RESUELTO")
            print("   ✅ Los mensajes flash ahora aparecen solo una vez")
        else:
            print("   ❌ PERSISTE: Aún hay indicios de duplicación")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")

if __name__ == "__main__":
    test_flash_fix()