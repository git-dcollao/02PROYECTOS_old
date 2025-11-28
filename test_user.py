# Test interno del sistema de autenticación
from app import create_app
from app.models import Trabajador
import sys

app = create_app()

with app.app_context():
    # Buscar el usuario admin
    admin_user = Trabajador.query.filter_by(email='admin@sistema.local').first()
    
    if admin_user:
        print(f'✅ Usuario encontrado: {admin_user.nombre}')
        print(f'📧 Email: {admin_user.email}')
        print(f'🔐 Rol: {admin_user.rol.name if admin_user.rol else "Sin rol"}')
        print(f'✅ Activo: {admin_user.activo}')
        print(f'🔑 Password verify: {admin_user.verify_password("admin123")}')
        print(f'🆔 ID: {admin_user.id}')
        
        # Verificar bloqueos
        print(f'🔒 Intentos fallidos: {admin_user.intentos_fallidos}')
        print(f'⏰ Bloqueado hasta: {admin_user.bloqueado_hasta}')
        
    else:
        print('❌ Usuario admin no encontrado')
        users = Trabajador.query.all()
        print(f'Usuarios disponibles: {[u.email for u in users]}')