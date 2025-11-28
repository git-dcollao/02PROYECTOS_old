#!/usr/bin/env python3
"""
Script para probar los endpoints corregidos y verificar que el error HTTP 400 se haya solucionado
"""
import requests
import json

def test_endpoint(url, description):
    print(f"\n{'='*50}")
    print(f"Probando: {description}")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            print("✅ ÉXITO - Endpoint funcionando correctamente")
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    data = response.json()
                    print(f"Respuesta JSON válida con {len(data)} elementos" if isinstance(data, list) else "Respuesta JSON válida")
                except:
                    print("Respuesta no es JSON válido")
            else:
                print(f"Respuesta HTML/texto de {len(response.text)} caracteres")
        elif response.status_code == 400:
            print("❌ ERROR 400 - Bad Request (el problema persiste)")
            print("Respuesta:", response.text[:200])
        elif response.status_code == 302:
            print("🔄 REDIRECCIÓN - Probablemente requiere autenticación")
            print("Location:", response.headers.get('Location', 'No especificado'))
        else:
            print(f"⚠️  Status Code {response.status_code}")
            print("Respuesta:", response.text[:200])
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")

if __name__ == "__main__":
    base_url = "http://localhost:5050"
    
    # Probar los endpoints que fueron corregidos
    endpoints = [
        ("/gestion-administradores", "Gestión de Administradores (corregido)"),
        ("/api/matriz-administradores", "API Matriz Administradores (corregido)"), 
        ("/api/asignar-recinto", "API Asignar Recinto (corregido - era el que daba error 400)"),
        ("/", "Página principal (referencia)")
    ]
    
    print("🧪 PROBANDO ENDPOINTS CORREGIDOS")
    print("=" * 60)
    
    for endpoint, description in endpoints:
        test_endpoint(f"{base_url}{endpoint}", description)
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)