MOVE FILE test_backup_system.py to .test/test_backup_system.py
#!/usr/bin/env python3
"""
Test completo del sistema de backups
Programa de diagnóstico y corrección automática
"""

import requests
import json
import os
import sys
from datetime import datetime

class BackupSystemTester:
    def __init__(self):
        self.base_url = "http://localhost:5050"
        self.session = requests.Session()
        self.authenticated = False
        
    def login(self, email="admin@sistema.local", password="123456"):
        """Autenticar con el sistema"""
        print("🔐 Intentando autenticación...")
        
        # Primero obtener el formulario de login para el token CSRF
        login_page = self.session.get(f"{self.base_url}/auth/login")
        if login_page.status_code != 200:
            print(f"❌ Error al acceder a la página de login: {login_page.status_code}")
            return False
            
        # Buscar el token CSRF en el HTML
        csrf_token = None
        if 'csrf_token' in login_page.text:
            import re
            match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
            if match:
                csrf_token = match.group(1)
                print(f"🎫 Token CSRF obtenido: {csrf_token[:20]}...")
        
        # Enviar credenciales
        login_data = {
            'email': email,
            'password': password,
            'submit': 'Iniciar Sesión'
        }
        
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        response = self.session.post(f"{self.base_url}/auth/login", data=login_data, allow_redirects=True)
        
        print(f"📨 Respuesta de login: {response.status_code}")
        
        # Verificar si la autenticación fue exitosa
        # Si ya no estamos en la página de login, probablemente fue exitoso
        if response.status_code == 200:
            if "Iniciar Sesión" not in response.text and ("dashboard" in response.text.lower() or "admin" in response.text.lower() or "sistema" in response.text.lower()):
                print("✅ Autenticación exitosa")
                self.authenticated = True
                return True
            elif "error" in response.text.lower() or "incorrecto" in response.text.lower():
                print("❌ Credenciales incorrectas")
                return False
            else:
                print("⚠️ Respuesta ambigua, probando acceso a área protegida...")
                # Probar acceso a una página protegida
                test_response = self.session.get(f"{self.base_url}/admin/gestion_backup")
                if test_response.status_code == 200 and "Gestión de Backups" in test_response.text:
                    print("✅ Autenticación confirmada (acceso a área protegida)")
                    self.authenticated = True
                    return True
                else:
                    print("❌ No se puede acceder a áreas protegidas")
                    return False
        else:
            print(f"❌ Error de autenticación: {response.status_code}")
            return False
    
    def test_backup_list(self):
        """Probar endpoint de lista de backups"""
        print("\n📋 Probando lista de backups...")
        
        response = self.session.get(f"{self.base_url}/admin/backup/list")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    backups = data.get('backups', [])
                    print(f"✅ Lista obtenida: {len(backups)} backups encontrados")
                    
                    # Mostrar algunos detalles
                    for i, backup in enumerate(backups[:3]):
                        print(f"   📁 {i+1}. {backup.get('name', 'Sin nombre')} - {backup.get('size', 0)} bytes")
                    
                    if len(backups) > 3:
                        print(f"   ... y {len(backups) - 3} más")
                    
                    return True, backups
                else:
                    print(f"❌ Error en respuesta: {data.get('message', 'Sin mensaje')}")
                    return False, []
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                return False, []
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            if response.status_code == 302:
                print("   (Probable redirección a login)")
            return False, []
    
    def test_backup_creation(self):
        """Probar creación de backup"""
        print("\n💾 Probando creación de backup...")
        
        backup_data = {
            'backup_name': f'test_automatico_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Backup de prueba automática del sistema',
            'include_data': 'on',
            'compress': 'on'
        }
        
        response = self.session.post(f"{self.base_url}/admin/backup/create", data=backup_data)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Backup creado: {data.get('filename')} ({data.get('size', 0)} bytes)")
                    return True, data.get('filename')
                else:
                    print(f"❌ Error en creación: {data.get('message', 'Sin mensaje')}")
                    return False, None
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                return False, None
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False, None
    
    def test_backup_page_access(self):
        """Probar acceso a la página de gestión"""
        print("\n🌐 Probando acceso a página de gestión...")
        
        response = self.session.get(f"{self.base_url}/admin/gestion_backup")
        
        if response.status_code == 200:
            if "Gestión de Backups" in response.text:
                print("✅ Página de gestión accesible")
                
                # Verificar elementos importantes
                checks = [
                    ("backupsList", "Lista de backups"),
                    ("backupForm", "Formulario de creación"),
                    ("testBackupSystem", "Función de diagnóstico"),
                    ("BackupManager", "Clase JavaScript")
                ]
                
                for element, description in checks:
                    if element in response.text:
                        print(f"   ✅ {description}")
                    else:
                        print(f"   ❌ {description}")
                
                return True
            else:
                print("❌ Página no contiene el contenido esperado")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
    
    def test_backup_stats(self):
        """Probar estadísticas de backup"""
        print("\n📊 Probando estadísticas...")
        
        response = self.session.get(f"{self.base_url}/admin/backup/stats")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', {})
                    print(f"✅ Estadísticas obtenidas:")
                    print(f"   📁 Total backups: {stats.get('total_backups', 0)}")
                    print(f"   💾 Tamaño total: {stats.get('total_size', 0)} bytes")
                    print(f"   📅 Último backup: {stats.get('last_backup', 'N/A')}")
                    return True, stats
                else:
                    print(f"❌ Error en estadísticas: {data.get('message', 'Sin mensaje')}")
                    return False, {}
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                return False, {}
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False, {}
    
    def run_full_test(self):
        """Ejecutar batería completa de pruebas"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA DE BACKUPS")
        print("=" * 60)
        
        # 1. Autenticación
        if not self.login():
            print("\n❌ No se pudo autenticar. Verifique credenciales.")
            return False
        
        # 2. Acceso a página
        if not self.test_backup_page_access():
            print("\n❌ Problema con la página de gestión.")
        
        # 3. Lista de backups
        success, backups = self.test_backup_list()
        if not success:
            print("\n❌ Problema con la lista de backups.")
        
        # 4. Estadísticas
        success, stats = self.test_backup_stats()
        if not success:
            print("\n❌ Problema con las estadísticas.")
        
        # 5. Creación de backup (opcional)
        print("\n¿Desea probar la creación de un backup? (s/n): ", end="")
        try:
            if input().lower().startswith('s'):
                success, filename = self.test_backup_creation()
                if success:
                    print(f"✅ Backup de prueba creado: {filename}")
        except:
            pass
        
        print("\n" + "=" * 60)
        print("🎯 DIAGNÓSTICO COMPLETADO")
        
        return True

def main():
    """Función principal"""
    print("🔧 SISTEMA DE DIAGNÓSTICO DE BACKUPS")
    print("Desarrollado por: Programador Senior")
    print("-" * 50)
    
    tester = BackupSystemTester()
    
    try:
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\n\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    
    print("\n👋 Diagnóstico finalizado")

if __name__ == "__main__":
    main()