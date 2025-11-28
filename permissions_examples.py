# Ejemplo: Agregar nuevos permisos personalizados

# 1. En app/models.py - Agregar nuevos métodos al modelo Trabajador:

def can_export_data(self):
    """Puede exportar datos del sistema"""
    return self.rol in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.SUPERVISOR]

def can_import_data(self):
    """Puede importar datos al sistema"""
    return self.rol in [UserRole.SUPERADMIN, UserRole.ADMIN]

def can_view_financial_reports(self):
    """Puede ver reportes financieros"""
    return self.rol in [UserRole.SUPERADMIN, UserRole.ADMIN]

def can_access_api(self):
    """Puede acceder a la API"""
    return self.rol != UserRole.USUARIO  # Todos excepto usuario básico

# 2. En app/routes/auth_routes.py - Crear nuevos decoradores:

def export_required(f):
    """Decorador para rutas que requieren permisos de exportación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_export_data():
            flash('No tiene permisos para exportar datos', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def financial_reports_required(f):
    """Decorador para reportes financieros"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_view_financial_reports():
            flash('No tiene permisos para ver reportes financieros', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# 3. Usar en las rutas:

@app.route('/export/projects')
@login_required
@export_required
def export_projects():
    return "Exportar proyectos"

@app.route('/reports/financial')
@login_required
@financial_reports_required
def financial_reports():
    return "Reportes financieros"

# 4. En templates - Control condicional:

# En templates/dashboard.html:
{% if current_user.can_export_data() %}
    <a href="{{ url_for('export_projects') }}" class="btn btn-success">
        <i class="fas fa-download"></i>
        Exportar Proyectos
    </a>
{% endif %}

{% if current_user.can_view_financial_reports() %}
    <div class="financial-section">
        <h3>Reportes Financieros</h3>
        <a href="{{ url_for('financial_reports') }}">Ver Reportes</a>
    </div>
{% endif %}
