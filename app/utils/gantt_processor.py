import re
import pandas as pd
from datetime import datetime, date
from app.models import db, ActividadGantt, RecursoTrabajador, Trabajador
from sqlalchemy.exc import IntegrityError

class GanttProcessor:
    
    @staticmethod
    def procesar_archivo_xlsx(file_path, requerimiento_id):
        """
        Procesa un archivo XLSX de Gantt y guarda los datos en la base de datos
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file_path)
            
            print(f"📊 Procesando archivo con {len(df)} filas")
            print(f"📋 Columnas encontradas: {list(df.columns)}")
            
            # Limpiar datos existentes del requerimiento
            GanttProcessor._limpiar_datos_existentes(requerimiento_id)
            
            actividades_procesadas = 0
            recursos_procesados = 0
            errores = []
            
            for index, row in df.iterrows():
                try:
                    # Procesar actividad
                    actividad = GanttProcessor._procesar_actividad(row, requerimiento_id, index + 1)
                    if actividad:
                        db.session.add(actividad)
                        db.session.flush()  # Para obtener el ID
                        
                        # Procesar recursos de la actividad
                        recursos_count = GanttProcessor._procesar_recursos_actividad(
                            actividad, row, requerimiento_id
                        )
                        
                        actividades_procesadas += 1
                        recursos_procesados += recursos_count
                        
                except Exception as e:
                    error_msg = f"Error en fila {index + 1}: {str(e)}"
                    errores.append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Confirmar cambios
            db.session.commit()
            
            resultado = {
                'success': True,
                'actividades_procesadas': actividades_procesadas,
                'recursos_procesados': recursos_procesados,
                'errores': errores,
                'total_filas': len(df)
            }
            
            print(f"✅ Procesamiento completado: {actividades_procesadas} actividades, {recursos_procesados} recursos")
            return resultado
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error general en procesamiento: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'actividades_procesadas': 0,
                'recursos_procesados': 0
            }
    
    @staticmethod
    def _limpiar_datos_existentes(requerimiento_id):
        """Elimina datos existentes del requerimiento"""
        try:
            # Eliminar recursos trabajadores
            RecursoTrabajador.query.filter_by(requerimiento_id=requerimiento_id).delete()
            
            # Eliminar actividades gantt
            ActividadGantt.query.filter_by(requerimiento_id=requerimiento_id).delete()
            
            print(f"🧹 Datos existentes eliminados para requerimiento {requerimiento_id}")
            
        except Exception as e:
            print(f"⚠️ Error al limpiar datos existentes: {str(e)}")
    
    @staticmethod
    def _procesar_actividad(row, requerimiento_id, numero_fila):
        """Procesa una fila del Excel y crea una ActividadGantt"""
        try:
            # Obtener valores usando múltiples posibles nombres de columnas
            edt = GanttProcessor._obtener_valor(row, ['EDT', 'E.D.T.', 'Edt', 'WBS', 'ID'])
            nombre_tarea = GanttProcessor._obtener_valor(row, ['Nombre de tarea', 'Actividad', 'Nombre', 'Task Name', 'Tarea'])
            fecha_inicio = GanttProcessor._convertir_fecha(
                GanttProcessor._obtener_valor(row, ['Inicio', 'Comienzo', 'Start', 'Fecha Inicio', 'Start Date'])
            )
            fecha_fin = GanttProcessor._convertir_fecha(
                GanttProcessor._obtener_valor(row, ['Fin', 'End', 'Fecha Fin', 'End Date', 'Finalización'])
            )
            # Obtener duración y limpiar texto como "25 días"
            duracion_raw = GanttProcessor._obtener_valor(row, ['Duración', 'Duration', 'Días']) or 1
            duracion = GanttProcessor._limpiar_numero(duracion_raw)
            
            # Obtener progreso y limpiar porcentaje
            progreso_raw = GanttProcessor._obtener_valor(row, ['Progreso', '% Completado', 'Progress']) or 0
            progreso = GanttProcessor._limpiar_porcentaje(progreso_raw)
            
            nivel_esquema = GanttProcessor._obtener_valor(row, ['Nivel de esquema', 'Nivel', 'Level']) or 1
            predecesoras = GanttProcessor._obtener_valor(row, ['Predecesoras', 'Predecessors', 'Dependencias']) or ''
            recursos = GanttProcessor._obtener_valor(row, ['Recursos', 'Resource Names', 'Nombres de los recursos']) or ''
            
            # Validaciones básicas
            if not edt or not nombre_tarea:
                print(f"⚠️ Fila {numero_fila}: EDT o nombre_tarea faltante")
                return None
                
            if not fecha_inicio or not fecha_fin:
                print(f"⚠️ Fila {numero_fila}: Fechas inválidas")
                return None
            
            # Crear actividad
            actividad = ActividadGantt(
                requerimiento_id=requerimiento_id,
                edt=str(edt),
                nombre_tarea=str(nombre_tarea),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                duracion=int(duracion) if duracion else 1,
                progreso=float(progreso) / 100 if progreso and progreso > 1 else float(progreso) if progreso else 0.0,
                nivel_esquema=int(nivel_esquema) if nivel_esquema else 1,
                predecesoras=str(predecesoras) if predecesoras else '',
                recursos_originales=str(recursos) if recursos else ''
            )
            
            return actividad
            
        except Exception as e:
            print(f"❌ Error procesando actividad fila {numero_fila}: {str(e)}")
            return None
    
    @staticmethod
    def _limpiar_numero(valor):
        """Extrae el número de un texto que puede contener palabras como '25 días'"""
        if not valor:
            return 1
        
        try:
            # Si ya es un número, devolverlo
            if isinstance(valor, (int, float)):
                return max(1, int(valor))
            
            # Si es string, extraer solo los números
            valor_str = str(valor).strip()
            
            # Buscar el primer número en el string
            import re
            numeros = re.findall(r'\d+(?:\.\d+)?', valor_str)
            
            if numeros:
                return max(1, int(float(numeros[0])))
            else:
                return 1
                
        except Exception as e:
            print(f"⚠️ Error limpiando número '{valor}': {str(e)}")
            return 1
    
    @staticmethod
    def _limpiar_porcentaje(valor):
        """Extrae el porcentaje de un texto que puede contener '%' """
        if not valor:
            return 0.0
        
        try:
            # Si ya es un número, devolverlo
            if isinstance(valor, (int, float)):
                return float(valor)
            
            # Si es string, limpiar y extraer número
            valor_str = str(valor).strip().replace('%', '').replace(',', '.')
            
            # Buscar el primer número en el string
            import re
            numeros = re.findall(r'\d+(?:\.\d+)?', valor_str)
            
            if numeros:
                porcentaje = float(numeros[0])
                return max(0.0, min(100.0, porcentaje))
            else:
                return 0.0
                
        except Exception as e:
            print(f"⚠️ Error limpiando porcentaje '{valor}': {str(e)}")
            return 0.0
    
    @staticmethod
    def _procesar_recursos_actividad(actividad, row, requerimiento_id):
        """Procesa los recursos de una actividad y los divide por trabajadores"""
        recursos_count = 0
        
        try:
            recursos_texto = actividad.recursos_originales
            if not recursos_texto or recursos_texto.strip() == '':
                return 0
            
            # Parsear recursos usando el nuevo formato que soporta nombrecorto[porcentaje%]
            recursos_parseados = GanttProcessor._parsear_recursos(recursos_texto)
            
            for recurso_info in recursos_parseados:
                # Usar el nombre_corto en lugar del nombre completo
                trabajador = GanttProcessor._obtener_o_crear_trabajador(recurso_info['nombre_corto'])
                
                if trabajador:
                    # Crear registro en recursos_trabajador
                    recurso_trabajador = RecursoTrabajador(
                        requerimiento_id=requerimiento_id,
                        actividad_gantt_id=actividad.id,
                        edt=actividad.edt,
                        recurso=recurso_info['nombre_corto'],  # Usar nombre_corto
                        id_trabajador=trabajador.id,
                        porcentaje_asignacion=recurso_info['porcentaje']
                    )
                    
                    db.session.add(recurso_trabajador)
                    recursos_count += 1
                    print(f"  💼 Recurso asignado: {recurso_info['nombre_corto']} -> {recurso_info['porcentaje']}% en actividad {actividad.edt}")
                    
        except Exception as e:
            print(f"❌ Error procesando recursos para actividad {actividad.edt}: {str(e)}")
        
        return recursos_count
    
    @staticmethod
    def _parsear_recursos(recursos_texto):
        """
        Parsea el texto de recursos y extrae nombres cortos y porcentajes
        Formato esperado: PM1[100%];PM2[50%];DEV3[75%]
        También soporta formatos alternativos como:
        - "PM1[100%],PM2[50%]" (separado por comas)
        - "PM1(100%);PM2(50%)" (paréntesis en lugar de corchetes)
        - "PM1 100%;PM2 50%" (espacios en lugar de corchetes)
        - "PM1;PM2" (asume 100% para cada uno)
        """
        recursos = []
        
        try:
            if not recursos_texto or recursos_texto.strip() == '':
                return recursos
                
            # Limpiar el texto inicial
            texto_limpio = recursos_texto.strip().replace('\n', ' ').replace('\r', '')
            print(f"🔍 Procesando recursos: '{texto_limpio}'")
            
            # Dividir por separadores comunes (punto y coma, coma, salto de línea)
            items = re.split(r'[;,\n]', texto_limpio)
            
            for item in items:
                item = item.strip()
                if not item:
                    continue
                
                nombre_corto = ""
                porcentaje = 100.0
                
                # Patrón principal: "PM1[100%]" o "PM1(100%)"
                match_corchetes = re.search(r'^([^[\(\s]+)[\[\(](\d+(?:\.\d+)?)%?[\]\)]$', item)
                if match_corchetes:
                    nombre_corto = match_corchetes.group(1).strip()
                    porcentaje = float(match_corchetes.group(2))
                    print(f"  ✅ Patrón corchetes: '{nombre_corto}' -> {porcentaje}%")
                
                # Patrón alternativo: "PM1 100%" (con espacio)
                elif re.search(r'(\d+(?:\.\d+)?)%', item):
                    match_espacio = re.search(r'^([^\s]+)\s+(\d+(?:\.\d+)?)%?', item)
                    if match_espacio:
                        nombre_corto = match_espacio.group(1).strip()
                        porcentaje = float(match_espacio.group(2))
                        print(f"  ✅ Patrón espacio: '{nombre_corto}' -> {porcentaje}%")
                    else:
                        # Extraer nombre y porcentaje por separado
                        nombre_corto = re.sub(r'\d+(?:\.\d+)?%?', '', item).strip()
                        porcentaje_match = re.search(r'(\d+(?:\.\d+)?)%?', item)
                        if porcentaje_match:
                            porcentaje = float(porcentaje_match.group(1))
                        print(f"  ✅ Patrón extractivo: '{nombre_corto}' -> {porcentaje}%")
                
                # Patrón simple: Solo nombre corto (asume 100%)
                else:
                    # Limpiar cualquier carácter especial que pueda haber quedado
                    nombre_corto = re.sub(r'[^\w\-]', '', item).strip()
                    porcentaje = 100.0
                    print(f"  ✅ Patrón simple: '{nombre_corto}' -> {porcentaje}% (por defecto)")
                
                # Validar y procesar el resultado
                if nombre_corto and len(nombre_corto) >= 2:
                    # Validar que el porcentaje esté en rango válido
                    porcentaje = max(0.0, min(100.0, porcentaje))
                    
                    recursos.append({
                        'nombre_corto': nombre_corto,
                        'porcentaje': porcentaje
                    })
                    print(f"  ✅ Recurso agregado: '{nombre_corto}' -> {porcentaje}%")
                else:
                    print(f"  ⚠️ Nombre corto inválido ignorado: '{item}'")
                        
        except Exception as e:
            print(f"❌ Error parseando recursos '{recursos_texto}': {str(e)}")
            # Fallback: tratar todo como un solo recurso al 100%
            nombre_fallback = re.sub(r'[^\w\-]', '', recursos_texto.split('[')[0].split('(')[0]).strip()
            if nombre_fallback and len(nombre_fallback) >= 2:
                recursos = [{'nombre_corto': nombre_fallback, 'porcentaje': 100.0}]
                print(f"  🔄 Fallback aplicado: '{nombre_fallback}' -> 100%")
        
        print(f"🔍 Total recursos parseados: {len(recursos)}")
        return recursos
    
    @staticmethod
    def _obtener_o_crear_trabajador(nombre_corto_recurso):
        """
        Obtiene un trabajador existente por nombrecorto o crea uno nuevo
        Busca primero por nombrecorto exacto, luego por nombre parcial
        """
        try:
            # Limpiar y normalizar el nombre corto
            nombre_corto_limpio = nombre_corto_recurso.strip().upper()
            
            if not nombre_corto_limpio or len(nombre_corto_limpio) < 2:
                print(f"⚠️ Nombre corto muy corto o vacío: '{nombre_corto_recurso}'")
                return None
            
            print(f"🔍 Buscando trabajador con nombrecorto: '{nombre_corto_limpio}'")
            
            # Buscar trabajador por nombrecorto exacto (case-insensitive)
            trabajador = Trabajador.query.filter(
                Trabajador.nombrecorto.ilike(nombre_corto_limpio)
            ).first()
            
            if trabajador:
                print(f"✅ Trabajador encontrado por nombrecorto: {trabajador.nombre} ({trabajador.nombrecorto})")
                return trabajador
            
            # Si no encuentra por nombrecorto, buscar en el nombre completo
            trabajador = Trabajador.query.filter(
                Trabajador.nombre.ilike(f'%{nombre_corto_limpio}%')
            ).first()
            
            if trabajador:
                print(f"✅ Trabajador encontrado por nombre parcial: {trabajador.nombre} ({trabajador.nombrecorto})")
                return trabajador
            
            # Si no existe, crear un nuevo trabajador
            print(f"🆕 Creando nuevo trabajador con nombrecorto: '{nombre_corto_limpio}'")
            
            # Generar nombre completo basado en el nombrecorto
            nombre_completo = f"Trabajador {nombre_corto_limpio}"
            
            # Generar email automático basado en nombrecorto
            email_usuario = nombre_corto_limpio.lower()
            email_completo = f"{email_usuario}@empresa.com"
            
            # Verificar que el email no exista
            email_existente = Trabajador.query.filter_by(email=email_completo).first()
            if email_existente:
                # Agregar timestamp al email para evitar duplicados
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d')
                email_completo = f"{email_usuario}{timestamp}@empresa.com"
            
            # Crear nuevo trabajador
            nuevo_trabajador = Trabajador(
                nombre=nombre_completo,
                nombrecorto=nombre_corto_limpio,
                profesion='Por definir',
                email=email_completo,
                telefono='',
                activo=True
            )
            
            db.session.add(nuevo_trabajador)
            db.session.flush()  # Para obtener el ID sin hacer commit completo
            
            print(f"✅ Nuevo trabajador creado: {nuevo_trabajador.nombre} ({nuevo_trabajador.nombrecorto})")
            return nuevo_trabajador
            
        except Exception as e:
            print(f"❌ Error obteniendo/creando trabajador '{nombre_corto_recurso}': {str(e)}")
            return None
    
    @staticmethod
    def _obtener_valor(row, posibles_nombres):
        """Obtiene un valor de la fila usando múltiples posibles nombres de columna"""
        for nombre in posibles_nombres:
            if nombre in row and pd.notna(row[nombre]) and str(row[nombre]).strip() != '':
                return row[nombre]
        return None
    
    @staticmethod
    def _convertir_fecha(fecha_valor):
        """Convierte un valor a fecha"""
        if not fecha_valor or pd.isna(fecha_valor):
            return None
        
        try:
            if isinstance(fecha_valor, pd.Timestamp):
                return fecha_valor.date()
            elif isinstance(fecha_valor, datetime):
                return fecha_valor.date()
            elif isinstance(fecha_valor, date):
                return fecha_valor
            elif isinstance(fecha_valor, str):
                # Intentar varios formatos de fecha
                formatos = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y']
                for formato in formatos:
                    try:
                        return datetime.strptime(fecha_valor, formato).date()
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error convirtiendo fecha '{fecha_valor}': {str(e)}")
            return None
