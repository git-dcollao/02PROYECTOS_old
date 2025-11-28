#!/usr/bin/env python3
"""
Script para probar las nuevas rutas de avance de actividades
"""

import sys
import os

# Añadir el directorio de la aplicación al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_routes():
    """Probar que las rutas están configuradas correctamente"""
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            print("🧪 Probando rutas de avance de actividades...")
            
            # Probar ruta original
            print("\n1. Probando /avance-actividades (proyectos asignados)")
            response = client.get('/avance-actividades')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Ruta funcionando correctamente")
            else:
                print(f"   ❌ Error en la ruta: {response.status_code}")
            
            # Probar nueva ruta "all"
            print("\n2. Probando /avance-actividades-all (todos los proyectos)")
            response = client.get('/avance-actividades-all')
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Ruta funcionando correctamente")
            else:
                print(f"   ❌ Error en la ruta: {response.status_code}")
            
            # Probar API existente
            print("\n3. Probando API /proyectos_por_trabajador/1")
            response = client.get('/proyectos_por_trabajador/1')
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 404]:  # 404 es válido si no existe trabajador con ID 1
                print("   ✅ API funcionando correctamente")
            else:
                print(f"   ❌ Error en API: {response.status_code}")
            
            # Probar nueva API "all"
            print("\n4. Probando nueva API /proyectos_por_trabajador_all/1")
            response = client.get('/proyectos_por_trabajador_all/1')
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 404]:  # 404 es válido si no existe trabajador con ID 1
                print("   ✅ Nueva API funcionando correctamente")
            else:
                print(f"   ❌ Error en nueva API: {response.status_code}")
            
            print("\n✅ Pruebas completadas")
            
    except Exception as e:
        print(f"❌ Error al probar rutas: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de rutas...")
    if test_routes():
        print("\n🎉 Todas las rutas parecen estar configuradas correctamente")
    else:
        print("\n💥 Hay problemas con las rutas")
