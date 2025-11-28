from flask import Blueprint, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.models import Requerimiento, ActividadGantt, RecursoTrabajador
from app.utils.gantt_processor import GanttProcessor

bp = Blueprint('controllers', __name__)

@bp.route('/subir_gantt_xlsx/<int:req_id>', methods=['POST'])
@login_required
def subir_gantt_xlsx(req_id):
    """Subir archivo XLSX de Gantt para un requerimiento específico"""
    try:
        # Verificar que el requerimiento existe
        requerimiento = Requerimiento.query.get_or_404(req_id)
        
        # Verificar que se subió un archivo
        if 'archivo_gantt' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('controllers.proyectos_completar'))
        
        file = request.files['archivo_gantt']
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('controllers.proyectos_completar'))
        
        if not file or not file.filename.lower().endswith('.xlsx'):
            flash('Por favor seleccione un archivo XLSX válido', 'error')
            return redirect(url_for('controllers.proyectos_completar'))
        
        # Crear directorio para archivos Gantt si no existe
        gantt_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'gantt')
        os.makedirs(gantt_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"gantt_req_{req_id}_{timestamp}_{secure_filename(file.filename)}"
        file_path = os.path.join(gantt_dir, filename)
        
        # Guardar archivo
        file.save(file_path)
        
        print(f"📁 Archivo guardado en: {file_path}")
        
        # Procesar archivo y guardar en BD
        resultado = GanttProcessor.procesar_archivo_xlsx(file_path, req_id)
        
        if resultado['success']:
            # Mensaje de éxito con estadísticas
            mensaje = f"✅ Archivo procesado exitosamente:\n"
            mensaje += f"• {resultado['actividades_procesadas']} actividades guardadas\n"
            mensaje += f"• {resultado['recursos_procesados']} asignaciones de recursos creadas"
            
            if resultado['errores']:
                mensaje += f"\n⚠️ {len(resultado['errores'])} filas con errores (ver logs)"
            
            flash(mensaje, 'success')
            
            # Log detallado
            print(f"📊 Resumen del procesamiento:")
            print(f"   📋 Total de filas: {resultado['total_filas']}")
            print(f"   ✅ Actividades procesadas: {resultado['actividades_procesadas']}")
            print(f"   👥 Recursos procesados: {resultado['recursos_procesados']}")
            print(f"   ❌ Errores: {len(resultado['errores'])}")
            
        else:
            flash(f'Error al procesar el archivo: {resultado["error"]}', 'error')
            print(f"❌ Error en procesamiento: {resultado['error']}")
        
        # Eliminar archivo temporal (opcional)
        try:
            os.remove(file_path)
            print(f"🗑️ Archivo temporal eliminado: {file_path}")
        except Exception as e:
            print(f"⚠️ No se pudo eliminar archivo temporal: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error general en subir_gantt_xlsx: {str(e)}")
        flash(f'Error al procesar el archivo: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('controllers.proyectos_completar'))

@bp.route('/gantt_data/<int:req_id>')
@login_required
def gantt_data(req_id):
    """Obtener datos de Gantt para un requerimiento específico desde la BD"""
    try:
        # Verificar que el requerimiento existe
        requerimiento = Requerimiento.query.get_or_404(req_id)
        
        # Obtener actividades desde la base de datos
        actividades_bd = ActividadGantt.query.filter_by(
            requerimiento_id=req_id
        ).order_by(ActividadGantt.edt).all()
        
        if not actividades_bd:
            return jsonify({
                'success': False,
                'error': 'No hay actividades de Gantt guardadas para este requerimiento. Sube un archivo XLSX primero.',
                'actividades': [],
                'info': {
                    'fuente': 'base_de_datos',
                    'total_actividades': 0,
                    'fecha_actualizacion': None
                }
            })
        
        # Convertir actividades a formato para el frontend
        actividades_formato = []
        for actividad in actividades_bd:
            # Obtener recursos asignados
            recursos_asignados = RecursoTrabajador.query.filter_by(
                actividad_gantt_id=actividad.id
            ).all()
            
            recursos_texto = ', '.join([
                f"{rt.trabajador.nombre} ({rt.porcentaje_asignacion}%)" 
                for rt in recursos_asignados
            ]) if recursos_asignados else ''
            
            actividad_data = {
                'EDT': actividad.edt,
                'Nombre de tarea': actividad.nombre_tarea,
                'Inicio': actividad.fecha_inicio.strftime('%Y-%m-%d'),
                'Fin': actividad.fecha_fin.strftime('%Y-%m-%d'),
                'Duración': actividad.duracion,
                'Progreso': actividad.progreso * 100,  # Convertir a porcentaje
                'Nivel de esquema': actividad.nivel_esquema,
                'Predecesoras': actividad.predecesoras,
                'Recursos': recursos_texto,
                'Recursos originales': actividad.recursos_originales
            }
            actividades_formato.append(actividad_data)
        
        # Información adicional
        fecha_actualizacion = max([a.fecha_actualizacion for a in actividades_bd]) if actividades_bd else None
        
        return jsonify({
            'success': True,
            'actividades': actividades_formato,
            'info': {
                'fuente': 'base_de_datos',
                'total_actividades': len(actividades_bd),
                'fecha_actualizacion': fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if fecha_actualizacion else None,
                'requerimiento_id': req_id,
                'requerimiento_nombre': requerimiento.nombre
            }
        })
        
    except Exception as e:
        print(f"❌ Error en gantt_data para req_id {req_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al cargar datos de Gantt: {str(e)}',
            'actividades': []
        }), 500