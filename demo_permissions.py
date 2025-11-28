#!/usr/bin/env python3
"""
Demostración Completa del Sistema de Permisos por Página
Este script muestra cómo funciona el nuevo sistema de gestión de permisos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Trabajador, UserRole
from app.routes.permissions_routes import permission_manager

def show_system_overview():
    """Mostrar resumen del sistema de permisos"""
    print("\n" + "="*70)
    print("🛡️  **SISTEMA DE GESTIÓN DE PERMISOS POR PÁGINA**")
    print("="*70)
    
    print("\n🎯 **CARACTERÍSTICAS:**")
    print("   ✅ Gestión visual de permisos por página")
    print("   ✅ Control granular por rol de usuario") 
    print("   ✅ Interfaz web intuitiva")
    print("   ✅ API REST para actualizaciones dinámicas")
    print("   ✅ Sistema de categorías organizadas")
    print("   ✅ Decoradores automáticos de seguridad")
    
    print("\n🌐 **ACCESO AL SISTEMA:**")
    print("   📱 Interfaz Web: http://localhost:5050/permissions/")
    print("   👤 Login como Admin: admin@sistema.com / admin123")
    print("   🔐 Solo usuarios ADMIN y SUPERADMIN pueden acceder")
    
    print("\n🏗️  **ARQUITECTURA:**")
    print("   📁 Rutas: app/routes/permissions_routes.py")
    print("   🎨 Templates: app/templates/permissions/index.html")
    print("   💾 Datos: page_permissions.json (configuración dinámica)")
    print("   🔧 Decoradores: @check_page_permission('ruta.pagina')")

def show_current_permissions():
    """Mostrar permisos actuales del sistema"""
    print("\n📋 **CONFIGURACIÓN ACTUAL DE PERMISOS**")
    print("="*50)
    
    permissions = permission_manager.load_permissions()
    categories = permission_manager.get_pages_by_category()
    
    total_pages = len(permissions)
    total_categories = len(categories)
    
    print(f"📊 Total de páginas: {total_pages}")
    print(f"📊 Total de categorías: {total_categories}")
    
    print("\n🏷️  **PÁGINAS POR CATEGORÍA:**")
    
    for category, pages in categories.items():
        print(f"\n📁 **{category.upper()}** ({len(pages)} páginas)")
        
        for page in pages[:3]:  # Mostrar solo las primeras 3 por brevedad
            roles_str = " ".join([f"[{role}]" for role in page['roles']])
            print(f"   • {page['name']}")
            print(f"     Ruta: {page['route']}")
            print(f"     Roles: {roles_str}")
        
        if len(pages) > 3:
            print(f"   ... y {len(pages) - 3} páginas más")

def show_usage_examples():
    """Mostrar ejemplos de uso"""
    print("\n💡 **EJEMPLOS DE USO**")
    print("="*40)
    
    print("\n🔧 **1. Aplicar Decorador en Rutas:**")
    print("""
from app.routes.permissions_routes import check_page_permission

@app.route('/mi-pagina-especial')
@login_required
@check_page_permission('especial.mi_pagina')
def mi_pagina_especial():
    return "Solo usuarios autorizados pueden ver esto"
""")
    
    print("\n🎨 **2. Control en Templates:**")
    print("""
<!-- En cualquier template -->
{% if can_access_page(current_user.rol.name, 'reportes.financieros') %}
    <a href="{{ url_for('reportes.financieros') }}" class="btn btn-primary">
        Ver Reportes Financieros
    </a>
{% endif %}
""")
    
    print("\n🌐 **3. Gestión Web:**")
    print("   • Ir a http://localhost:5050/permissions/")
    print("   • Hacer clic en los checkboxes de roles")
    print("   • Presionar 'Guardar' para aplicar cambios")
    print("   • Agregar nuevas páginas con el botón '+ Agregar Página'")
    
    print("\n🔄 **4. Actualización Dinámica:**")
    print("   • Los cambios se guardan en page_permissions.json")
    print("   • No requiere reiniciar la aplicación")
    print("   • Los cambios son inmediatos")

def demonstrate_api():
    """Mostrar cómo usar la API REST"""
    print("\n🔌 **API REST ENDPOINTS**")
    print("="*35)
    
    print("\n📡 **POST /permissions/api/update**")
    print("Actualizar permisos de una página:")
    print("""
curl -X POST http://localhost:5050/permissions/api/update \\
  -H "Content-Type: application/json" \\
  -d '{
    "page_route": "proyectos.lista",
    "roles": ["ADMIN", "SUPERVISOR"]
  }'
""")
    
    print("\n➕ **POST /permissions/api/add-page**")
    print("Agregar nueva página:")
    print("""
curl -X POST http://localhost:5050/permissions/api/add-page \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Mi Nueva Página",
    "route": "modulo.nueva_pagina", 
    "category": "Mi Categoría",
    "description": "Descripción de la página",
    "roles": ["ADMIN"]
  }'
""")
    
    print("\n🗑️  **POST /permissions/api/delete-page**")
    print("Eliminar página:")
    print("""
curl -X POST http://localhost:5050/permissions/api/delete-page \\
  -H "Content-Type: application/json" \\
  -d '{
    "page_route": "modulo.pagina_a_eliminar"
  }'
""")

def create_demo_pages():
    """Crear páginas de demostración"""
    print("\n🎭 **CREAR PÁGINAS DE DEMOSTRACIÓN**")
    print("="*45)
    
    demo_pages = {
        'demo.dashboard_ejecutivo': {
            'name': 'Dashboard Ejecutivo',
            'category': 'Demo',
            'roles': ['SUPERADMIN', 'ADMIN'],
            'description': 'Dashboard con métricas ejecutivas y KPIs estratégicos'
        },
        'demo.informes_detallados': {
            'name': 'Informes Detallados',
            'category': 'Demo',
            'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR'],
            'description': 'Informes detallados con análisis profundo de datos'
        },
        'demo.panel_usuario': {
            'name': 'Panel de Usuario',
            'category': 'Demo',
            'roles': ['SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'USUARIO'],
            'description': 'Panel básico accesible para todos los usuarios'
        },
        'demo.configuracion_avanzada': {
            'name': 'Configuración Avanzada',
            'category': 'Demo',
            'roles': ['SUPERADMIN'],
            'description': 'Configuraciones críticas del sistema - Solo SuperAdmin'
        }
    }
    
    # Cargar permisos existentes
    permissions = permission_manager.load_permissions()
    
    pages_added = 0
    for route, page_data in demo_pages.items():
        if route not in permissions:
            permissions[route] = page_data
            pages_added += 1
            print(f"✅ Agregada: {page_data['name']} ({' '.join(page_data['roles'])})")
        else:
            print(f"⚠️  Ya existe: {page_data['name']}")
    
    if pages_added > 0:
        permission_manager.save_permissions(permissions)
        print(f"\n🎉 {pages_added} páginas de demostración agregadas exitosamente")
        print("💡 Recarga la página http://localhost:5050/permissions/ para verlas")
    else:
        print("\n📝 Todas las páginas de demostración ya existen")

def show_security_features():
    """Mostrar características de seguridad"""
    print("\n🔒 **CARACTERÍSTICAS DE SEGURIDAD**")
    print("="*45)
    
    print("✅ **Control de Acceso Basado en Roles (RBAC)**")
    print("   • 4 niveles: USUARIO → SUPERVISOR → ADMIN → SUPERADMIN")
    print("   • Herencia de permisos: roles superiores incluyen inferiores")
    
    print("\n✅ **Validación Multi-Capa**")
    print("   • Decoradores de ruta: @check_page_permission()")
    print("   • Validación en templates: {% if can_access_page() %}")
    print("   • Redirección automática si sin permisos")
    
    print("\n✅ **Gestión Centralizada**")
    print("   • Configuración en archivo JSON único")
    print("   • Interfaz web para administradores")
    print("   • Auditoría de cambios de permisos")
    
    print("\n✅ **Escalabilidad**")
    print("   • Agregar páginas sin código adicional")
    print("   • Categorización automática") 
    print("   • API REST para integraciones")

def main():
    """Menú principal de demostración"""
    app = create_app()
    with app.app_context():
        while True:
            print("\n" + "="*70)
            print("🎯 **DEMOSTRACIÓN: SISTEMA DE PERMISOS POR PÁGINA**")
            print("="*70)
            print("1️⃣  📖 Ver resumen del sistema")
            print("2️⃣  📋 Ver configuración actual")
            print("3️⃣  💡 Ver ejemplos de uso")
            print("4️⃣  🔌 Ver documentación API")
            print("5️⃣  🎭 Crear páginas de demostración")
            print("6️⃣  🔒 Ver características de seguridad")
            print("7️⃣  🌐 Abrir interfaz web")
            print("8️⃣  🚪 Salir")
            
            choice = input("\n🔢 Selecciona una opción (1-8): ").strip()
            
            if choice == '1':
                show_system_overview()
            elif choice == '2':
                show_current_permissions()
            elif choice == '3':
                show_usage_examples()
            elif choice == '4':
                demonstrate_api()
            elif choice == '5':
                create_demo_pages()
            elif choice == '6':
                show_security_features()
            elif choice == '7':
                print("\n🌐 **ABRIENDO INTERFAZ WEB**")
                print("=" * 30)
                print("📱 URL: http://localhost:5050/permissions/")
                print("👤 Usuario: admin@sistema.com")
                print("🔑 Contraseña: admin123")
                print("\n💡 Copia la URL en tu navegador para acceder")
                
                # Intentar abrir automáticamente
                try:
                    import webbrowser
                    webbrowser.open('http://localhost:5050/auth/login')
                    print("✅ Navegador abierto automáticamente")
                except:
                    print("⚠️  Abre manualmente la URL en tu navegador")
            elif choice == '8':
                print("\n👋 ¡Gracias por probar el Sistema de Permisos!")
                print("📧 ¿Preguntas? Consulta la documentación en el código")
                break
            else:
                print("❌ Opción inválida")
            
            input("\n⏎ Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
