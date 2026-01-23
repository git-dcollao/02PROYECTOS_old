from app import db
from datetime import datetime
from sqlalchemy import Index, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import validates
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError
import re
import enum

# Enum para roles de usuario del sistema (inmutables)
class UserRole(enum.Enum):
    SUPERADMIN = "superadmin"  # Único rol del sistema inmutable
    
    @classmethod
    def get_choices(cls):
        return [(role.value, role.name.title()) for role in cls]
    
    @property
    def display_name(self):
        names = {
            'SUPERADMIN': 'Super Administrador'
        }
        return names.get(self.name, self.name.title())

# Tabla intermedia para relación many-to-many entre Requerimiento, Trabajador y Especialidad
requerimiento_trabajador_especialidad = db.Table('requerimiento_trabajador_especialidad',
    db.Column('requerimiento_id', db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), primary_key=True),
    db.Column('trabajador_id', db.Integer, db.ForeignKey('trabajador.id', ondelete='CASCADE'), primary_key=True),
    db.Column('especialidad_id', db.Integer, db.ForeignKey('especialidad.id', ondelete='CASCADE'), primary_key=True),
    db.Column('fecha_asignacion', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('activo', db.Boolean, default=True, nullable=False)
)

class TimestampMixin:
    """Mixin para agregar timestamps automáticos a los modelos"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Tabla intermedia para relación many-to-many entre Trabajador y Area
trabajador_areas = db.Table('trabajador_areas',
    db.Column('trabajador_id', db.Integer, db.ForeignKey('trabajador.id', ondelete='CASCADE'), primary_key=True),
    db.Column('area_id', db.Integer, db.ForeignKey('area.id', ondelete='CASCADE'), primary_key=True),
    db.Column('fecha_asignacion', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('activo', db.Boolean, default=True, nullable=False),
    db.Index('idx_trabajador_areas_trabajador', 'trabajador_id'),
    db.Index('idx_trabajador_areas_area', 'area_id'),
    db.Index('idx_trabajador_areas_activo', 'activo')
)

class Prioridad(db.Model, TimestampMixin):
    __tablename__ = 'prioridad'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_prioridad_nombre'),
        CheckConstraint('cuadrante >= 1 AND cuadrante <= 4', name='ck_prioridad_cuadrante'),
        CheckConstraint('orden > 0', name='ck_prioridad_orden'),
        Index('idx_prioridad_cuadrante', 'cuadrante'),
        Index('idx_prioridad_orden', 'orden')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    urgencia = db.Column(db.Boolean, default=False, nullable=False)
    importancia = db.Column(db.Boolean, default=False, nullable=False)
    cuadrante = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(7), default='#6c757d', nullable=False)
    orden = db.Column(db.Integer, default=1, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones - Sin backref para evitar conflictos
    requerimientos = db.relationship('Requerimiento', back_populates='prioridad', lazy='dynamic')
    
    @validates('color')
    def validate_color(self, key, color):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValueError('El color debe estar en formato hexadecimal (#RRGGBB)')
        return color
    
    def __repr__(self):
        return f'<Prioridad {self.nombre}>'

class Estado(db.Model, TimestampMixin):
    __tablename__ = 'estado'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_estado_nombre'),
        Index('idx_estado_activo', 'activo')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    requerimientos = db.relationship('Requerimiento', back_populates='estado', lazy='dynamic')
    
    def __repr__(self):
        return f'<Estado {self.nombre}>'


class Fase(db.Model, TimestampMixin):
    __tablename__ = 'fase'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_fase_nombre'),
        Index('idx_fase_activo', 'activo')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<Fase {self.nombre}>'


class Tipologia(db.Model, TimestampMixin):
    __tablename__ = 'tipologia'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_tipologia_nombre'),
        Index('idx_tipologia_activo', 'activo')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    nombrecorto = db.Column(db.String(50), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    id_fase = db.Column(db.Integer, db.ForeignKey('fase.id'), nullable=True)
    
    # Relaciones
    fase = db.relationship('Fase', backref='tipologias')
    requerimientos = db.relationship('Requerimiento', back_populates='tipologia', lazy='dynamic')
    
    def __repr__(self):
        return f'<Tipologia {self.nombre}>'

class Financiamiento(db.Model, TimestampMixin):
    __tablename__ = 'financiamiento'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_financiamiento_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    requerimientos = db.relationship('Requerimiento', back_populates='financiamiento', lazy='dynamic')
    
    def __repr__(self):
        return f'<Financiamiento {self.nombre}>'

class TipoProyecto(db.Model, TimestampMixin):
    __tablename__ = 'tipoproyecto'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_tipoproyecto_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    nombrecorto = db.Column(db.String(50), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    requerimientos = db.relationship('Requerimiento', back_populates='tipoproyecto', lazy='dynamic')
    
    def __repr__(self):
        return f'<TipoProyecto {self.nombre}>'

class Area(db.Model, TimestampMixin):
    __tablename__ = 'area'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_area_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones TEMPORALES (hasta migración)
    trabajadores = db.relationship('Trabajador', foreign_keys='Trabajador.area_id', back_populates='area', lazy='dynamic')
    # trabajadores_principales = db.relationship('Trabajador', foreign_keys='Trabajador.area_principal_id', back_populates='area_principal', lazy='dynamic')
    trabajadores_asignados = db.relationship('Trabajador', secondary=trabajador_areas, back_populates='areas_asignadas', lazy='dynamic')
    
    @property
    def todos_trabajadores(self):
        """Obtiene todos los trabajadores (principales + asignados) de esta área - VERSION TEMPORAL"""
        # Por ahora, solo trabajadores con area_id
        return self.trabajadores.all()
        
        # VERSIÓN COMPLETA (después de migración):
        # principales = self.trabajadores_principales.all()
        # asignados = self.trabajadores_asignados.filter(trabajador_areas.c.activo == True).all()
        
        # # Combinar sin duplicados
        # trabajadores_ids = set()
        # result = []
        
        # for trabajador in principales + asignados:
        #     if trabajador.id not in trabajadores_ids:
        #         trabajadores_ids.add(trabajador.id)
        #         result.append(trabajador)
        
        # return result
    
    @property 
    def cantidad_trabajadores(self):
        """Cantidad total de trabajadores en esta área - VERSION TEMPORAL"""
        return self.trabajadores.count()
        # return len(self.todos_trabajadores)  # Versión completa después de migración
    
    def __repr__(self):
        return f'<Area {self.nombre}>'

class Especialidad(db.Model, TimestampMixin):
    __tablename__ = 'especialidad'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_especialidad_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    equipos_trabajo = db.relationship('EquipoTrabajo', back_populates='especialidad', lazy='dynamic')
    
    def __repr__(self):
        return f'<Especialidad {self.nombre}>'

class Equipo(db.Model, TimestampMixin):
    __tablename__ = 'equipo'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_equipo_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<Equipo {self.nombre}>'

class Trabajador(db.Model, TimestampMixin, UserMixin):
    __tablename__ = 'trabajador'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_trabajador_nombre'),
        UniqueConstraint('email', name='uq_trabajador_email'),
        UniqueConstraint('rut', name='uq_trabajador_rut'),
        Index('idx_trabajador_activo', 'activo'),
        Index('idx_trabajador_profesion', 'profesion'),
        Index('idx_trabajador_email', 'email'),
        Index('idx_trabajador_rol', 'rol'),
        Index('idx_trabajador_area', 'area_id'),  # Temporal
        Index('idx_trabajador_rut', 'rut')
        # Index('idx_trabajador_area_principal', 'area_principal_id')  # Se activará después de migración
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(12), nullable=True)  # Formato: 12.345.678-9 - Opcional para facilitar seeds
    profesion = db.Column(db.String(255), nullable=True)
    nombrecorto = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True, unique=True)
    telefono = db.Column(db.String(20), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    rol = db.Column(db.Enum(UserRole), nullable=True)  # Solo para SUPERADMIN
    custom_role_id = db.Column(db.Integer, db.ForeignKey('custom_roles.id'), nullable=True)  # Para otros roles
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    intentos_fallidos = db.Column(db.Integer, default=0, nullable=False)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    # TEMPORAL: Mantener area_id para compatibilidad hasta migración
    area_id = db.Column(db.Integer, db.ForeignKey('area.id', ondelete='SET NULL'), nullable=True)
    # area_principal_id = db.Column(db.Integer, db.ForeignKey('area.id', ondelete='SET NULL'), nullable=True)  # Se activará después de migración
    
    # NUEVOS CAMPOS: Sector y Recinto para reemplazar áreas
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id', ondelete='SET NULL'), nullable=True)
    recinto_id = db.Column(db.Integer, db.ForeignKey('recinto.id', ondelete='SET NULL'), nullable=True)
    
    # Instancia de Argon2 para hash de contraseñas
    _ph = PasswordHasher()
    
    # Relaciones TEMPORALES (compatibilidad)
    area = db.relationship('Area', foreign_keys=[area_id], back_populates='trabajadores')
    # area_principal = db.relationship('Area', foreign_keys=[area_principal_id], back_populates='trabajadores_principales')
    # areas_asignadas = db.relationship('Area', secondary=trabajador_areas, back_populates='trabajadores_asignados', lazy='dynamic')
    areas_asignadas = db.relationship('Area', secondary=trabajador_areas, back_populates='trabajadores_asignados', lazy='dynamic')
    
    # NUEVAS RELACIONES: Sector y Recinto
    sector = db.relationship('Sector', foreign_keys=[sector_id], backref='trabajadores')
    recinto = db.relationship('Recinto', foreign_keys=[recinto_id], backref='trabajadores')
    
    equipos_trabajo = db.relationship('EquipoTrabajo', back_populates='trabajador', lazy='dynamic')
    recursos_asignados = db.relationship('RecursoTrabajador', back_populates='trabajador', lazy='dynamic')
    avances_actividades = db.relationship('AvanceActividad', back_populates='trabajador', lazy='dynamic')
    
    # Relación con rol personalizado
    custom_role = db.relationship('CustomRole', backref='trabajadores')
    
    @property
    def password(self):
        """No permitir leer la contraseña"""
        raise AttributeError('La contraseña no es un atributo legible')
    
    @password.setter
    def password(self, password):
        """Establecer hash de contraseña usando Argon2"""
        if password:
            try:
                self.password_hash = self._ph.hash(password)
            except HashingError as e:
                raise ValueError(f'Error al hashear contraseña: {e}')
    
    def verify_password(self, password):
        """Verificar contraseña usando Argon2"""
        if not self.password_hash or not password:
            return False
        
        try:
            self._ph.verify(self.password_hash, password)
            
            # Si el hash necesita actualización (parámetros cambiaron)
            if self._ph.check_needs_rehash(self.password_hash):
                self.password = password  # Rehash automático
                db.session.commit()
            
            return True
        except VerifyMismatchError:
            return False
    
    def is_active(self):
        """Requerido por Flask-Login - usuario activo y no bloqueado"""
        if not self.activo:
            return False
        
        # Verificar si está bloqueado
        if self.bloqueado_hasta and datetime.utcnow() < self.bloqueado_hasta:
            return False
        
        return True
    
    def is_authenticated(self):
        """Requerido por Flask-Login"""
        return True
    
    def is_anonymous(self):
        """Requerido por Flask-Login"""
        return False
    
    def get_id(self):
        """Requerido por Flask-Login"""
        return str(self.id)
    
    def update_last_access(self):
        """Actualizar último acceso y resetear intentos fallidos"""
        self.ultimo_acceso = datetime.utcnow()
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        db.session.commit()
    
    def increment_failed_attempts(self):
        """Incrementar intentos fallidos y bloquear si es necesario"""
        self.intentos_fallidos += 1
        
        # Bloquear después de 5 intentos fallidos por 15 minutos
        if self.intentos_fallidos >= 5:
            from datetime import timedelta
            self.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=15)
        
        db.session.commit()
    
    @staticmethod
    def validate_rut(rut):
        """Validar formato y dígito verificador del RUT chileno"""
        if not rut:
            return False
        
        # Limpiar el RUT (quitar puntos, guiones y espacios)
        rut_clean = rut.replace('.', '').replace('-', '').replace(' ', '').upper()
        
        # Verificar que tenga al menos 2 caracteres (número + dígito verificador)
        if len(rut_clean) < 2:
            return False
        
        # Separar número del dígito verificador
        rut_number = rut_clean[:-1]
        dv = rut_clean[-1]
        
        # Verificar que el número sea numérico
        if not rut_number.isdigit():
            return False
        
        # Calcular dígito verificador
        suma = 0
        multiplicador = 2
        
        for digit in reversed(rut_number):
            suma += int(digit) * multiplicador
            multiplicador += 1
            if multiplicador == 8:
                multiplicador = 2
        
        remainder = suma % 11
        calculated_dv = 11 - remainder
        
        if calculated_dv == 11:
            calculated_dv = '0'
        elif calculated_dv == 10:
            calculated_dv = 'K'
        else:
            calculated_dv = str(calculated_dv)
        
        return dv == calculated_dv
    
    @staticmethod
    def format_rut(rut):
        """Formatear RUT con puntos y guión"""
        if not rut:
            return rut
        
        # Limpiar el RUT
        rut_clean = rut.replace('.', '').replace('-', '').replace(' ', '').upper()
        
        if len(rut_clean) < 2:
            return rut
        
        # Separar número del dígito verificador
        rut_number = rut_clean[:-1]
        dv = rut_clean[-1]
        
        # Formatear con puntos
        formatted = ""
        for i, digit in enumerate(reversed(rut_number)):
            if i > 0 and i % 3 == 0:
                formatted = "." + formatted
            formatted = digit + formatted
        
        return f"{formatted}-{dv}"
    
    @property
    def todas_las_areas(self):
        """Obtiene todas las áreas del trabajador (temporal + asignadas)"""
        areas = []
        
        # Área temporal (compatibilidad)
        if self.area:
            areas.append(self.area)
        
        # Áreas asignadas (many-to-many)
        areas_asignadas_activas = self.areas_asignadas.filter(trabajador_areas.c.activo == True).all()
        for area in areas_asignadas_activas:
            if area not in areas:
                areas.append(area)
        
        return areas
    
    # Métodos de autorización dinámicos basados en permisos de página
    def is_superadmin(self):
        """Verificar si es super administrador"""
        return self.rol == UserRole.SUPERADMIN
    
    def has_page_permission(self, page_route):
        """Verificar si el usuario tiene permiso para acceder a una página específica"""
        if self.rol == UserRole.SUPERADMIN:
            return True
        
        if not self.custom_role:
            return False
        
        # Buscar la página por ruta usando una query directa
        from sqlalchemy import and_
        page_query = db.session.query(Page).filter(
            and_(Page.route == page_route, Page.active == True)
        ).first()
        
        if not page_query:
            return False
        
        # Verificar si el rol tiene permiso para esta página
        permission_query = db.session.query(PagePermission).filter(
            and_(
                PagePermission.page_id == page_query.id,
                PagePermission.custom_role_id == self.custom_role.id
            )
        ).first()
        
        return permission_query is not None
    
    def get_accessible_pages(self):
        """Obtener todas las páginas a las que el usuario tiene acceso"""
        if self.rol == UserRole.SUPERADMIN:
            # SUPERADMIN tiene acceso a todas las páginas
            return db.session.query(Page).filter(Page.active == True).all()
        
        if not self.custom_role:
            return []
        
        # Obtener páginas específicas del rol personalizado
        permissions = db.session.query(PagePermission).filter(
            PagePermission.custom_role_id == self.custom_role.id
        ).all()
        
        page_ids = [perm.page_id for perm in permissions]
        if not page_ids:
            return []
        
        return db.session.query(Page).filter(
            Page.id.in_(page_ids), Page.active == True
        ).all()
    
    def can_access_category(self, category_name):
        """Verificar si el usuario puede acceder a alguna página de una categoría"""
        if self.rol == UserRole.SUPERADMIN:
            return True
        
        if not self.custom_role:
            return False
        
        # Buscar la categoría
        category_query = db.session.query(Category).filter(
            Category.name == category_name
        ).first()
        
        if not category_query:
            return False
        
        # Verificar si tiene acceso a alguna página de esta categoría
        accessible_pages = self.get_accessible_pages()
        for page in accessible_pages:
            if page.category_id == category_query.id:
                return True
        
        return False
    
    # Métodos de compatibilidad (obsoletos pero mantenidos por compatibilidad)
    def is_admin(self):
        """Verificar si es administrador - Basado en permisos dinámicos"""
        return (self.rol == UserRole.SUPERADMIN or 
                self.can_access_category('Administración'))
    
    def is_supervisor(self):
        """Verificar si es supervisor - Basado en permisos dinámicos"""
        return (self.rol == UserRole.SUPERADMIN or 
                self.can_access_category('Control'))
    
    def is_usuario(self):
        """Verificar si es usuario básico - Basado en permisos dinámicos"""
        return self.custom_role and self.custom_role.name == 'USUARIO'
    
    def can_manage_users(self):
        """Puede gestionar usuarios - Basado en permisos de página específica"""
        return (self.rol == UserRole.SUPERADMIN or 
                self.has_page_permission('/users') or
                self.can_access_category('Usuarios'))
    
    def can_manage_projects(self):
        """Puede gestionar proyectos - Basado en permisos de página específica"""
        return (self.rol == UserRole.SUPERADMIN or 
                self.has_page_permission('/projects') or
                self.can_access_category('Requerimiento'))
    
    def can_view_reports(self):
        """Puede ver reportes - Basado en permisos de página específica"""
        return (self.rol == UserRole.SUPERADMIN or 
                self.has_page_permission('/reports') or
                self.can_access_category('Sistema'))
    
    def can_modify_system(self):
        """Puede modificar configuraciones del sistema"""
        return self.rol == UserRole.SUPERADMIN
    
    @property
    def rol_display(self):
        """Nombre legible del rol"""
        if self.rol == UserRole.SUPERADMIN:
            return self.rol.display_name
        elif self.custom_role:
            return self.custom_role.name
        return 'Sin rol'
    
    @property
    def effective_role(self):
        """Obtiene el rol efectivo (UserRole o CustomRole)"""
        if self.rol == UserRole.SUPERADMIN:
            return self.rol.value
        elif self.custom_role:
            return self.custom_role.name
        return None
    
    @property
    def effective_role_display(self):
        """Obtiene el nombre legible del rol efectivo"""
        if self.rol == UserRole.SUPERADMIN:
            return self.rol.display_name
        elif self.custom_role:
            return self.custom_role.description or self.custom_role.name
        return 'Sin rol'
    
    def set_custom_role_by_name(self, role_name):
        """Asignar un rol personalizado por nombre"""
        if role_name == 'SUPERADMIN':
            self.rol = UserRole.SUPERADMIN
            self.custom_role_id = None
            return True
        
        custom_role = db.session.query(CustomRole).filter(
            CustomRole.name == role_name, CustomRole.active == True
        ).first()
        
        if custom_role:
            self.rol = None
            self.custom_role_id = custom_role.id
            return True
        
        return False
    
    def update_last_access(self):
        """Actualizar último acceso"""
        self.ultimo_acceso = datetime.utcnow()
        db.session.commit()
    
    # Métodos para manejo de áreas múltiples (VERSIÓN TEMPORAL)
    def is_control(self):
        """Verificar si es administrador de control"""
        if self.rol == UserRole.SUPERADMIN:
            return True
        # Verificar si tiene rol personalizado de control
        if self.custom_role and self.custom_role.name == 'CONTROL':
            return True
        return False
    
    def get_todas_areas(self):
        """Obtener todas las áreas del trabajador - VERSION TEMPORAL"""
        areas = []
        if self.area:  # Usando area_id temporal
            areas.append(self.area)
        return areas
    
    def tiene_area(self, area_id):
        """Verificar si el trabajador pertenece a un área específica - VERSION TEMPORAL"""
        return self.area_id == area_id
    
    def agregar_area(self, area_id):
        """Agregar trabajador a un área adicional - VERSION TEMPORAL (no implementado)"""
        # En versión temporal, solo se puede cambiar el área principal
        return False
    
    def remover_area(self, area_id):
        """Remover trabajador de un área - VERSION TEMPORAL (no implementado)"""
        return False
    
    def puede_administrar_area(self, area_id):
        """Verificar si puede administrar un área específica - VERSION TEMPORAL"""
        if self.rol == UserRole.SUPERADMIN:
            return True
        
        # Verificar roles personalizados
        if self.custom_role:
            if self.custom_role.name == 'CONTROL':
                return self.area_id == area_id
            
            if self.custom_role.name == 'ADMIN':
                return self.area_id == area_id if self.area_id else True
        
        return False
    
    # Propiedades de compatibilidad temporal
    @property
    def area_principal_id(self):
        """Compatibilidad temporal: mapear area_principal_id a area_id"""
        return self.area_id
    
    @property
    def area_principal(self):
        """Compatibilidad temporal: mapear area_principal a area"""
        return self.area
    
    @validates('email')
    def validate_email(self, key, email):
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Email inválido')
        return email
    
    def __repr__(self):
        return f'<Trabajador {self.nombre}>'

class Sector(db.Model, TimestampMixin):
    __tablename__ = 'sector'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_sector_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    requerimientos = db.relationship('Requerimiento', back_populates='sector', lazy='dynamic')
    tipos_recinto = db.relationship('TipoRecinto', back_populates='sector', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Sector {self.nombre}>'

class TipoRecinto(db.Model, TimestampMixin):
    __tablename__ = 'tiporecinto'
    __table_args__ = (
        UniqueConstraint('nombre', 'id_sector', name='uq_tiporecinto_nombre_sector'),
        Index('idx_tiporecinto_sector', 'id_sector'),
        Index('idx_tiporecinto_activo', 'activo')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_sector = db.Column(db.Integer, db.ForeignKey('sector.id', ondelete='RESTRICT'), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    sector = db.relationship('Sector', back_populates='tipos_recinto')
    requerimientos = db.relationship('Requerimiento', back_populates='tiporecinto', lazy='dynamic')
    recintos = db.relationship('Recinto', back_populates='tiporecinto', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TipoRecinto {self.nombre}>'

class Recinto(db.Model, TimestampMixin):
    __tablename__ = 'recinto'
    __table_args__ = (
        UniqueConstraint('nombre', 'id_tiporecinto', name='uq_recinto_nombre_tiporecinto'),
        Index('idx_recinto_tiporecinto', 'id_tiporecinto'),
        Index('idx_recinto_activo', 'activo')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_tiporecinto = db.Column(db.Integer, db.ForeignKey('tiporecinto.id', ondelete='RESTRICT'), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    tiporecinto = db.relationship('TipoRecinto', back_populates='recintos')
    requerimientos = db.relationship('Requerimiento', back_populates='recinto', lazy='dynamic')
    
    @property
    def sector(self):
        """Obtener el sector a través del tiporecinto"""
        return self.tiporecinto.sector if self.tiporecinto else None
    
    @property  
    def sector_id(self):
        """Obtener el sector_id a través del tiporecinto"""
        return self.tiporecinto.id_sector if self.tiporecinto else None
    
    def __repr__(self):
        return f'<Recinto {self.nombre}>'


class Requerimiento(db.Model, TimestampMixin):
    __tablename__ = 'requerimiento'
    __table_args__ = (
        Index('idx_requerimiento_estado', 'id_estado'),
        Index('idx_requerimiento_fecha', 'fecha'),
        Index('idx_requerimiento_prioridad', 'id_prioridad'),
        Index('idx_requerimiento_sector', 'id_sector')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    observacion = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    id_sector = db.Column(db.Integer, db.ForeignKey('sector.id', ondelete='RESTRICT'), nullable=False)
    id_tiporecinto = db.Column(db.Integer, db.ForeignKey('tiporecinto.id', ondelete='RESTRICT'), nullable=False)
    id_recinto = db.Column(db.Integer, db.ForeignKey('recinto.id', ondelete='RESTRICT'), nullable=False)
    id_estado = db.Column(db.Integer, db.ForeignKey('estado.id', ondelete='RESTRICT'), nullable=False)
    id_prioridad = db.Column(db.Integer, db.ForeignKey('prioridad.id', ondelete='RESTRICT'), nullable=True)
    id_grupo = db.Column(db.Integer, db.ForeignKey('grupo.id', ondelete='RESTRICT'), nullable=True)
    id_area = db.Column(db.Integer, db.ForeignKey('area.id', ondelete='RESTRICT'), nullable=True)  # Área que solicita el requerimiento
    
    # Campos opcionales que se llenan después de la aceptación
    fecha_aceptacion = db.Column(db.DateTime, nullable=True)
    id_tipologia = db.Column(db.Integer, db.ForeignKey('tipologia.id', ondelete='RESTRICT'), nullable=True)
    id_financiamiento = db.Column(db.Integer, db.ForeignKey('financiamiento.id', ondelete='RESTRICT'), nullable=True)
    id_tipoproyecto = db.Column(db.Integer, db.ForeignKey('tipoproyecto.id', ondelete='RESTRICT'), nullable=True)
    
    # Campo para asignar proyecto (EDT del nivel_esquema = 1)
    proyecto = db.Column(db.String(50), nullable=True)  # EDT del proyecto asignado
    
    # Control
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones - Usar back_populates en lugar de backref
    sector = db.relationship('Sector', back_populates='requerimientos')
    tiporecinto = db.relationship('TipoRecinto', back_populates='requerimientos')
    recinto = db.relationship('Recinto', back_populates='requerimientos')
    estado = db.relationship('Estado', back_populates='requerimientos')
    prioridad = db.relationship('Prioridad', back_populates='requerimientos')
    tipologia = db.relationship('Tipologia', back_populates='requerimientos')
    financiamiento = db.relationship('Financiamiento', back_populates='requerimientos')
    tipoproyecto = db.relationship('TipoProyecto', back_populates='requerimientos')
    grupo = db.relationship('Grupo', back_populates='requerimientos')
    area_solicitante = db.relationship('Area', foreign_keys=[id_area], backref='requerimientos_solicitados')
    equipos_trabajo = db.relationship('EquipoTrabajo', back_populates='requerimiento', lazy='dynamic', cascade='all, delete-orphan')
    gantt_archivo = db.relationship('GanttArchivo', back_populates='requerimiento', uselist=False, cascade='all, delete-orphan')
    avances_actividades = db.relationship('AvanceActividad', back_populates='requerimiento', lazy='dynamic', cascade='all, delete-orphan')
    actividades_proyecto = db.relationship('ActividadProyecto', back_populates='requerimiento', lazy='dynamic', cascade='all, delete-orphan')
    actividades_gantt = db.relationship('ActividadGantt', back_populates='requerimiento', lazy='dynamic', cascade='all, delete-orphan')
    recursos_trabajadores = db.relationship('RecursoTrabajador', back_populates='requerimiento', lazy='dynamic', cascade='all, delete-orphan')
    historial_control = db.relationship('HistorialControl', back_populates='requerimiento', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Requerimiento {self.nombre}>'

class EquipoTrabajo(db.Model, TimestampMixin):
    __tablename__ = 'equipotrabajo'
    __table_args__ = (
        UniqueConstraint('id_requerimiento', 'id_trabajador', 'id_especialidad', name='uq_equipo_req_trab_esp'),
        Index('idx_equipo_requerimiento', 'id_requerimiento'),
        Index('idx_equipo_trabajador', 'id_trabajador'),
        Index('idx_equipo_especialidad', 'id_especialidad'),
        Index('idx_equipo_fecha_asignacion', 'fecha_asignacion')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_requerimiento = db.Column(db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), nullable=False)
    id_trabajador = db.Column(db.Integer, db.ForeignKey('trabajador.id', ondelete='RESTRICT'), nullable=False)
    id_especialidad = db.Column(db.Integer, db.ForeignKey('especialidad.id', ondelete='RESTRICT'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_desasignacion = db.Column(db.DateTime, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    
    # Relaciones
    requerimiento = db.relationship('Requerimiento', back_populates='equipos_trabajo')
    trabajador = db.relationship('Trabajador', back_populates='equipos_trabajo')
    especialidad = db.relationship('Especialidad', back_populates='equipos_trabajo')
    
    def __repr__(self):
        return f'<EquipoTrabajo {self.id}'

class GanttArchivo(db.Model, TimestampMixin):
    __tablename__ = 'gantt_archivo'
    __table_args__ = (
        UniqueConstraint('id_requerimiento', name='uq_gantt_requerimiento'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_requerimiento = db.Column(db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), nullable=False)
    archivo = db.Column(db.LargeBinary, nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    tipo_archivo = db.Column(db.String(50), nullable=False)
    tamano_archivo = db.Column(db.Integer, nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Cambia la relación para evitar conflicto de backref
    requerimiento = db.relationship('Requerimiento', back_populates='gantt_archivo')

    def __repr__(self):
        return f'<GanttArchivo {self.nombre_archivo}>'

class AvanceActividad(db.Model):
    """Modelo para registrar avances de actividades"""
    __tablename__ = 'avance_actividad'
    
    id = db.Column(db.Integer, primary_key=True)
    requerimiento_id = db.Column(db.Integer, db.ForeignKey('requerimiento.id'), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividad_proyecto.id'), nullable=True)
    
    # Información de asignación
    porcentaje_asignacion = db.Column(db.Float, default=100.0)  # % asignado en el Gantt
    
    # Información de progreso
    progreso_actual = db.Column(db.Float, default=0.0)  # % de avance actual
    progreso_anterior = db.Column(db.Float, default=0.0)  # % anterior (para historial)
    
    # Fechas
    fecha_registro = db.Column(db.Date, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Información adicional
    observaciones = db.Column(db.Text)
    
    # Relaciones - Usar back_populates en lugar de backref
    requerimiento = db.relationship('Requerimiento', back_populates='avances_actividades')
    trabajador = db.relationship('Trabajador', back_populates='avances_actividades')
    actividad = db.relationship('ActividadProyecto', back_populates='avances')
    
    def to_dict(self):
        return {
            'id': self.id,
            'requerimiento_id': self.requerimiento_id,
            'trabajador_id': self.trabajador_id,
            'actividad_id': self.actividad_id,
            'porcentaje_asignacion': self.porcentaje_asignacion,
            'progreso_actual': self.progreso_actual,
            'progreso_anterior': self.progreso_anterior,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'observaciones': self.observaciones
        }

class ActividadProyecto(db.Model, TimestampMixin):
    """Modelo para almacenar las actividades de los proyectos extraídas del archivo XLSX"""
    __tablename__ = 'actividad_proyecto'
    __table_args__ = (
        UniqueConstraint('requerimiento_id', 'edt', name='uq_actividad_proyecto_edt'),
        Index('idx_actividad_proyecto_requerimiento', 'requerimiento_id'),
        Index('idx_actividad_proyecto_fecha_inicio', 'fecha_inicio'),
        Index('idx_actividad_proyecto_fecha_fin', 'fecha_fin')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requerimiento_id = db.Column(db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), nullable=False)
    
    # Datos principales de la actividad
    edt = db.Column(db.String(50), nullable=False)  # Estructura de Descomposición del Trabajo
    nombre_tarea = db.Column(db.String(500), nullable=False)  # Nombre de la tarea/actividad
    nivel_esquema = db.Column(db.Integer, default=1, nullable=False)  # Nivel jerárquico
    
    # Fechas y duración
    fecha_inicio = db.Column(db.Date, nullable=False)  # Fecha de inicio
    fecha_fin = db.Column(db.Date, nullable=False)  # Fecha de fin
    duracion = db.Column(db.Integer, nullable=False)  # Duración en días
    dias_corridos = db.Column(db.Integer, nullable=True)  # Días corridos
    
    # Dependencias y recursos
    predecesoras = db.Column(db.Text, nullable=True)  # Actividades predecesoras
    recursos = db.Column(db.Text, nullable=True)  # Recursos asignados
    
    # Progreso
    progreso = db.Column(db.Numeric(5,2), default=0.00, nullable=False)  # Progreso en % (registrado)
    porcentaje_avance_validado = db.Column(db.Numeric(5,2), default=0.00, nullable=False)  # Progreso validado por supervisor
    
    # Datos adicionales del archivo
    datos_adicionales = db.Column(db.JSON, nullable=True)  # Columnas adicionales del XLSX
    
    # Estado
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relación con requerimiento - Usar back_populates
    requerimiento = db.relationship('Requerimiento', back_populates='actividades_proyecto')
    avances = db.relationship('AvanceActividad', back_populates='actividad', lazy='dynamic')
    historial_control = db.relationship('HistorialControl', back_populates='actividad', lazy='dynamic')
    
    def __repr__(self):
        return f'<ActividadProyecto {self.edt}: {self.nombre_tarea}>'
    
    def to_dict(self):
        """Convierte la actividad a diccionario para JSON"""
        return {
            'id': self.id,
            'edt': self.edt,
            'nombre_tarea': self.nombre_tarea,
            'nivel_esquema': self.nivel_esquema,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'duracion': self.duracion,
            'dias_corridos': self.dias_corridos,
            'predecesoras': self.predecesoras,
            'recursos': self.recursos,
            'progreso': float(self.progreso) if self.progreso else 0.0,
            'datos_adicionales': self.datos_adicionales
        }

class ActividadGantt(db.Model, TimestampMixin):
    __tablename__ = 'actividades_gantt'
    __table_args__ = (
        UniqueConstraint('requerimiento_id', 'edt', name='uq_actividades_gantt_req_edt'),
        Index('idx_actividades_gantt_requerimiento', 'requerimiento_id'),
        Index('idx_actividades_gantt_edt', 'edt'),
        Index('idx_actividades_gantt_fecha_inicio', 'fecha_inicio'),
        Index('idx_actividades_gantt_fecha_fin', 'fecha_fin')
    )
    
    id = db.Column(db.Integer, primary_key=True)
    requerimiento_id = db.Column(db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), nullable=False)
    edt = db.Column(db.String(50), nullable=False)
    nombre_tarea = db.Column(db.String(255), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    duracion = db.Column(db.Integer, nullable=False)
    progreso = db.Column(db.Float, default=0.0)
    nivel_esquema = db.Column(db.Integer, default=1)
    predecesoras = db.Column(db.String(255))
    recursos_originales = db.Column(db.Text)  # Campo para guardar recursos como vienen del Excel
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    requerimiento = db.relationship('Requerimiento', back_populates='actividades_gantt')
    recursos_trabajadores = db.relationship('RecursoTrabajador', back_populates='actividad_gantt', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ActividadGantt {self.edt}: {self.nombre_tarea}>'

class RecursoTrabajador(db.Model, TimestampMixin):
    __tablename__ = 'recursos_trabajador'
    __table_args__ = (
        Index('idx_recurso_trabajador_unique', 'actividad_gantt_id', 'id_trabajador'),
        Index('idx_recurso_trabajador_requerimiento', 'requerimiento_id'),
        Index('idx_recurso_trabajador_edt', 'edt'),
        Index('idx_recurso_trabajador_trabajador', 'id_trabajador')
    )
    
    id = db.Column(db.Integer, primary_key=True)
    requerimiento_id = db.Column(db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), nullable=False)
    actividad_gantt_id = db.Column(db.Integer, db.ForeignKey('actividades_gantt.id', ondelete='CASCADE'), nullable=False)
    edt = db.Column(db.String(50), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    recurso = db.Column(db.String(255), nullable=False)  # Nombre del recurso como aparece en Excel
    id_trabajador = db.Column(db.Integer, db.ForeignKey('trabajador.id', ondelete='RESTRICT'), nullable=False)
    porcentaje_asignacion = db.Column(db.Float, default=100.0)  # Porcentaje de asignación
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    requerimiento = db.relationship('Requerimiento', back_populates='recursos_trabajadores')
    trabajador = db.relationship('Trabajador', back_populates='recursos_asignados')
    actividad_gantt = db.relationship('ActividadGantt', back_populates='recursos_trabajadores')
    
    def __repr__(self):
        return f'<RecursoTrabajador {self.recurso}: {self.trabajador.nombre}>'


class Grupo(db.Model, TimestampMixin):
    __tablename__ = 'grupo'
    __table_args__ = (
        UniqueConstraint('nombre', name='uq_grupo_nombre'),
        Index('idx_grupo_nombre', 'nombre'),
        Index('idx_grupo_activo', 'activo')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relaciones
    requerimientos = db.relationship('Requerimiento', back_populates='grupo')
    
    def __repr__(self):
        return f'<Grupo {self.nombre}>'


class HistorialAvanceActividad(db.Model):
    """Modelo para guardar historial de cambios en avances de actividades"""
    __tablename__ = 'historial_avance_actividad'
    
    id = db.Column(db.Integer, primary_key=True)
    requerimiento_id = db.Column(db.Integer, db.ForeignKey('requerimiento.id'), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividad_proyecto.id'), nullable=False)
    
    # Información del cambio
    progreso_anterior = db.Column(db.Float, nullable=False, default=0.0)
    progreso_nuevo = db.Column(db.Float, nullable=False, default=0.0)
    diferencia = db.Column(db.Float, nullable=False, default=0.0)  # progreso_nuevo - progreso_anterior
    
    # Información adicional
    comentarios = db.Column(db.Text)  # Comentarios del trabajador
    fecha_cambio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Información de sesión de guardado (para agrupar cambios del mismo "Guardar todos")
    sesion_guardado = db.Column(db.String(50))  # UUID o timestamp para agrupar cambios de la misma sesión
    
    # Campos de validación
    validado = db.Column(db.Boolean, default=False, nullable=False)  # Si el avance ha sido validado
    validado_por_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=True)  # Supervisor que validó
    fecha_validacion = db.Column(db.DateTime, nullable=True)  # Fecha de validación
    comentario_validacion = db.Column(db.Text)  # Comentarios del supervisor al validar
    
    # Relaciones
    requerimiento = db.relationship('Requerimiento')
    trabajador = db.relationship('Trabajador', foreign_keys=[trabajador_id])
    validado_por = db.relationship('Trabajador', foreign_keys=[validado_por_id])
    actividad = db.relationship('ActividadProyecto')
    
    def to_dict(self):
        return {
            'id': self.id,
            'requerimiento_id': self.requerimiento_id,
            'proyecto_nombre': self.requerimiento.nombre if self.requerimiento else 'N/A',
            'trabajador_id': self.trabajador_id,
            'trabajador_nombre': self.trabajador.nombre if self.trabajador else 'N/A',
            'actividad_id': self.actividad_id,
            'actividad_nombre': self.actividad.nombre if self.actividad else 'N/A',
            'actividad_edt': self.actividad.edt if self.actividad else 'N/A',
            'progreso_anterior': self.progreso_anterior,
            'progreso_nuevo': self.progreso_nuevo,
            'diferencia': self.diferencia,
            'comentarios': self.comentarios,
            'fecha_cambio': self.fecha_cambio.isoformat() if self.fecha_cambio else None,
            'sesion_guardado': self.sesion_guardado,
            'validado': self.validado,
            'validado_por_id': self.validado_por_id,
            'validado_por_nombre': self.validado_por.nombre if self.validado_por else None,
            'fecha_validacion': self.fecha_validacion.isoformat() if self.fecha_validacion else None,
            'comentario_validacion': self.comentario_validacion
        }
    
    def __repr__(self):
        return f'<HistorialAvance {self.actividad.edt if self.actividad else "N/A"}: {self.progreso_anterior}% → {self.progreso_nuevo}%>'


class HistorialControl(db.Model):
    """Modelo para guardar historial de cambios realizados a través de la subida de archivos de control"""
    __tablename__ = 'historial_control'
    __table_args__ = (
        Index('idx_historial_control_fecha', 'fecha_operacion'),
        Index('idx_historial_control_sesion', 'sesion_subida'),
        Index('idx_historial_control_actividad', 'actividad_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Información de la operación
    sesion_subida = db.Column(db.String(50), nullable=False)  # UUID para agrupar cambios de la misma subida
    fecha_operacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nombre_archivo = db.Column(db.String(255), nullable=False)  # Nombre del archivo subido
    
    # Información de la actividad afectada
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividad_proyecto.id'), nullable=False)
    requerimiento_id = db.Column(db.Integer, db.ForeignKey('requerimiento.id'), nullable=False)
    
    # Tipo de operación realizada
    tipo_operacion = db.Column(db.String(50), nullable=False)  # 'INSERT', 'UPDATE', 'SUBIDA_ARCHIVO_COMPLETA'
    
    # Datos anteriores y nuevos (JSON para flexibilidad)
    datos_anteriores = db.Column(db.JSON, nullable=True)  # Valores antes del cambio
    datos_nuevos = db.Column(db.JSON, nullable=False)  # Valores después del cambio
    
    # Información adicional
    fila_excel = db.Column(db.Integer, nullable=False)  # Número de fila en el Excel
    comentarios = db.Column(db.Text, nullable=True)
    
    # Relaciones
    actividad = db.relationship('ActividadProyecto', back_populates='historial_control')
    requerimiento = db.relationship('Requerimiento', back_populates='historial_control')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sesion_subida': self.sesion_subida,
            'fecha_operacion': self.fecha_operacion.isoformat() if self.fecha_operacion else None,
            'nombre_archivo': self.nombre_archivo,
            'actividad_id': self.actividad_id,
            'actividad_nombre': self.actividad.nombre if self.actividad else 'N/A',
            'actividad_edt': self.actividad.edt if self.actividad else 'N/A',
            'requerimiento_id': self.requerimiento_id,
            'proyecto_nombre': self.requerimiento.nombre if self.requerimiento else 'N/A',
            'tipo_operacion': self.tipo_operacion,
            'datos_anteriores': self.datos_anteriores,
            'datos_nuevos': self.datos_nuevos,
            'fila_excel': self.fila_excel,
            'comentarios': self.comentarios
        }
    
    def __repr__(self):
        return f'<HistorialControl {self.tipo_operacion} - {self.actividad.edt if self.actividad else "N/A"}>'


# ============================================================================
# MODELOS PARA SISTEMA DE PERMISOS Y CATEGORÍAS
# ============================================================================

class Category(db.Model, TimestampMixin):
    """Modelo para categorías de páginas"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(20), default='primary', nullable=False)
    description = db.Column(db.Text)
    
    # Nuevos campos para organización de menú
    display_order = db.Column(db.Integer, default=0, nullable=False)
    icon = db.Column(db.String(100), default='fas fa-folder', nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # Relación con páginas
    pages = db.relationship('Page', backref='category_obj', lazy=True, cascade='all, delete-orphan')
    
    # Relación para categorías padre/hijo
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'display_order': self.display_order,
            'icon': self.icon,
            'is_visible': self.is_visible,
            'parent_id': self.parent_id,
            'pages_count': len(self.pages),
            'children_count': len(self.children),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Page(db.Model, TimestampMixin):
    """Modelo para páginas del sistema"""
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    template_path = db.Column(db.String(300))  # Ruta al template HTML
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Nuevos campos para organización de menú
    display_order = db.Column(db.Integer, default=0, nullable=False)
    icon = db.Column(db.String(100), default='fas fa-file', nullable=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    parent_page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=True)
    menu_group = db.Column(db.String(100), nullable=True)  # Para agrupar páginas en submenús
    external_url = db.Column(db.String(500), nullable=True)  # Para enlaces externos
    target_blank = db.Column(db.Boolean, default=False, nullable=False)  # Abrir en nueva ventana
    
    # Relación con permisos
    permissions = db.relationship('PagePermission', backref='page', lazy=True, cascade='all, delete-orphan')
    
    # Relación para páginas padre/hijo
    children = db.relationship('Page', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    def __repr__(self):
        return f'<Page {self.route}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'route': self.route,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category_obj.name if self.category_obj else None,
            'active': self.active,
            'display_order': self.display_order,
            'icon': self.icon,
            'is_visible': self.is_visible,
            'parent_page_id': self.parent_page_id,
            'menu_group': self.menu_group,
            'external_url': self.external_url,
            'target_blank': self.target_blank,
            'roles': [perm.role for perm in self.permissions],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PagePermission(db.Model, TimestampMixin):
    """Modelo para permisos por página y rol (sistema + personalizados)"""
    __tablename__ = 'page_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False)
    
    # Campos para manejar tanto roles del sistema como personalizados
    system_role = db.Column(db.Enum(UserRole), nullable=True)  # Para roles del sistema
    custom_role_id = db.Column(db.Integer, db.ForeignKey('custom_roles.id'), nullable=True)  # Para roles personalizados
    role_name = db.Column(db.String(50), nullable=False)  # Nombre del rol (cache para performance)
    
    # Relación con rol personalizado
    custom_role = db.relationship('CustomRole', backref='page_permissions')
    
    # Constraint para evitar duplicados
    __table_args__ = (
        UniqueConstraint('page_id', 'role_name', name='uq_page_permission_name'),
        CheckConstraint('(system_role IS NOT NULL AND custom_role_id IS NULL) OR (system_role IS NULL AND custom_role_id IS NOT NULL)', 
                       name='ck_permission_role_type'),
    )
    
    @property
    def role(self):
        """Propiedad para mantener compatibilidad con código existente"""
        if self.system_role:
            return self.system_role
        elif self.custom_role:
            # Crear un objeto similar a enum para compatibilidad
            class CustomRoleProxy:
                def __init__(self, name):
                    self.name = name
                    self.value = name.lower()
                
                def __str__(self):
                    return self.name
                
                def __repr__(self):
                    return f'CustomRole.{self.name}'
            
            return CustomRoleProxy(self.custom_role.name)
        return None
    
    @role.setter
    def role(self, value):
        """Setter para mantener compatibilidad con código existente"""
        if isinstance(value, UserRole):
            self.system_role = value
            self.custom_role_id = None
            self.role_name = value.name
        elif isinstance(value, str):
            # Intentar como rol del sistema primero
            try:
                system_role = UserRole[value.upper()]
                self.system_role = system_role
                self.custom_role_id = None
                self.role_name = value.upper()
            except KeyError:
                # Buscar en roles personalizados
                custom_role = CustomRole.query.filter_by(name=value.upper(), active=True).first()
                if custom_role:
                    self.system_role = None
                    self.custom_role_id = custom_role.id
                    self.role_name = value.upper()
                else:
                    raise ValueError(f"Rol '{value}' no encontrado en sistema ni personalizados")
        else:
            raise ValueError(f"Tipo de rol no válido: {type(value)}")
    
    def is_system_role(self):
        """Verificar si es un rol del sistema"""
        return self.system_role is not None
    
    def is_custom_role(self):
        """Verificar si es un rol personalizado"""
        return self.custom_role_id is not None
    
    def __repr__(self):
        role_str = self.role_name if self.role_name else 'Unknown'
        role_type = 'System' if self.is_system_role() else 'Custom'
        return f'<PagePermission {self.page.route if self.page else "Unknown"} - {role_str} ({role_type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'role': self.role_name,
            'role_type': 'system' if self.is_system_role() else 'custom',
            'page_route': self.page.route if self.page else None,
            'page_name': self.page.name if self.page else None
        }

class CustomRole(db.Model, TimestampMixin):
    """Modelo para roles personalizados del sistema"""
    __tablename__ = 'custom_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<CustomRole {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MenuConfiguration(db.Model, TimestampMixin):
    """Modelo para configuración global del menú"""
    __tablename__ = 'menu_configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    sidebar_collapsed = db.Column(db.Boolean, default=False, nullable=False)
    theme = db.Column(db.String(20), default='light', nullable=False)  # light, dark
    menu_style = db.Column(db.String(20), default='vertical', nullable=False)  # vertical, horizontal
    show_icons = db.Column(db.Boolean, default=True, nullable=False)
    show_badges = db.Column(db.Boolean, default=True, nullable=False)
    custom_css = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<MenuConfiguration {self.theme} - {self.menu_style}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sidebar_collapsed': self.sidebar_collapsed,
            'theme': self.theme,
            'menu_style': self.menu_style,
            'show_icons': self.show_icons,
            'show_badges': self.show_badges,
            'custom_css': self.custom_css,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_default_config(cls):
        """Obtener configuración por defecto"""
        config = cls.query.filter_by(id=1).first()
        if not config:
            config = cls(
                id=1,
                sidebar_collapsed=False,
                theme='light',
                menu_style='vertical',
                show_icons=True,
                show_badges=True
            )
            db.session.add(config)
            db.session.commit()
        return config


# Modelo para gestión de asignaciones de administradores a recintos específicos
class AdministradorRecinto(db.Model):
    """
    Tabla intermedia que relaciona administradores con recintos específicos
    que pueden gestionar. Solo SUPERADMIN puede modificar estas asignaciones.
    """
    __tablename__ = 'administrador_recinto'
    
    id = db.Column(db.Integer, primary_key=True)
    administrador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    recinto_id = db.Column(db.Integer, db.ForeignKey('recinto.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    administrador = db.relationship('Trabajador', backref='recintos_asignados')
    recinto = db.relationship('Recinto', backref='administradores_asignados')
    
    # Índices únicos para evitar duplicados
    __table_args__ = (
        db.UniqueConstraint('administrador_id', 'recinto_id', name='_administrador_recinto_uc'),
    )
    
    def __repr__(self):
        return f'<AdministradorRecinto {self.administrador.nombre} -> {self.recinto.nombre}>'
    
    @staticmethod
    def asignar_recinto(administrador_id, recinto_id):
        """
        Asigna un recinto a un administrador o reactiva la asignación si existe
        """
        try:
            # Buscar si ya existe la asignación
            asignacion = AdministradorRecinto.query.filter_by(
                administrador_id=administrador_id,
                recinto_id=recinto_id
            ).first()
            
            if asignacion:
                # Si existe, activarla
                asignacion.activo = True
                asignacion.updated_at = datetime.utcnow()
            else:
                # Si no existe, crearla
                asignacion = AdministradorRecinto(
                    administrador_id=administrador_id,
                    recinto_id=recinto_id,
                    activo=True
                )
                db.session.add(asignacion)
            
            db.session.commit()
            return True, "Recinto asignado exitosamente"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error al asignar recinto: {str(e)}"
    
    @staticmethod
    def desasignar_recinto(administrador_id, recinto_id):
        """
        Desasigna un recinto de un administrador (marca como inactivo)
        """
        try:
            asignacion = AdministradorRecinto.query.filter_by(
                administrador_id=administrador_id,
                recinto_id=recinto_id
            ).first()
            
            if asignacion:
                asignacion.activo = False
                asignacion.updated_at = datetime.utcnow()
                db.session.commit()
                return True, "Recinto desasignado exitosamente"
            else:
                return False, "La asignación no existe"
                
        except Exception as e:
            db.session.rollback()
            return False, f"Error al desasignar recinto: {str(e)}"
    
    @staticmethod
    def obtener_recintos_administrador(administrador_id):
        """
        Obtiene todos los recintos asignados a un administrador
        """
        return AdministradorRecinto.query.filter_by(
            administrador_id=administrador_id,
            activo=True
        ).all()
    
    @staticmethod
    def tiene_acceso_recinto(administrador_id, recinto_id):
        """
        Verifica si un administrador tiene acceso a un recinto específico
        """
        asignacion = AdministradorRecinto.query.filter_by(
            administrador_id=administrador_id,
            recinto_id=recinto_id,
            activo=True
        ).first()
        
        return asignacion is not None
    
    @staticmethod
    def obtener_matriz_completa():
        """
        Obtiene la matriz completa de administradores vs recintos
        para la página de gestión
        """
        # Obtener todos los administradores (dinámicamente buscando rol ADMIN)
        admin_role = CustomRole.query.filter(
            CustomRole.name.in_(['ADMIN', 'ADMINISTRADOR'])
        ).first()
        
        if not admin_role:
            return [], {}, {}
        
        administradores = Trabajador.query.filter(
            Trabajador.custom_role_id == admin_role.id
        ).order_by(Trabajador.nombre).all()
        
        # Obtener estructura jerárquica de sectores > tipos > recintos
        sectores = Sector.query.filter_by(activo=True).order_by(Sector.nombre).all()
        
        estructura = {}
        for sector in sectores:
            estructura[sector] = {}
            tipos_recinto = TipoRecinto.query.filter_by(
                id_sector=sector.id, 
                activo=True
            ).order_by(TipoRecinto.nombre).all()
            
            for tipo in tipos_recinto:
                estructura[sector][tipo] = Recinto.query.filter_by(
                    id_tiporecinto=tipo.id,
                    activo=True
                ).order_by(Recinto.nombre).all()
        
        # Obtener todas las asignaciones activas
        asignaciones = {}
        for admin in administradores:
            asignaciones[admin.id] = []
            asignaciones_admin = AdministradorRecinto.query.filter_by(
                administrador_id=admin.id,
                activo=True
            ).all()
            for asignacion in asignaciones_admin:
                asignaciones[admin.id].append(asignacion.recinto_id)
        
        return administradores, estructura, asignaciones


class TrabajadorRecinto(db.Model):
    """
    Tabla intermedia que relaciona trabajadores con recintos adicionales
    a los que pueden tener acceso. Los administradores pueden gestionar
    estas asignaciones para trabajadores de sus recintos asignados.
    """
    __tablename__ = 'trabajador_recinto'
    
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    recinto_id = db.Column(db.Integer, db.ForeignKey('recinto.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    trabajador = db.relationship('Trabajador', backref='recintos_adicionales')
    recinto = db.relationship('Recinto', backref='trabajadores_adicionales')
    
    # Índices únicos para evitar duplicados
    __table_args__ = (
        db.UniqueConstraint('trabajador_id', 'recinto_id', name='_trabajador_recinto_uc'),
    )
    
    def __repr__(self):
        return f'<TrabajadorRecinto {self.trabajador.nombre} -> {self.recinto.nombre}>'
    
    @staticmethod
    def asignar_recinto(trabajador_id, recinto_id):
        """
        Asigna un recinto adicional a un trabajador o reactiva la asignación si existe
        """
        try:
            # Buscar si ya existe la asignación
            asignacion = TrabajadorRecinto.query.filter_by(
                trabajador_id=trabajador_id,
                recinto_id=recinto_id
            ).first()
            
            if asignacion:
                # Si existe, activarla
                asignacion.activo = True
                asignacion.updated_at = datetime.utcnow()
            else:
                # Si no existe, crearla
                asignacion = TrabajadorRecinto(
                    trabajador_id=trabajador_id,
                    recinto_id=recinto_id,
                    activo=True
                )
                db.session.add(asignacion)
            
            db.session.commit()
            return True, "Recinto asignado exitosamente al trabajador"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error al asignar recinto: {str(e)}"
    
    @staticmethod
    def desasignar_recinto(trabajador_id, recinto_id):
        """
        Desasigna un recinto de un trabajador (marca como inactivo)
        """
        try:
            asignacion = TrabajadorRecinto.query.filter_by(
                trabajador_id=trabajador_id,
                recinto_id=recinto_id
            ).first()
            
            if asignacion:
                asignacion.activo = False
                asignacion.updated_at = datetime.utcnow()
                db.session.commit()
                return True, "Recinto desasignado exitosamente"
            else:
                return False, "La asignación no existe"
                
        except Exception as e:
            db.session.rollback()
            return False, f"Error al desasignar recinto: {str(e)}"
    
    @staticmethod
    def obtener_recintos_trabajador(trabajador_id):
        """
        Obtiene todos los recintos adicionales asignados a un trabajador
        """
        return TrabajadorRecinto.query.filter_by(
            trabajador_id=trabajador_id,
            activo=True
        ).all()
    
    @staticmethod
    def tiene_acceso_recinto(trabajador_id, recinto_id):
        """
        Verifica si un trabajador tiene acceso adicional a un recinto específico
        """
        asignacion = TrabajadorRecinto.query.filter_by(
            trabajador_id=trabajador_id,
            recinto_id=recinto_id,
            activo=True
        ).first()
        
        return asignacion is not None
    
    @staticmethod
    def obtener_matriz_por_administrador(administrador_id):
        """
        Obtiene la matriz de trabajadores vs recintos para un administrador específico
        Solo muestra trabajadores que pertenecen a los recintos que gestiona el admin
        """
        from app.models import Trabajador, Recinto, Sector, TipoRecinto
        
        # Obtener recintos que gestiona el administrador
        recintos_admin = AdministradorRecinto.obtener_recintos_administrador(administrador_id)
        recinto_ids = [asignacion.recinto_id for asignacion in recintos_admin]
        
        if not recinto_ids:
            return [], {}, {}
        
        # Obtener trabajadores que pertenecen a esos recintos (excluyendo administradores)
        # Buscar dinámicamente los roles de administrador
        admin_roles = CustomRole.query.filter(
            CustomRole.name.in_(['ADMIN', 'ADMINISTRADOR', 'SUPERADMIN'])
        ).all()
        admin_role_ids = [role.id for role in admin_roles]
        
        trabajadores = Trabajador.query.filter(
            Trabajador.recinto_id.in_(recinto_ids),
            ~Trabajador.custom_role_id.in_(admin_role_ids) if admin_role_ids else True
        ).order_by(Trabajador.nombre).all()
        
        # Obtener estructura jerárquica solo de los recintos que gestiona
        recintos = Recinto.query.filter(
            Recinto.id.in_(recinto_ids),
            Recinto.activo == True
        ).all()
        
        estructura = {}
        for recinto in recintos:
            tipo = TipoRecinto.query.get(recinto.id_tiporecinto)
            sector = Sector.query.get(tipo.id_sector) if tipo else None
            
            if sector not in estructura:
                estructura[sector] = {}
            if tipo not in estructura[sector]:
                estructura[sector][tipo] = []
            
            estructura[sector][tipo].append(recinto)
        
        # Obtener todas las asignaciones activas de los trabajadores
        asignaciones = {}
        for trabajador in trabajadores:
            asignaciones[trabajador.id] = []
            asignaciones_trabajador = TrabajadorRecinto.query.filter_by(
                trabajador_id=trabajador.id,
                activo=True
            ).all()
            for asignacion in asignaciones_trabajador:
                asignaciones[trabajador.id].append(asignacion.recinto_id)
        
        return trabajadores, estructura, asignaciones


class ObservacionRequerimiento(db.Model, TimestampMixin):
    """Modelo para registrar todas las observaciones y eventos del ciclo de vida de los requerimientos"""
    __tablename__ = 'observacion_requerimiento'
    __table_args__ = (
        Index('idx_observacion_requerimiento', 'id_requerimiento'),
        Index('idx_observacion_fecha', 'fecha_registro'),
        Index('idx_observacion_usuario', 'id_usuario'),
        Index('idx_observacion_tipo', 'tipo_evento')
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_requerimiento = db.Column(db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), nullable=False)
    observacion = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('trabajador.id', ondelete='RESTRICT'), nullable=False)
    pagina_origen = db.Column(db.String(100), nullable=False)  # Página desde donde se hizo la observación
    tipo_evento = db.Column(db.Enum(
        'requerimiento', 'aceptado', 'rechazado', 'completado', 
        'proyecto_aceptado', 'proyecto_rechazado', 'obs_control', 'finalizado'
    ), nullable=False)
    
    # Relaciones
    requerimiento = db.relationship('Requerimiento', backref=db.backref('observaciones_historial', lazy='dynamic', cascade='all, delete-orphan'))
    usuario = db.relationship('Trabajador', backref=db.backref('observaciones_realizadas', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ObservacionRequerimiento {self.id}: {self.tipo_evento} - {self.observacion[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_requerimiento': self.id_requerimiento,
            'observacion': self.observacion,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'id_usuario': self.id_usuario,
            'usuario_nombre': self.usuario.nombre if self.usuario else 'Usuario eliminado',
            'pagina_origen': self.pagina_origen,
            'tipo_evento': self.tipo_evento
        }
