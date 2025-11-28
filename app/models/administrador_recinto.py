"""
Modelo para gestión de asignaciones de administradores a recintos específicos.
Permite que un SUPERADMIN asigne qué recintos puede gestionar cada administrador.
"""
from app import db
from datetime import datetime

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
        from app.models import Trabajador, Sector, TipoRecinto, Recinto, CustomRole
        
        # Obtener todos los administradores
        administradores = Trabajador.query.join(CustomRole).filter(
            CustomRole.name == 'ADMINISTRADOR'
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
            asignaciones[admin.id] = set()
            asignaciones_admin = AdministradorRecinto.query.filter_by(
                administrador_id=admin.id,
                activo=True
            ).all()
            for asignacion in asignaciones_admin:
                asignaciones[admin.id].add(asignacion.recinto_id)
        
        return administradores, estructura, asignaciones