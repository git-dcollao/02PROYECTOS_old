"""
🎯 CONTROLADOR DE VALIDACIÓN DE AVANCES
========================================

Este controlador maneja toda la lógica relacionada con la validación supervisada
de avances reportados por trabajadores en actividades de proyectos.

Responsabilidades:
- Listar avances pendientes de validación
- Aprobar avances reportados
- Corregir porcentajes antes de validar
- Rechazar avances con comentarios
- Actualizar historial y actividad_proyecto

Permisos requeridos:
- SUPERADMIN (acceso total)
- Administrador
- Control
- Usuarios con permiso específico a /validar-avances

Author: Sistema de Gestión de Proyectos
Date: Diciembre 2025
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import csrf
from app.models import (
    HistorialAvanceActividad, ActividadProyecto, Requerimiento, 
    Trabajador, db
)
from datetime import datetime
from sqlalchemy import func, or_, and_, desc
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear Blueprint
validar_avances_bp = Blueprint('validar_avances', __name__, url_prefix='/validar-avances')


@validar_avances_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Página principal de validación de avances
    Muestra avances pendientes de validación con filtros
    """
    print(f"🔍 Endpoint validar_avances.index llamado por {current_user.email}")
    start_time = datetime.now()
    
    try:
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Renderizar página
        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ Página validar-avances cargada en {duration:.3f}s")
        
        return render_template('validar-avances.html')
        
    except Exception as e:
        print(f"❌ Error en validar_avances.index: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error al cargar la página: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@validar_avances_bp.route('/listar', methods=['GET'])
@login_required
def listar_avances():
    """
    API: Listar avances pendientes de validación
    Filtros: proyecto, trabajador, estado (pendiente/validado/todos)
    """
    print(f"🔍 API validar_avances.listar_avances llamado por {current_user.email}")
    
    try:
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
        # Obtener filtros
        proyecto_id = request.args.get('proyecto_id', type=int)
        trabajador_id = request.args.get('trabajador_id', type=int)
        estado_validacion = request.args.get('estado', 'pendiente')  # pendiente, validado, rechazado, todos
        
        # Query base
        query = db.session.query(
            HistorialAvanceActividad,
            ActividadProyecto,
            Requerimiento,
            Trabajador
        ).join(
            ActividadProyecto, HistorialAvanceActividad.actividad_id == ActividadProyecto.id
        ).join(
            Requerimiento, HistorialAvanceActividad.requerimiento_id == Requerimiento.id
        ).join(
            Trabajador, HistorialAvanceActividad.trabajador_id == Trabajador.id
        )
        
        # Filtrar según nivel de acceso
        if not current_user.is_superadmin():
            query = query.filter(Requerimiento.id_recinto == current_user.recinto_id)
        
        # Aplicar filtros
        if proyecto_id:
            query = query.filter(HistorialAvanceActividad.requerimiento_id == proyecto_id)
        
        if trabajador_id:
            query = query.filter(HistorialAvanceActividad.trabajador_id == trabajador_id)
        
        if estado_validacion == 'pendiente':
            query = query.filter(HistorialAvanceActividad.validado == False)
        elif estado_validacion == 'validado':
            query = query.filter(
                HistorialAvanceActividad.validado == True,
                HistorialAvanceActividad.comentario_validacion.is_(None) | 
                (HistorialAvanceActividad.comentario_validacion != 'RECHAZADO')
            )
        elif estado_validacion == 'rechazado':
            query = query.filter(
                HistorialAvanceActividad.validado == True,
                HistorialAvanceActividad.comentario_validacion.like('%RECHAZADO%')
            )
        # 'todos' no filtra por estado
        
        # Ordenar por fecha más reciente
        query = query.order_by(desc(HistorialAvanceActividad.fecha_cambio))
        
        resultados = query.all()
        
        # Preparar datos para respuesta
        avances = []
        for historial, actividad, proyecto, trabajador in resultados:
            avances.append({
                'id': historial.id,
                'proyecto_id': proyecto.id,
                'proyecto_nombre': proyecto.nombre,
                'proyecto_edt': proyecto.id,  # Usar id en lugar de codigo que no existe
                'actividad_id': actividad.id,
                'actividad_nombre': actividad.nombre_tarea,
                'actividad_edt': actividad.edt,
                'trabajador_id': trabajador.id,
                'trabajador_nombre': trabajador.nombre,
                'trabajador_email': trabajador.email,
                'progreso_anterior': float(historial.progreso_anterior),
                'progreso_nuevo': float(historial.progreso_nuevo),
                'diferencia': float(historial.diferencia),
                'comentarios': historial.comentarios,
                'fecha_cambio': historial.fecha_cambio.strftime('%Y-%m-%d %H:%M:%S'),
                'validado': historial.validado,
                'validado_por_id': historial.validado_por_id,
                'validado_por_nombre': historial.validado_por.nombre if historial.validado_por else None,
                'fecha_validacion': historial.fecha_validacion.strftime('%Y-%m-%d %H:%M:%S') if historial.fecha_validacion else None,
                'comentario_validacion': historial.comentario_validacion,
                'porcentaje_validado_actual': float(actividad.porcentaje_avance_validado),
                'estado_visual': 'Validado' if historial.validado and 'RECHAZADO' not in (historial.comentario_validacion or '') else ('Rechazado' if historial.validado and 'RECHAZADO' in (historial.comentario_validacion or '') else 'Pendiente')
            })
        
        print(f"✅ Listados {len(avances)} avances")
        
        return jsonify({
            'success': True,
            'avances': avances,
            'total': len(avances)
        })
        
    except Exception as e:
        print(f"❌ Error en listar_avances: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@validar_avances_bp.route('/validar', methods=['POST'])
@csrf.exempt
@login_required
def validar_avance():
    """
    API: Validar (aprobar) un avance reportado
    Actualiza historial y porcentaje_avance_validado en actividad_proyecto
    """
    print(f"🔍 API validar_avances.validar_avance llamado por {current_user.email}")
    
    try:
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
        data = request.get_json()
        historial_id = data.get('historial_id')
        comentario = data.get('comentario', '')
        
        if not historial_id:
            return jsonify({'success': False, 'message': 'ID de historial requerido'}), 400
        
        # Buscar registro de historial
        historial = HistorialAvanceActividad.query.get(historial_id)
        if not historial:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        
        # Verificar permisos de acceso al proyecto
        if not current_user.is_superadmin():
            proyecto = Requerimiento.query.get(historial.requerimiento_id)
            if proyecto.id_recinto != current_user.recinto_id:
                return jsonify({'success': False, 'message': 'Sin permisos para este proyecto'}), 403
        
        # Actualizar historial
        historial.validado = True
        historial.validado_por_id = current_user.id
        historial.fecha_validacion = datetime.utcnow()
        historial.comentario_validacion = comentario or 'Aprobado'
        
        # Actualizar porcentaje_avance_validado en actividad_proyecto
        actividad = ActividadProyecto.query.get(historial.actividad_id)
        if actividad:
            actividad.porcentaje_avance_validado = historial.progreso_nuevo
            
            # **NUEVO: Recalcular progreso jerárquico tras validación**
            print(f"🌳 Recalculando progreso jerárquico tras validación de {actividad.edt}...")
            from app.controllers_main import calcular_progreso_actividad, recalcular_padres_recursivo
            
            # 1. Recalcular progreso de la actividad (promedio trabajadores)
            progreso_calculado = calcular_progreso_actividad(actividad.id)
            actividad.progreso = progreso_calculado
            print(f"   📊 Progreso actividad {actividad.edt}: {progreso_calculado:.2f}%")
            
            # 2. Recalcular todos los padres en la jerarquía
            recalcular_padres_recursivo(actividad.edt, historial.requerimiento_id)
            print(f"   ✅ Jerarquía recalculada desde {actividad.edt}")
        
        db.session.commit()
        
        print(f"✅ Avance validado: Historial {historial_id}, Actividad {actividad.edt}, {historial.progreso_nuevo}%")
        
        return jsonify({
            'success': True,
            'message': 'Avance validado exitosamente',
            'porcentaje_validado': float(historial.progreso_nuevo)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en validar_avance: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@validar_avances_bp.route('/corregir', methods=['POST'])
@csrf.exempt
@login_required
def corregir_avance():
    """
    API: Corregir porcentaje antes de validar
    Permite al supervisor ajustar el % reportado
    
    IMPORTANTE: Crea un NUEVO registro en historial_avance_actividad con el valor corregido,
    manteniendo el registro original del trabajador intacto para trazabilidad completa.
    """
    print(f"🔍 API validar_avances.corregir_avance llamado por {current_user.email}")
    
    try:
        import uuid
        from app.models import AvanceActividad
        
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
        data = request.get_json()
        historial_id = data.get('historial_id')
        porcentaje_corregido = data.get('porcentaje_corregido')
        comentario = data.get('comentario', '')
        
        if not historial_id or porcentaje_corregido is None:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
        
        # Validar rango de porcentaje
        try:
            porcentaje_corregido = float(porcentaje_corregido)
            if porcentaje_corregido < 0 or porcentaje_corregido > 100:
                return jsonify({'success': False, 'message': 'Porcentaje debe estar entre 0 y 100'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Porcentaje inválido'}), 400
        
        # Buscar registro de historial ORIGINAL del trabajador
        historial_original = HistorialAvanceActividad.query.get(historial_id)
        if not historial_original:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        
        # Verificar permisos de acceso al proyecto
        if not current_user.is_superadmin():
            proyecto = Requerimiento.query.get(historial_original.requerimiento_id)
            if proyecto.id_recinto != current_user.recinto_id:
                return jsonify({'success': False, 'message': 'Sin permisos para este proyecto'}), 403
        
        # 1. Marcar el registro original como "corregido" sin modificar sus valores
        historial_original.validado = True
        historial_original.validado_por_id = current_user.id
        historial_original.fecha_validacion = datetime.utcnow()
        historial_original.comentario_validacion = f"CORREGIDO por supervisor de {historial_original.progreso_nuevo}% a {porcentaje_corregido}%"
        
        print(f"📝 Registro original {historial_id} marcado como corregido")
        print(f"   Valor reportado por trabajador: {historial_original.progreso_nuevo}%")
        print(f"   Valor corregido por supervisor: {porcentaje_corregido}%")
        
        # 2. Crear NUEVO registro con el valor corregido
        sesion_correccion = f"CORRECCION_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        nuevo_historial = HistorialAvanceActividad(
            requerimiento_id=historial_original.requerimiento_id,
            trabajador_id=historial_original.trabajador_id,
            actividad_id=historial_original.actividad_id,
            progreso_anterior=historial_original.progreso_nuevo,  # El valor reportado por trabajador
            progreso_nuevo=porcentaje_corregido,  # El valor corregido
            diferencia=porcentaje_corregido - historial_original.progreso_nuevo,
            comentarios=f"Corrección supervisada: {comentario}" if comentario else "Corrección supervisada",
            fecha_cambio=datetime.utcnow(),
            sesion_guardado=sesion_correccion,
            validado=True,  # Ya viene validado
            validado_por_id=current_user.id,
            fecha_validacion=datetime.utcnow(),
            comentario_validacion=f"Corregido de {historial_original.progreso_nuevo}% a {porcentaje_corregido}%. {comentario}"
        )
        db.session.add(nuevo_historial)
        
        print(f"✅ Nuevo registro de corrección creado:")
        print(f"   Sesión: {sesion_correccion}")
        print(f"   Diferencia: {nuevo_historial.diferencia:+.1f}%")
        
        # 3. Actualizar tabla avance_actividad con el valor corregido
        avance_actividad = AvanceActividad.query.filter_by(
            requerimiento_id=historial_original.requerimiento_id,
            trabajador_id=historial_original.trabajador_id,
            actividad_id=historial_original.actividad_id
        ).first()
        
        if avance_actividad:
            avance_actividad.progreso_anterior = avance_actividad.progreso_actual
            avance_actividad.progreso_actual = porcentaje_corregido
            avance_actividad.fecha_actualizacion = datetime.utcnow()
            avance_actividad.observaciones = f"Corregido por supervisor {current_user.nombre}: {historial_original.progreso_nuevo}% → {porcentaje_corregido}%"
            print(f"📊 Tabla avance_actividad actualizada con valor corregido")
        
        # 4. Actualizar porcentaje_avance_validado en actividad_proyecto
        actividad = ActividadProyecto.query.get(historial_original.actividad_id)
        if actividad:
            actividad.porcentaje_avance_validado = porcentaje_corregido
            
            # 5. Recalcular progreso jerárquico tras corrección
            print(f"🌳 Recalculando progreso jerárquico tras corrección de {actividad.edt}...")
            from app.controllers_main import calcular_progreso_actividad, recalcular_padres_recursivo
            
            # Recalcular progreso de la actividad (promedio trabajadores)
            progreso_calculado = calcular_progreso_actividad(actividad.id)
            actividad.progreso = progreso_calculado
            print(f"   📊 Progreso actividad {actividad.edt}: {progreso_calculado:.2f}%")
            
            # Recalcular todos los padres en la jerarquía
            recalcular_padres_recursivo(actividad.edt, historial_original.requerimiento_id)
            print(f"   ✅ Jerarquía recalculada desde {actividad.edt}")
        
        db.session.commit()
        
        print(f"✅ Avance corregido exitosamente:")
        print(f"   Historial original: {historial_id} (conservado para auditoría)")
        print(f"   Nuevo historial: {nuevo_historial.id}")
        print(f"   Actividad: {actividad.edt}")
        print(f"   Porcentaje final: {porcentaje_corregido}%")
        
        return jsonify({
            'success': True,
            'message': 'Avance corregido y validado exitosamente',
            'porcentaje_validado': float(porcentaje_corregido),
            'historial_original_id': historial_id,
            'nuevo_historial_id': nuevo_historial.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en corregir_avance: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@validar_avances_bp.route('/rechazar', methods=['POST'])
@csrf.exempt
@login_required
def rechazar_avance():
    """
    API: Rechazar un avance reportado
    Marca como validado con comentario de rechazo
    """
    print(f"🔍 API validar_avances.rechazar_avance llamado por {current_user.email}")
    
    try:
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
        data = request.get_json()
        historial_id = data.get('historial_id')
        motivo = data.get('motivo', 'Sin especificar')
        
        if not historial_id:
            return jsonify({'success': False, 'message': 'ID de historial requerido'}), 400
        
        # Buscar registro de historial
        historial = HistorialAvanceActividad.query.get(historial_id)
        if not historial:
            return jsonify({'success': False, 'message': 'Registro no encontrado'}), 404
        
        # Verificar permisos de acceso al proyecto
        if not current_user.is_superadmin():
            proyecto = Requerimiento.query.get(historial.requerimiento_id)
            if proyecto.id_recinto != current_user.recinto_id:
                return jsonify({'success': False, 'message': 'Sin permisos para este proyecto'}), 403
        
        # Actualizar historial con rechazo
        historial.validado = True  # Se marca como "revisado"
        historial.validado_por_id = current_user.id
        historial.fecha_validacion = datetime.utcnow()
        historial.comentario_validacion = f"RECHAZADO - Motivo: {motivo}"
        
        # NO actualizar porcentaje_avance_validado (mantener el anterior)
        
        db.session.commit()
        
        print(f"✅ Avance rechazado: Historial {historial_id}, Motivo: {motivo}")
        
        return jsonify({
            'success': True,
            'message': 'Avance rechazado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en rechazar_avance: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@validar_avances_bp.route('/estadisticas', methods=['GET'])
@login_required
def estadisticas():
    """
    API: Obtener estadísticas de validación
    Total pendientes, validados, rechazados
    """
    print(f"🔍 API validar_avances.estadisticas llamado por {current_user.email}")
    
    try:
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
        # Query base
        query = HistorialAvanceActividad.query
        
        # Filtrar según nivel de acceso
        if not current_user.is_superadmin():
            query = query.join(Requerimiento).filter(Requerimiento.id_recinto == current_user.recinto_id)
        
        # Contar estados
        total = query.count()
        pendientes = query.filter(HistorialAvanceActividad.validado == False).count()
        validados = query.filter(
            HistorialAvanceActividad.validado == True,
            or_(
                HistorialAvanceActividad.comentario_validacion.is_(None),
                ~HistorialAvanceActividad.comentario_validacion.like('%RECHAZADO%')
            )
        ).count()
        rechazados = query.filter(
            HistorialAvanceActividad.validado == True,
            HistorialAvanceActividad.comentario_validacion.like('%RECHAZADO%')
        ).count()
        
        print(f"✅ Estadísticas: {total} total, {pendientes} pendientes, {validados} validados, {rechazados} rechazados")
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'total': total,
                'pendientes': pendientes,
                'validados': validados,
                'rechazados': rechazados
            }
        })
        
    except Exception as e:
        print(f"❌ Error en estadisticas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@validar_avances_bp.route('/proyectos', methods=['GET'])
@login_required
def listar_proyectos():
    """
    API: Listar proyectos en estado 'Desarrollo Aceptado' (4) o 'En Ejecución' (6)
    Para filtro de selección en validación de avances
    """
    try:
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
        # Listar proyectos en estado 4 (Desarrollo Aceptado) o 6 (En Ejecución)
        query = Requerimiento.query.filter(
            Requerimiento.id_estado.in_([4, 6])
        )
        
        # Filtrar según nivel de acceso
        if not current_user.is_superadmin():
            query = query.filter(Requerimiento.id_recinto == current_user.recinto_id)
        
        proyectos = query.all()
        
        resultado = [
            {
                'id': p.id,
                'nombre': p.nombre,
                'estado': p.estado.nombre if p.estado else 'Sin estado'
            }
            for p in proyectos
        ]
        
        return jsonify({
            'success': True,
            'proyectos': resultado
        })
        
    except Exception as e:
        print(f"❌ Error en listar_proyectos: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@validar_avances_bp.route('/trabajadores', methods=['GET'])
@login_required
def listar_trabajadores():
    """
    API: Listar trabajadores con avances pendientes
    Para filtro de selección
    """
    try:
        # VERIFICAR PERMISOS
        if not (current_user.is_superadmin() or current_user.has_page_permission('/validar-avances')):
            return jsonify({'success': False, 'message': 'Sin permisos'}), 403
        
        # Query base
        query = db.session.query(
            Trabajador.id,
            Trabajador.nombre,
            Trabajador.email
        ).join(
            HistorialAvanceActividad, HistorialAvanceActividad.trabajador_id == Trabajador.id
        ).filter(
            HistorialAvanceActividad.validado == False
        ).distinct()
        
        # Filtrar según nivel de acceso
        if not current_user.is_superadmin():
            query = query.join(
                Requerimiento, HistorialAvanceActividad.requerimiento_id == Requerimiento.id
            ).filter(Requerimiento.id_recinto == current_user.recinto_id)
        
        trabajadores = query.all()
        
        resultado = [
            {
                'id': t.id,
                'nombre': t.nombre,
                'email': t.email
            }
            for t in trabajadores
        ]
        
        return jsonify({
            'success': True,
            'trabajadores': resultado
        })
        
    except Exception as e:
        print(f"❌ Error en listar_trabajadores: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
