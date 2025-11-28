import requests

# Crear una sesión para mantener las cookies
session = requests.Session()

# Primero hacer login
login_data = {
    'email': 'admin@sistema.local',
    'password': 'admin123',
    'csrf_token': ''  # Necesitaremos obtener esto
}

# Obtener la página de login para conseguir el CSRF token
login_page = session.get('http://localhost:5050/login')
print(f"Login page status: {login_page.status_code}")

# Simplificado - hacer login básico
login_response = session.post('http://localhost:5050/login', data={
    'email': 'admin@sistema.local',
    'password': 'admin123'
})

print(f"Login response status: {login_response.status_code}")

# Ahora probar la API de trabajador
api_response = session.get('http://localhost:5050/api/trabajador/1')
print(f"API response status: {api_response.status_code}")

if api_response.status_code == 200:
    try:
        data = api_response.json()
        print("API Response JSON:")
        print(data)
    except:
        print("Response is not JSON:")
        print(api_response.text[:200])
else:
    print(f"Error: {api_response.status_code}")
    print(api_response.text[:200])