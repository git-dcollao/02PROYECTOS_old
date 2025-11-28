#!/usr/bin/env python3
"""
Script para listar todas las rutas disponibles en la aplicación Flask
"""
from app import create_app

def list_routes():
    app = create_app()
    
    print("🔍 RUTAS DISPONIBLES EN LA APLICACIÓN")
    print("=" * 60)
    
    routes = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        routes.append((rule.rule, methods, rule.endpoint))
    
    # Ordenar por ruta
    routes.sort(key=lambda x: x[0])
    
    gestion_routes = []
    api_routes = []
    other_routes = []
    
    for route, methods, endpoint in routes:
        if 'gestion' in route:
            gestion_routes.append((route, methods, endpoint))
        elif route.startswith('/api'):
            api_routes.append((route, methods, endpoint))
        else:
            other_routes.append((route, methods, endpoint))
    
    print("\n📋 RUTAS DE GESTIÓN:")
    print("-" * 40)
    for route, methods, endpoint in gestion_routes:
        print(f"{route:<35} [{methods:<10}] {endpoint}")
    
    print("\n🔗 RUTAS API:")
    print("-" * 40)
    for route, methods, endpoint in api_routes:
        print(f"{route:<35} [{methods:<10}] {endpoint}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   • Total rutas: {len(routes)}")
    print(f"   • Rutas gestión: {len(gestion_routes)}")
    print(f"   • Rutas API: {len(api_routes)}")
    print(f"   • Otras rutas: {len(other_routes)}")
    
    # Buscar específicamente las rutas que nos interesan
    target_routes = ['/gestion-administradores', '/api/matriz-administradores', '/api/asignar-recinto']
    print(f"\n🎯 VERIFICACIÓN DE RUTAS OBJETIVO:")
    print("-" * 40)
    for target in target_routes:
        found = any(route == target for route, _, _ in routes)
        status = "✅ ENCONTRADA" if found else "❌ NO ENCONTRADA"
        print(f"{target:<35} {status}")

if __name__ == "__main__":
    try:
        list_routes()
    except Exception as e:
        print(f"❌ Error al listar rutas: {e}")
        import traceback
        traceback.print_exc()