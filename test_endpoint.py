import requests
import json

# Crear una sesión para mantener las cookies
session = requests.Session()

try:
    # Hacer login con la contraseña correcta
    login_data = {
        'email': 'admin@sistema.local',
        'password': 'Maho#2024'  # Contraseña correcta del admin
    }

    print('🔐 Iniciando sesión con contraseña correcta...')
    login_response = session.post(
        'http://localhost:5050/auth/login',
        data=login_data,
        allow_redirects=False,  # No seguir redirecciones
        timeout=10
    )

    print(f'📊 Login Status: {login_response.status_code}')
    print(f'📍 Location: {login_response.headers.get("Location", "No redirect")}')

    if login_response.status_code in [302, 301]:
        print('✅ Login exitoso - Redirección detectada')
        
        # Seguir la redirección manualmente para mantener la sesión
        if 'Location' in login_response.headers:
            redirect_url = login_response.headers['Location']
            if not redirect_url.startswith('http'):
                redirect_url = 'http://localhost:5050' + redirect_url
            session.get(redirect_url)

        # Ahora probar el endpoint con autenticación real
        asignacion_data = {
            'administrador_id': 2,
            'recinto_id': 1,
            'asignar': True
        }

        response = session.post(
            'http://localhost:5050/api/asignar-recinto',
            json=asignacion_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        print(f'📊 Endpoint Status: {response.status_code}')
        print(f'📄 Content Type: {response.headers.get("Content-Type", "Unknown")}')

        if response.status_code == 200:
            try:
                result = response.json()
                print('✅ ASIGNACIÓN EXITOSA CON AUTENTICACIÓN:')
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except:
                print('❌ Response is not JSON')
                print(f'Response: {response.text[:300]}...')
        else:
            print(f'❌ Error: {response.status_code}')
            print(f'Response: {response.text[:300]}...')

    else:
        print('❌ Login aún falla')
        print('Preview:', login_response.text[:300])

except Exception as e:
    print(f'💥 Error: {e}')