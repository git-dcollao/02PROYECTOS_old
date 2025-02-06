from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from app import db

db = SQLAlchemy()

# Agregar la tabla de asociación antes de las definiciones de clase
requerimiento_trabajador_especialidad = db.Table('requerimiento_trabajador_especialidad',
    db.Column('requerimiento_id', db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), primary_key=True),
    db.Column('trabajador_id', db.Integer, db.ForeignKey('trabajador.id', ondelete='CASCADE'), primary_key=True),
    db.Column('especialidad_id', db.Integer, db.ForeignKey('especialidad.id', ondelete='CASCADE'), primary_key=True)
)

class Sector(db.Model):
    __tablename__ = 'sector'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class TipoRecinto(db.Model):
    __tablename__ = 'tiporecinto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)    
    id_sector = db.Column(db.Integer, db.ForeignKey('sector.id', ondelete='CASCADE'), nullable=False)
    sector = db.relationship('Sector', backref=db.backref('sector', lazy=True, cascade='all, delete-orphan'))

class Recinto(db.Model):
    __tablename__ = 'recinto'
    id = db.Column(db.Integer, primary_key=True) 
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_tiporecinto = db.Column(db.Integer, db.ForeignKey('tiporecinto.id', ondelete='CASCADE'), nullable=False)
    tiporecinto = db.relationship('TipoRecinto', backref=db.backref('tiposrecintos', lazy=True, cascade='all, delete-orphan'))

class Etapa(db.Model):
    __tablename__ = 'etapa'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    financiamiento = db.Column(db.Boolean, nullable=True)
    id_tipologia = db.Column(db.Integer, db.ForeignKey('tipologia.id', ondelete='CASCADE'), nullable=False)
    tipologia = db.relationship('Tipologia', backref=db.backref('etapas', lazy=True, cascade='all, delete-orphan'))

class Trabajador(db.Model):
    __tablename__ = 'trabajador'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    profesion = db.Column(db.String(100), nullable=True)  # Cambiado a nullable=True
    nombrecorto = db.Column(db.String(50), nullable=True)
    password = db.Column(db.Text, nullable=True)

class EtapaN1(db.Model):
    __tablename__ = 'etapaN1'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

class EtapaN2(db.Model):
    __tablename__ = 'etapaN2'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_etapaN1 = db.Column(db.Integer, db.ForeignKey('etapaN1.id', ondelete='CASCADE'), nullable=False)
    etapaN1 = db.relationship('EtapaN1', backref=db.backref('etapasN2', lazy=True, cascade='all, delete-orphan'))

class EtapaN3(db.Model):
    __tablename__ = 'etapaN3'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_etapaN2 = db.Column(db.Integer, db.ForeignKey('etapaN2.id', ondelete='CASCADE'), nullable=False)
    etapaN2 = db.relationship('EtapaN2', backref=db.backref('etapasN3', lazy=True, cascade='all, delete-orphan'))

class EtapaN4(db.Model):
    __tablename__ = 'etapaN4'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_etapaN3 = db.Column(db.Integer, db.ForeignKey('etapaN3.id', ondelete='CASCADE'), nullable=False)
    etapaN3 = db.relationship('EtapaN3', backref=db.backref('etapasN4', lazy=True, cascade='all, delete-orphan'))

class Financiamiento(db.Model):
    __tablename__ = 'financiamiento'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

class Especialidad(db.Model):
    __tablename__ = 'especialidad'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Equipo(db.Model):
    __tablename__ = 'equipo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Tipologia(db.Model):
    __tablename__ = 'tipologia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nombrecorto = db.Column(db.String(50), nullable=True)
    id_fase = db.Column(db.Integer, db.ForeignKey('fase.id', ondelete='CASCADE'), nullable=False)
    fase = db.relationship('Fase', backref=db.backref('tipologia', lazy=True, cascade='all, delete-orphan'))

class Fase(db.Model):
    __tablename__ = 'fase'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
 
class TipoProyecto(db.Model):
    __tablename__ = 'tipoproyecto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nombrecorto = db.Column(db.String(50), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    
class Estado(db.Model):
    __tablename__ = 'estado'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Requerimiento(db.Model): 
    __tablename__ = 'requerimiento'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    descripcion = db.Column(db.Text)
    observacion = db.Column(db.Text, nullable=True)
    id_sector = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    id_tiporecinto = db.Column(db.Integer, db.ForeignKey('tiporecinto.id'), nullable=False)
    id_recinto = db.Column(db.Integer, db.ForeignKey('recinto.id'), nullable=False)
    id_estado = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    fecha_aceptacion = db.Column(db.DateTime, nullable=True)
    id_tipologia = db.Column(db.Integer, db.ForeignKey('tipologia.id'), nullable=True)
    id_financiamiento = db.Column(db.Integer, db.ForeignKey('financiamiento.id'), nullable=True)
    id_tipoproyecto = db.Column(db.Integer, db.ForeignKey('tipoproyecto.id'), nullable=True)

    # Relaciones
    trabajadores = db.relationship(
        'Trabajador',
        secondary=requerimiento_trabajador_especialidad,
        backref=db.backref('requerimientos', lazy='dynamic'),
        overlaps="trabajadores_especialidades,requerimientos_con_especialidad"
    )
    
    trabajadores_especialidades = db.relationship(
        'Trabajador',
        secondary=requerimiento_trabajador_especialidad,
        primaryjoin=(id == requerimiento_trabajador_especialidad.c.requerimiento_id),
        secondaryjoin=(Trabajador.id == requerimiento_trabajador_especialidad.c.trabajador_id),
        backref=db.backref('requerimientos_con_especialidad', lazy='dynamic'),
        overlaps="trabajadores,requerimientos",
        viewonly=True  # Hacer esta relación de solo lectura
    )
    sector = db.relationship('Sector', backref='requerimientos')
    tiporecinto = db.relationship('TipoRecinto', backref='requerimientos')
    recinto = db.relationship('Recinto', backref='requerimientos')
    estado = db.relationship('Estado', backref='requerimientos')
    equipos_trabajo = db.relationship(
        'EquipoTrabajo',
        backref=db.backref('requerimiento_padre', lazy=True),  # Cambiado de 'requerimiento' a 'requerimiento_padre'
        lazy=True,
        cascade='all, delete-orphan'
    )
    tipologia = db.relationship('Tipologia', backref='requerimientos')
    financiamiento = db.relationship('Financiamiento', backref='requerimientos')
    tipoproyecto = db.relationship('TipoProyecto', backref='requerimientos')

    def agregar_trabajador_especialidad(self, trabajador, especialidad):
        """Método para agregar un trabajador con su especialidad"""
        stmt = requerimiento_trabajador_especialidad.insert().values(
            requerimiento_id=self.id,
            trabajador_id=trabajador.id,
            especialidad_id=especialidad.id
        )
        db.session.execute(stmt)
        db.session.commit()

class EquipoTrabajo(db.Model):
    __tablename__ = 'equipo_trabajo'
    id = db.Column(db.Integer, primary_key=True)
    id_requerimiento = db.Column(db.Integer, db.ForeignKey('requerimiento.id', ondelete='CASCADE'), nullable=False)
    id_trabajador = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    id_especialidad = db.Column(db.Integer, db.ForeignKey('especialidad.id'), nullable=False)
    
    # Relaciones
    trabajador = db.relationship('Trabajador', backref='equipos_trabajo')
    especialidad = db.relationship('Especialidad', backref='equipos_trabajo')

def init_db():
    """Crear todas las tablas en la base de datos"""
    db.drop_all()  # Eliminar todas las tablas existentes
    db.create_all()  # Crear las tablas nuevamente
    
    # Importar y ejecutar los seeds
    from .seeds import seed_data
    seed_data()
    #pass

