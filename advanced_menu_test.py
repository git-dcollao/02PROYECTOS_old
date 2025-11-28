"""
Test directo para verificar el menú en tiempo real
"""

from app import create_app
from app.models import Trabajador
from app.jinja_filters import get_user_menu, get_menu_item_count
from flask import render_template_string

def test_menu_real():
    """Test del menú con usuario real"""
    
    app = create_app()
    with app.app_context():
        
        print("🔧 DIAGNÓSTICO AVANZADO DEL MENÚ")
        print("=" * 50)
        
        # Obtener usuario real
        admin = Trabajador.query.filter_by(email='admin@test.com').first()
        
        if not admin:
            print("❌ No se encontró el usuario admin@test.com")
            return False
        
        print(f"✅ Usuario encontrado: {admin.nombre} ({admin.rol.value})")
        
        # Test 1: Funciones básicas
        print("\n📋 TEST 1: Funciones básicas")
        try:
            menu = get_user_menu()  # Sin parámetro, debería usar current_user
            print(f"   get_user_menu(): {type(menu)} con {len(menu) if menu else 0} elementos")
            
            count = get_menu_item_count()
            print(f"   get_menu_item_count(): {count}")
            
        except Exception as e:
            print(f"   ❌ Error en funciones: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: Simulación de login
        print("\n🔐 TEST 2: Simulación de contexto de usuario")
        try:
            # Simular un contexto con usuario
            with app.test_request_context('/', base_url='http://localhost:5050'):
                from flask_login import login_user
                login_user(admin, remember=False)
                
                # Ahora probar las funciones
                menu = get_user_menu()
                count = get_menu_item_count()
                
                print(f"   Con usuario logueado - Menú: {len(menu) if menu else 0} categorías")
                print(f"   Con usuario logueado - Total elementos: {count}")
                
                if menu:
                    for cat in menu:
                        print(f"     📁 {cat['category']}: {cat['count']} páginas")
                
        except Exception as e:
            print(f"   ❌ Error en simulación: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Template rendering directo
        print("\n🎨 TEST 3: Renderizado de template")
        try:
            simple_template = """
            {% if current_user.is_authenticated %}
                <h1>Usuario: {{ current_user.nombre }}</h1>
                <p>Menú items: {{ get_menu_item_count() }}</p>
                {% set menu = get_user_menu() %}
                {% if menu %}
                    <ul>
                    {% for category in menu %}
                        <li>{{ category.category }} ({{ category.count }})</li>
                    {% endfor %}
                    </ul>
                {% else %}
                    <p>Sin menú</p>
                {% endif %}
            {% else %}
                <p>No autenticado</p>
            {% endif %}
            """
            
            with app.test_request_context('/', base_url='http://localhost:5050'):
                from flask_login import login_user
                login_user(admin, remember=False)
                
                rendered = render_template_string(simple_template)
                print(f"   Template renderizado exitosamente")
                print(f"   Longitud HTML: {len(rendered)} caracteres")
                
                if "Usuario: " in rendered:
                    print("   ✅ Usuario detectado en template")
                else:
                    print("   ❌ Usuario NO detectado en template")
                
                if "Menú items:" in rendered:
                    print("   ✅ Función de menú funciona en template")
                else:
                    print("   ❌ Función de menú NO funciona en template")
                
        except Exception as e:
            print(f"   ❌ Error en renderizado: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🏁 Diagnóstico completado")

if __name__ == "__main__":
    test_menu_real()
