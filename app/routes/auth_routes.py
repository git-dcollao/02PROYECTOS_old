from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime
from app import db
from app.models import Trabajador, UserRole
from app.forms.auth_forms import LoginForm, PasswordChangeForm, UserRegistrationForm, UserEditForm
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def role_required(*roles):
    """Decorador para rutas que requieren roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión para acceder a esta página', 'error')
                return redirect(url_for('auth.login'))
            
            if not any(current_user.rol == role for role in roles):
                flash('No tiene permisos suficientes para acceder a esta página', 'error')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorador para rutas que requieren privilegios de administrador o superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_manage_users():
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        trabajador = Trabajador.query.filter_by(email=form.email.data).first()
        
        if trabajador is None:
            flash('Email o contraseña incorrectos', 'error')
            return render_template('auth/login.html', form=form)
        
        # Verificar si el usuario está bloqueado
        if trabajador.bloqueado_hasta and datetime.utcnow() < trabajador.bloqueado_hasta:
            tiempo_restante = trabajador.bloqueado_hasta - datetime.utcnow()
            minutos = int(tiempo_restante.total_seconds() / 60)
            flash(f'Cuenta bloqueada. Intente nuevamente en {minutos} minutos', 'error')
            return render_template('auth/login.html', form=form)
        
        # Verificar contraseña
        if not trabajador.verify_password(form.password.data):
            trabajador.increment_failed_attempts()
            
            if trabajador.intentos_fallidos >= 5:
                flash('Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos', 'error')
            else:
                intentos_restantes = 5 - trabajador.intentos_fallidos
                flash(f'Email o contraseña incorrectos. {intentos_restantes} intentos restantes', 'error')
            
            return render_template('auth/login.html', form=form)
        
        if not trabajador.activo:
            flash('Su cuenta está desactivada. Contacte al administrador', 'error')
            return render_template('auth/login.html', form=form)
        
        # Iniciar sesión exitoso
        login_user(trabajador, remember=form.remember_me.data)
        trabajador.update_last_access()
        
        # Redireccionar a la página solicitada o al índice
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        flash(f'Bienvenido, {trabajador.nombre}! ({trabajador.rol_display})', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Ruta de cierre de sesión"""
    nombre = current_user.nombre
    logout_user()
    flash(f'Sesión cerrada correctamente. Hasta luego, {nombre}!', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña del usuario actual"""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if not current_user.verify_password(form.current_password.data):
            flash('La contraseña actual es incorrecta', 'error')
            return render_template('auth/change_password.html', form=form)
        
        current_user.password = form.new_password.data
        db.session.commit()
        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/users')
@login_required
@admin_required
def list_users():
    """Listar todos los usuarios (solo admin)"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('USERS_PER_PAGE', 20)
    
    users = Trabajador.query.order_by(Trabajador.nombre).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('auth/list_users.html', users=users)


@auth_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Crear nuevo usuario (solo admin)"""
    form = UserRegistrationForm(current_user_role=current_user.rol)
    
    if form.validate_on_submit():
        try:
            trabajador = Trabajador(
                nombre=form.nombre.data,
                email=form.email.data,
                profesion=form.profesion.data or None,
                telefono=form.telefono.data or None,
                rol=UserRole(form.rol.data),
                activo=form.activo.data
            )
            trabajador.password = form.password.data
            
            db.session.add(trabajador)
            db.session.commit()
            
            flash(f'Usuario {trabajador.nombre} creado correctamente con rol {trabajador.rol_display}', 'success')
            return redirect(url_for('auth.list_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
    
    return render_template('auth/create_user.html', form=form)


@auth_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Editar usuario existente (solo admin)"""
    trabajador = Trabajador.query.get_or_404(user_id)
    
    # Verificar permisos adicionales
    if (not current_user.is_superadmin() and 
        trabajador.rol == UserRole.SUPERADMIN):
        flash('No puede editar un Super Administrador', 'error')
        return redirect(url_for('auth.list_users'))
    
    form = UserEditForm(
        original_email=trabajador.email, 
        current_user_role=current_user.rol,
        target_user_role=trabajador.rol,
        obj=trabajador
    )
    
    if form.validate_on_submit():
        try:
            # Verificar si se intenta cambiar rol de SuperAdmin siendo Admin
            if (not current_user.is_superadmin() and 
                trabajador.rol == UserRole.SUPERADMIN and 
                form.rol.data != UserRole.SUPERADMIN.value):
                flash('No puede cambiar el rol de un Super Administrador', 'error')
                return render_template('auth/edit_user.html', form=form, trabajador=trabajador)
            
            trabajador.nombre = form.nombre.data
            trabajador.email = form.email.data
            trabajador.profesion = form.profesion.data or None
            trabajador.telefono = form.telefono.data or None
            trabajador.rol = UserRole(form.rol.data)
            trabajador.activo = form.activo.data
            
            db.session.commit()
            flash(f'Usuario {trabajador.nombre} actualizado correctamente', 'success')
            return redirect(url_for('auth.list_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
    
    return render_template('auth/edit_user.html', form=form, trabajador=trabajador)


@auth_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Resetear contraseña de usuario (solo admin)"""
    trabajador = Trabajador.query.get_or_404(user_id)
    
    try:
        # Generar contraseña temporal
        import secrets
        import string
        
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) 
                               for _ in range(8))
        
        trabajador.password = temp_password
        db.session.commit()
        
        flash(f'Contraseña de {trabajador.nombre} reseteada. Nueva contraseña: {temp_password}', 
              'info')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al resetear contraseña: {str(e)}', 'error')
    
    return redirect(url_for('auth.list_users'))


@auth_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Activar/desactivar usuario (solo admin)"""
    trabajador = Trabajador.query.get_or_404(user_id)
    
    if trabajador.id == current_user.id:
        flash('No puede desactivar su propia cuenta', 'error')
        return redirect(url_for('auth.list_users'))
    
    try:
        trabajador.activo = not trabajador.activo
        db.session.commit()
        
        status = 'activado' if trabajador.activo else 'desactivado'
        flash(f'Usuario {trabajador.nombre} {status} correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado del usuario: {str(e)}', 'error')
    
    return redirect(url_for('auth.list_users'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Perfil del usuario actual"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/mi-perfil', methods=['GET', 'POST'])
@login_required
def mi_perfil():
    """Página para que los trabajadores editen su perfil personal"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            current_user.nombre = request.form.get('nombre', '').strip()
            current_user.email = request.form.get('email', '').strip()
            current_user.rut = request.form.get('rut', '').strip() or None
            current_user.telefono = request.form.get('telefono', '').strip() or None
            current_user.profesion = request.form.get('profesion', '').strip() or None
            
            # Validar campos requeridos
            if not current_user.nombre or not current_user.email:
                flash('Nombre y email son campos requeridos', 'error')
                return render_template('mi-perfil.html', trabajador=current_user)
            
            # Validar email único
            existing_user = Trabajador.query.filter(
                Trabajador.email == current_user.email,
                Trabajador.id != current_user.id
            ).first()
            
            if existing_user:
                flash('Este email ya está en uso por otro usuario', 'error')
                return render_template('mi-perfil.html', trabajador=current_user)
            
            # Validar RUT único si se proporcionó
            if current_user.rut:
                existing_rut = Trabajador.query.filter(
                    Trabajador.rut == current_user.rut,
                    Trabajador.id != current_user.id
                ).first()
                
                if existing_rut:
                    flash('Este RUT ya está registrado por otro usuario', 'error')
                    return render_template('mi-perfil.html', trabajador=current_user)
            
            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar perfil: {str(e)}', 'error')
    
    return render_template('mi-perfil.html', trabajador=current_user)


@auth_bp.route('/validar-rut', methods=['POST'])
@login_required
def validar_rut():
    """Validar RUT en tiempo real"""
    try:
        data = request.get_json()
        rut = data.get('rut', '').strip()
        
        if not rut:
            return jsonify({'valid': True})  # RUT vacío es válido
        
        # Verificar si el RUT ya existe (excluyendo al usuario actual)
        existing = Trabajador.query.filter(
            Trabajador.rut == rut,
            Trabajador.id != current_user.id
        ).first()
        
        if existing:
            return jsonify({
                'valid': False,
                'message': 'Este RUT ya está registrado por otro usuario'
            })
        
        return jsonify({'valid': True})
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': 'Error al validar RUT'
        }), 500


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editar perfil personal del usuario actual"""
    from app.forms.auth_forms import ProfileEditForm
    
    form = ProfileEditForm(
        original_email=current_user.email,
        obj=current_user
    )
    
    if form.validate_on_submit():
        try:
            current_user.nombre = form.nombre.data
            current_user.email = form.email.data
            current_user.profesion = form.profesion.data or None
            current_user.telefono = form.telefono.data or None
            
            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar perfil: {str(e)}', 'error')
    
    return render_template('auth/edit_profile.html', form=form, user=current_user)
