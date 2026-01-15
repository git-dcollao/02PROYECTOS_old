# -*- coding: utf-8 -*-
from app import db
from app.models import (
    Estado, Tipologia, Financiamiento, TipoProyecto, Especialidad,  
    Equipo, Trabajador, Sector, TipoRecinto, Recinto, Requerimiento, Prioridad, Grupo, Area,
    Category, Page, PagePermission, UserRole, CustomRole, MenuConfiguration
)
from datetime import datetime

def crear_estados_iniciales():
    try:
        # Verificar si ya existen estados
        if Estado.query.first():
            print("✅ Los estados ya existen, saltando creación...")
            return True

        print("📋 Creando estados iniciales...")
        estados_data = [
            {'nombre': 'En Solicitud'},
            {'nombre': 'Solicitud Aceptada'},
            {'nombre': 'En Desarrollo'},
            {'nombre': 'Desarrollo Aceptado'},
            {'nombre': 'Desarrollo Completado'},
            {'nombre': 'En Ejecución'},
            {'nombre': 'Fin de Ejecución'},
            {'nombre': 'Finalizado'},
            {'nombre': 'Rechazado'},
            {'nombre': 'Cancelado'}
        ]
        
        for estado_data in estados_data:
            estado = Estado(**estado_data)
            db.session.add(estado)

        db.session.commit()
        print("✅ Estados iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando estados iniciales: {e}")
        return False

def crear_prioridades_iniciales():
    try:
        if Prioridad.query.first():
            print("✅ Las prioridades ya existen, saltando creación...")
            return True

        print("📋 Creando prioridades iniciales...")
        prioridades_data = [
            {
                'nombre': 'Urgente e Importante',
                'descripcion': 'Crisis, emergencias, problemas urgentes con fechas límite',
                'urgencia': True,
                'importancia': True,
                'cuadrante': 1,
                'color': '#dc3545',
                'orden': 1
            },
            {
                'nombre': 'Importante, No Urgente',
                'descripcion': 'Planificación, prevención, desarrollo personal, nuevas oportunidades',
                'urgencia': False,
                'importancia': True,
                'cuadrante': 2,
                'color': '#ffc107',
                'orden': 2
            },
            {
                'nombre': 'Urgente, No Importante',
                'descripcion': 'Interrupciones, algunas llamadas, correos, reuniones',
                'urgencia': True,
                'importancia': False,
                'cuadrante': 3,
                'color': '#fd7e14',
                'orden': 3
            },
            {
                'nombre': 'No Urgente, No Importante',
                'descripcion': 'Trivialidades, pérdidas de tiempo, actividades placenteras',
                'urgencia': False,
                'importancia': False,
                'cuadrante': 4,
                'color': '#6c757d',
                'orden': 4
            }
        ]

        for prioridad_data in prioridades_data:
            prioridad = Prioridad(**prioridad_data)
            db.session.add(prioridad)

        db.session.commit()
        print("✅ Prioridades iniciales creadas exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando prioridades iniciales: {e}")
        return False


def crear_tipologias_iniciales():
    try:
        if Tipologia.query.first():
            print("✅ Las tipologías ya existen, saltando creación...")
            return True


        print("📋 Creando tipologías iniciales...")
        tipologias_data = [
            {'nombre': 'Por definir', 'nombrecorto': 'Por definir'},
            {'nombre': 'Estudios Básicos - PreInv', 'nombrecorto': 'EB-PreInv'},
            {'nombre': 'Programa de Inversión - PreInv', 'nombrecorto': 'Prog_Inv-PreInv'},
            {'nombre': 'Proyecto de Inversión - PreInv', 'nombrecorto': 'Proy_Inv-PreInv'},
            {'nombre': 'Estudios Básicos - Inv', 'nombrecorto': 'EB-Inv'},
            {'nombre': 'Programa de Inversión - Inv', 'nombrecorto': 'Prog_Inv-Inv'},
            {'nombre': 'Proyecto de Inversión - Inv', 'nombrecorto': 'Proy_Inv-Inv'},
            {'nombre': 'Proyecto de Inversión - Op', 'nombrecorto': 'Proy_Inv-Op'}
        ]
        for tipologia_data in tipologias_data:
            tipologia = Tipologia(**tipologia_data)
            db.session.add(tipologia)

        db.session.commit()
        print("✅ Tipologías iniciales creadas exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando tipologías iniciales: {e}")
        return False

def crear_financiamientos_iniciales():
    try:
        if Financiamiento.query.first():
            print("✅ Los financiamientos ya existen, saltando creación...")
            return True

        print("📋 Creando financiamientos iniciales...")
        financiamientos_data = [
            {'nombre': 'Por Definir', 'descripcion': 'Aún no se define el financiamiento'},
            {'nombre': 'Gobierno Regional', 'descripcion': 'Gobierno regional financia el proyecto'},
            {'nombre': 'MINSAL', 'descripcion': 'Ministerio de Salud financia el proyecto'},
            {'nombre': 'DEPSA', 'descripcion': 'Departamento de Salud financia el proyecto'},
            {'nombre': 'SUBDERE', 'descripcion': 'Subsecretaría de Desarrollo Regional financia el proyecto'},
            {'nombre': 'MUNICIPAL', 'descripcion': 'Municipalidad financia el proyecto'},
        ]
        
        for financiamiento_data in financiamientos_data:
            financiamiento = Financiamiento(**financiamiento_data)
            db.session.add(financiamiento)

        db.session.commit()
        print("✅ Financiamientos iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando financiamientos iniciales: {e}")
        return False

def crear_tipoproyectos_iniciales():
    try:
        if TipoProyecto.query.first():
            print("✅ Los tipos de proyecto ya existen, saltando creación...")
            return True

        print("📋 Creando tipos de proyecto iniciales...")
        tipoproyectos_data = [
            {'nombre': 'Por Definir', 'nombrecorto': 'Por Definir', 'descripcion': 'Fondos por definir'},
            {'nombre': 'PMI', 'nombrecorto': 'PMI', 'descripcion': 'Fondo para Proyectos de Mejoramiento Integral'},
            {'nombre': 'AGL', 'nombrecorto': 'AGL', 'descripcion': 'Fondo de Ampliación y Generación de Lugares'},
            {'nombre': 'FNDR - Circular 33', 'nombrecorto': 'FNDR-C33', 'descripcion': 'Fondo Nacional de Desarrollo Regional - Circular 33'},
            {'nombre': 'FNDR - Circular 31', 'nombrecorto': 'FNDR-C31', 'descripcion': 'Fondo Nacional de Desarrollo Regional - Circular 31'},
        ]
        
        for tipoproyecto_data in tipoproyectos_data:
            tipoproyecto = TipoProyecto(**tipoproyecto_data)
            db.session.add(tipoproyecto)

        db.session.commit()
        print("✅ Tipos de proyecto iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando tipos de proyecto iniciales: {e}")
        return False

def crear_especialidades_iniciales():
    try:
        if Especialidad.query.first():
            print("✅ Las especialidades ya existen, saltando creación...")
            return True

        print("📋 Creando especialidades iniciales...")
        especialidades_data = [
            {'nombre': 'Formulador'},
            {'nombre': 'Arquitecto'},
            {'nombre': 'Ing. Electrico'},
            {'nombre': 'Ing. Civil'},
            {'nombre': 'Ing. Constructor'},
        ]
        
        for especialidad_data in especialidades_data:
            especialidad = Especialidad(**especialidad_data)
            db.session.add(especialidad)

        db.session.commit()
        print("✅ Especialidades iniciales creadas exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando especialidades iniciales: {e}")
        return False

def crear_equipos_iniciales():
    try:
        if Equipo.query.first():
            print("✅ Los equipos ya existen, saltando creación...")
            return True

        print("📋 Creando equipos iniciales...")
        equipos_data = [
            {'nombre': 'Equipo 1'},
            {'nombre': 'Equipo 2'},
            {'nombre': 'Equipo 3'},
        ]
        
        for equipo_data in equipos_data:
            equipo = Equipo(**equipo_data)
            db.session.add(equipo)

        db.session.commit()
        print("✅ Equipos iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando equipos iniciales: {e}")
        return False

def crear_trabajadores_iniciales():
    try:
        print("📋 Verificando trabajadores iniciales...")
        
        # Obtener sectores por nombre para usar sus IDs reales
        sector_municipal = Sector.query.filter_by(nombre='MUNICIPAL').first()
        sector_salud = Sector.query.filter_by(nombre='SALUD').first()
        sector_educacion = Sector.query.filter_by(nombre='EDUCACION').first()
        sector_otro = Sector.query.filter_by(nombre='OTRO').first()
        
        if not all([sector_municipal, sector_salud, sector_educacion, sector_otro]):
            print("❌ No se encontraron todos los sectores necesarios")
            return False
        
        # Lista de todos los usuarios que deben existir
        trabajadores_data = [
            # Usuario principal - SUPERADMIN
            {
                'nombre': 'Admin Sistema',
                'email': 'admin@sistema.local',
                'profesion': 'Administrador Sistema',
                'nombrecorto': 'admin',
                'password': 'Maho#2024',
                'rut': '11111111-1',  # RUT temporal para admin
                'sector_id': sector_municipal.id,  # MUNICIPAL
                'rol': 'SUPERADMIN'
            },
            # Usuarios de ejemplo para cada rol
            {
                'nombre': 'Administrador L1',
                'email': 'administrador@sistema.local',
                'profesion': 'Administrador',
                'nombrecorto': 'admingen',
                'password': 'Admin#2024',
                'rut': '22222222-2',  # RUT temporal
                'sector_id': sector_municipal.id,  # MUNICIPAL
                'rol': 'ADMIN'
            },
            {
                'nombre': 'Control de Proyectos',
                'email': 'control@sistema.local',
                'profesion': 'Jefe de Control',
                'nombrecorto': 'control',
                'password': 'Control#2024',
                'rut': '33333333-3',  # RUT temporal
                'sector_id': sector_municipal.id,  # MUNICIPAL
                'rol': 'CONTROL'
            },
            {
                'nombre': 'Usuario Operativo',
                'email': 'usuario@sistema.local',
                'profesion': 'Especialista',
                'nombrecorto': 'usuario',
                'password': 'Usuario#2024',
                'rut': '44444444-4',  # RUT temporal
                'sector_id': sector_salud.id,  # SALUD
                'rol': 'USUARIO'
            },
            {
                'nombre': 'Solicitante Externo',
                'email': 'solicitante@sistema.local',
                'profesion': 'Solicitante',
                'nombrecorto': 'solicit',
                'password': 'Solicit#2024',
                'rut': '55555555-5',  # RUT temporal
                'sector_id': sector_educacion.id,  # EDUCACION
                'rol': 'ADMIN'
            },
            {
                'nombre': 'Lector del Sistema',
                'email': 'lector@sistema.local',
                'profesion': 'Consultor',
                'nombrecorto': 'lector',
                'password': 'Lector#2024',
                'rut': '66666666-6',  # RUT temporal
                'sector_id': sector_otro.id,  # OTRO
                'rol': 'LECTOR'
            }
        ]
        
        usuarios_creados = 0
        for trabajador_data in trabajadores_data:
            # Verificar si el usuario ya existe
            existing_user = Trabajador.query.filter_by(email=trabajador_data['email']).first()
            if not existing_user:
                # Separar los datos del rol (hacer una copia para no modificar el original)
                datos_trabajador = trabajador_data.copy()
                rol_name = datos_trabajador.pop('rol')
                trabajador = Trabajador(**datos_trabajador)
                
                # Asignar rol usando el nuevo método
                if not trabajador.set_custom_role_by_name(rol_name):
                    print(f"⚠️ No se pudo asignar el rol '{rol_name}' al usuario {trabajador_data['email']}")
                    continue
                
                db.session.add(trabajador)
                usuarios_creados += 1
                print(f"➕ Creando usuario: {trabajador_data['email']} con rol {rol_name}")
            else:
                print(f"✅ Usuario ya existe: {trabajador_data['email']}")

        if usuarios_creados > 0:
            db.session.commit()
            print(f"✅ {usuarios_creados} trabajadores nuevos creados exitosamente")
        else:
            print("✅ Todos los trabajadores ya existían")
        
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando trabajadores iniciales: {e}")
        return False

def crear_sectores_iniciales():
    try:
        if Sector.query.first():
            print("✅ Los sectores ya existen, saltando creación...")
            return True

        print("📋 Creando sectores iniciales...")
        sectores_data = [
            {'nombre': 'MUNICIPAL'},
            {'nombre': 'SALUD'},
            {'nombre': 'CEMENTERIO'},
            {'nombre': 'EDUCACION'},
            {'nombre': 'OTRO'},
        ]
        
        for sector_data in sectores_data:
            sector = Sector(**sector_data)
            db.session.add(sector)

        db.session.commit()
        print("✅ Sectores iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando sectores iniciales: {e}")
        return False

def crear_tiposrecintos_iniciales():
    try:
        if TipoRecinto.query.first():
            print("✅ Los tipos de recinto ya existen, saltando creación...")
            return True

        print("📋 Creando tipos de recinto iniciales...")
        
        # Obtener sectores por nombre para usar sus IDs reales
        sector_municipal = Sector.query.filter_by(nombre='MUNICIPAL').first()
        sector_salud = Sector.query.filter_by(nombre='SALUD').first()
        
        if not all([sector_municipal, sector_salud]):
            print("❌ No se encontraron todos los sectores necesarios")
            return False
        
        tiposrecintos_data = [
            {'nombre': 'CESFAM', 'descripcion': 'Centro de Salud Familiar', 'id_sector': sector_salud.id},
            {'nombre': 'CECOSF', 'descripcion': 'Centro Comunitario de Salud Familiar', 'id_sector': sector_salud.id},
            {'nombre': 'SAPU', 'descripcion': 'Servicio de Atención Primaria de Urgencia', 'id_sector': sector_salud.id},
            {'nombre': 'SAR', 'descripcion': 'Servicio de Alta Resolución', 'id_sector': sector_salud.id},
            {'nombre': 'ED. CONSISTORIAL', 'descripcion': 'Edificio Consistorial', 'id_sector': sector_municipal.id},
        ]
        
        for tiporecinto_data in tiposrecintos_data:
            tiporecinto = TipoRecinto(**tiporecinto_data)
            db.session.add(tiporecinto)

        db.session.commit()
        print("✅ Tipos de recinto iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando tipos de recinto iniciales: {e}")
        return False

def crear_recintos_iniciales():
    try:
        if Recinto.query.first():
            print("✅ Los recintos ya existen, saltando creación...")
            return True

        print("📋 Creando recintos iniciales...")
        
        # Obtener tipos de recinto por nombre para usar sus IDs reales
        tipo_cesfam = TipoRecinto.query.filter_by(nombre='CESFAM').first()
        tipo_cecosf = TipoRecinto.query.filter_by(nombre='CECOSF').first()
        tipo_sapu = TipoRecinto.query.filter_by(nombre='SAPU').first()
        tipo_consistorial = TipoRecinto.query.filter_by(nombre='ED. CONSISTORIAL').first()
        
        if not all([tipo_cesfam, tipo_cecosf, tipo_sapu, tipo_consistorial]):
            print("❌ No se encontraron todos los tipos de recinto necesarios")
            return False
        
        recintos_data = [
            {'nombre': 'CESFAM La Tortuga', 'descripcion': 'Centro de Salud Familiar La Tortuga', 'id_tiporecinto': tipo_cesfam.id},
            {'nombre': 'CECOSF El Boro', 'descripcion': 'Centro Comunitario El Boro', 'id_tiporecinto': tipo_cecosf.id},
            {'nombre': 'SAPU Dr. Héctor Reyno', 'descripcion': 'Servicio de Atención Primaria', 'id_tiporecinto': tipo_sapu.id},
            {'nombre': 'Oficinas DEPSA', 'descripcion': 'Oficinas del Departamento de Salud', 'id_tiporecinto': tipo_consistorial.id},
        ]
        
        for recinto_data in recintos_data:
            recinto = Recinto(**recinto_data)
            db.session.add(recinto)

        db.session.commit()
        print("✅ Recintos iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando recintos iniciales: {e}")
        return False


def crear_requerimientos_iniciales():
    try:
        # DESHABILITADO: No crear requerimientos de prueba automáticamente
        print("⚠️ Creación de requerimientos de prueba DESHABILITADA para producción")
        return True
        
        # CÓDIGO ORIGINAL COMENTADO ABAJO
        """
        if Requerimiento.query.first():
            print("✅ Los requerimientos ya existen, saltando creación...")
            return True

        print("📋 Creando requerimientos iniciales...")
        
        # Obtener referencias por nombre para usar sus IDs reales
        sector_municipal = Sector.query.filter_by(nombre='MUNICIPAL').first()
        sector_salud = Sector.query.filter_by(nombre='SALUD').first()
        estado_solicitud = Estado.query.filter_by(nombre='En Solicitud').first()
        estado_aceptada = Estado.query.filter_by(nombre='Solicitud Aceptada').first()
        prioridad_1 = Prioridad.query.filter(Prioridad.cuadrante == 1).first()
        prioridad_2 = Prioridad.query.filter(Prioridad.cuadrante == 2).first()
        tipo_cesfam = TipoRecinto.query.filter_by(nombre='CESFAM').first()
        tipo_cecosf = TipoRecinto.query.filter_by(nombre='CECOSF').first()
        recinto_tortuga = Recinto.query.filter_by(nombre='CESFAM La Tortuga').first()
        recinto_boro = Recinto.query.filter_by(nombre='CECOSF El Boro').first()
        
        # Obtener referencias opcionales
        tipologia_preinv = Tipologia.query.filter_by(nombre='Estudios Básicos - PreInv').first()
        financiamiento_gore = Financiamiento.query.filter_by(nombre='Gobierno Regional').first()
        tipoproyecto_pmi = TipoProyecto.query.filter_by(nombre='PMI').first()
        
        if not all([sector_municipal, sector_salud, estado_solicitud, estado_aceptada, 
                   prioridad_1, prioridad_2, tipo_cesfam, tipo_cecosf, 
                   recinto_tortuga, recinto_boro]):
            print("❌ No se encontraron todas las referencias necesarias para los requerimientos")
            return False
        
        requerimientos_data = [
            {
                'nombre': 'PROYECTO PRUEBA 1',
                'fecha': datetime(2025, 1, 15),
                'descripcion': 'Proyecto de prueba para el sistema',
                'observacion': 'Solo prueba 1',
                'id_sector': sector_municipal.id,
                'id_tiporecinto': tipo_cesfam.id,
                'id_recinto': recinto_tortuga.id,
                'id_estado': estado_solicitud.id,
                'fecha_aceptacion': None,
                'id_tipologia': None,
                'id_financiamiento': None,
                'id_tipoproyecto': None,
                'id_prioridad': prioridad_1.id
            },
            {
                'nombre': 'PROYECTO PRUEBA 2',
                'fecha': datetime(2025, 1, 16),
                'descripcion': 'Segundo proyecto de prueba',
                'observacion': 'Solo prueba 2',
                'id_sector': sector_salud.id,
                'id_tiporecinto': tipo_cecosf.id,
                'id_recinto': recinto_boro.id,
                'id_estado': estado_solicitud.id,
                'fecha_aceptacion': None,
                'id_tipologia': None,
                'id_financiamiento': None,
                'id_tipoproyecto': None,
                'id_prioridad': prioridad_2.id
            },
            {
                'nombre': 'PROYECTO EN DESARROLLO',
                'fecha': datetime(2025, 1, 14),
                'descripcion': 'Proyecto que ya fue aceptado y está en desarrollo',
                'observacion': 'Aceptado para desarrollo',
                'id_sector': sector_municipal.id,
                'id_tiporecinto': tipo_cesfam.id,
                'id_recinto': recinto_tortuga.id,
                'id_estado': estado_aceptada.id,
                'fecha_aceptacion': datetime(2025, 1, 15),
                'id_tipologia': tipologia_preinv.id if tipologia_preinv else None,
                'id_financiamiento': financiamiento_gore.id if financiamiento_gore else None,
                'id_tipoproyecto': tipoproyecto_pmi.id if tipoproyecto_pmi else None,
                'id_prioridad': prioridad_1.id
            }
        ]

        for req_data in requerimientos_data:
            requerimiento = Requerimiento(**req_data)
            db.session.add(requerimiento)

        db.session.commit()
        print("✅ Requerimientos iniciales creados exitosamente")
        """  # FIN CÓDIGO COMENTADO
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando requerimientos iniciales: {e}")
        return False


def crear_categorias_iniciales():
    """Crear categorías iniciales para el sistema de permisos"""
    try:
        if Category.query.first():
            print("✅ Las categorías ya existen, saltando creación...")
            return True

        print("📋 Creando categorías iniciales...")
        categorias_data = [
            {
                'name': 'Sistema', 
                'description': 'Páginas del sistema principal y navegación',
                'color': 'primary',
                'display_order': 1,
                'icon': 'fas fa-home',
                'is_visible': True
            },
            {
                'name': 'Requerimiento', 
                'description': 'Gestión de requerimientos y proyectos',
                'color': 'success',
                'display_order': 2,
                'icon': 'fas fa-clipboard-list',
                'is_visible': True
            },
            {
                'name': 'Usuarios', 
                'description': 'Gestión de usuarios y trabajadores',
                'color': 'info',
                'display_order': 3,
                'icon': 'fas fa-users',
                'is_visible': True
            },
            {
                'name': 'Configuración', 
                'description': 'Configuración de catálogos y parámetros del sistema',
                'color': 'warning',
                'display_order': 4,
                'icon': 'fas fa-cogs',
                'is_visible': True
            },
            {
                'name': 'Administración', 
                'description': 'Administración avanzada y permisos del sistema',
                'color': 'danger',
                'display_order': 5,
                'icon': 'fas fa-shield-alt',
                'is_visible': True
            }
        ]
        
        for cat_data in categorias_data:
            categoria = Category(**cat_data)
            db.session.add(categoria)

        db.session.commit()
        print("✅ Categorías iniciales creadas exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando categorías iniciales: {e}")
        return False


def crear_paginas_iniciales():
    """Crear páginas iniciales para el sistema de permisos"""
    try:
        if Page.query.first():
            print("✅ Las páginas ya existen, saltando creación...")
            return True

        print("📋 Creando páginas iniciales...")
        
        # Obtener categorías
        cat_sistema = Category.query.filter_by(name='Sistema').first()
        cat_requerimiento = Category.query.filter_by(name='Requerimiento').first()
        cat_usuarios = Category.query.filter_by(name='Usuarios').first()
        cat_config = Category.query.filter_by(name='Configuración').first()
        cat_admin = Category.query.filter_by(name='Administración').first()
        
        paginas_data = [
            # === PÁGINAS DEL SISTEMA ===
            {
                'route': '/', 
                'name': 'Inicio', 
                'description': 'Página principal del sistema', 
                'category_id': cat_sistema.id,
                'display_order': 1,
                'icon': 'fas fa-home',
                'is_visible': True
            },
            {
                'route': '/dashboard', 
                'name': 'Dashboard', 
                'description': 'Panel de control y estadísticas', 
                'category_id': cat_sistema.id,
                'display_order': 2,
                'icon': 'fas fa-tachometer-alt',
                'is_visible': True
            },
            {
                'route': '/health', 
                'name': 'Estado del Sistema', 
                'description': 'Estado y salud del sistema', 
                'category_id': cat_sistema.id,
                'display_order': 3,
                'icon': 'fas fa-heartbeat',
                'is_visible': False
            },

            # === GESTIÓN DE PROYECTOS ===
            {
                'route': '/projects', 
                'name': 'Lista de Proyectos', 
                'description': 'Ver todos los proyectos', 
                'category_id': cat_requerimiento.id,
                'display_order': 1,
                'icon': 'fas fa-list',
                'is_visible': True
            },
            {
                'route': '/projects/create', 
                'name': 'Crear Proyecto', 
                'description': 'Crear nuevo proyecto', 
                'category_id': cat_requerimiento.id,
                'display_order': 2,
                'icon': 'fas fa-plus',
                'is_visible': True
            },
            {
                'route': '/actividades', 
                'name': 'Actividades', 
                'description': 'Gestión de actividades de proyecto', 
                'category_id': cat_requerimiento.id,
                'display_order': 3,
                'icon': 'fas fa-tasks',
                'is_visible': True
            },
            {
                'route': '/gantt', 
                'name': 'Diagrama de Gantt', 
                'description': 'Visualización de cronogramas', 
                'category_id': cat_requerimiento.id,
                'display_order': 4,
                'icon': 'fas fa-chart-line',
                'is_visible': True
            },

            # === CONFIGURACIÓN DE CATÁLOGOS ===
            {
                'route': '/estados', 
                'name': 'Estados', 
                'description': 'Gestión de estados de proyecto', 
                'category_id': cat_config.id,
                'display_order': 1,
                'icon': 'fas fa-flag',
                'is_visible': True
            },
            {
                'route': '/prioridades', 
                'name': 'Prioridades', 
                'description': 'Gestión de prioridades', 
                'category_id': cat_config.id,
                'display_order': 2,
                'icon': 'fas fa-exclamation-triangle',
                'is_visible': True
            },
            {
                'route': '/fases', 
                'name': 'Fases', 
                'description': 'Gestión de fases de proyecto', 
                'category_id': cat_config.id,
                'display_order': 3,
                'icon': 'fas fa-layer-group',
                'is_visible': True
            },
            {
                'route': '/tipologias', 
                'name': 'Tipologías', 
                'description': 'Gestión de tipologías', 
                'category_id': cat_config.id,
                'display_order': 4,
                'icon': 'fas fa-tags',
                'is_visible': True
            },
            {
                'route': '/financiamientos', 
                'name': 'Financiamientos', 
                'description': 'Gestión de tipos de financiamiento', 
                'category_id': cat_config.id,
                'display_order': 5,
                'icon': 'fas fa-money-bill-wave',
                'is_visible': True
            },
            {
                'route': '/tipoproyectos', 
                'name': 'Tipos de Proyecto', 
                'description': 'Gestión de tipos de proyecto', 
                'category_id': cat_config.id,
                'display_order': 6,
                'icon': 'fas fa-project-diagram',
                'is_visible': True
            },
            {
                'route': '/sectores', 
                'name': 'Sectores', 
                'description': 'Gestión de sectores', 
                'category_id': cat_config.id,
                'display_order': 7,
                'icon': 'fas fa-building',
                'is_visible': True
            },
            {
                'route': '/tiposrecintos', 
                'name': 'Tipos de Recinto', 
                'description': 'Gestión de tipos de recinto', 
                'category_id': cat_config.id,
                'display_order': 8,
                'icon': 'fas fa-home',
                'is_visible': True
            },
            {
                'route': '/recintos', 
                'name': 'Recintos', 
                'description': 'Gestión de recintos', 
                'category_id': cat_config.id,
                'display_order': 9,
                'icon': 'fas fa-map-marker-alt',
                'is_visible': True
            },
            {
                'route': '/equipos', 
                'name': 'Equipos', 
                'description': 'Gestión de equipos de trabajo', 
                'category_id': cat_config.id,
                'display_order': 10,
                'icon': 'fas fa-users-cog',
                'is_visible': True
            },
            {
                'route': '/especialidades', 
                'name': 'Especialidades', 
                'description': 'Gestión de especialidades', 
                'category_id': cat_config.id,
                'display_order': 11,
                'icon': 'fas fa-graduation-cap',
                'is_visible': True
            },
            {
                'route': '/areas', 
                'name': 'Áreas', 
                'description': 'Gestión de áreas organizacionales', 
                'category_id': cat_config.id,
                'display_order': 12,
                'icon': 'fas fa-sitemap',
                'is_visible': True
            },
            {
                'route': '/grupos', 
                'name': 'Grupos', 
                'description': 'Gestión de grupos de trabajo', 
                'category_id': cat_config.id,
                'display_order': 13,
                'icon': 'fas fa-layer-group',
                'is_visible': True
            },

            # === GESTIÓN DE USUARIOS ===
            {
                'route': '/trabajadores', 
                'name': 'Trabajadores', 
                'description': 'Gestión de usuarios del sistema', 
                'category_id': cat_usuarios.id,
                'display_order': 1,
                'icon': 'fas fa-users',
                'is_visible': True
            },
            {
                'route': '/auth/login', 
                'name': 'Iniciar Sesión', 
                'description': 'Página de inicio de sesión', 
                'category_id': cat_usuarios.id,
                'display_order': 2,
                'icon': 'fas fa-sign-in-alt',
                'is_visible': False
            },
            {
                'route': '/auth/logout', 
                'name': 'Cerrar Sesión', 
                'description': 'Cerrar sesión del usuario', 
                'category_id': cat_usuarios.id,
                'display_order': 3,
                'icon': 'fas fa-sign-out-alt',
                'is_visible': False
            },
            {
                'route': '/profile', 
                'name': 'Mi Perfil', 
                'description': 'Ver información personal del perfil', 
                'category_id': cat_usuarios.id,
                'display_order': 4,
                'icon': 'fas fa-user-circle',
                'is_visible': True
            },
            {
                'route': '/profile/edit', 
                'name': 'Editar Mi Perfil', 
                'description': 'Editar información personal del perfil', 
                'category_id': cat_usuarios.id,
                'display_order': 5,
                'icon': 'fas fa-user-edit',
                'is_visible': False
            },
            {
                'route': '/auth/mi-perfil', 
                'name': 'Mi Perfil (Trabajadores)', 
                'description': 'Página completa para editar perfil de trabajadores', 
                'category_id': cat_usuarios.id,
                'display_order': 6,
                'icon': 'fas fa-id-card',
                'is_visible': True
            },

            # === GESTIÓN DE REQUERIMIENTOS ===
            {
                'route': '/requerimientos', 
                'name': 'Requerimientos', 
                'description': 'Gestión de requerimientos', 
                'category_id': cat_requerimiento.id,
                'display_order': 1,
                'icon': 'fas fa-clipboard-list',
                'is_visible': True
            },
            {
                'route': '/requerimientos_aceptar', 
                'name': 'Requerimientos Aceptar', 
                'description': 'Aceptar requerimientos', 
                'category_id': cat_requerimiento.id,
                'display_order': 2,
                'icon': 'fas fa-check-circle',
                'is_visible': True
            },
            {
                'route': '/requerimientos_completar', 
                'name': 'Requerimientos Completar', 
                'description': 'Completar requerimientos', 
                'category_id': cat_requerimiento.id,
                'display_order': 3,
                'icon': 'fas fa-clipboard-check',
                'is_visible': True
            },
            {
                'route': '/proyectos_aceptar', 
                'name': 'Proyecto Aceptar', 
                'description': 'Aceptar proyectos', 
                'category_id': cat_requerimiento.id,
                'display_order': 4,
                'icon': 'fas fa-thumbs-up',
                'is_visible': True
            },
            {
                'route': '/proyectos_completar', 
                'name': 'Proyectos Completar OLD', 
                'description': 'Completar proyectos (versión anterior)', 
                'category_id': cat_requerimiento.id,
                'display_order': 5,
                'icon': 'fas fa-archive',
                'is_visible': True
            },
            {
                'route': '/proyecto-llenar', 
                'name': 'Proyectos Completar', 
                'description': 'Completar información de proyectos', 
                'category_id': cat_requerimiento.id,
                'display_order': 6,
                'icon': 'fas fa-edit',
                'is_visible': True
            },
            {
                'route': '/control_actividades', 
                'name': 'Controles', 
                'description': 'Control de actividades', 
                'category_id': cat_requerimiento.id,
                'display_order': 7,
                'icon': 'fas fa-clipboard-list',
                'is_visible': True
            },
            {
                'route': '/avance-actividades', 
                'name': 'Avance Actividades', 
                'description': 'Seguimiento de avance de actividades', 
                'category_id': cat_requerimiento.id,
                'display_order': 8,
                'icon': 'fas fa-chart-line',
                'is_visible': True
            },
            {
                'route': '/avance-actividades-all', 
                'name': 'Avance Actividades - Todos', 
                'description': 'Seguimiento de avance de actividades (todos los proyectos)', 
                'category_id': cat_requerimiento.id,
                'display_order': 9,
                'icon': 'fas fa-chart-area',
                'is_visible': True
            },
            {
                'route': '/historial-avances', 
                'name': 'Historial Avances', 
                'description': 'Historial de avances registrados', 
                'category_id': cat_requerimiento.id,
                'display_order': 10,
                'icon': 'fas fa-history',
                'is_visible': True
            },

            # === ADMINISTRACIÓN AVANZADA ===
            {
                'route': '/permissions/', 
                'name': 'Gestión de Permisos', 
                'description': 'Administrar permisos de usuarios', 
                'category_id': cat_admin.id,
                'display_order': 1,
                'icon': 'fas fa-shield-alt',
                'is_visible': True
            },
            {
                'route': '/admin/config', 
                'name': 'Configuración Sistema', 
                'description': 'Configurar parámetros del sistema', 
                'category_id': cat_admin.id,
                'display_order': 2,
                'icon': 'fas fa-cogs',
                'is_visible': True
            },
            {
                'route': '/admin/logs', 
                'name': 'Logs del Sistema', 
                'description': 'Ver logs y auditoría', 
                'category_id': cat_admin.id,
                'display_order': 3,
                'icon': 'fas fa-file-alt',
                'is_visible': True
            },
            {
                'route': '/admin/backup', 
                'name': 'Respaldos', 
                'description': 'Gestión de respaldos', 
                'category_id': cat_admin.id,
                'display_order': 4,
                'icon': 'fas fa-database',
                'is_visible': True
            },
            {
                'route': '/admin/maintenance', 
                'name': 'Mantenimiento', 
                'description': 'Tareas de mantenimiento del sistema', 
                'category_id': cat_admin.id,
                'display_order': 5,
                'icon': 'fas fa-tools',
                'is_visible': True
            },
            {
                'route': '/gestion-administradores', 
                'name': 'Gestión de Administradores', 
                'description': 'Asignar recintos específicos a cada administrador', 
                'category_id': cat_admin.id,
                'display_order': 6,
                'icon': 'fas fa-users-cog',
                'is_visible': True
            },
            {
                'route': '/gestion-usuarios', 
                'name': 'Gestión de Usuarios por Recinto', 
                'description': 'Asignar recintos adicionales a trabajadores de mis recintos', 
                'category_id': cat_admin.id,
                'display_order': 7,
                'icon': 'fas fa-users',
                'is_visible': True
            },
            {
                'route': '/admin/backup', 
                'name': 'Gestión de Backups', 
                'description': 'Crear y restaurar copias de seguridad de la base de datos', 
                'category_id': cat_admin.id,
                'display_order': 8,
                'icon': 'fas fa-database',
                'is_visible': True
            }
        ]
        
        for pag_data in paginas_data:
            pagina = Page(**pag_data)
            db.session.add(pagina)

        db.session.commit()
        print("✅ Páginas iniciales creadas exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando páginas iniciales: {e}")
        return False


def crear_permisos_iniciales():
    """Crear permisos iniciales para el sistema"""
    try:
        if PagePermission.query.first():
            print("✅ Los permisos ya existen, saltando creación...")
            return True

        print("📋 Creando permisos iniciales...")
        
        # Obtener todas las páginas
        todas_las_paginas = Page.query.all()
        
        # Definir permisos solo para SUPERADMIN (rol del sistema)
        permisos_config = {
            UserRole.SUPERADMIN: {
                'description': 'Acceso total al sistema - Único superusuario',
                'pages': [p.name for p in todas_las_paginas]  # Acceso a todo
            }
        }
        
        permisos_data = []
        
        # Crear permisos basados en la configuración
        for role, config in permisos_config.items():
            print(f"  📄 Configurando permisos para {role.value}: {config['description']}")
            
            for page_name in config['pages']:
                page = next((p for p in todas_las_paginas if p.name == page_name), None)
                if page:
                    permisos_data.append({
                        'page_id': page.id,
                        'system_role': role,
                        'role_name': role.value
                    })
                else:
                    print(f"    ⚠️  Página '{page_name}' no encontrada para rol {role.value}")
        
        # Insertar permisos en lotes para mejor performance
        for perm_data in permisos_data:
            permiso = PagePermission(**perm_data)
            db.session.add(permiso)

        db.session.commit()
        
        # Mostrar resumen
        total_permisos = len(permisos_data)
        print(f"✅ {total_permisos} permisos iniciales creados exitosamente")
        
        # Mostrar estadísticas por rol
        for role in UserRole:
            count = len([p for p in permisos_data if p['system_role'] == role])
            print(f"  📊 {role.value}: {count} permisos")
        
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando permisos iniciales: {e}")
        return False

def crear_roles_personalizados_iniciales():
    """Crear roles personalizados iniciales"""
    try:
        if CustomRole.query.first():
            print("✅ Los roles personalizados ya existen, saltando creación...")
            return True

        print("📋 Creando roles personalizados iniciales...")
        
        roles_data = [
            {
                'name': 'ADMIN',
                'description': 'Administrador con permisos amplios pero limitados',
                'active': True
            },
            {
                'name': 'CONTROL',
                'description': 'Control de Proyectos con permisos básicos de control',
                'active': True
            },
            {
                'name': 'USUARIO',
                'description': 'Usuario Operativo con acceso a funcionalidades básicas',
                'active': True
            },
            {
                'name': 'LECTOR',
                'description': 'Usuario con permisos mínimos de solo lectura',
                'active': True
            }
        ]
        
        for role_data in roles_data:
            role = CustomRole(**role_data)
            db.session.add(role)

        db.session.commit()
        print("✅ Roles personalizados iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando roles personalizados iniciales: {e}")
        return False

def crear_configuracion_menu_inicial():
    """Crear configuración inicial del menú"""
    try:
        if MenuConfiguration.query.first():
            print("✅ La configuración del menú ya existe, saltando creación...")
            return True

        print("📋 Creando configuración inicial del menú...")
        
        config = MenuConfiguration(
            id=1,
            sidebar_collapsed=False,
            theme='light',
            menu_style='vertical',
            show_icons=True,
            show_badges=True,
            custom_css=None
        )
        
        db.session.add(config)
        db.session.commit()
        
        print("✅ Configuración inicial del menú creada exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando configuración inicial del menú: {e}")
        return False

def crear_permisos_roles_personalizados():
    """Crear permisos para roles personalizados"""
    try:
        # Verificar si ya existen permisos para roles personalizados
        existing_custom_perms = PagePermission.query.filter(PagePermission.custom_role_id.isnot(None)).first()
        if existing_custom_perms:
            print("✅ Los permisos para roles personalizados ya existen, saltando creación...")
            return True

        print("📋 Creando permisos para roles personalizados...")
        
        # Definir permisos específicos por rol personalizado
        roles_permissions = {
            'ADMIN': [
                # Acceso completo excepto configuración de sistema
                'Inicio', 'Dashboard', 'Trabajadores',
                'Gestión de Administradores', 'Gestión de Usuarios por Recinto',
                'Requerimientos', 'Requerimientos Aceptar', 'Requerimientos Completar',
                'Proyecto Aceptar', 'Proyectos Completar',
                'Controles', 'Avance Actividades', 'Historial Avances',
                'Estados', 'Prioridades', 'Fases', 'Tipologías', 'Financiamientos',
                'Tipos de Proyecto', 'Sectores', 'Tipos de Recinto', 'Recintos',
                'Equipos', 'Especialidades', 'Áreas', 'Grupos',
                'Mi Perfil', 'Editar Mi Perfil', 'Mi Perfil (Trabajadores)',
                'Gestión de Backups'
            ],
            'CONTROL': [
                # Permisos básicos de control - otros se asignan desde gestión de permisos
                'Inicio', 'Dashboard', 'Controles',
                'Mi Perfil', 'Editar Mi Perfil', 'Mi Perfil (Trabajadores)'
            ],
            'USUARIO': [
                # Acceso operativo limitado
                'Inicio', 'Dashboard',
                'Requerimientos', 'Lista de Proyectos',
                'Actividades', 'Diagrama de Gantt', 'Avance Actividades',
                'Estados', 'Prioridades', 'Sectores', 'Tipos de Recinto', 'Recintos',
                'Equipos', 'Especialidades',
                'Mi Perfil', 'Editar Mi Perfil', 'Mi Perfil (Trabajadores)'
            ],
            'LECTOR': [
                # Solo lectura de información básica
                'Inicio', 'Dashboard',
                'Lista de Proyectos', 'Actividades', 'Diagrama de Gantt',
                'Estados', 'Prioridades', 'Sectores', 'Tipos de Recinto', 'Recintos',
                'Equipos', 'Especialidades',
                'Mi Perfil', 'Editar Mi Perfil', 'Mi Perfil (Trabajadores)'
            ]
        }
        
        # Crear permisos para cada rol personalizado
        for role_name, page_names in roles_permissions.items():
            role = CustomRole.query.filter_by(name=role_name).first()
            if role:
                for page_name in page_names:
                    page = Page.query.filter_by(name=page_name).first()
                    if page:
                        # Verificar si el permiso ya existe
                        existing_perm = PagePermission.query.filter_by(
                            page_id=page.id,
                            custom_role_id=role.id
                        ).first()
                        
                        if not existing_perm:
                            permission = PagePermission(
                                page_id=page.id,
                                custom_role_id=role.id,
                                role_name=role_name
                            )
                            db.session.add(permission)
                            print(f"  ✅ Permiso creado: {role_name} -> {page_name}")
        
        db.session.commit()
        print("✅ Permisos para roles personalizados creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando permisos para roles personalizados: {e}")
        return False

def crear_datos_iniciales():
    """Función principal que ejecuta todas las creaciones de datos iniciales"""
    print("🚀 Iniciando creación de datos iniciales...")
    
    # Lista de funciones de creación en orden de dependencia
    funciones_creacion = [
        ("Estados", crear_estados_iniciales),
        ("Prioridades", crear_prioridades_iniciales),
        ("Tipos de Proyecto", crear_tipoproyectos_iniciales),
        ("Especialidades", crear_especialidades_iniciales),
        ("Equipos", crear_equipos_iniciales),
        ("Áreas", crear_areas_iniciales),
        # === CREAR ROLES PERSONALIZADOS ANTES QUE TRABAJADORES ===
        ("Roles Personalizados", crear_roles_personalizados_iniciales),
        ("Trabajadores", crear_trabajadores_iniciales),
        ("Sectores", crear_sectores_iniciales),
        ("Tipos de Recinto", crear_tiposrecintos_iniciales),
        ("Recintos", crear_recintos_iniciales),
    # ("Etapas N1", crear_etapasN1_iniciales),
    # ("Etapas N2", crear_etapasN2_iniciales),
    # ("Etapas N3", crear_etapasN3_iniciales),
    # ("Etapas N4", crear_etapasN4_iniciales),
    # ("Etapas", crear_etapas_iniciales),
        ("Grupos", crear_grupos_iniciales),
        ("Requerimientos", crear_requerimientos_iniciales),
        # === SISTEMA DE PERMISOS ===
        ("Categorías de Permisos", crear_categorias_iniciales),
        ("Páginas de Permisos", crear_paginas_iniciales),
        ("Permisos del Sistema", crear_permisos_iniciales),
        ("Permisos Roles Personalizados", crear_permisos_roles_personalizados),
        ("Configuración del Menú", crear_configuracion_menu_inicial)
    ]
    
    errores = []
    exitos = []
    
    for nombre, funcion in funciones_creacion:
        try:
            print(f"\n📋 Procesando {nombre}...")
            if funcion():
                exitos.append(nombre)
                print(f"✅ {nombre} - Completado")
            else:
                errores.append(nombre)
                print(f"❌ {nombre} - Falló")
        except Exception as e:
            print(f"❌ Error fatal en {nombre}: {e}")
            errores.append(nombre)
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE CREACIÓN DE DATOS INICIALES")
    print("="*60)
    
    if exitos:
        print(f"✅ COMPLETADOS ({len(exitos)}):")
        for item in exitos:
            print(f"   • {item}")
    
    if errores:
        print(f"\n❌ CON ERRORES ({len(errores)}):")
        for item in errores:
            print(f"   • {item}")
        print(f"\n⚠️  Se completó con errores en: {', '.join(errores)}")
        return False
    else:
        print(f"\n🎉 TODOS LOS DATOS INICIALES CREADOS EXITOSAMENTE")
        print(f"📈 Total de elementos procesados: {len(funciones_creacion)}")
        return True

def crear_datos_ejemplo():
    """Crear datos de ejemplo adicionales para desarrollo"""
    print("🌱 Creando datos de ejemplo para desarrollo...")
    
    try:
        # Crear más requerimientos de ejemplo
        requerimientos_ejemplo = [
            {
                'nombre': 'PROYECTO AMPLIACIÓN CESFAM',
                'fecha': datetime(2025, 1, 10),
                'descripcion': 'Ampliación del Centro de Salud Familiar La Tortuga',
                'observacion': 'Proyecto prioritario para mejorar atención',
                'id_sector': 2,
                'id_tiporecinto': 1,
                'id_recinto': 1,
                'id_estado': 2,
                'fecha_aceptacion': datetime(2025, 1, 12),
                'id_tipologia': 3,
                'id_financiamiento': 2,
                'id_tipoproyecto': 2,
                'id_prioridad': 1
            },
            {
                'nombre': 'MEJORAMIENTO INFRAESTRUCTURA CECOSF',
                'fecha': datetime(2025, 1, 8),
                'descripcion': 'Mejoramiento de la infraestructura del CECOSF El Boro',
                'observacion': 'Requiere reparaciones urgentes',
                'id_sector': 2,
                'id_tiporecinto': 2,
                'id_recinto': 2,
                'id_estado': 3,
                'fecha_aceptacion': datetime(2025, 1, 10),
                'id_tipologia': 4,
                'id_financiamiento': 3,
                'id_tipoproyecto': 1,
                'id_prioridad': 2
            }
        ]
        
        for req_data in requerimientos_ejemplo:
            req = Requerimiento(**req_data)
            db.session.add(req)
        
        db.session.commit()
        print("✅ Datos de ejemplo creados exitosamente")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando datos de ejemplo: {e}")
        return False

def crear_areas_iniciales():
    try:
        if Area.query.first():
            print("✅ Las áreas ya existen, saltando creación...")
            return True

        print("📋 Creando áreas iniciales...")
        areas_data = [
            {
                'nombre': 'Administración',
                'descripcion': 'Área de administración general',
                'activo': True
            },
            {
                'nombre': 'SuperAdmin',
                'descripcion': 'Primeras personas administradores de la app',
                'activo': True
            },
            {
                'nombre': 'SECOPLAC',
                'descripcion': 'Personas encargadas de SECOPLAC',
                'activo': True
            },
            {
                'nombre': 'DOM',
                'descripcion': 'Personas encargadas de DOM',
                'activo': True
            },
            {
                'nombre': 'SALUD',
                'descripcion': 'Área de gestión de salud',
                'activo': True
            }
        ]
        
        for area_data in areas_data:
            area = Area(**area_data)
            db.session.add(area)

        db.session.commit()
        print("✅ Áreas iniciales creadas exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando áreas iniciales: {e}")
        return False

def crear_grupos_iniciales():
    try:
        if Grupo.query.first():
            print("✅ Los grupos ya existen, saltando creación...")
            return True

        print("📋 Creando grupos iniciales...")
        grupos_data = [
            {'nombre': 'Grupo 1'},
            {'nombre': 'Grupo 2'},
            {'nombre': 'Grupo 3'},
        ]

        for grupo_data in grupos_data:
            grupo = Grupo(**grupo_data)
            db.session.add(grupo)

        db.session.commit()
        print("✅ Grupos iniciales creados exitosamente")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando grupos iniciales: {e}")
        return False


