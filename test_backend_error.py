import requests

session = requests.Session()

try:
    # Login
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
    
    print(f'Login Status: {login_response.status_code}')
    
    if login_response.status_code in [302, 301]:
        print('Login exitoso, accediendo a gestión administradores...')
        
        # Ahora intentar acceder a la página
        admin_response = session.get('http://localhost:5050/gestion-administradores')
        
        print(f'Admin page status: {admin_response.status_code}')
        print(f'Final URL: {admin_response.url}')
        
        # Verificar si es redirect al dashboard (error en backend)
        if admin_response.url and 'dashboard' in admin_response.url:
            print('❌ REDIRIGIDO AL DASHBOARD - Error en el backend')
        
        # Verificar contenido
        if 'Error interno del servidor' in admin_response.text:
            print('❌ ERROR CONFIRMADO: Error interno del servidor en el flash message')
        elif 'Gestión de Administradores' in admin_response.text:
            print('✅ Página carga correctamente')
        else:
            print('⚠️ Estado inesperado')
            
        # Mostrar preview del contenido
        preview = admin_response.text[:300].replace('\n', ' ')
        print(f'Preview: {preview}...')
        
    else:
        print('❌ Login falló')
        
except Exception as e:
    print(f'Error en test: {e}')