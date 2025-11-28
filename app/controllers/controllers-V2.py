from flask import Blueprint, request, jsonify, render_template, session, current_app
from werkzeug.utils import secure_filename
import os

from app.controllers.gantt.xlsx_processor import XLSXProcessor
from app.services.gantt_db_service import GanttDatabaseService
import pandas as pd

gantt_bp = Blueprint('gantt', __name__)
gantt_controller_bp = Blueprint('gantt_controller', __name__, url_prefix='/gantt-controller')

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
UPLOAD_FOLDER = 'uploads/gantt'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@gantt_bp.route('/upload_gantt', methods=['POST'])
def upload_gantt():
    """Maneja la carga del archivo XLSX para cartas Gantt"""
    try:
        if 'gantt_file' not in request.files:
            return jsonify({'success': False, 'error': 'No se encontró archivo'})
        
        file = request.files['gantt_file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Crear directorio si no existe
            upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            os.makedirs(upload_path, exist_ok=True)
            
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            
            # Procesar el archivo
            processor = XLSXProcessor()
            result = processor.process_file(file_path)
            
            if result['success']:
                # Guardar datos en sesión para acceso posterior
                session['gantt_data'] = result['data']
                session['gantt_summary'] = processor.get_summary()
                session['gantt_filename'] = filename
                
                return jsonify({
                    'success': True,
                    'message': 'Archivo procesado correctamente',
                    'summary': processor.get_summary(),
                    'filename': filename
                })
            else:
                return jsonify(result)
        
        return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'})
        
    except Exception as e:
        current_app.logger.error(f"Error en upload_gantt: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'})

@gantt_bp.route('/get_gantt_data')
def get_gantt_data():
    """Retorna los datos de la carta Gantt almacenados en sesión"""
    try:
        gantt_data = session.get('gantt_data', [])
        gantt_summary = session.get('gantt_summary', {})
        filename = session.get('gantt_filename', 'Sin archivo')
        
        return jsonify({
            'success': True,
            'data': gantt_data,
            'summary': gantt_summary,
            'filename': filename
        })
        
    except Exception as e:
        current_app.logger.error(f"Error en get_gantt_data: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener datos'})

@gantt_bp.route('/clear_gantt_data', methods=['POST'])
def clear_gantt_data():
    """Limpia los datos de la carta Gantt de la sesión"""
    try:
        session.pop('gantt_data', None)
        session.pop('gantt_summary', None)
        session.pop('gantt_filename', None)
        
        return jsonify({'success': True, 'message': 'Datos limpiados'})
        
    except Exception as e:
        current_app.logger.error(f"Error en clear_gantt_data: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al limpiar datos'})

@gantt_controller_bp.route('/test', methods=['GET'])
def test_gantt_controller():
    """Endpoint de prueba para verificar que el controlador funciona"""
    return jsonify({
        'success': True,
        'message': 'Gantt Controller funcionando correctamente',
        'routes': [
            '/gantt/ruta_llenar_xml',
            '/gantt/upload_gantt',
            '/gantt/get_gantt_data',
            '/gantt/clear_gantt_data'
        ]
    })

@controllers_bp.route('/cargar_carta_gantt/<int:id_requerimiento>', methods=['POST'])
def cargar_carta_gantt(id_requerimiento):
    """Cargar archivo Excel de carta Gantt y procesarlo"""
    try:
        if 'archivo_gantt' not in request.files:
            return jsonify({'success': False, 'error': 'No se encontró archivo'})
        
        file = request.files['archivo_gantt']
        nombre_gantt = request.form.get('nombre_gantt', '')
        descripcion_gantt = request.form.get('descripcion_gantt', '')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'error': 'Tipo de archivo no válido'})
        
        # Crear directorio temporal
        upload_folder = os.path.join(current_app.root_path, 'temp_uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            # Leer y procesar el archivo Excel
            df = pd.read_excel(file_path)
            
            # Mapeo de columnas
            column_mappings = {
                'Id': 'ID',
                'Nivel de esquema': 'Nivel_Esquema',
                'Nombre de tarea': 'Nombre_Tarea',
                'Duración': 'Duracion',
                'Comienzo': 'Fecha_Inicio',
                'Fin': 'Fecha_Fin',
                'Predecesoras': 'Predecesoras',
                'Nombres de los recursos': 'Recursos'
            }
            
            # Renombrar columnas
            df = df.rename(columns=column_mappings)
            
            # Procesar y limpiar datos
            tareas_procesadas = []
            for index, row in df.iterrows():
                if pd.notna(row.get('Nombre_Tarea', '')):
                    tarea = {
                        'id_fila': index,
                        'nombre': str(row.get('Nombre_Tarea', '')).strip(),
                        'duracion': row.get('Duracion', ''),
                        'fecha_inicio': row.get('Fecha_Inicio', ''),
                        'fecha_fin': row.get('Fecha_Fin', ''),
                        'nivel_esquema': row.get('Nivel_Esquema', 1),
                        'predecesoras': row.get('Predecesoras', ''),
                        'recursos': row.get('Recursos', '')
                    }
                    tareas_procesadas.append(tarea)
            
            # Guardar datos en sesión para uso posterior
            session[f'gantt_data_{id_requerimiento}'] = {
                'tareas': tareas_procesadas,
                'archivo_original': filename,
                'nombre_proyecto': nombre_gantt,
                'descripcion': descripcion_gantt
            }
            
            # Calcular estadísticas
            estadisticas = {
                'nombre_archivo': filename,
                'total_tareas': len(tareas_procesadas),
                'tareas_con_fechas': len([t for t in tareas_procesadas if t['fecha_inicio'] and t['fecha_fin']]),
                'tamaño_archivo': os.path.getsize(file_path)
            }
            
            return jsonify({
                'success': True,
                'message': 'Archivo procesado exitosamente',
                'estadisticas': estadisticas
            })
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al procesar archivo: {str(e)}'
        })

@controllers_bp.route('/obtener_tareas_gantt/<int:id_requerimiento>')
def obtener_tareas_gantt(id_requerimiento):
    """Obtener las tareas del Gantt cargado en sesión"""
    try:
        gantt_data = session.get(f'gantt_data_{id_requerimiento}')
        
        if not gantt_data:
            return jsonify({
                'success': False,
                'error': 'No hay datos de Gantt cargados para este proyecto'
            })
        
        tareas = gantt_data.get('tareas', [])
        
        # Formatear fechas para visualización
        for tarea in tareas:
            if isinstance(tarea.get('fecha_inicio'), pd.Timestamp):
                tarea['fecha_inicio'] = tarea['fecha_inicio'].strftime('%Y-%m-%d')
            if isinstance(tarea.get('fecha_fin'), pd.Timestamp):
                tarea['fecha_fin'] = tarea['fecha_fin'].strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'tareas': tareas,
            'total': len(tareas)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener tareas: {str(e)}'
        })

@controllers_bp.route('/guardar_tareas_seleccionadas/<int:id_requerimiento>', methods=['POST'])
def guardar_tareas_seleccionadas(id_requerimiento):
    """Guardar las tareas seleccionadas en la base de datos"""
    try:
        data = request.get_json()
        tareas_indices = data.get('tareas_indices', [])
        
        if not tareas_indices:
            return jsonify({
                'success': False,
                'error': 'No se seleccionaron tareas'
            })
        
        # Obtener datos de la sesión
        gantt_data = session.get(f'gantt_data_{id_requerimiento}')
        
        if not gantt_data:
            return jsonify({
                'success': False,
                'error': 'No hay datos de Gantt disponibles'
            })
        
        tareas = gantt_data.get('tareas', [])
        tareas_seleccionadas = [tareas[i] for i in tareas_indices if i < len(tareas)]
        
        if not tareas_seleccionadas:
            return jsonify({
                'success': False,
                'error': 'Las tareas seleccionadas no son válidas'
            })
        
        # Crear DataFrame con las tareas seleccionadas
        df_tareas = pd.DataFrame(tareas_seleccionadas)
        
        # Usar el servicio de base de datos para guardar
        resultado = GanttDatabaseService.crear_proyecto_desde_xlsx(
            id_requerimiento=id_requerimiento,
            df=df_tareas,
            nombre_proyecto=gantt_data.get('nombre_proyecto', f'Proyecto {id_requerimiento}')
        
        
        if resultado['success']:
            # Limpiar datos de sesión después del guardado exitoso
            session.pop(f'gantt_data_{id_requerimiento}', None)
            
            return jsonify({
                'success': True,
                'message': 'Tareas guardadas exitosamente',
                'tareas_guardadas': len(tareas_seleccionadas),
                'proyecto_id': resultado.get('proyecto_id')
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Error desconocido al guardar')
            })
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al guardar tareas: {str(e)}'
        })