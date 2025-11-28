import requests

# Acceder directamente a la página sin autenticación
response = requests.get('http://localhost:5050/gestion-administradores')

print(f'Status: {response.status_code}')
is_login_page = 'Iniciar Sesión' in response.text
has_email_input = 'name="email"' in response.text
print(f'Es página de login: {is_login_page}')
print(f'Contiene input email: {has_email_input}')
print(f'Tamaño de respuesta: {len(response.text)} caracteres')

# Mostrar un preview del contenido
preview = response.text[:500].replace('\n', ' ').replace('  ', ' ')
print(f'Preview: {preview}...')