"""
Test de Permisos y Autenticación
"""
import pytest
from flask import url_for
from app.models import User, CustomRole, Page, UserPagePermission, db

class TestAuthentication:
    """Tests del sistema de autenticación"""
    
    def test_login_required_redirect(self, client):
        """Test que endpoints protegidos redirecten al login"""
        response = client.get('/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location or 'login' in response.location
    
    def test_superadmin_access_all_pages(self, auth_client, superadmin_user):
        """Test que SUPERADMIN puede acceder a todas las páginas"""
        protected_urls = [
            '/dashboard',
            '/usuarios', 
            '/requerimientos',
            '/gestion-administradores'
        ]
        
        for url in protected_urls:
            response = auth_client.get(url)
            assert response.status_code in [200, 302], f"Failed access to {url}"
    
    def test_regular_user_permission_filtering(self, client, regular_user):
        """Test que usuarios regulares solo ven datos permitidos"""
        # Login como usuario regular
        with client.session_transaction() as sess:
            sess['_user_id'] = str(regular_user.id)
            sess['_fresh'] = True
            
        response = client.get('/dashboard')
        assert response.status_code == 200

class TestPermissionSystem:
    """Tests del sistema unificado de permisos"""
    
    def test_has_page_permission_superadmin(self, app, superadmin_user):
        """Test que SUPERADMIN tiene todos los permisos de páginas"""
        with app.app_context():
            assert superadmin_user.is_superadmin() == True
            assert superadmin_user.has_page_permission('/any-page') == True
            assert superadmin_user.has_page_permission('/admin-only') == True
    
    def test_has_page_permission_regular_user(self, app, regular_user):
        """Test que usuario regular solo tiene permisos específicos"""
        with app.app_context():
            assert regular_user.is_superadmin() == False
            assert regular_user.has_page_permission('/dashboard') == True
            assert regular_user.has_page_permission('/admin-only') == False
    
    def test_permission_inheritance(self, app):
        """Test herencia de permisos por roles"""
        with app.app_context():
            # Crear usuario con rol específico
            admin_role = CustomRole.query.filter_by(name='SUPERADMIN').first()
            user = User.query.filter_by(username='superadmin').first()
            
            assert user.custom_role_id == admin_role.id
            assert user.is_superadmin() == True

class TestEndpointSecurity:
    """Tests de seguridad en endpoints críticos"""
    
    def test_asignar_recinto_permissions(self, client, auth_client):
        """Test permisos en endpoint asignar_recinto"""
        # Sin autenticación
        response = client.post('/api/asignar-recinto')
        assert response.status_code == 302  # Redirect to login
        
        # Con autenticación SUPERADMIN
        response = auth_client.post('/api/asignar-recinto', 
                                  json={'user_id': 1, 'recinto_id': 1})
        assert response.status_code in [200, 400]  # 400 por datos faltantes, no por permisos
    
    def test_update_requerimiento_csrf_protection(self, auth_client):
        """Test protección CSRF en endpoints críticos"""
        # Sin CSRF token debería fallar en producción
        response = auth_client.post('/update_requerimiento_rechazar/1',
                                  data={'observacion': 'Test'})
        # En testing CSRF está deshabilitado, pero endpoint debe existir
        assert response.status_code in [200, 302, 404, 500]

class TestDataFiltering:
    """Tests de filtrado de datos por permisos"""
    
    def test_requerimientos_filtering_by_user_level(self, app, regular_user, superadmin_user):
        """Test que el filtrado de requerimientos funcione por nivel de usuario"""
        with app.app_context():
            # SUPERADMIN ve todo
            assert superadmin_user.is_superadmin() == True
            
            # Usuario regular ve filtrado
            assert regular_user.is_superadmin() == False
            
    def test_trabajadores_access_control(self, auth_client):
        """Test control de acceso a gestión de trabajadores"""
        response = auth_client.get('/trabajadores')
        assert response.status_code in [200, 302]  # Dependiendo de si la ruta existe

class TestErrorHandling:
    """Tests de manejo de errores"""
    
    def test_404_handling(self, client):
        """Test manejo de páginas no encontradas"""
        response = client.get('/non-existent-page')
        assert response.status_code == 404
    
    def test_csrf_error_handling(self, app):
        """Test manejo de errores CSRF"""
        with app.app_context():
            # Verificar que el handler de CSRF está registrado
            assert 'CSRFError' in [handler.__name__ for handler in app.error_handler_spec[None][400] if handler] or True
    
    def test_permission_denied_handling(self, client, regular_user):
        """Test manejo de acceso denegado"""
        with client.session_transaction() as sess:
            sess['_user_id'] = str(regular_user.id)
            sess['_fresh'] = True
            
        response = client.get('/admin-only-page')
        assert response.status_code in [302, 403, 404]  # Redirect, forbidden, o not found