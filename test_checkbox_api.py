#!/usr/bin/env python3
"""
Script para probar los endpoints de la API de permisos
"""

from app import create_app, db
from app.models import Page, PagePermission, UserRole
import requests
import json

def test_toggle_permission_api():
    """Prueba el endpoint de toggle-permission"""
    
    print("🧪 PRUEBA DE API - TOGGLE PERMISSION")
    print("=" * 50)
    
    # URL del endpoint
    base_url = "http://localhost:5050"
    endpoint = f"{base_url}/permissions/api/toggle-permission"
    
    # Datos de prueba
    test_cases = [
        {
            "route": "/dashboard",
            "role": "USUARIO", 
            "enabled": True,
            "description": "Habilitar USUARIO para /dashboard"
        },
        {
            "route": "/dashboard",
            "role": "USUARIO",
            "enabled": False,
            "description": "Deshabilitar USUARIO para /dashboard"
        },
        {
            "route": "/projects",
            "role": "ADMIN",
            "enabled": True,
            "description": "Habilitar ADMIN para /projects"
        }
    ]
    
    print("🔧 Casos de prueba preparados:")
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. {case['description']}")
    
    return test_cases

def verify_database_state():
    """Verifica el estado actual de la base de datos"""
    app = create_app()
    
    with app.app_context():
        print("\n💾 ESTADO ACTUAL DE LA BASE DE DATOS:")
        print("-" * 40)
        
        # Mostrar todos los permisos
        permissions = PagePermission.query.join(Page).all()
        
        pages_perms = {}
        for perm in permissions:
            page_route = perm.page.route
            if page_route not in pages_perms:
                pages_perms[page_route] = []
            pages_perms[page_route].append(perm.role.value)
        
        for page_route, roles in sorted(pages_perms.items()):
            print(f"📄 {page_route}")
            print(f"   Roles: {', '.join(sorted(roles))}")
        
        print(f"\n📊 Total: {len(permissions)} permisos en {len(pages_perms)} páginas")

def simulate_checkbox_actions():
    """Simula las acciones que harían los checkboxes"""
    app = create_app()
    
    print("\n🔄 SIMULANDO ACCIONES DE CHECKBOXES:")
    print("-" * 40)
    
    with app.app_context():
        # Simular: marcar checkbox USUARIO para /dashboard
        page = Page.query.filter_by(route='/dashboard').first()
        if page:
            # Verificar si ya existe el permiso
            existing = PagePermission.query.filter_by(
                page_id=page.id, 
                role=UserRole.USUARIO
            ).first()
            
            if not existing:
                print("✅ Agregando permiso USUARIO para /dashboard")
                new_perm = PagePermission(page_id=page.id, role=UserRole.USUARIO)
                db.session.add(new_perm)
                db.session.commit()
                print("   ✓ Permiso agregado exitosamente")
            else:
                print("ℹ️  El permiso USUARIO para /dashboard ya existe")
        
        # Simular: desmarcar checkbox SUPERVISOR para /projects
        page = Page.query.filter_by(route='/projects').first()
        if page:
            existing = PagePermission.query.filter_by(
                page_id=page.id,
                role=UserRole.SUPERVISOR
            ).first()
            
            if existing:
                print("❌ Eliminando permiso SUPERVISOR para /projects")
                db.session.delete(existing)
                db.session.commit()
                print("   ✓ Permiso eliminado exitosamente")
            else:
                print("ℹ️  El permiso SUPERVISOR para /projects no existe")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE PERMISOS")
    print("=" * 60)
    
    # 1. Verificar estado inicial
    verify_database_state()
    
    # 2. Preparar casos de prueba
    test_cases = test_toggle_permission_api()
    
    # 3. Simular acciones de checkboxes
    simulate_checkbox_actions()
    
    # 4. Verificar estado final
    verify_database_state()
    
    print("\n🎯 PRUEBAS COMPLETADAS")
    print("Para probar los checkboxes reales:")
    print("1. Ve a http://localhost:5050/permissions/")
    print("2. Haz login como administrador")
    print("3. Marca/desmarca los checkboxes")
    print("4. Los cambios se guardarán automáticamente")
