#!/usr/bin/env python
"""
Script para probar el filtrado de trabajadores por recintos asignados a administradores
"""

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://localhost:5050"

def login_user(email, password="123456"):
    """
    Realiza login de un usuario y devuelve la sesión
    """
    session = requests.Session()
    
    try:
        # 1. Obtener la página de login para el CSRF token
        login_page = session.get(f"{BASE_URL}/auth/login")
        if login_page.status_code != 200:
            print(f"❌ No se pudo acceder a la página de login: {login_page.status_code}")
            return None
            
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token:
            print("❌ No se encontró el token CSRF")
            return None
            
        # 2. Realizar el login
        login_data = {
            'email': email,
            'password': password,
            'csrf_token': csrf_token['value']
        }
        
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        # 3. Verificar si el login fue exitoso (redirección)
        if login_response.status_code == 302 or 'dashboard' in login_response.url:
            print(f"✅ Login exitoso para {email}")
            return session
        else:
            print(f"❌ Login fallido para {email} - Status: {login_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error durante el login: {e}")
        return None

def test_trabajadores_filtrado(session, email, expected_count=None):
    """
    Prueba el acceso a la página de trabajadores y verifica el filtrado
    """
    try:
        # 1. Acceder a la página de trabajadores
        workers_url = f"{BASE_URL}/trabajadores"
        workers_response = session.get(workers_url)
        
        print(f"📋 Página trabajadores: Status {workers_response.status_code}")
        
        if workers_response.status_code == 200:
            # Parsear el HTML para contar trabajadores
            soup = BeautifulSoup(workers_response.content, 'html.parser')
            
            # Buscar las filas de la tabla de trabajadores (ajustar selector según tu HTML)
            # Intentar diferentes selectores comunes
            worker_rows = soup.find_all('tr', class_=['worker-row', 'trabajador-row'])
            if not worker_rows:
                # Buscar en tabla genérica
                table = soup.find('table')
                if table:
                    worker_rows = table.find_all('tr')[1:]  # Excluir header
                
            worker_count = len(worker_rows)
            print(f"📊 Trabajadores visibles en la página: {worker_count}")
            
            # También probar la API si existe
            try:
                api_url = f"{BASE_URL}/api/trabajadores"
                api_response = session.get(api_url)
                
                if api_response.status_code == 200:
                    api_data = api_response.json()
                    if isinstance(api_data, list):
                        api_worker_count = len(api_data)
                    elif isinstance(api_data, dict) and 'data' in api_data:
                        api_worker_count = len(api_data['data'])
                    else:
                        api_worker_count = 0
                        
                    print(f"📊 Trabajadores desde API: {api_worker_count}")
                    
                    # Mostrar algunos detalles de los trabajadores
                    if isinstance(api_data, list) and api_data:
                        print("👥 Primeros trabajadores visibles:")
                        for i, worker in enumerate(api_data[:3]):
                            nombre = worker.get('nombre', 'N/A')
                            recinto = worker.get('recinto', {}).get('nombre', 'Sin recinto') if worker.get('recinto') else 'Sin recinto'
                            print(f"   {i+1}. {nombre} - {recinto}")
                        if len(api_data) > 3:
                            print(f"   ... y {len(api_data) - 3} trabajadores más")
                    
                    # Validar el conteo esperado
                    if expected_count is not None:
                        if api_worker_count == expected_count:
                            print(f"✅ VALIDACIÓN EXITOSA: Se esperaban {expected_count} trabajadores y se obtuvieron {api_worker_count}")
                            return True
                        else:
                            print(f"❌ VALIDACIÓN FALLIDA: Se esperaban {expected_count} trabajadores pero se obtuvieron {api_worker_count}")
                            return False
                    
                    return True
                else:
                    print(f"❌ API no disponible - Status: {api_response.status_code}")
            except:
                print("ℹ️  API no disponible, usando conteo de HTML")
                
        else:
            print(f"❌ No se pudo acceder a la página de trabajadores")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

def main():
    """
    Función principal para probar el filtrado de trabajadores
    """
    print("🧪 INICIANDO PRUEBAS DE FILTRADO DE TRABAJADORES")
    print("=" * 60)
    
    # Casos de prueba
    test_cases = [
        {
            'email': 'admin@sistema.local',
            'expected_count': None,  # SUPERADMIN debería ver todos
            'description': 'SUPERADMIN - Debe ver todos los trabajadores'
        },
        {
            'email': 'administrador@sistema.local',
            'expected_count': 5,  # Solo trabajadores de recintos asignados
            'description': 'ADMINISTRADOR - Debe ver solo trabajadores de recintos asignados'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Probando: {test_case['description']}")
        print(f"📧 Usuario: {test_case['email']}")
        
        # Login
        session = login_user(test_case['email'])
        
        if session:
            # Probar filtrado
            result = test_trabajadores_filtrado(
                session, 
                test_case['email'], 
                test_case['expected_count']
            )
            
            if result:
                print(f"✅ Prueba exitosa para {test_case['email']}")
            else:
                print(f"❌ Prueba fallida para {test_case['email']}")
        else:
            print(f"❌ No se pudo realizar login para {test_case['email']}")
        
        print("-" * 40)
    
    print("\n🏁 PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    main()