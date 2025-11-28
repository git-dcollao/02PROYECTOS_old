#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_csrf_avances():
    print("🧪 PROBANDO CSRF TOKEN EN GUARDAR AVANCES")
    print("=" * 60)
    
    base_url = "http://localhost:5050"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Obtener página de login para conseguir CSRF token
        print("1. 🔐 Obteniendo CSRF token desde login...")
        login_page = session.get(f"{base_url}/auth/login")
        
        if login_page.status_code != 200:
            print(f"❌ Error al acceder login: {login_page.status_code}")
            return
        
        # Extraer CSRF token
        import re
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
        if not csrf_match:
            print("❌ No se encontró CSRF token en página de login")
            return
            
        csrf_token = csrf_match.group(1)
        print(f"✅ CSRF Token obtenido: {csrf_token[:20]}...")
        
        # 2. Login con usuario de prueba
        print("\n2. 🔑 Haciendo login...")
        login_data = {
            'email': 'arq01@temp.com',
            'password': 'Maho2025',  # Password de los trabajadores temporales
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200 and login_response.status_code != 302:
            print(f"❌ Error en login: {login_response.status_code}")
            return
            
        # 3. Obtener página de avance-actividades para obtener CSRF token fresco
        print("\n3. 📄 Obteniendo página avance-actividades...")
        avance_page = session.get(f"{base_url}/avance-actividades")
        
        if avance_page.status_code != 200:
            print(f"❌ Error al acceder avance-actividades: {avance_page.status_code}")
            return
            
        # Extraer nuevo CSRF token de meta tag
        meta_csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)">', avance_page.text)
        if meta_csrf_match:
            csrf_token_meta = meta_csrf_match.group(1)
            print(f"✅ CSRF Token desde meta: {csrf_token_meta[:20]}...")
        else:
            print("❌ No se encontró CSRF token en meta tag")
            return
        
        # 4. Probar petición con diferentes headers CSRF
        print("\n4. 🧪 Probando peticiones con CSRF...")
        
        test_payload = {
            "trabajador_id": 7,  # ID del trabajador ARQ01
            "proyecto_id": 2,    # ID de proyecto de prueba
            "fecha_registro": "2025-11-18",
            "avances": [
                {
                    "edt": "1.1",
                    "progreso_anterior": 0,
                    "progreso_nuevo": 25
                }
            ]
        }
        
        # Probar con X-CSRFToken
        print("\n   🔍 Probando con header X-CSRFToken...")
        headers_csrf = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token_meta
        }
        
        response1 = session.post(
            f"{base_url}/guardar_avances_trabajador", 
            json=test_payload,
            headers=headers_csrf
        )
        print(f"   Status: {response1.status_code}")
        print(f"   Response: {response1.text[:200]}...")
        
        if response1.status_code == 200:
            print("   ✅ Funciona con X-CSRFToken")
        else:
            # Probar con X-CSRF-TOKEN (diferente caso)
            print("\n   🔍 Probando con header X-CSRF-TOKEN...")
            headers_csrf2 = {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrf_token_meta
            }
            
            response2 = session.post(
                f"{base_url}/guardar_avances_trabajador", 
                json=test_payload,
                headers=headers_csrf2
            )
            print(f"   Status: {response2.status_code}")
            print(f"   Response: {response2.text[:200]}...")
            
            if response2.status_code == 200:
                print("   ✅ Funciona con X-CSRF-TOKEN")
            else:
                # Probar con csrf_token en el JSON
                print("\n   🔍 Probando con csrf_token en JSON...")
                test_payload_with_csrf = test_payload.copy()
                test_payload_with_csrf['csrf_token'] = csrf_token_meta
                
                response3 = session.post(
                    f"{base_url}/guardar_avances_trabajador", 
                    json=test_payload_with_csrf,
                    headers={'Content-Type': 'application/json'}
                )
                print(f"   Status: {response3.status_code}")
                print(f"   Response: {response3.text[:200]}...")
                
                if response3.status_code == 200:
                    print("   ✅ Funciona con csrf_token en JSON")
                else:
                    print("   ❌ Ningún método funcionó")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_csrf_avances()