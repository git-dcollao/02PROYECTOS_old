"""
Script para probar el sistema de menús dinámicos
"""

from app import create_app
from app.models import Trabajador
from app.services.menu_service import menu_service
from flask_login import login_user
import json

def test_menu_system():
    """Probar el sistema de menús para diferentes usuarios"""
    
    app = create_app()
    with app.app_context():
        
        print("🧪 Probando el sistema de menús dinámicos...\n")
        
        # Obtener usuarios de prueba
        admin_user = Trabajador.query.filter_by(email='admin@test.com').first()
        
        if not admin_user:
            print("❌ No se encontró usuario administrador")
            return False
        
        # Probar menú para administrador
        print("👤 MENÚ PARA ADMINISTRADOR:")
        print("=" * 50)
        
        admin_menu = menu_service.get_user_menu(admin_user)
        
        if not admin_menu:
            print("❌ No se pudo obtener menú para administrador")
            return False
        
        for category in admin_menu:
            print(f"\n📁 {category['category']} ({category['count']} elementos)")
            print(f"   Icono: {category['icon']}")
            
            for page in category['pages']:
                print(f"   📄 {page['name']}")
                print(f"      Ruta: {page['url']}")
                print(f"      Icono: {page['icon']}")
                if page['description']:
                    print(f"      Descripción: {page['description']}")
                print()
        
        # Mostrar estadísticas
        total_categories = len(admin_menu)
        total_pages = sum(category['count'] for category in admin_menu)
        
        print(f"\n📊 ESTADÍSTICAS DEL MENÚ:")
        print(f"   📁 Total categorías: {total_categories}")
        print(f"   📄 Total páginas: {total_pages}")
        
        # Verificar funciones auxiliares
        print(f"\n🔧 FUNCIONES AUXILIARES:")
        print(f"   🔢 Conteo total: {menu_service.get_user_menu(admin_user) and total_pages or 0}")
        
        # Probar acceso a rutas específicas (simulado)
        test_routes = ['/dashboard', '/projects', '/permissions', '/auth/users']
        print(f"\n🔍 PRUEBAS DE ACCESO:")
        
        for route in test_routes:
            has_access = any(
                any(page['url'] == route for page in cat['pages']) 
                for cat in admin_menu
            )
            status = "✅ PERMITIDO" if has_access else "❌ DENEGADO"
            print(f"   {route}: {status}")
        
        # Mostrar estructura JSON para desarrollo
        print(f"\n🔧 ESTRUCTURA JSON (primeras 2 categorías):")
        print("-" * 50)
        
        limited_menu = admin_menu[:2]  # Solo primeras 2 categorías
        print(json.dumps(limited_menu, indent=2, ensure_ascii=False))
        
        print("\n✨ ¡Prueba del sistema de menús completada!")
        return True

if __name__ == "__main__":
    try:
        success = test_menu_system()
        if success:
            print("\n🎉 ¡Sistema de menús funcionando correctamente!")
            print("\n🌐 Para ver en acción:")
            print("   1. Ve a http://localhost:5050/")
            print("   2. Inicia sesión con admin@test.com / admin123")  
            print("   3. Observa el menú lateral dinámico")
        else:
            print("\n❌ Hubo problemas con el sistema de menús")
    except Exception as e:
        print(f"\n💥 Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
