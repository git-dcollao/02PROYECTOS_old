from .models import db, TipoRecinto, Recinto, Sector, Trabajador, EtapaN1, EtapaN2, EtapaN3, EtapaN4, Financiamiento, Especialidad, Equipo, Tipologia, Fase, TipoProyecto, Estado, Requerimiento, User

def seed_data():
    """Función para crear datos iniciales en la base de datos"""
    try:
        # Datos iniciales para los sectores
        sector_data = [
            {'nombre': 'MUNICIPAL'},
            {'nombre': 'SALUD'},
            {'nombre': 'CEMENTERIO'},
            {'nombre': 'EDUCACION'},
            {'nombre': 'OTRO'},
        ]
        sectores = [Sector(**data) for data in sector_data]
        db.session.add_all(sectores)
        db.session.commit()

        # Datos iniciales para Tipo de Recintos
        tiposrecintos_data = [
            {'nombre': 'CESFAM', 'descripcion': 'Centro de ...', 'id_sector': 2},
            {'nombre': 'CECOSF', 'descripcion': 'Centro de ...', 'id_sector': 2},
            {'nombre': 'SAPU', 'descripcion': 'Servicio de ...', 'id_sector': 2},
            {'nombre': 'SAR', 'descripcion': 'Servicio de ...', 'id_sector': 2},
            {'nombre': 'ED. CONSISTORIAL', 'descripcion': 'Edificio Consistorial', 'id_sector': 1},
            {'nombre': 'CENTRO DE APOYO', 'descripcion': 'Ejecuciónde  estudio', 'id_sector': 4},
            {'nombre': 'RECINTOS VARIOS', 'descripcion': 'Ejecuciónde  estudio', 'id_sector': 4},
            {'nombre': 'CEMENTERIO', 'descripcion': 'Ejecuciónde  estudio', 'id_sector': 3},
        ]
        tiposrecintos = [TipoRecinto(**data) for data in tiposrecintos_data]
        db.session.add_all(tiposrecintos)
        db.session.commit()
        
        # Datos iniciales para Recintos
        recintos_data = [
            {'nombre': 'La Tortuga', 'descripcion': 'Centro de ...', 'id_tiporecinto': 2},
            {'nombre': 'El Boro', 'descripcion': 'Centro de ...', 'id_tiporecinto': 2},
            {'nombre': 'Dr. Héctor Reyno Gutiérre', 'descripcion': 'Servicio de ...', 'id_tiporecinto': 3},
            {'nombre': 'El Boro', 'descripcion': 'Servicio de ...', 'id_tiporecinto': 3},
            {'nombre': 'CCR', 'descripcion': 'Edificio Consistorial', 'id_tiporecinto': 7},
            {'nombre': 'CESCO', 'descripcion': 'Recintos ...', 'id_tiporecinto': 7},
            {'nombre': 'CAAPS', 'descripcion': 'Recintos ...', 'id_tiporecinto': 7},
            {'nombre': 'Oficinas DEPSA', 'descripcion': 'Recintos ...', 'id_tiporecinto': 5},
            {'nombre': 'Recintos Varios', 'descripcion': 'Recintos varios ...', 'id_tiporecinto': 7},
        ]
        recintos = [Recinto(**data) for data in recintos_data]
        db.session.add_all(recintos)
        db.session.commit()
        
        # Agregar estados base
        estados_data = [
            {'nombre': 'En Solicitud'},
            {'nombre': 'En Desarrollo - Preparación'},
            {'nombre': 'En Desarrollo - Ejecución'},
            {'nombre': 'Finalizado'},
            {'nombre': 'Rechazado'},
            {'nombre': 'Cancelado'}
        ]
        estados = [Estado(**data) for data in estados_data]
        db.session.add_all(estados)
        db.session.commit()

        # Datos iniciales para EtapaN1
        etapas_n1_data = [
            {'nombre': 'Preparación', 'descripcion': 'Etapa de preparación del proyecto'},
            {'nombre': 'Licitación', 'descripcion': 'Etapa de licitación del proyecto'},
            {'nombre': 'Ejecución', 'descripcion': 'Etapa de ejecución del proyecto'},
            {'nombre': 'Gestión Servicios Externos', 'descripcion': 'Etapa de gestión de servicios externos del proyecto'},
        ]
        etapas_n1 = [EtapaN1(**data) for data in etapas_n1_data]
        db.session.add_all(etapas_n1)
        db.session.commit()

        # Datos iniciales para EtapaN2
        etapas_n2_data = [
            {'nombre': 'Formulación', 'descripcion': 'Formulación', 'id_etapaN1': 1},
            {'nombre': 'Proceso Licitación', 'descripcion': 'Licitación', 'id_etapaN1': 2},
            {'nombre': 'Ejecución OOCC', 'descripcion': 'Ejecución ', 'id_etapaN1': 3},
            {'nombre': 'Ejecución Estudio', 'descripcion': 'Ejecuciónde  estudio', 'id_etapaN1': 4},
            {'nombre': 'Supervición Mantención Profecional', 'descripcion': 'Ejecuciónde  estudio', 'id_etapaN1': 4},
        ]
        etapas_n2 = [EtapaN2(**data) for data in etapas_n2_data]
        db.session.add_all(etapas_n2)
        db.session.commit()

        # Datos iniciales para EtapaN3
        etapas_n3_data = [
            # Para EtapaN3 "Formulación" (id=1)
            {'nombre': 'Levantamiento de información', 'descripcion': 'Levantamiento', 'id_etapaN2': 1},
            {'nombre': 'Diagnóstico', 'descripcion': 'Análisis de factibilidad', 'id_etapaN2': 1},
            {'nombre': 'Evaluación Social', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Confección Ficha IDI', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Planimetría', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Arquitectura / Diseño', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Identificación beneficiarios y población afecatada', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Términos de Referencia / Matriz Marcológico', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Ing. Eléctrica', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Ing. Civil', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Presupuesto', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Especificaciones Técnicas', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Ficha resumen e Ingreso a la plataforma', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Topografía y Mecánica de suelos', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Proyecto Arquitectura', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Proyecto Especialidad (Eléctrico, Sanitario, clima)', 'descripcion': 'Definición', 'id_etapaN2': 1},
            {'nombre': 'Certificaciones, Revisores, Permisos Edificación', 'descripcion': 'Definición', 'id_etapaN2': 1},
        
            # Para EtapaN3 "Proceso Licitación" (id=2)
            {'nombre': 'Bases para Contratación', 'descripcion': 'Desarrollo de planos detallados', 'id_etapaN2': 2},
            {'nombre': 'Licitación Pública o trato Directo', 'descripcion': 'Especificaciones técnicas', 'id_etapaN2': 2},
           {'nombre': 'Evaluación Ofertas, Informe adjudicatario y aprobación del CM (sobe 5.000 UTM)', 'descripcion': 'Especificaciones', 'id_etapaN2': 2},
           #{'nombre': 'Evaluación Ofertas, elaboración Informe adjudicatario y aprobación del Concejo Municipal (sobe 5.000 UTM)', 'descripcion': 'Documentación', 'id_etapaN2': 2},
            {'nombre': 'Confección DA de aprobación adjudicación', 'descripcion': 'Definición', 'id_etapaN2': 2},
            {'nombre': 'Presentción BG', 'descripcion': 'Definición', 'id_etapaN2': 2},
            {'nombre': 'Firma de Contrato / Aceptación OC', 'descripcion': 'Definición', 'id_etapaN2': 2},
         
            # Para EtapaN3 "Ejecución OOCC" (id=3)
            {'nombre': 'Gasto Remesa 1', 'descripcion': 'Construcción de cimientos', 'id_etapaN2': 3},
            {'nombre': 'Gasto Remesa 2', 'descripcion': 'Levantamiento estructural', 'id_etapaN2': 3},
            {'nombre': 'Rendición Frima', 'descripcion': 'Instalación de cubiertas', 'id_etapaN2': 3},
            {'nombre': 'Entrega de Terreno ', 'descripcion': 'Instalación de cubiertas', 'id_etapaN2': 3},
            {'nombre': 'Obras Preliminares ', 'descripcion': 'Instalación de cubiertas', 'id_etapaN2': 3},
            {'nombre': 'Obras Gruesa ', 'descripcion': 'Instalación de cubiertas', 'id_etapaN2': 3},
            {'nombre': 'Terminaciones ', 'descripcion': 'Instalación de cubiertas', 'id_etapaN2': 3},
            {'nombre': 'Aseo y Entrega de Obra ', 'descripcion': 'Instalación de cubiertas', 'id_etapaN2': 3},
         
            # Para EtapaN3 "Ejecución Estudio" (id=4)
            {'nombre': 'Levantamiento de Información', 'descripcion': 'Construcción', 'id_etapaN2': 4},
            {'nombre': 'Estudio Geofísico REMI', 'descripcion': 'Levantamiento', 'id_etapaN2': 4},
            {'nombre': 'Análisis Sonómetro y Video de Inspección', 'descripcion': 'Instalación', 'id_etapaN2': 4},
            {'nombre': 'Informe de Daños y Propuesta de Reparación', 'descripcion': 'Instalación', 'id_etapaN2': 4},
            {'nombre': 'Planimetría, EE.TT. y Presupuesto', 'descripcion': 'Instalación', 'id_etapaN2': 4},
         
            # Para EtapaN3 "Ejecución Diseño" (id=5)
            {'nombre': 'Avance 1 - Anteproyecto Arquitectura ', 'descripcion': 'Trámites', 'id_etapaN2': 5},
            {'nombre': 'Avance 2 - Proyecto Arq. e Ing.', 'descripcion': 'Estimación', 'id_etapaN2': 5},
            {'nombre': 'Avance 3 - Desarrollo Especialidades', 'descripcion': 'Planificación', 'id_etapaN2': 5},
            {'nombre': 'Avance 4 - Ingreso Revisión Independiente e Ingreso P.E.', 'descripcion': 'Planificación', 'id_etapaN2': 5},
            {'nombre': 'Avance 5 - Permiso Edificación', 'descripcion': 'Planificación', 'id_etapaN2': 5},
         
            # Para EtapaN3 "Supervición Mantención Profecional" (id=6)
            {'nombre': 'Levantamiento de Información', 'descripcion': 'Trámites', 'id_etapaN2': 5},
            {'nombre': 'Diseño, TDR/EE.TT. y Presupuesto', 'descripcion': 'Estimación', 'id_etapaN2': 5},
            {'nombre': 'Contratación', 'descripcion': 'Planificación', 'id_etapaN2': 5},
            {'nombre': 'Supervisión y Ejecución', 'descripcion': 'Planificación', 'id_etapaN2': 5},
        ]
        etapas_n3 = [EtapaN3(**data) for data in etapas_n3_data]
        db.session.add_all(etapas_n3)
        db.session.commit()

        # Datos iniciales para EtapaN4
        etapas_n4_data = [
            # Para EtapaN4 "Esquemas Básicos" (id=1)
            {'nombre': 'Análisis del Sitio', 'descripcion': 'Estudio del terreno y contexto', 'id_etapaN3': 1},
            {'nombre': 'Programa Arquitectónico', 'descripcion': 'Definición de requerimientos', 'id_etapaN3': 1},
            {'nombre': 'Zonificación', 'descripcion': 'Organización espacial básica', 'id_etapaN3': 1},

            # Para EtapaN4 "Planos Arquitectónicos" (id=4)
            {'nombre': 'Plantas', 'descripcion': 'Dibujo de plantas arquitectónicas', 'id_etapaN3': 4},
            {'nombre': 'Cortes', 'descripcion': 'Secciones del proyecto', 'id_etapaN3': 4},
            {'nombre': 'Elevaciones', 'descripcion': 'Vistas exteriores', 'id_etapaN3': 4},

            # Para EtapaN4 "Detalles Constructivos" (id=5)
            {'nombre': 'Detalles de Ventanas', 'descripcion': 'Especificaciones de ventanería', 'id_etapaN3': 5},
            {'nombre': 'Detalles de Puertas', 'descripcion': 'Especificaciones de puertas', 'id_etapaN3': 5},
            {'nombre': 'Detalles de Acabados', 'descripcion': 'Especificaciones de materiales', 'id_etapaN3': 5},

            # Para EtapaN4 "Fundaciones" (id=7)
            {'nombre': 'Excavación', 'descripcion': 'Preparación del terreno', 'id_etapaN3': 7},
            {'nombre': 'Armado', 'descripcion': 'Colocación de armadura', 'id_etapaN3': 7},
            {'nombre': 'Hormigonado', 'descripcion': 'Vertido de hormigón', 'id_etapaN3': 7},

            # Para EtapaN4 "Estructura" (id=8)
            {'nombre': 'Columnas', 'descripcion': 'Elementos verticales', 'id_etapaN3': 8},
            {'nombre': 'Vigas', 'descripcion': 'Elementos horizontales', 'id_etapaN3': 8},
            {'nombre': 'Losas', 'descripcion': 'Elementos de piso', 'id_etapaN3': 8},

            # Para EtapaN4 "Techumbre" (id=9)
            {'nombre': 'Estructura de Techo', 'descripcion': 'Armado de cerchas', 'id_etapaN3': 9},
            {'nombre': 'Cubierta', 'descripcion': 'Instalación de tejas/planchas', 'id_etapaN3': 9},
            {'nombre': 'Aislación', 'descripcion': 'Instalación de aislantes', 'id_etapaN3': 9}
        ]
        # Crear EtapasN4
        etapas_n4 = [EtapaN4(**data) for data in etapas_n4_data]
        db.session.add_all(etapas_n4)
        db.session.commit()

        # Datos iniciales para Financiamiento
        financiamientos_data = [
            {'nombre': 'Por Definir', 'descripcion': 'Aún no se define el financiamiento'},
            {'nombre': 'Gobierno Regional', 'descripcion': 'Gobierno regional financia el proyecto'},
            {'nombre': 'MINSAL', 'descripcion': 'Ministerio de Salud financia el proyecto'},
            {'nombre': 'DEPSA', 'descripcion': 'Departamento de Salud financia el proyecto'},
            {'nombre': 'SUBDERE', 'descripcion': 'Subsecretaría de Desarrollo Regional financia el proyecto'},
            {'nombre': 'MUNICIPAL', 'descripcion': 'Municipalidad financia el proyecto'},
        ]
        financiamientos = [Financiamiento(**data) for data in financiamientos_data]
        db.session.add_all(financiamientos)
        db.session.commit()

        # Datos iniciales para Fase
        fases_data = [
            {'nombre': 'Por Definir'},
            {'nombre': 'Preinversión'},
            {'nombre': 'Inversión'},
            {'nombre': 'Operación'}
        ]
        fases = [Fase(**data) for data in fases_data]
        db.session.add_all(fases)
        db.session.commit()

        # Datos iniciales para Tipologia
        tipologias_data = [
            {'nombre': 'Por definir','nombrecorto':'Por definir','id_fase':1},  # Cambiado a id_fase:1
            {'nombre': 'Estudios Básicos - PreInv','nombrecorto':'EB-PreInv','id_fase':2},
            {'nombre': 'Programa de Inversión - PreInv','nombrecorto':'Prog_Inv-PreInv','id_fase':2},
            {'nombre': 'Proyecto de Inversión - PreInv','nombrecorto':'Proy_Inv-PreInv','id_fase':2},
            {'nombre': 'Estudios Básicos - Inv','nombrecorto':'EB-Inv','id_fase':3},
            {'nombre': 'Programa de Inversión - Inv','nombrecorto':'Prog_Inv-Inv','id_fase':3},
            {'nombre': 'Proyecto de Inversión - Inv','nombrecorto':'Proy_Inv-Inv','id_fase':3},
            {'nombre': 'Proyecto de Inversión - Op','nombrecorto':'Proy_Inv-Op','id_fase':4}
        ]
        tipologias = [Tipologia(**data) for data in tipologias_data]
        db.session.add_all(tipologias)
        db.session.commit()

        #-----------------------------------------------------------------------------
        # Datos iniciales para REQUERIMIENTO
        requerimiento_data = [
            {'nombre': 'PRUEBA 1',
            'fecha': '2025-02-03 00:00:00',
            'descripcion': 'SOLO DESCRIPCIÓN DE PRUEBA 1',
            'observacion': 'Solo prueba',
            'id_sector': 1 ,
            'id_tiporecinto': 5 ,
            'id_recinto': 8 ,
            'id_estado': 2 ,
            'fecha_aceptacion': '2025-02-05 15:53:01'},
        ]

       
        requerimientos = [Requerimiento(**data) for data in requerimiento_data]
        db.session.add_all(requerimientos)
        db.session.commit()
        #-----------------------------------------------------------------------------
        
        # Datos iniciales para otras tablas
        datos_iniciales = {
            Especialidad: [
                {'nombre': 'Formulador'},
                {'nombre': 'Arquitecto'},
                {'nombre': 'Ing. Electrico'},
                {'nombre': 'Ing. Civil'},
                {'nombre': 'Ing. Constructor'},
            ],
            Equipo: [
                {'nombre': 'Equipo 1'},
                {'nombre': 'Equipo 2'},
                {'nombre': 'Equipo 3'},
            ],
            TipoProyecto: [
                
                {'nombre': 'Por Definir', 'nombrecorto': 'Por Definir', 'descripcion': 'Fondos por definir'},
                {'nombre': 'PMI', 'nombrecorto': 'PMI', 'descripcion': 'Fondo para Proyectos de Mejoramiento Integral'},
                {'nombre': 'AGL', 'nombrecorto': 'AGL', 'descripcion': 'Fondo de Ampliación y Generación de Lugares'},
                {'nombre': 'FNDR - Circular 33', 'nombrecorto': 'FNDR-C33', 'descripcion': 'Fondo Nacional de Desarrollo Regional - Circular 33'},
                {'nombre': 'FNDR - Circular 31', 'nombrecorto': 'FNDR-C31', 'descripcion': 'Fondo Nacional de Desarrollo Regional - Circular 31'},
                {'nombre': 'Subtitulo 24 - Subsidios', 'nombrecorto': 'Sub24', 'descripcion': 'Fondo de Subtitulo 24 - subsidios'},
                {'nombre': 'Percapitado', 'nombrecorto': 'Percapitado', 'descripcion': 'Fondo Per Capitado'},
                {'nombre': 'PMU', 'nombrecorto': 'PMU', 'descripcion': 'Fondos de programas de Mejoramiento Urbano'},
                {'nombre': 'FRIL', 'nombrecorto': 'FRIL', 'descripcion': 'Fondo Regional de Inversion Local'},
                {'nombre': 'Municipal', 'nombrecorto': 'MUNICIPAL', 'descripcion': 'Fondo municipal'},
            ],
            Trabajador : [
            {
                'nombre': 'Admin',
                'profesion': 'Admin',
                'nombrecorto': 'admin',
                'password': 'Maho#2024'
            },
            {
                'nombre': 'Usuario Demo',
                'profesion': 'Admin',
                'nombrecorto': 'demo',
                'password': 'Demo#2024'
            }
            ]
        }

        for model, items in datos_iniciales.items():
            db.session.add_all([model(**item) for item in items])
            db.session.commit()
        
        print("Datos iniciales creados exitosamente")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creando datos iniciales: {e}")
        raise e

# Asegúrate de que la configuración de conexión a la base de datos sea correcta
# Verifica que el servicio de MySQL esté en funcionamiento y accesible desde tu aplicación

# Llamar a la función seed_data para cargar los datos iniciales
#seed_data()
