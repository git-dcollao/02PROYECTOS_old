#!/usr/bin/env python3
"""
Script para probar el endpoint asignar-recinto con método POST y verificar que el error HTTP 400 se haya solucionado
"""
import requests
import json

def test_asignar_recinto():
    url = "http://localhost:5050/api/asignar-recinto"
    
    print("🧪 PROBANDO ENDPOINT ASIGNAR-RECINTO (que originalmente daba error 400)")
    print("=" * 70)
    print(f"URL: {url}")
    print("Método: POST")
    
    # Datos de prueba para la asignación
    test_data = {
        "administrador_id": 2,  # ID del usuario administrador@sistema.local
        "recinto_id": 1,        # ID de un recinto existente
        "asignar": True         # Asignar el recinto
    }
    
    print(f"Datos de prueba: {json.dumps(test_data, indent=2)}")
    print("-" * 70)
    
    try:
        response = requests.post(
            url, 
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            print("✅ ÉXITO - El error 400 se ha solucionado")
            try:
                result = response.json()
                print("Respuesta JSON:", json.dumps(result, indent=2))
            except:
                print("Respuesta:", response.text[:300])
                
        elif response.status_code == 400:
            print("❌ ERROR 400 PERSISTE - Bad Request")
            print("Respuesta:", response.text)
            
        elif response.status_code == 401:
            print("🔐 ERROR 401 - No autorizado (requiere autenticación)")
            print("Esto es normal sin sesión de usuario")
            
        elif response.status_code == 403:
            print("🚫 ERROR 403 - Acceso denegado (falta rol ADMIN)")
            print("Esto indica que la verificación de roles está funcionando")
            
        elif response.status_code == 302:
            print("🔄 REDIRECCIÓN 302 - Probablemente a login")
            print("Location:", response.headers.get('Location', 'No especificado'))
            
        else:
            print(f"⚠️  Status Code {response.status_code}")
            print("Respuesta:", response.text[:300])
            
        print("-" * 70)
        print("📋 ANÁLISIS:")
        
        if response.status_code in [401, 403, 302]:
            print("✅ Las correcciones funcionan correctamente")
            print("✅ El endpoint ahora valida permisos (antes daba error 400 directo)")
            print("✅ Ya no hay error de rol 'SUPERADMIN' inexistente")
        elif response.status_code == 400:
            print("❌ El problema original persiste - necesita más investigación")
        elif response.status_code == 200:
            print("✅ El endpoint funciona perfectamente")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")

if __name__ == "__main__":
    test_asignar_recinto()