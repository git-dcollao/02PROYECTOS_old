#!/usr/bin/env python3
"""
Monitor en tiempo real de cambios en la tabla page_permissions
Ejecutar este script y luego cambiar checkboxes para ver los cambios
"""

from app import create_app, db
from app.models import PagePermission, Page
import time
import os

def monitor_permissions():
    app = create_app()
    
    print("🔍 MONITOR DE PERMISOS EN TIEMPO REAL")
    print("=" * 50)
    print("Presiona Ctrl+C para detener")
    print("Cambia checkboxes en: http://localhost:5050/permissions/")
    print()
    
    last_count = 0
    last_permissions = set()
    
    try:
        while True:
            with app.app_context():
                # Obtener permisos actuales
                permissions = PagePermission.query.join(Page).all()
                current_count = len(permissions)
                
                current_permissions = set()
                for perm in permissions:
                    current_permissions.add(f"{perm.page.route}|{perm.role.value}")
                
                # Detectar cambios
                if current_count != last_count or current_permissions != last_permissions:
                    os.system('cls' if os.name == 'nt' else 'clear')  # Limpiar pantalla
                    
                    print("🔍 MONITOR DE PERMISOS EN TIEMPO REAL")
                    print("=" * 50)
                    print(f"⏰ {time.strftime('%H:%M:%S')} - Total: {current_count} permisos")
                    print()
                    
                    # Mostrar cambios
                    if last_permissions:
                        added = current_permissions - last_permissions
                        removed = last_permissions - current_permissions
                        
                        if added:
                            print("✅ PERMISOS AGREGADOS:")
                            for perm in added:
                                page, role = perm.split('|')
                                print(f"   + {role} → {page}")
                            print()
                        
                        if removed:
                            print("❌ PERMISOS ELIMINADOS:")
                            for perm in removed:
                                page, role = perm.split('|')
                                print(f"   - {role} → {page}")
                            print()
                    
                    # Mostrar estado actual
                    print("📊 ESTADO ACTUAL:")
                    pages_perms = {}
                    for perm in permissions:
                        page_route = perm.page.route
                        if page_route not in pages_perms:
                            pages_perms[page_route] = []
                        pages_perms[page_route].append(perm.role.value)
                    
                    for page_route, roles in sorted(pages_perms.items()):
                        print(f"   {page_route}: {', '.join(sorted(roles))}")
                    
                    print()
                    print("🔄 Esperando cambios... (Ctrl+C para salir)")
                    
                    last_count = current_count
                    last_permissions = current_permissions
            
            time.sleep(1)  # Verificar cada segundo
            
    except KeyboardInterrupt:
        print("\n👋 Monitor detenido")

if __name__ == "__main__":
    monitor_permissions()
