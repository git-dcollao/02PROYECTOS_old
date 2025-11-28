import requests
import re

session = requests.Session()

# Login primero
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
    print('Login OK, obteniendo página de admin...')
    
    # Obtener la página de administradores
    admin_page = session.get('http://localhost:5050/gestion-administradores')
    
    # Buscar las URLs generadas por url_for en el JavaScript
    urls_encontradas = re.findall(r'fetch\(\'([^\']+)\',', admin_page.text)
    
    print('URLs encontradas en fetch():')
    for url in urls_encontradas:
        print(f'  - {url}')
    
    # Verificar si hay errores de JavaScript visible en el HTML
    if 'Error al cargar' in admin_page.text:
        print('❌ Texto "Error al cargar" encontrado en la página')
    else:
        print('✅ No se encontró texto de error en la página')
        
    # Verificar que la página contiene la estructura esperada
    tiene_matriz = 'matriz-container' in admin_page.text or 'checkbox' in admin_page.text
    print(f'Contiene elementos de matriz: {tiene_matriz}')
    
    print(f'Tamaño de la página: {len(admin_page.text)} caracteres')
    
else:
    print('Login falló')