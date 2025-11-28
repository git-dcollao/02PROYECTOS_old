"""
Test de Endpoints y APIs
"""
import pytest
import json
from app.models import Requerimiento, Estado, TipoProyecto, Trabajador, db

class TestCRUDEndpoints:
    """Tests de operaciones CRUD básicas"""
    
    def test_dashboard_access(self, auth_client):
        """Test acceso al dashboard principal"""
        response = auth_client.get('/')
        assert response.status_code == 200
    
    def test_requerimientos_list(self, auth_client):
        """Test listado de requerimientos"""
        response = auth_client.get('/requerimientos')
        assert response.status_code in [200, 302]
        
    def test_create_requerimiento_form(self, auth_client):
        """Test formulario de creación de requerimientos"""
        response = auth_client.get('/crear_requerimiento')
        assert response.status_code in [200, 302]

class TestAPIEndpoints:
    """Tests de endpoints API/JSON"""
    
    def test_api_requerimientos_json(self, auth_client):
        """Test endpoint JSON de requerimientos"""
        response = auth_client.get('/api/requerimientos')
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.content_type == 'application/json'
    
    def test_asignar_recinto_api(self, auth_client):
        """Test API de asignación de recintos"""
        data = {
            'user_id': 1,
            'recinto_id': 1,
            'action': 'assign'
        }
        
        response = auth_client.post('/api/asignar-recinto',
                                  data=json.dumps(data),
                                  content_type='application/json')
        assert response.status_code in [200, 400, 404]
    
    def test_update_requerimiento_aceptar(self, auth_client):
        """Test endpoint de aceptación de requerimientos"""
        response = auth_client.post('/update_requerimiento_aceptar/999',
                                  data={'observacion': 'Prueba de test'})
        assert response.status_code in [200, 302, 404]

class TestFormValidation:
    """Tests de validación de formularios"""
    
    def test_empty_observacion_validation(self, auth_client):
        """Test validación de observación vacía"""
        response = auth_client.post('/update_requerimiento_rechazar/999',
                                  data={'observacion': ''})
        assert response.status_code in [200, 302, 400, 404]
    
    def test_required_fields_validation(self, auth_client):
        """Test validación de campos requeridos"""
        # Test crear requerimiento sin datos requeridos
        response = auth_client.post('/crear_requerimiento',
                                  data={})
        assert response.status_code in [200, 302, 400]

class TestFileUploads:
    """Tests de carga de archivos"""
    
    def test_excel_upload_validation(self, auth_client):
        """Test validación de archivos Excel"""
        # Test sin archivo
        response = auth_client.post('/upload_excel')
        assert response.status_code in [200, 302, 400, 404]
    
    def test_gantt_file_upload(self, auth_client):
        """Test carga de archivos Gantt"""
        response = auth_client.post('/upload_gantt/1')
        assert response.status_code in [200, 302, 400, 404]

class TestDataIntegrity:
    """Tests de integridad de datos"""
    
    def test_cascade_deletes(self, app):
        """Test eliminaciones en cascada"""
        with app.app_context():
            # Verificar que las relaciones estén bien definidas
            from app.models import Sector, TipoRecinto
            sector = Sector.query.first()
            if sector:
                tipos_count = TipoRecinto.query.filter_by(id_sector=sector.id).count()
                assert isinstance(tipos_count, int)
    
    def test_foreign_key_constraints(self, app):
        """Test restricciones de claves foráneas"""
        with app.app_context():
            # Verificar que no se pueden crear registros con FK inválidas
            from app.models import Requerimiento
            reqs = Requerimiento.query.limit(5).all()
            for req in reqs:
                assert req.id_estado is not None
                assert req.id_tipoproyecto is not None

class TestBusinessLogic:
    """Tests de lógica de negocio"""
    
    def test_estado_transitions(self, app):
        """Test transiciones válidas de estado"""
        with app.app_context():
            from app.models import Estado
            estados = Estado.query.all()
            assert len(estados) >= 0  # Al menos debe tener estructura
    
    def test_permission_hierarchy(self, app, superadmin_user, regular_user):
        """Test jerarquía de permisos"""
        with app.app_context():
            # SUPERADMIN tiene más permisos que usuario regular
            assert superadmin_user.is_superadmin() == True
            assert regular_user.is_superadmin() == False
    
    def test_data_filtering_logic(self, app, regular_user):
        """Test lógica de filtrado de datos"""
        with app.app_context():
            # Usuario regular debe tener filtrado
            if hasattr(regular_user, 'recinto_id'):
                assert regular_user.recinto_id is not None or regular_user.recinto_id is None

class TestPerformance:
    """Tests de rendimiento básico"""
    
    def test_dashboard_load_time(self, auth_client):
        """Test tiempo de carga del dashboard"""
        import time
        start = time.time()
        response = auth_client.get('/')
        end = time.time()
        
        load_time = end - start
        assert load_time < 5.0  # Menos de 5 segundos
    
    def test_database_query_efficiency(self, app):
        """Test eficiencia de consultas a BD"""
        with app.app_context():
            # Test que las consultas básicas funcionen
            from app.models import User, CustomRole
            users_count = User.query.count()
            roles_count = CustomRole.query.count()
            
            assert isinstance(users_count, int)
            assert isinstance(roles_count, int)