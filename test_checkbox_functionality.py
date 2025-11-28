#!/usr/bin/env python
"""
Test específico para la funcionalidad de checkboxes y APIs
"""
import requests
import sys
import os
import json

def test_checkbox_functionality():
    """
    Prueba la funcionalidad completa de los checkboxes
    """
    print("🧪 TESTING FUNCIONALIDAD DE CHECKBOXES")
    print("="*50)
    
    session = requests.Session()
    
    try:
        # Step 1: Login
        print("🔐 Paso 1: Realizando login...")
        form_response = session.get('http://localhost:5050/auth/login')
        form_html = form_response.text
        
        csrf_start = form_html.find('name="csrf_token"')
        value_start = form_html.find('value="', csrf_start) + 7
        value_end = form_html.find('"', value_start)
        csrf_token = form_html[value_start:value_end]
        
        login_data = {
            'email': 'admin@sistema.local',
            'password': 'Maho#2024',
            'csrf_token': csrf_token,
            'submit': 'Iniciar Sesión'
        }
        
        login_response = session.post(
            'http://localhost:5050/auth/login',
            data=login_data,
            allow_redirects=False
        )
        
        if login_response.status_code not in [302, 301]:
            print("❌ ERROR: Login falló")
            return False
        
        print("✅ Login exitoso")
        
        # Step 2: Acceder a la página de gestión
        print("\n📋 Paso 2: Accediendo a gestión de administradores...")
        admin_page = session.get('http://localhost:5050/gestion-administradores')
        
        if admin_page.status_code != 200:
            print(f"❌ ERROR: No se pudo cargar la página (status: {admin_page.status_code})")
            return False
        
        if 'Error interno del servidor' in admin_page.text:
            print("❌ ERROR: La página muestra error interno del servidor")
            return False
        
        print("✅ Página cargada correctamente")
        
        # Step 3: Probar API de health-check
        print("\n🔌 Paso 3: Probando API health-check...")
        health_response = session.get('http://localhost:5050/api/health-check')
        
        print(f"📡 Health-check status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health-check OK: {health_data.get('message', 'Sin mensaje')}")
        else:
            print(f"❌ Health-check falló: {health_response.status_code}")
            return False
        
        # Step 4: Obtener datos de la matriz
        print("\n📊 Paso 4: Obteniendo matriz de administradores...")
        matriz_response = session.get('http://localhost:5050/api/matriz-administradores')
        
        print(f"📡 Matriz API status: {matriz_response.status_code}")
        
        if matriz_response.status_code == 200:
            matriz_data = matriz_response.json()
            if matriz_data.get('success'):
                administradores = matriz_data['data']['administradores']
                print(f"✅ Matriz obtenida: {len(administradores)} administradores")
                
                if administradores:
                    admin = administradores[0]
                    print(f"👤 Admin ejemplo: {admin['nombre']} (ID: {admin['id']})")
                else:
                    print("⚠️  No hay administradores disponibles para testing")
                    return True  # No es error, solo no hay datos
                
            else:
                print(f"❌ Error en matriz API: {matriz_data.get('error', 'Sin error especificado')}")
                return False
        else:
            print(f"❌ Matriz API falló: {matriz_response.status_code}")
            return False
        
        # Step 5: Simular cambio de asignación (si hay datos)
        if administradores and matriz_data['data'].get('estructura'):
            print("\n🔄 Paso 5: Simulando cambio de asignación...")
            
            admin_id = administradores[0]['id']
            
            # Buscar un recinto para probar
            estructura = matriz_data['data']['estructura']
            recinto_id = None
            
            for sector_id, sector_data in estructura.items():
                for tipo_id, tipo_data in sector_data['tipos'].items():
                    if tipo_data['recintos']:
                        recinto_id = tipo_data['recintos'][0]['id']
                        recinto_nombre = tipo_data['recintos'][0]['nombre']
                        break
                if recinto_id:
                    break
            
            if recinto_id:
                print(f"🎯 Probando asignación: Admin {admin_id} -> Recinto {recinto_id} ({recinto_nombre})")
                
                # Test: asignar
                asignar_data = {
                    'administrador_id': admin_id,
                    'recinto_id': recinto_id,
                    'asignar': True
                }
                
                asignar_response = session.post(
                    'http://localhost:5050/api/asignar-recinto',
                    json=asignar_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"📡 Asignar status: {asignar_response.status_code}")
                
                if asignar_response.status_code == 200:
                    asignar_result = asignar_response.json()
                    if asignar_result.get('success'):
                        print(f"✅ Asignación exitosa: {asignar_result.get('message', 'Sin mensaje')}")
                        
                        # Test: desasignar
                        print("🔄 Probando desasignación...")
                        desasignar_data = {
                            'administrador_id': admin_id,
                            'recinto_id': recinto_id,
                            'asignar': False
                        }
                        
                        desasignar_response = session.post(
                            'http://localhost:5050/api/asignar-recinto',
                            json=desasignar_data,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        print(f"📡 Desasignar status: {desasignar_response.status_code}")
                        
                        if desasignar_response.status_code == 200:
                            desasignar_result = desasignar_response.json()
                            if desasignar_result.get('success'):
                                print(f"✅ Desasignación exitosa: {desasignar_result.get('message', 'Sin mensaje')}")
                                print("\n🎉 TODAS LAS FUNCIONALIDADES FUNCIONAN CORRECTAMENTE")
                                return True
                            else:
                                print(f"❌ Error en desasignación: {desasignar_result.get('error', 'Sin error')}")
                                return False
                        else:
                            print(f"❌ Desasignar falló: {desasignar_response.status_code}")
                            if desasignar_response.headers.get('content-type', '').startswith('application/json'):
                                error_data = desasignar_response.json()
                                print(f"   Error: {error_data}")
                            return False
                    else:
                        print(f"❌ Error en asignación: {asignar_result.get('error', 'Sin error')}")
                        return False
                else:
                    print(f"❌ Asignar falló: {asignar_response.status_code}")
                    if asignar_response.headers.get('content-type', '').startswith('application/json'):
                        error_data = asignar_response.json()
                        print(f"   Error: {error_data}")
                    return False
            else:
                print("⚠️  No se encontraron recintos para testing")
                return True
        else:
            print("⚠️  No hay datos suficientes para probar asignaciones")
            return True
        
    except Exception as e:
        print(f"❌ ERROR DURANTE TEST: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_checkbox_functionality()
    
    print("\n" + "="*50)
    if success:
        print("🎉 RESULTADO: TODOS LOS TESTS PASARON")
        print("✅ Los checkboxes deberían funcionar correctamente ahora")
    else:
        print("❌ RESULTADO: ALGUNOS TESTS FALLARON")
        print("🔧 Revisar los errores mostrados arriba")