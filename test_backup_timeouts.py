#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema de backup/restore funciona con los nuevos timeouts
"""
import requests
import time
import sys
import json

def test_backup_system():
    """Probar el sistema de backup/restore con timeouts extendidos"""
    
    base_url = "http://localhost:5050"
    
    print("🧪 Probando sistema de backup con timeouts extendidos...")
    
    # 1. Verificar que la aplicación está funcionando
    print("\n1. Verificando estado de la aplicación...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Aplicación: {health_data.get('status', 'unknown')}")
            print(f"   ✅ Base de datos: {health_data.get('database', 'unknown')}")
        else:
            print(f"   ❌ Error en health check: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error conectando a la aplicación: {e}")
        return False
    
    # 2. Crear una sesión para mantener la autenticación
    print("\n2. Iniciando sesión como administrador...")
    session = requests.Session()
    
    try:
        # Obtener página de login para el token CSRF
        login_page = session.get(f"{base_url}/auth/login")
        if login_page.status_code != 200:
            print(f"   ❌ Error obteniendo página de login: {login_page.status_code}")
            return False
        
        # Buscar token CSRF en la página
        csrf_token = None
        for line in login_page.text.split('\\n'):
            if 'csrf_token' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
        
        if not csrf_token:
            print("   ❌ No se pudo obtener token CSRF")
            return False
        
        # Hacer login
        login_data = {
            'email': 'admin@sistema.local',
            'password': 'admin123',
            'csrf_token': csrf_token,
            'submit': 'Iniciar Sesión'
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"   ❌ Error en login: {login_response.status_code}")
            return False
        
        # Verificar que el login fue exitoso revisando si hay redirección o contenido del dashboard
        if "dashboard" in login_response.url or "Dashboard" in login_response.text:
            print("   ✅ Login exitoso")
        else:
            print("   ❌ Login falló - verificar credenciales")
            return False
        
    except Exception as e:
        print(f"   ❌ Error en proceso de login: {e}")
        return False
    
    # 3. Probar la creación de backup
    print("\n3. Probando creación de backup...")
    try:
        # Obtener página de backup para token CSRF
        backup_page = session.get(f"{base_url}/admin/backup")
        if backup_page.status_code != 200:
            print(f"   ❌ Error accediendo a página de backup: {backup_page.status_code}")
            return False
        
        # Buscar token CSRF
        csrf_token = None
        for line in backup_page.text.split('\\n'):
            if 'csrf_token' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
        
        if not csrf_token:
            print("   ❌ No se pudo obtener token CSRF para backup")
            return False
        
        # Crear backup de prueba
        backup_data = {
            'name': f'Test_Timeout_{int(time.time())}',
            'description': 'Backup de prueba para verificar timeouts',
            'tipo': 'manual',
            'csrf_token': csrf_token
        }
        
        print(f"   🔄 Creando backup: {backup_data['name']}")
        
        # Usar timeout largo para la creación del backup
        backup_response = session.post(
            f"{base_url}/admin/backup/create", 
            data=backup_data,
            timeout=300  # 5 minutos de timeout
        )
        
        if backup_response.status_code == 200:
            backup_result = backup_response.json()
            if backup_result.get('success'):
                print(f"   ✅ Backup creado: {backup_result.get('filename')}")
                print(f"   📊 Tamaño: {backup_result.get('size')} bytes")
                return True
            else:
                print(f"   ❌ Error creando backup: {backup_result.get('message')}")
                return False
        else:
            print(f"   ❌ Error HTTP creando backup: {backup_response.status_code}")
            print(f"   Respuesta: {backup_response.text[:200]}...")
            return False
        
    except requests.exceptions.Timeout:
        print("   ❌ Timeout creando backup - los timeouts pueden necesitar más ajustes")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado creando backup: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de timeout para sistema de backup\\n")
    
    # Esperar a que la aplicación esté lista
    print("⏳ Esperando que la aplicación esté lista...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:5050/health", timeout=5)
            if response.status_code == 200:
                print("✅ Aplicación lista")
                break
        except:
            print(f"   Intento {i+1}/10...")
            time.sleep(2)
    else:
        print("❌ La aplicación no está respondiendo")
        return 1
    
    # Ejecutar pruebas
    success = test_backup_system()
    
    if success:
        print("\\n🎉 ¡Todas las pruebas pasaron! Los timeouts están funcionando correctamente.")
        return 0
    else:
        print("\\n❌ Algunas pruebas fallaron. Revisar la configuración de timeouts.")
        return 1

if __name__ == "__main__":
    sys.exit(main())