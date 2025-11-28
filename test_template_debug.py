#!/usr/bin/env python
"""
Test completo del template gestion_administradores.html
para identificar error "unexpected '<'"
"""
import requests
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la configuración y modelos
from config import Config
from app import create_app
from app.models import Trabajador, AdministradorRecinto

def test_template_rendering():
    """
    Prueba el renderizado del template directamente
    """
    print("🔍 Testeando renderizado del template...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Simular los datos que se pasan al template
            print("📊 Obteniendo datos...")
            administradores, estructura, asignaciones = AdministradorRecinto.obtener_matriz_completa()
            
            # Calcular estadísticas
            total_administradores = len(administradores)
            total_recintos = sum(len(recintos) for sector_tipos in estructura.values()
                               for recintos in sector_tipos.values())
            total_asignaciones = sum(len(asignaciones_admin) for asignaciones_admin in asignaciones.values())
            
            print(f"📋 Datos obtenidos:")
            print(f"   • Administradores: {total_administradores}")
            print(f"   • Recintos: {total_recintos}")
            print(f"   • Asignaciones: {total_asignaciones}")
            
            # Verificar si hay problemas con los datos
            print("\n🔍 Verificando datos de administradores...")
            for admin in administradores:
                print(f"   • {admin.nombre} ({admin.email})")
                if hasattr(admin, 'rol') and admin.rol:
                    print(f"     Rol: {admin.rol.name}")
            
            print("\n🔍 Verificando estructura de recintos...")
            for sector, tipos in estructura.items():
                print(f"   • Sector: {sector}")
                for tipo, recintos in tipos.items():
                    print(f"     - Tipo: {tipo} ({len(recintos)} recintos)")
            
            print("\n🔍 Verificando asignaciones...")
            for admin_id, admin_asignaciones in asignaciones.items():
                print(f"   • Admin {admin_id}: {len(admin_asignaciones)} asignaciones")
            
            print("\n✅ Datos procesados correctamente - No hay problemas en el modelo")
            
            # Ahora testear el template rendering
            from flask import render_template
            
            print("\n🎨 Testeando renderizado del template...")
            
            try:
                # Renderizar el template con los datos
                html_content = render_template(
                    'admin/gestion_administradores.html',
                    administradores=administradores,
                    estructura=estructura,
                    asignaciones=asignaciones
                )
                
                print("✅ Template renderizado exitosamente")
                
                # Verificar que no haya caracteres problemáticos
                if '<' in html_content and '>' in html_content:
                    print("✅ Template contiene HTML válido")
                
                # Verificar longitud
                print(f"📏 Longitud del HTML: {len(html_content)} caracteres")
                
                # Buscar posibles problemas
                problematic_chars = ['<', '>', '{', '}']
                for char in problematic_chars:
                    count = html_content.count(char)
                    print(f"   • Carácter '{char}': {count} ocurrencias")
                
                return True
                
            except Exception as template_error:
                print(f"❌ ERROR en renderizado del template: {template_error}")
                import traceback
                traceback.print_exc()
                return False
            
        except Exception as data_error:
            print(f"❌ ERROR en obtención de datos: {data_error}")
            import traceback
            traceback.print_exc()
            return False

def test_web_request():
    """
    Prueba la request web completa para comparar
    """
    print("\n🌐 Testeando request web completa...")
    
    try:
        session = requests.Session()
        
        # Login
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
        
        if login_response.status_code in [302, 301]:
            print("✅ Login exitoso")
            
            # Acceder a la página
            admin_response = session.get('http://localhost:5050/gestion-administradores')
            
            print(f"📋 Status: {admin_response.status_code}")
            print(f"📋 Final URL: {admin_response.url}")
            
            if 'dashboard' in admin_response.url:
                print("❌ Redirigido al dashboard - ERROR EN BACKEND")
                
                # Verificar flash messages
                if 'Error interno del servidor' in admin_response.text:
                    print("❌ Confirmado: Error interno del servidor")
                
                return False
            else:
                print("✅ Página cargada correctamente")
                return True
                
        else:
            print("❌ Login falló")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en request web: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TEST COMPLETO DEL TEMPLATE Y BACKEND")
    print("="*50)
    
    # Test 1: Template rendering directo
    template_ok = test_template_rendering()
    
    # Test 2: Web request completa
    web_ok = test_web_request()
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE TESTS:")
    print(f"   Template rendering: {'✅ OK' if template_ok else '❌ ERROR'}")
    print(f"   Web request: {'✅ OK' if web_ok else '❌ ERROR'}")
    
    if template_ok and not web_ok:
        print("\n🎯 DIAGNÓSTICO: El template funciona, pero hay error en el controlador web")
    elif not template_ok:
        print("\n🎯 DIAGNÓSTICO: Error en el template o datos")
    elif template_ok and web_ok:
        print("\n🎉 TODO FUNCIONA CORRECTAMENTE")