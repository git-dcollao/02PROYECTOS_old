import requests
import json

session = requests.Session()

try:
    # 1. Obtener el formulario de login para extraer el CSRF token
    print('📝 Obteniendo formulario de login...')
    form_response = session.get('http://localhost:5050/auth/login')
    
    if form_response.status_code != 200:
        print(f'❌ Error obteniendo formulario: {form_response.status_code}')
        exit()
    
    # Extraer CSRF token del formulario (usando texto simple)
    form_html = form_response.text
    csrf_start = form_html.find('name="csrf_token"')
    if csrf_start == -1:
        print('❌ No se encontró campo csrf_token')
        exit()
        
    value_start = form_html.find('value="', csrf_start) + 7
    value_end = form_html.find('"', value_start)
    csrf_token = form_html[value_start:value_end]
    
    print(f'🔑 CSRF token obtenido: {csrf_token[:20]}...')
    
    # 2. Hacer login con CSRF token
    login_data = {
        'email': 'admin@sistema.local',
        'password': 'Maho#2024',
        'csrf_token': csrf_token,
        'submit': 'Iniciar Sesión'
    }
    
    print('🔐 Enviando login con CSRF token...')
    login_response = session.post(
        'http://localhost:5050/auth/login',
        data=login_data,
        allow_redirects=False
    )
    
    print(f'📊 Login Status: {login_response.status_code}')
    print(f'📍 Redirect: {login_response.headers.get("Location", "None")}')
    
    if login_response.status_code in [302, 301]:
        print('✅ LOGIN EXITOSO!')
        
        # 3. Probar endpoint
        asignacion_data = {
            'administrador_id': 2,
            'recinto_id': 1,
            'asignar': True
        }
        
        response = session.post(
            'http://localhost:5050/api/asignar-recinto',
            json=asignacion_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f'🎯 Endpoint Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('🎉 ENDPOINT FUNCIONA PERFECTAMENTE:')
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print('❌ Endpoint falló')
            print('Response:', response.text[:200])
            
    else:
        print('❌ Login falló aún con CSRF')
        has_errors = 'class="alert alert-danger"' in login_response.text
        print(f'Tiene errores visibles: {has_errors}')
        
except Exception as e:
    print(f'💥 Error: {e}')