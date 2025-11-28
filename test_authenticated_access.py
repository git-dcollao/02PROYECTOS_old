import requests

session = requests.Session()

try:
    # 1. Obtener CSRF token
    form_response = session.get('http://localhost:5050/auth/login')
    form_html = form_response.text
    
    csrf_start = form_html.find('name="csrf_token"')
    value_start = form_html.find('value="', csrf_start) + 7
    value_end = form_html.find('"', value_start)
    csrf_token = form_html[value_start:value_end]
    
    print(f'CSRF token obtenido: {csrf_token[:20]}...')
    
    # 2. Login
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
        print('✅ Login exitoso')
        
        # 3. Acceder a página de gestión de administradores
        admin_page = session.get('http://localhost:5050/gestion-administradores')
        print(f'Admin page status: {admin_page.status_code}')
        
        is_login_page = 'Iniciar Sesión' in admin_page.text
        has_admin_content = 'Gestión de Administradores' in admin_page.text
        has_matrix = 'matriz-administradores' in admin_page.text
        
        print(f'Es página de login: {is_login_page}')
        print(f'Tiene contenido admin: {has_admin_content}')
        print(f'Tiene matriz: {has_matrix}')
        
        if has_admin_content:
            print('✅ Página de gestión de administradores carga correctamente')
        else:
            print('❌ Problema: aún siendo redirigido al login después de autenticación exitosa')
    else:
        print('❌ Login falló')
        
except Exception as e:
    print(f'Error: {e}')