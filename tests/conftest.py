"""
Configuración central para tests con pytest
"""
import pytest
import tempfile
import os
from app import create_app
from app.models import db, User, CustomRole, Page, UserPagePermission
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='session')
def app():
    """Fixture de aplicación Flask para testing"""
    # Crear archivo temporal para SQLite de testing
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Configuración de testing
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Deshabilitar CSRF en tests
        'LOGIN_DISABLED': False
    }
    
    app = create_app()
    app.config.update(test_config)
    
    with app.app_context():
        db.create_all()
        _create_test_data()
        yield app
        
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Cliente de testing Flask"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner para testing"""
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """Cliente autenticado como SUPERADMIN"""
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'  # ID del superadmin
        sess['_fresh'] = True
    return client

def _create_test_data():
    """Crear datos de prueba básicos"""
    # Crear roles
    superadmin_role = CustomRole(name='SUPERADMIN', description='Super Administrator')
    user_role = CustomRole(name='USER', description='Regular User')
    
    db.session.add_all([superadmin_role, user_role])
    db.session.flush()  # Para obtener IDs
    
    # Crear páginas
    pages = [
        Page(name='dashboard', url='/dashboard'),
        Page(name='usuarios', url='/usuarios'),
        Page(name='requerimientos', url='/requerimientos'),
        Page(name='proyectos', url='/proyectos')
    ]
    db.session.add_all(pages)
    db.session.flush()
    
    # Crear usuarios de prueba
    superadmin = User(
        username='superadmin',
        email='admin@test.com',
        password=generate_password_hash('admin123'),
        nombre='Super Admin',
        apellido='Test',
        is_active=True,
        custom_role_id=superadmin_role.id
    )
    
    regular_user = User(
        username='testuser',
        email='user@test.com', 
        password=generate_password_hash('user123'),
        nombre='Test User',
        apellido='Regular',
        is_active=True,
        custom_role_id=user_role.id
    )
    
    db.session.add_all([superadmin, regular_user])
    db.session.flush()
    
    # Asignar permisos específicos al usuario regular
    user_permission = UserPagePermission(
        user_id=regular_user.id,
        page_id=pages[0].id  # Solo dashboard
    )
    db.session.add(user_permission)
    
    db.session.commit()

@pytest.fixture
def superadmin_user(app):
    """Usuario superadmin para tests"""
    with app.app_context():
        return User.query.filter_by(username='superadmin').first()

@pytest.fixture
def regular_user(app):
    """Usuario regular para tests"""
    with app.app_context():
        return User.query.filter_by(username='testuser').first()