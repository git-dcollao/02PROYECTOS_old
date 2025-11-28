#!/usr/bin/env python3
"""
Script para comparar templates y encontrar diferencias en el manejo del menú Bootstrap
"""
import requests
import sys
import re
import json
from bs4 import BeautifulSoup

def obtener_contenido_menu(url, session):
    """Obtener el contenido HTML del menú de una página específica"""
    print(f"\n🔍 Analizando: {url}")
    
    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el menú Configuración
        config_menus = []
        
        # Buscar por texto del botón
        for link in soup.find_all('a', text=lambda text: text and 'configuraci' in text.lower()):
            config_menus.append(('link_text', link.get_text().strip(), str(link)))
        
        # Buscar dropdowns con "Configuración"
        for dropdown in soup.find_all('a', class_='dropdown-toggle'):
            if dropdown.get_text() and 'configuraci' in dropdown.get_text().lower():
                # Encontrar el menú asociado
                dropdown_id = dropdown.get('aria-controls') or dropdown.get('data-bs-target')
                if dropdown_id:
                    menu = soup.find('ul', id=dropdown_id)
                    if menu:
                        items = menu.find_all('li') or menu.find_all('a', class_='dropdown-item')
                        config_menus.append(('dropdown', dropdown.get_text().strip(), [item.get_text().strip() for item in items]))
        
        # Buscar cualquier dropdown con items relacionados con configuración
        for dropdown_menu in soup.find_all('ul', class_='dropdown-menu'):
            items = dropdown_menu.find_all('a', class_='dropdown-item')
            item_texts = [item.get_text().strip() for item in items if item.get_text()]
            
            # Si contiene palabras clave de configuración
            config_keywords = ['estado', 'prioridad', 'tipo', 'fase', 'especialidad', 'equipo']
            if any(keyword in ' '.join(item_texts).lower() for keyword in config_keywords):
                
                # Encontrar el botón asociado
                dropdown_id = dropdown_menu.get('aria-labelledby')
                button = soup.find('a', id=dropdown_id) if dropdown_id else None
                button_text = button.get_text().strip() if button else 'Sin botón'
                
                config_menus.append(('dropdown_menu', button_text, item_texts))
        
        print(f"✅ Encontrados {len(config_menus)} menús de configuración")
        return config_menus
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🔧 COMPARADOR DE TEMPLATES - ANÁLISIS DE MENÚS")
    print("=" * 60)
    
    # URLs a comparar
    base_url = "http://localhost:5050"
    urls = {
        'funcional': f"{base_url}/prueba-menu",
        'problematica': f"{base_url}/proyecto-llenar"
    }
    
    # Credenciales para autenticación
    login_data = {
        'email': 'administrador@sistema.local',
        'password': 'admin123'
    }
    
    session = requests.Session()
    
    # Login
    print(f"🔐 Autenticándose en {base_url}/auth/login...")
    try:
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        print(f"🔍 Response status: {login_response.status_code}")
        print(f"🔍 Response URL: {login_response.url}")
        
        if login_response.status_code == 200 or login_response.status_code == 302:
            print("✅ Login exitoso")
        else:
            print(f"❌ Login falló: {login_response.status_code}")
            print(f"Response: {login_response.text[:500]}")
            return
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return
    
    # Analizar cada página
    resultados = {}
    for nombre, url in urls.items():
        resultados[nombre] = obtener_contenido_menu(url, session)
    
    # Comparar resultados
    print("\n" + "=" * 60)
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("=" * 60)
    
    for nombre, menus in resultados.items():
        print(f"\n📄 {nombre.upper()}:")
        if menus:
            for i, (tipo, titulo, contenido) in enumerate(menus):
                print(f"   {i+1}. {tipo}: {titulo}")
                if isinstance(contenido, list):
                    for j, item in enumerate(contenido):
                        print(f"      {j+1}. {item}")
                else:
                    print(f"      {contenido}")
        else:
            print("   ❌ No se encontraron menús")
    
    # Detectar diferencias
    print(f"\n🔍 ANÁLISIS DE DIFERENCIAS:")
    print("=" * 40)
    
    func_menus = resultados.get('funcional', [])
    prob_menus = resultados.get('problematica', [])
    
    if func_menus and prob_menus:
        print(f"📊 Página funcional: {len(func_menus)} menús")
        print(f"📊 Página problemática: {len(prob_menus)} menús")
        
        # Comparar contenido de los menús
        for i, (func_menu, prob_menu) in enumerate(zip(func_menus, prob_menus)):
            func_tipo, func_titulo, func_contenido = func_menu
            prob_tipo, prob_titulo, prob_contenido = prob_menu
            
            print(f"\n📋 Menú {i+1}:")
            print(f"   Funcional:    {func_titulo} → {func_contenido}")
            print(f"   Problemático: {prob_titulo} → {prob_contenido}")
            
            if func_titulo != prob_titulo:
                print(f"   🚨 DIFERENCIA EN TÍTULO: '{func_titulo}' vs '{prob_titulo}'")
            
            if func_contenido != prob_contenido:
                print(f"   🚨 DIFERENCIA EN CONTENIDO")
    
    print(f"\n✅ Análisis completado")

if __name__ == "__main__":
    main()