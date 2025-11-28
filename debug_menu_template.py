"""
Script para verificar si el menú dinámico se está cargando en los templates
"""

from app import create_app
from flask import render_template_string

def test_menu_template():
    """Probar si el menú se renderiza correctamente en los templates"""
    
    app = create_app()
    with app.app_context():
        
        print("🧪 Probando renderización del menú en templates...\n")
        
        # Template de prueba simple
        test_template = """
        {% from 'components/menu.html' import render_sidebar_menu %}
        
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Test del Menú</h1>
            {% if current_user.is_authenticated %}
                <p>Usuario autenticado: {{ current_user.nombre }}</p>
                {{ render_sidebar_menu() }}
            {% else %}
                <p>Usuario no autenticado</p>
            {% endif %}
        </body>
        </html>
        """
        
        try:
            # Intentar renderizar el template
            rendered = render_template_string(test_template)
            
            if "sidebar-menu" in rendered:
                print("✅ El menú se renderiza correctamente")
                print("✅ Se encontró la clase 'sidebar-menu' en el HTML")
                return True
            else:
                print("❌ El menú no se encuentra en el HTML renderizado")
                print("📄 HTML renderizado:")
                print(rendered[:500] + "...")
                return False
                
        except Exception as e:
            print(f"❌ Error al renderizar template: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_menu_functions():
    """Probar las funciones del menú directamente"""
    
    try:
        # Importar funciones
        from app.jinja_filters import get_user_menu, get_menu_item_count
        from flask_login import current_user
        
        print("🔧 Probando funciones del menú directamente...")
        
        # Probar función de menú
        menu = get_user_menu()
        print(f"   📋 get_user_menu() retorna: {type(menu)} con {len(menu) if menu else 0} elementos")
        
        # Probar conteo
        count = get_menu_item_count()
        print(f"   🔢 get_menu_item_count() retorna: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en funciones del menú: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        print("🔍 DIAGNÓSTICO DEL MENÚ DINÁMICO")
        print("=" * 50)
        
        # Test 1: Funciones del menú
        if test_menu_functions():
            print("✅ Test 1 PASADO: Funciones del menú")
        else:
            print("❌ Test 1 FALLIDO: Funciones del menú")
        
        print()
        
        # Test 2: Renderización del template  
        if test_menu_template():
            print("✅ Test 2 PASADO: Renderización del template")
        else:
            print("❌ Test 2 FALLIDO: Renderización del template")
        
        print("\n🏁 Diagnóstico completado")
        
    except Exception as e:
        print(f"\n💥 Error general en el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
