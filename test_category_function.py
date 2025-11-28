#!/usr/bin/env python3
"""
🧪 TEST ESPECÍFICO: Agregar Categorías
"""

import requests
import json

def test_add_category():
    """Probar específicamente la función de agregar categorías"""
    base_url = "http://localhost:5050"
    session = requests.Session()
    
    print("🔍 PROBANDO FUNCIONALIDAD DE AGREGAR CATEGORÍAS")
    print("=" * 50)
    
    # 1. Login primero
    print("1️⃣ Haciendo login...")
    
    # Obtener página de login para CSRF token
    login_page = session.get(f"{base_url}/auth/login")
    if login_page.status_code != 200:
        print("❌ Error al acceder a login")
        return
    
    # Extraer CSRF token
    import re
    csrf_match = re.search(r'csrf_token.*?value="([^"]+)"', login_page.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    # Hacer login
    login_data = {
        'email': 'admin@sistema.com',
        'password': 'admin123'
    }
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Error en login: {login_response.status_code}")
        return
    
    print("✅ Login exitoso")
    
    # 2. Probar API de agregar categoría
    print("\n2️⃣ Probando API add-category...")
    
    test_category = {
        'name': 'Categoria de Prueba',
        'color': 'primary'
    }
    
    try:
        api_response = session.post(
            f"{base_url}/permissions/api/add-category",
            json=test_category,
            headers={
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )
        
        print(f"Status Code: {api_response.status_code}")
        print(f"Headers: {dict(api_response.headers)}")
        
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                print(f"Respuesta JSON: {json.dumps(data, indent=2)}")
                
                if data.get('success'):
                    print("✅ API funcionando correctamente")
                else:
                    print(f"⚠️ API retornó error: {data.get('message')}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Contenido: {api_response.text[:200]}...")
        else:
            print(f"❌ Error HTTP: {api_response.status_code}")
            print(f"Contenido: {api_response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Verificar que la página principal carga
    print("\n3️⃣ Verificando página principal...")
    main_page = session.get(f"{base_url}/permissions/")
    
    if main_page.status_code == 200:
        print("✅ Página principal accesible")
        
        # Verificar elementos clave
        content = main_page.text
        elements_to_check = [
            'manageCategoriesModal',
            'addNewCategory()',
            'newCategoryName',
            'newCategoryColor'
        ]
        
        missing = []
        for element in elements_to_check:
            if element not in content:
                missing.append(element)
        
        if missing:
            print(f"⚠️ Elementos faltantes: {missing}")
        else:
            print("✅ Todos los elementos de la interfaz presentes")
    else:
        print(f"❌ Error accediendo a página principal: {main_page.status_code}")

if __name__ == "__main__":
    test_add_category()
    
    print("\n📋 INSTRUCCIONES DE DEBUG:")
    print("=" * 30)
    print("1. Abre http://localhost:5050/permissions/")
    print("2. Abre las herramientas de desarrollador (F12)")
    print("3. Ve a la pestaña 'Console'")
    print("4. Intenta agregar una categoría")
    print("5. Observa los mensajes de debug que aparecen")
    print("6. Si ves errores, cópiamelos para ayudarte")
