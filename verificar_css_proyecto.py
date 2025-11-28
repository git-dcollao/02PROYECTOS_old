#!/usr/bin/env python3
"""
Script para verificar que el CSS de proyecto-llenar se está cargando correctamente
"""
import requests
import re
import sys

def verificar_css_cargado():
    """Verificar que proyecto-llenar.css está incluido en la página"""
    print("🔍 VERIFICANDO CARGA DE CSS proyecto-llenar.css")
    print("=" * 50)
    
    try:
        # Crear sesión con cookies
        session = requests.Session()
        
        # Login primero
        login_data = {
            'email': 'administrador@sistema.local',
            'password': 'admin123'
        }
        
        print("🔐 Autenticándose...")
        login_response = session.post("http://localhost:5050/auth/login", data=login_data)
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ Error de login: {login_response.status_code}")
            return
        
        # Obtener la página proyecto-llenar
        print("📄 Obteniendo página proyecto-llenar...")
        response = session.get("http://localhost:5050/proyecto-llenar")
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo página: {response.status_code}")
            return
        
        html = response.text
        
        # Buscar referencias a CSS
        print("\n🎨 ARCHIVOS CSS ENCONTRADOS:")
        css_pattern = r'<link[^>]*href="[^"]*\.css[^"]*"[^>]*>'
        css_links = re.findall(css_pattern, html)
        
        modal_styles_found = False
        proyecto_llenar_found = False
        
        for i, link in enumerate(css_links):
            print(f"   {i+1}. {link}")
            if 'modal-styles.css' in link:
                modal_styles_found = True
            if 'proyecto-llenar.css' in link:
                proyecto_llenar_found = True
        
        print(f"\n📋 ANÁLISIS:")
        print(f"   ✅ modal-styles.css encontrado: {modal_styles_found}")
        print(f"   ✅ proyecto-llenar.css encontrado: {proyecto_llenar_found}")
        
        # Verificar orden de carga
        if modal_styles_found and proyecto_llenar_found:
            modal_pos = html.find('modal-styles.css')
            proyecto_pos = html.find('proyecto-llenar.css')
            if modal_pos < proyecto_pos:
                print("   ✅ Orden correcto: modal-styles.css antes que proyecto-llenar.css")
            else:
                print("   ❌ Orden incorrecto: proyecto-llenar.css antes que modal-styles.css")
        
        # Probar acceso directo al CSS
        print(f"\n🔗 PROBANDO ACCESO DIRECTO AL CSS:")
        css_url = "http://localhost:5050/static/css/proyecto-llenar.css"
        css_response = session.get(css_url)
        
        print(f"   📁 URL: {css_url}")
        print(f"   📊 Status: {css_response.status_code}")
        
        if css_response.status_code == 200:
            print("   ✅ Archivo CSS accesible")
            
            # Verificar que contiene las reglas de z-index
            css_content = css_response.text
            if 'z-index: 1060' in css_content:
                print("   ✅ Reglas de z-index presentes en el CSS")
            else:
                print("   ❌ Reglas de z-index NO encontradas en el CSS")
                
            if '.dropdown-menu' in css_content:
                print("   ✅ Selectores .dropdown-menu presentes")
            else:
                print("   ❌ Selectores .dropdown-menu NO encontrados")
                
        else:
            print(f"   ❌ Error accediendo al CSS: {css_response.status_code}")
        
        # Buscar tablas sticky en el HTML
        print(f"\n📊 ELEMENTOS STICKY EN HTML:")
        sticky_pattern = r'<[^>]*class="[^"]*sticky[^"]*"[^>]*>'
        sticky_elements = re.findall(sticky_pattern, html, re.IGNORECASE)
        
        for i, element in enumerate(sticky_elements):
            print(f"   {i+1}. {element}")
        
        # Buscar dropdowns
        print(f"\n📋 DROPDOWNS EN HTML:")
        dropdown_pattern = r'<[^>]*class="[^"]*dropdown[^"]*"[^>]*>'
        dropdown_elements = re.findall(dropdown_pattern, html, re.IGNORECASE)
        
        for i, element in enumerate(dropdown_elements[:5]):  # Solo primeros 5
            print(f"   {i+1}. {element}")
        
        if len(dropdown_elements) > 5:
            print(f"   ... y {len(dropdown_elements) - 5} más")
        
        # Guardar HTML completo para inspección
        with open('debug_html_proyecto_llenar.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n💾 HTML completo guardado en: debug_html_proyecto_llenar.html")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    verificar_css_cargado()
    print(f"\n✅ Verificación completada")

if __name__ == "__main__":
    main()