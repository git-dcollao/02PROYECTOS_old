"""
Ruta de emergencia para acceso directo al sistema de backup
Permite acceder al backup sin depender del menú principal
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from flask_login import login_required, current_user
from functools import wraps

# Crear blueprint de emergencia
emergency_bp = Blueprint('emergency', __name__, url_prefix='/emergency')

def superadmin_required(f):
    """Decorador para requerir rol de superadmin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Verificar si es superadmin
        if hasattr(current_user, 'rol') and str(current_user.rol).upper() == 'SUPERADMIN':
            return f(*args, **kwargs)
        
        return jsonify({
            'success': False,
            'message': 'Acceso denegado: Se requiere rol de superadmin'
        }), 403
    
    return decorated_function

@emergency_bp.route('/')
@login_required  
@superadmin_required
def emergency_panel():
    """Panel de emergencia para superadmin"""
    try:
        return render_template('emergency/emergency_panel.html', 
                             title="Panel de Emergencia - Sistema de Backup",
                             user=current_user)
    except Exception as e:
        # Si no existe el template, crear una respuesta HTML básica
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Panel de Emergencia - Backup</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card shadow">
                            <div class="card-header bg-danger text-white text-center">
                                <h4><i class="fas fa-exclamation-triangle"></i> Panel de Emergencia</h4>
                                <p class="mb-0">Sistema de Backup - Solo para Superadmin</p>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-warning">
                                    <h5><i class="fas fa-info-circle"></i> Información</h5>
                                    <p>Este es el panel de emergencia para acceder al sistema de backup cuando el menú principal no está disponible.</p>
                                    <p><strong>Usuario actual:</strong> {current_user.email if hasattr(current_user, 'email') else 'N/A'}</p>
                                    <p><strong>Rol:</strong> {current_user.rol if hasattr(current_user, 'rol') else 'N/A'}</p>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <div class="card border-primary">
                                            <div class="card-body text-center">
                                                <i class="fas fa-database fa-3x text-primary mb-3"></i>
                                                <h5>Sistema de Backup</h5>
                                                <p class="text-muted">Acceder al sistema completo de gestión de backups</p>
                                                <a href="/admin/backup" class="btn btn-primary">
                                                    <i class="fas fa-database"></i> Ir a Backups
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="col-md-6 mb-3">
                                        <div class="card border-success">
                                            <div class="card-body text-center">
                                                <i class="fas fa-home fa-3x text-success mb-3"></i>
                                                <h5>Página Principal</h5>
                                                <p class="text-muted">Volver al dashboard principal del sistema</p>
                                                <a href="/" class="btn btn-success">
                                                    <i class="fas fa-home"></i> Ir al Dashboard
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-12">
                                        <div class="card border-info">
                                            <div class="card-body">
                                                <h5><i class="fas fa-tools"></i> Herramientas de Diagnóstico</h5>
                                                <div class="row">
                                                    <div class="col-md-4">
                                                        <button class="btn btn-outline-info w-100 mb-2" onclick="testSystemStatus()">
                                                            <i class="fas fa-heartbeat"></i> Estado del Sistema
                                                        </button>
                                                    </div>
                                                    <div class="col-md-4">
                                                        <button class="btn btn-outline-warning w-100 mb-2" onclick="initMinimalSystem()">
                                                            <i class="fas fa-rocket"></i> Reinicializar Sistema
                                                        </button>
                                                    </div>
                                                    <div class="col-md-4">
                                                        <a href="/auth/logout" class="btn btn-outline-secondary w-100 mb-2">
                                                            <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                                                        </a>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div id="system-status" class="mt-3" style="display: none;">
                                    <div class="alert alert-info">
                                        <h6>Estado del Sistema:</h6>
                                        <div id="status-content"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                function testSystemStatus() {{
                    const statusDiv = document.getElementById('system-status');
                    const statusContent = document.getElementById('status-content');
                    
                    statusContent.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verificando estado del sistema...';
                    statusDiv.style.display = 'block';
                    
                    fetch('/admin/backup/test')
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                statusContent.innerHTML = `
                                    <strong>✅ Sistema funcionando correctamente</strong><br>
                                    Directorio de backup: ${{data.backup_dir_exists ? '✅' : '❌'}}<br>
                                    Archivos de backup: ${{data.backup_files_count}}<br>
                                    Usuario autenticado: ✅
                                `;
                            }} else {{
                                statusContent.innerHTML = `<strong>❌ Error:</strong> ${{data.message}}`;
                            }}
                        }})
                        .catch(error => {{
                            statusContent.innerHTML = `<strong>❌ Error de conexión:</strong> ${{error.message}}`;
                        }});
                }}
                
                function initMinimalSystem() {{
                    if (confirm('¿Estás seguro de que quieres reinicializar el sistema? Esto recreará los datos mínimos necesarios.')) {{
                        const statusDiv = document.getElementById('system-status');
                        const statusContent = document.getElementById('status-content');
                        
                        statusContent.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reinicializando sistema...';
                        statusDiv.style.display = 'block';
                        
                        fetch('/emergency/reinit', {{method: 'POST'}})
                            .then(response => response.json())
                            .then(data => {{
                                if (data.success) {{
                                    statusContent.innerHTML = `<strong>✅ ${{data.message}}</strong>`;
                                    setTimeout(() => {{ 
                                        window.location.reload(); 
                                    }}, 2000);
                                }} else {{
                                    statusContent.innerHTML = `<strong>❌ Error:</strong> ${{data.message}}`;
                                }}
                            }})
                            .catch(error => {{
                                statusContent.innerHTML = `<strong>❌ Error:</strong> ${{error.message}}`;
                            }});
                    }}
                }}
            </script>
        </body>
        </html>
        """
        return html_content

@emergency_bp.route('/reinit', methods=['POST'])
@login_required
@superadmin_required
def reinit_system():
    """Reinicializar sistema mínimo"""
    try:
        from init_minimal import init_minimal_system
        if init_minimal_system():
            return jsonify({
                'success': True,
                'message': 'Sistema reinicializado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error durante la reinicialización'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@emergency_bp.route('/status')
@login_required
@superadmin_required  
def system_status():
    """Estado del sistema para diagnóstico"""
    try:
        from app.models import Page, PagePermission, Category, Trabajador
        
        pages_count = Page.query.filter_by(active=True).count()
        permissions_count = PagePermission.query.count()
        categories_count = Category.query.count()
        users_count = Trabajador.query.count()
        
        return jsonify({
            'success': True,
            'status': {
                'pages': pages_count,
                'permissions': permissions_count,
                'categories': categories_count,
                'users': users_count,
                'current_user': {
                    'email': current_user.email if hasattr(current_user, 'email') else None,
                    'role': str(current_user.rol) if hasattr(current_user, 'rol') else None,
                    'authenticated': current_user.is_authenticated
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo estado: {str(e)}'
        }), 500