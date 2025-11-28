"""
Test específico para ver si el problema es del template header_menu.html
"""
import sys
import os

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask import render_template_string

def test_header_menu_debug():
    print("🔍 TEST DEL TEMPLATE HEADER_MENU")
    print("=" * 50)
    
    app = create_app()
    
    # Template de debug que muestra los datos RAW del menú
    debug_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Debug Header Menu</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% set user = get_current_user() %}
    {% if user %}
    <div class="container mt-4">
        <h3>🔍 DEBUG DEL MENÚ</h3>
        
        {% set user_menu = get_user_menu() %}
        {% if user_menu %}
        <h4>📊 Datos RAW del menú:</h4>
        <pre>{{ user_menu | pprint }}</pre>
        
        <h4>🎯 Menú Configuración específico:</h4>
        {% for category in user_menu %}
            {% if category.category == 'Configuración' %}
            <div class="alert alert-info">
                <h5>Categoría: {{ category.category }}</h5>
                <p>Icono: {{ category.icon }}</p>
                <p>Count: {{ category.count }}</p>
                <p>Páginas ({{ category.pages|length }}):</p>
                <ul>
                    {% for page in category.pages %}
                    <li>
                        <strong>name:</strong> "{{ page.name }}" 
                        | <strong>url:</strong> "{{ page.url }}"
                        | <strong>icon:</strong> "{{ page.icon }}"
                    </li>
                    {% endfor %}
                </ul>
            </div>
            
            <h5>🔧 Test del dropdown Bootstrap:</h5>
            <div class="dropdown">
                <button class="btn btn-primary dropdown-toggle" type="button" 
                        id="testDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="{{ category.icon }} me-1"></i>
                    {{ category.category }}
                    <span class="badge bg-light text-primary ms-2">{{ category.count }}</span>
                </button>
                <ul class="dropdown-menu" aria-labelledby="testDropdown">
                    {% for page in category.pages %}
                    <li>
                        <a class="dropdown-item d-flex align-items-center py-2" href="{{ page.url }}">
                            <i class="{{ page.icon }} me-2 text-primary" style="width: 18px;"></i>
                            <span>{{ page.name }}</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        {% endfor %}
        {% endif %}
    </div>
    {% endif %}
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🔍 Verificando contenido del menú de test...');
            
            // Listar todos los dropdown-item
            const dropdownItems = document.querySelectorAll('.dropdown-item');
            console.log(`📄 Items encontrados: ${dropdownItems.length}`);
            
            dropdownItems.forEach((item, index) => {
                const text = item.textContent.trim();
                const href = item.href;
                console.log(`   ${index + 1}. "${text}" → ${href}`);
                
                // Verificar si hay texto extraño
                if (text.includes('ID') && text.includes('Nombre') && !text.includes('ID') === false) {
                    console.error(`❌ PROBLEMA DETECTADO en item ${index + 1}: "${text}"`);
                }
            });
        });
    </script>
</body>
</html>
"""
    
    with app.app_context():
        with app.test_request_context('/test-debug'):
            # Crear el endpoint de debug
            @app.route('/test-header-debug')
            def test_header_debug():
                return render_template_string(debug_template)
            
            print("✅ Template de debug creado")
            print("🔗 Para probar:")
            print("   1. Acceder a http://localhost:5050/test-header-debug")
            print("   2. Revisar la consola del navegador")
            print("   3. Comparar el contenido RAW vs renderizado")

if __name__ == "__main__":
    test_header_menu_debug()