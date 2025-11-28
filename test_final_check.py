import requests

session = requests.Session()

# Login completo
try:
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
        # Ahora verificar la página de gestión
        admin_page = session.get('http://localhost:5050/gestion-administradores')
        
        has_error_message = 'Error al cargar la gestión de administradores' in admin_page.text
        has_admin_content = 'Gestión de Administradores' in admin_page.text
        has_matrix_elements = 'checkbox' in admin_page.text or 'matriz' in admin_page.text.lower()
        
        print(f'❌ Contiene mensaje de error: {has_error_message}')
        print(f'✅ Contiene contenido admin: {has_admin_content}')
        print(f'📋 Contiene elementos de matriz: {has_matrix_elements}')
        
        if not has_error_message and has_admin_content:
            print('🎉 PROBLEMA RESUELTO: La página carga sin errores')
        else:
            print('⚠️ Aún hay problemas pendientes')
    else:
        print('❌ Login falló')
        
except Exception as e:
    print(f'Error: {e}')