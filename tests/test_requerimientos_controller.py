"""
Test unitarios para el controlador de requerimientos
Validación de funcionalidades CRUD y endpoints AJAX según InstruccionesPROMPT.md
"""

import unittest
import json
from flask import url_for
from app import create_app, db
from app.models import User, Sector, TipoRecinto, Recinto, Requerimiento
from werkzeug.security import generate_password_hash

class TestRequerimientosController(unittest.TestCase):
    """
    Suite de pruebas para el controlador de requerimientos
    Cubre endpoints CRUD y funcionalidades AJAX
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Crear tablas de prueba
        db.create_all()
        
        # Crear usuario de prueba
        self.test_user = User(
            email='test@ejemplo.com',
            nombre='Usuario Test',
            password_hash=generate_password_hash('password123'),
            is_active=True,
            tipo_usuario='administrador'
        )
        db.session.add(self.test_user)
        
        # Crear datos de prueba
        self.sector_test = Sector(nombre='Sector Test', descripcion='Sector para pruebas')
        db.session.add(self.sector_test)
        
        db.session.commit()
        
        # Login del usuario de prueba
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user.id)
            sess['_fresh'] = True
    
    def tearDown(self):
        """Limpieza después de cada test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_requerimientos_access(self):
        """Test: Acceso a la página principal de requerimientos"""
        response = self.client.get(url_for('requerimientos.ruta_requerimientos'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'requerimientos', response.data.lower())
    
    def test_ajax_get_tiposrecintos_by_sector(self):
        """Test: Endpoint AJAX para obtener tipos de recinto por sector"""
        # Crear tipo de recinto de prueba
        tipo_recinto = TipoRecinto(
            nombre='Tipo Test',
            descripcion='Tipo para pruebas',
            sector_id=self.sector_test.id
        )
        db.session.add(tipo_recinto)
        db.session.commit()
        
        response = self.client.get(
            url_for('requerimientos.get_tiposrecintos_by_sector'),
            query_string={'sector_id': self.sector_test.id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre'], 'Tipo Test')
    
    def test_ajax_get_recintos_by_tipo(self):
        """Test: Endpoint AJAX para obtener recintos por tipo"""
        # Crear tipo de recinto y recinto de prueba
        tipo_recinto = TipoRecinto(
            nombre='Tipo Test',
            descripcion='Tipo para pruebas',
            sector_id=self.sector_test.id
        )
        db.session.add(tipo_recinto)
        db.session.commit()
        
        recinto = Recinto(
            nombre='Recinto Test',
            descripcion='Recinto para pruebas',
            tipo_recinto_id=tipo_recinto.id
        )
        db.session.add(recinto)
        db.session.commit()
        
        response = self.client.get(
            url_for('requerimientos.get_recintos_by_tipo'),
            query_string={'tipo_recinto_id': tipo_recinto.id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['nombre'], 'Recinto Test')
    
    def test_ajax_all_tiposrecintos(self):
        """Test: Endpoint AJAX para obtener todos los tipos de recinto"""
        response = self.client.get(url_for('requerimientos.get_tiposrecintos'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_ajax_all_recintos(self):
        """Test: Endpoint AJAX para obtener todos los recintos"""
        response = self.client.get(url_for('requerimientos.get_recintos'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_add_requerimiento_post_success(self):
        """Test: Crear nuevo requerimiento exitosamente"""
        # Crear recinto de prueba
        tipo_recinto = TipoRecinto(
            nombre='Tipo Test',
            descripcion='Tipo para pruebas',
            sector_id=self.sector_test.id
        )
        db.session.add(tipo_recinto)
        db.session.commit()
        
        recinto = Recinto(
            nombre='Recinto Test',
            descripcion='Recinto para pruebas',
            tipo_recinto_id=tipo_recinto.id
        )
        db.session.add(recinto)
        db.session.commit()
        
        form_data = {
            'descripcion': 'Requerimiento de prueba',
            'sector_id': self.sector_test.id,
            'tipo_recinto_id': tipo_recinto.id,
            'recinto_id': recinto.id,
            'prioridad': 'Alta'
        }
        
        response = self.client.post(
            url_for('requerimientos.add_requerimiento'),
            data=form_data,
            follow_redirects=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creó el requerimiento
        requerimiento = Requerimiento.query.filter_by(descripcion='Requerimiento de prueba').first()
        self.assertIsNotNone(requerimiento)
        self.assertEqual(requerimiento.recinto_id, recinto.id)
    
    def test_permissions_required(self):
        """Test: Verificar que se requieren permisos para acceder"""
        # Logout del usuario
        with self.client.session_transaction() as sess:
            sess.clear()
        
        response = self.client.get(url_for('requerimientos.ruta_requerimientos'))
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.location)
    
    def test_ajax_endpoints_without_auth(self):
        """Test: Endpoints AJAX sin autenticación deben fallar"""
        # Logout del usuario
        with self.client.session_transaction() as sess:
            sess.clear()
        
        endpoints = [
            'requerimientos.get_tiposrecintos_by_sector',
            'requerimientos.get_recintos_by_tipo',
            'requerimientos.get_tiposrecintos',
            'requerimientos.get_recintos'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(url_for(endpoint))
            # Debe redirigir al login o retornar 401
            self.assertIn(response.status_code, [302, 401])

if __name__ == '__main__':
    unittest.main()