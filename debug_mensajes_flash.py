"""
Debug de mensajes flash duplicados en proyecto-llenar
Inspecciona directamente la página para ver mensajes flash
"""
import requests
from urllib.parse import urljoin

def test_direct_access():
    print("🔍 DEBUGGING MENSAJES FLASH DUPLICADOS")
    print("="*50)
    
    # Acceso directo a la página
    base_url = "http://localhost:5050"
    proyecto_url = f"{base_url}/proyecto-llenar"
    
    try:
        print("1️⃣ Acceso directo a proyecto-llenar...")
        session = requests.Session()
        
        response = session.get(proyecto_url, allow_redirects=True)
        print(f"   ✅ Response: {response.status_code}")
        print(f"   🔗 URL final: {response.url}")
        
        # Verificar contenido HTML
        html = response.text
        
        print("\n2️⃣ Buscando flash messages en HTML...")
        
        # Buscar diferentes patrones de flash messages
        import re
        
        # Patron 1: div con clase alert
        alerts = re.findall(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
        if alerts:
            print(f"   📝 Encontrados {len(alerts)} elementos con clase 'alert':")
            for i, alert in enumerate(alerts):
                clean_alert = re.sub(r'<[^>]*>', '', alert).strip()
                if clean_alert:
                    print(f"      {i+1}. {clean_alert}")
        
        # Patron 2: texto específico "bienvenido" o "sesión"
        welcome_matches = re.findall(r'(Bienvenido[^<]*)', html, re.IGNORECASE)
        if welcome_matches:
            print(f"\n   👋 Mensajes de bienvenida encontrados:")
            for msg in welcome_matches:
                print(f"      - {msg}")
        
        session_matches = re.findall(r'([^<]*[sS]esión[^<]*)', html, re.IGNORECASE)
        if session_matches:
            print(f"\n   🔐 Mensajes de sesión encontrados:")
            for msg in session_matches[:5]:  # Solo los primeros 5 para evitar spam
                print(f"      - {msg}")
        
        # Patron 3: Cualquier texto que parezca flash message
        flash_patterns = [
            r'([^<]*correctamente[^<]*)',
            r'([^<]*exitosamente[^<]*)', 
            r'([^<]*error[^<]*)',
            r'([^<]*éxito[^<]*)'
        ]
        
        for pattern in flash_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"\n   ✨ Mensajes encontrados con patrón '{pattern}':")
                for msg in matches[:3]:  # Solo los primeros 3
                    clean_msg = msg.strip()
                    if len(clean_msg) > 10 and len(clean_msg) < 200:  # Filtrar mensajes muy cortos o muy largos
                        print(f"      - {clean_msg}")
        
        print(f"\n3️⃣ Verificando redirecciones:")
        if response.history:
            print("   🔄 Historial de redirecciones:")
            for i, resp in enumerate(response.history):
                print(f"      {i+1}. {resp.status_code} -> {resp.url}")
        else:
            print("   ✅ Sin redirecciones")
        
        # Guardar HTML para análisis manual
        with open('debug_proyecto_llenar.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n💾 HTML guardado en: debug_proyecto_llenar.html")
        
        # Ver tamaño del HTML
        print(f"� Tamaño del HTML: {len(html)} caracteres")
        
        # Buscar bloque específico de flash messages en template
        if 'get_flashed_messages' in html:
            print("\n🎯 ENCONTRADO: Template contiene código de flash messages")
            # Extraer el bloque
            flash_block = re.search(r'({% with messages = get_flashed_messages.*?{% endwith %})', html, re.DOTALL)
            if flash_block:
                print("   📝 Bloque encontrado en template")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_access()