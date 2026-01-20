from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.forms.auth_forms import LoginForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/docs/info.html')
def docs_info():
    """Página de información para pruebas - Pública"""
    return render_template('docs/info.html')

@main_bp.route('/')
def index():
    """Página principal - pública con login incluido"""
    if current_user.is_authenticated:
        # Usuario logueado, mostrar dashboard simple sin dependencias externas
        context = {
            'user': current_user,
            'can_manage_users': current_user.can_manage_users(),
            'can_manage_projects': current_user.can_manage_projects(),
            'can_view_reports': current_user.can_view_reports(),
            'can_modify_system': current_user.can_modify_system()
        }
        return render_template('dashboard_simple.html', **context)
    else:
        # Usuario no logueado, mostrar home simple sin dependencias externas
        form = LoginForm()
        return render_template('home_simple.html', form=form)

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard principal para usuarios autenticados"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Datos del dashboard según el rol usando template simple
    context = {
        'user': current_user,
        'can_manage_users': current_user.can_manage_users(),
        'can_manage_projects': current_user.can_manage_projects(),
        'can_view_reports': current_user.can_view_reports(),
        'can_modify_system': current_user.can_modify_system()
    }
    
    return render_template('dashboard_simple.html', **context)

@main_bp.route('/about')
def about():
    """Página acerca de - pública"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Página de contacto - pública"""
    return render_template('contact.html')

@main_bp.route('/test')
def test():
    """Página de prueba simple"""
    return render_template('test.html')

@main_bp.route('/simple')
def simple():
    """Versión simple de home sin CDNs externos"""
    form = LoginForm()
    return render_template('home_simple.html', form=form)

@main_bp.route('/test-dashboard')
def test_dashboard():
    """Ruta de prueba para ver el dashboard sin autenticación (solo para testing)"""
    # Simular contexto de usuario para pruebas
    from app.models import Trabajador, UserRole
    
    # Crear usuario de prueba simulado
    class MockUser:
        def __init__(self):
            self.nombre = "Usuario de Prueba"
            self.rol_display = "Administrador"
            self.ultimo_acceso = None
            self.equipos_trabajo = MockQuery()
            self.recursos_asignados = MockQuery()
            self.avances_actividades = MockQuery()
            
        def can_manage_users(self):
            return True
            
        def can_manage_projects(self):
            return True
            
        def can_view_reports(self):
            return True
            
        def can_modify_system(self):
            return True
    
    class MockQuery:
        def count(self):
            return 5
        def limit(self, n):
            return []
    
    # Datos del dashboard según el rol usando template simple
    context = {
        'user': MockUser(),
        'can_manage_users': True,
        'can_manage_projects': True,
        'can_view_reports': True,
        'can_modify_system': True
    }
    
    return render_template('dashboard_simple.html', **context)

@main_bp.route('/test-menu')
def test_menu():
    """Página de prueba para el menú dinámico"""
    return render_template('test_menu.html')

@main_bp.route('/test-menu-simple')
def test_menu_simple():
    """Página de prueba simple para el menú dinámico"""
    return render_template('test_menu_simple.html')

@main_bp.route('/menu-visual-test')
def menu_visual_test():
    """Test visual para diagnosticar problemas del menú"""
    return render_template('menu_visual_test.html')

@main_bp.route('/menu-diagnostico')
def menu_diagnostico():
    """Página de diagnóstico completo del menú"""
    return render_template('menu_diagnostico.html')

@main_bp.route('/gantt-v2')
def gantt_v2():
    """Gantt v2 - Nueva versión del diagrama de Gantt"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Aquí puedes agregar lógica para cargar datos de proyectos
    # Por ahora usaremos datos de ejemplo
    context = {
        'user': current_user,
        'page_title': 'Diagrama de Gantt v2',
        'proyectos': [],  # Aquí cargarías los proyectos reales
    }
    
    return render_template('gantt-proyecto.html', **context)
