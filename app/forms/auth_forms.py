from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, Regexp
from wtforms import ValidationError
from app.models import Trabajador, UserRole
import re


def flexible_email_validator(form, field):
    """Validador de email más permisivo que acepta dominios .local"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, field.data):
        raise ValidationError('Email inválido')


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        flexible_email_validator
    ], render_kw={'placeholder': 'Ingrese su email'})
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ], render_kw={'placeholder': 'Ingrese su contraseña'})
    
    remember_me = BooleanField('Recordarme')
    
    submit = SubmitField('Iniciar Sesión')


class PasswordChangeForm(FlaskForm):
    """Formulario para cambiar contraseña"""
    current_password = PasswordField('Contraseña Actual', validators=[
        DataRequired(message='La contraseña actual es requerida')
    ], render_kw={'placeholder': 'Contraseña actual'})
    
    new_password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(message='La nueva contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ], render_kw={'placeholder': 'Nueva contraseña'})
    
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Confirme la nueva contraseña'),
        EqualTo('new_password', message='Las contraseñas no coinciden')
    ], render_kw={'placeholder': 'Confirmar nueva contraseña'})
    
    submit = SubmitField('Cambiar Contraseña')


class UserRegistrationForm(FlaskForm):
    """Formulario de registro de usuario (solo para admin)"""
    nombre = StringField('Nombre Completo', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=255, message='El nombre debe tener entre 2 y 255 caracteres')
    ], render_kw={'placeholder': 'Nombre completo'})
    
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido'),
        Length(max=255, message='El email es muy largo')
    ], render_kw={'placeholder': 'email@ejemplo.com'})
    
    profesion = StringField('Profesión', validators=[
        Optional(),
        Length(max=255, message='La profesión es muy larga')
    ], render_kw={'placeholder': 'Profesión (opcional)'})
    
    telefono = StringField('Teléfono', validators=[
        Optional(),
        Length(max=20, message='El teléfono es muy largo')
    ], render_kw={'placeholder': 'Teléfono (opcional)'})
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ], render_kw={'placeholder': 'Contraseña'})
    
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Confirme la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ], render_kw={'placeholder': 'Confirmar contraseña'})
    
    rol = SelectField('Rol de Usuario', 
                     choices=[],  # Se llena dinámicamente
                     validators=[DataRequired(message='Seleccione un rol')])
    
    activo = BooleanField('Usuario Activo', default=True)
    
    submit = SubmitField('Crear Usuario')
    
    def __init__(self, current_user_role=None, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        
        # Filtrar roles según el usuario actual
        if current_user_role == UserRole.SUPERADMIN:
            # SuperAdmin puede asignar cualquier rol
            self.rol.choices = [(role.value, role.display_name) for role in UserRole]
        elif current_user_role == UserRole.ADMIN:
            # Admin puede asignar solo roles inferiores
            allowed_roles = [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.USUARIO]
            self.rol.choices = [(role.value, role.display_name) for role in allowed_roles]
        else:
            # Otros roles no pueden crear usuarios
            self.rol.choices = []
    
    def validate_email(self, email):
        """Validar que el email no esté en uso"""
        trabajador = Trabajador.query.filter_by(email=email.data).first()
        if trabajador:
            raise ValidationError('Este email ya está registrado')


class ProfileEditForm(FlaskForm):
    """Formulario para editar perfil personal"""
    nombre = StringField('Nombre Completo', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=255, message='El nombre debe tener entre 2 y 255 caracteres')
    ], render_kw={'placeholder': 'Nombre completo'})
    
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        flexible_email_validator,
        Length(max=255, message='El email es muy largo')
    ], render_kw={'placeholder': 'email@ejemplo.com'})
    
    profesion = StringField('Profesión', validators=[
        Optional(),
        Length(max=255, message='La profesión es muy larga')
    ], render_kw={'placeholder': 'Tu profesión'})
    
    telefono = StringField('Teléfono', validators=[
        Optional(),
        Length(max=20, message='El teléfono es muy largo')
    ], render_kw={'placeholder': 'Número de teléfono'})
    
    submit = SubmitField('Actualizar Perfil')
    
    def __init__(self, original_email=None, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """Validar que el email no esté en uso por otro usuario"""
        if email.data != self.original_email:
            trabajador = Trabajador.query.filter_by(email=email.data).first()
            if trabajador:
                raise ValidationError('Este email ya está registrado')


class UserEditForm(FlaskForm):
    """Formulario para editar usuario existente"""
    nombre = StringField('Nombre Completo', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=255, message='El nombre debe tener entre 2 y 255 caracteres')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido'),
        Length(max=255, message='El email es muy largo')
    ])
    
    profesion = StringField('Profesión', validators=[
        Optional(),
        Length(max=255, message='La profesión es muy larga')
    ])
    
    telefono = StringField('Teléfono', validators=[
        Optional(),
        Length(max=20, message='El teléfono es muy largo')
    ])
    
    rol = SelectField('Rol de Usuario', 
                     choices=[],  # Se llena dinámicamente
                     validators=[DataRequired(message='Seleccione un rol')])
    
    activo = BooleanField('Usuario Activo')
    
    submit = SubmitField('Actualizar Usuario')
    
    def __init__(self, original_email=None, current_user_role=None, target_user_role=None, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
        
        # Filtrar roles según el usuario actual y el usuario objetivo
        if current_user_role == UserRole.SUPERADMIN:
            # SuperAdmin puede modificar cualquier rol
            self.rol.choices = [(role.value, role.display_name) for role in UserRole]
        elif current_user_role == UserRole.ADMIN:
            # Admin puede modificar roles inferiores, pero no puede crear SuperAdmins
            # ni modificar otros SuperAdmins
            if target_user_role == UserRole.SUPERADMIN:
                # Si el objetivo es SuperAdmin, no puede cambiar el rol
                self.rol.choices = [(target_user_role.value, target_user_role.display_name)]
            else:
                allowed_roles = [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.USUARIO]
                self.rol.choices = [(role.value, role.display_name) for role in allowed_roles]
        else:
            # Otros roles no pueden editar usuarios
            self.rol.choices = []
    
    def validate_email(self, email):
        """Validar que el email no esté en uso por otro usuario"""
        if email.data != self.original_email:
            trabajador = Trabajador.query.filter_by(email=email.data).first()
            if trabajador:
                raise ValidationError('Este email ya está registrado')
