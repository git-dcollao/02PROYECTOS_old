#!/usr/bin/env python3
"""
Script simple para examinar el HTML de ambas páginas y encontrar el texto "ID Nombre"
"""
import requests
import re
import sys

def analizar_pagina(url, nombre_pagina):
    """Analizar una página específica buscando el texto problemático"""
    print(f"\n🔍 ANALIZANDO {nombre_pagina.upper()}: {url}")
    print("=" * 50)
    
    try:
        # Crear sesión con cookies
        session = requests.Session()
        
        # Login primero
        login_data = {
            'email': 'administrador@sistema.local',
            'password': 'admin123'
        }
        
        login_response = session.post("http://localhost:5050/auth/login", data=login_data)
        
        # Obtener la página
        response = session.get(url)
        html = response.text
        
        # Buscar "ID Nombre" específicamente
        if "ID Nombre" in html:
            print("🚨 ENCONTRADO: Texto 'ID Nombre' presente")
            
            # Buscar el contexto donde aparece
            lines = html.split('\n')
            for i, line in enumerate(lines):
                if "ID Nombre" in line:
                    print(f"📍 Línea {i+1}: {line.strip()}")
                    
                    # Mostrar contexto (3 líneas antes y después)
                    start = max(0, i-3)
                    end = min(len(lines), i+4)
                    print("\n📋 CONTEXTO:")
                    for j in range(start, end):
                        prefix = ">>> " if j == i else "    "
                        print(f"{prefix}{j+1:3}: {lines[j]}")
        else:
            print("✅ NO encontrado: Texto 'ID Nombre' no está presente")
        
        # Buscar menús dropdown
        dropdown_pattern = r'<a[^>]*class="[^"]*dropdown-toggle[^"]*"[^>]*>(.*?)</a>'
        dropdowns = re.findall(dropdown_pattern, html, re.DOTALL)
        
        print(f"\n📋 Dropdowns encontrados: {len(dropdowns)}")
        for i, dropdown in enumerate(dropdowns):
            # Limpiar HTML
            clean_text = re.sub(r'<[^>]+>', '', dropdown).strip()
            print(f"   {i+1}. {clean_text}")
        
        # Buscar dropdown-menu específicamente
        menu_pattern = r'<ul[^>]*class="[^"]*dropdown-menu[^"]*"[^>]*>(.*?)</ul>'
        menus = re.findall(menu_pattern, html, re.DOTALL | re.MULTILINE)
        
        print(f"\n📋 Menús dropdown encontrados: {len(menus)}")
        for i, menu in enumerate(menus):
            # Buscar items del menú
            items_pattern = r'<a[^>]*class="[^"]*dropdown-item[^"]*"[^>]*>(.*?)</a>'
            items = re.findall(items_pattern, menu, re.DOTALL)
            
            print(f"   📁 Menú {i+1}: {len(items)} items")
            for j, item in enumerate(items):
                clean_item = re.sub(r'<[^>]+>', '', item).strip()
                if clean_item:
                    print(f"      {j+1}. {clean_item}")
        
        print(f"\n💾 HTML guardado temporalmente")
        with open(f'debug_html_{nombre_pagina}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔧 ANÁLISIS DIRECTO DE HTML - BÚSQUEDA DE 'ID Nombre'")
    print("=" * 60)
    
    # Analizar ambas páginas
    analizar_pagina("http://localhost:5050/prueba-menu", "funcional")
    analizar_pagina("http://localhost:5050/proyecto-llenar", "problemática")
    
    print(f"\n✅ Análisis completado")
    print("📁 Archivos HTML guardados para inspección manual")

if __name__ == "__main__":
    main()