"""
🎯 CONTROLADOR DE PROYECTOS
============================

Este controlador maneja toda la lógica relacionada con proyectos en ejecución,
incluyendo su gestión, finalización y seguimiento.

Responsabilidades:
- Gestión de proyectos en estado "En Desarrollo - Ejecución" (id_estado = 3)
- Finalización de proyectos (cambio a estado "Finalizado")
- Rechazo de proyectos (cambio a estado "Rechazado") 
- Completar información adicional de proyectos
- Gestión de etapas de proyectos

Estados que maneja:
- Estado 3: "En Desarrollo - Ejecución" (proyectos activos)
- Estado 4: "Finalizado" (proyectos completados exitosamente)
- Estado 9: "Rechazado" (proyectos rechazados)

Author: Sistema de Gestión de Proyectos
Date: Octubre 2025
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app.models import (
    Requerimiento, Sector, Recinto, TipoRecinto, Tipologia, Financiamiento, 
    TipoProyecto, Trabajador, Especialidad, Prioridad, Grupo, Estado,
    EquipoTrabajo, ObservacionRequerimiento, CustomRole, AdministradorRecinto,
    ActividadProyecto, AvanceActividad, db
)
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_
import pandas as pd
import os
import re
import time
from werkzeug.utils import secure_filename
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# 🔑 SOLUCIÓN PROGRAMADOR SENIOR: STORAGE PERSISTENTE CON FLASK SESSION
# ✅ FUNCIONES HELPER PARA GESTIONAR ACTIVIDADES TEMPORALES
def get_actividades_temp_storage():
    """Obtener storage de actividades temporales de la sesión"""
    if 'actividades_temp_storage' not in session:
        session['actividades_temp_storage'] = {}
        session.permanent = True  # Hacer la sesión persistente
        session.modified = True
    return session['actividades_temp_storage']

def set_actividades_temp_storage(user_id, actividades):
    """Guardar actividades temporales en la sesión"""
    storage = get_actividades_temp_storage()
    storage[str(user_id)] = actividades  # Convertir a string para JSON
    session['actividades_temp_storage'] = storage
    session.modified = True  # Marcar sesión como modificada

def clear_actividades_temp_storage(user_id):
    """Limpiar actividades temporales de un usuario"""
    storage = get_actividades_temp_storage()
    user_key = str(user_id)
    if user_key in storage:
        del storage[user_key]
        session['actividades_temp_storage'] = storage
        session.modified = True
        print(f"🧹 Variables temporales limpiadas para usuario {user_id}")

# Importar funciones del controlador principal
def parsear_fecha_espanol(fecha_str):
    """
    Parser de fechas en español mejorado con soporte para múltiples formatos
    Maneja tanto strings como objetos datetime de pandas/Excel
    """
    from datetime import datetime, date
    import pandas as pd
    
    if pd.isna(fecha_str) or fecha_str is None:
        return None
    
    # Si ya es un objeto datetime/date, convertir directamente
    if isinstance(fecha_str, (datetime, date)):
        return fecha_str.date() if isinstance(fecha_str, datetime) else fecha_str
    
    # Si es un timestamp de pandas, convertir
    if isinstance(fecha_str, pd.Timestamp):
        return fecha_str.date()
    
    # Convertir a string si no lo es
    fecha_str = str(fecha_str).strip()
    
    if not fecha_str or fecha_str.lower() in ['nan', 'nat', 'none', '']:
        return None
    
    # Lista de formatos soportados (más comunes primero)
    formatos = [
        '%Y-%m-%d',           # 2024-01-15
        '%d/%m/%Y',           # 15/01/2024
        '%d-%m-%Y',           # 15-01-2024
        '%m/%d/%Y',           # 01/15/2024 (formato US)
        '%Y/%m/%d',           # 2024/01/15
        '%d.%m.%Y',           # 15.01.2024
        '%Y.%m.%d',           # 2024.01.15
        '%Y-%m-%d %H:%M:%S',  # 2024-01-15 00:00:00 (con hora)
        '%d/%m/%Y %H:%M:%S',  # 15/01/2024 00:00:00
    ]
    
    # NUEVO: Intentar formato específico de MS Project: 'lun 25-08-25 8:30'
    try:
        # Extraer solo la parte de fecha, ignorando día de la semana y hora
        import re
        # Buscar patrón: día_semana dd-mm-yy hora (más flexible para días de semana)
        match = re.search(r'[a-záéíóú]{3,4}\s+(\d{1,2})-(\d{1,2})-(\d{2})\s+\d{1,2}:\d{2}', fecha_str.lower())
        if match:
            dia, mes, año = match.groups()
            # Convertir año de 2 dígitos a 4 dígitos (asumimos años 20xx)
            año_completo = f"20{año}"
            fecha_reformateada = f"{dia.zfill(2)}/{mes.zfill(2)}/{año_completo}"
            parsed_date = datetime.strptime(fecha_reformateada, '%d/%m/%Y')
            print(f"✅ Fecha MS Project parseada: '{fecha_str}' → {parsed_date.date()}")
            return parsed_date.date()
    except Exception as e:
        pass
    
    # Intentar parsear con cada formato
    for formato in formatos:
        try:
            parsed_date = datetime.strptime(fecha_str, formato)
            print(f"✅ Fecha parseada exitosamente: '{fecha_str}' → {parsed_date.date()} (formato: {formato})")
            return parsed_date.date()
        except ValueError:
            continue
    
    # Si llegamos aquí, no se pudo parsear
    print(f"❌ No se pudo parsear la fecha: '{fecha_str}' (tipo: {type(fecha_str)})")
    return None

def procesar_recursos_actividad(recursos_string):
    """Procesar recursos de una actividad y extraer trabajadores"""
    if not recursos_string:
        return []
    
    recursos_lista = []
    recursos_partes = str(recursos_string).split(',')
    
    for recurso in recursos_partes:
        recurso = recurso.strip()
        if recurso:
            recursos_lista.append({
                'nombre': recurso,
                'tipo': 'trabajador',
                'capacidad': 1.0
            })
    
    return recursos_lista

def crear_avances_actividad(requerimiento_id, actividad_id, recursos_string, progreso_actual=0.0):
    """Crear registros de avance para una actividad"""
    if not recursos_string:
        return
    
    # Procesar recursos separados por coma o punto y coma
    separadores = [',', ';']
    recursos_partes = []
    
    for sep in separadores:
        if sep in recursos_string:
            recursos_partes = str(recursos_string).split(sep)
            break
    
    # Si no hay separadores, tratar como un solo recurso
    if not recursos_partes:
        recursos_partes = [recursos_string]
    
    for recurso in recursos_partes:
        recurso = recurso.strip()
        if recurso:
            try:
                print(f"   🔍 Procesando recurso: '{recurso}'")
                
                # VERIFICACIÓN ROBUSTA: Buscar trabajador existente por nombrecorto Y por email
                trabajador = Trabajador.query.filter_by(nombrecorto=recurso).first()
                
                # Verificación adicional por email (en caso de que exista por email pero no por nombrecorto)
                email_esperado = f"{recurso.lower().replace(' ', '.')}@temp.com"
                trabajador_por_email = Trabajador.query.filter_by(email=email_esperado).first()
                
                # Si existe por email, usar ese trabajador
                if trabajador_por_email:
                    trabajador = trabajador_por_email
                    print(f"   ✅ Trabajador encontrado por EMAIL: ID {trabajador.id} - Email: {trabajador.email}")
                    print(f"      📝 Actualizando nombrecorto si es necesario: '{trabajador.nombrecorto}' → '{recurso}'")
                    # Actualizar nombrecorto si no coincide
                    if trabajador.nombrecorto != recurso:
                        trabajador.nombrecorto = recurso
                        db.session.flush()
                
                elif not trabajador:
                    print(f"   📝 Creando nuevo trabajador: '{recurso}' (no existe por nombrecorto ni email)")
                    
                    # Obtener sector_id y recinto_id del usuario logueado
                    from flask_login import current_user
                    usuario_sector_id = current_user.sector_id if hasattr(current_user, 'sector_id') else None
                    usuario_recinto_id = current_user.recinto_id if hasattr(current_user, 'recinto_id') else None
                    
                    print(f"      Heredando ubicación: sector_id={usuario_sector_id}, recinto_id={usuario_recinto_id}")
                    
                    trabajador = Trabajador(
                        nombre=f"Usuario {recurso}",  # Nombre genérico temporal - debe completarse después
                        nombrecorto=recurso,  # El recurso es el nombre corto
                        email=email_esperado,
                        rut=f"{hash(recurso) % 10000000}",  # Acortado para evitar "Data too long"
                        activo=True,
                        custom_role_id=3,  # Rol de usuario por defecto
                        sector_id=usuario_sector_id,  # Heredar del usuario logueado
                        recinto_id=usuario_recinto_id  # Heredar del usuario logueado
                    )
                    
                    # Establecer password por defecto "Maho2025"
                    trabajador.password = "Maho2025"
                    print(f"      Password asignado: Maho2025")
                    print(f"      Rol asignado: custom_role_id=3 (Usuario)")
                    print(f"      Nombre temporal: 'Usuario {recurso}', Nombre corto: '{recurso}'")
                    
                    try:
                        db.session.add(trabajador)
                        db.session.flush()  # Para obtener el ID
                        print(f"   ✅ Trabajador creado: ID {trabajador.id} (sector: {usuario_sector_id}, recinto: {usuario_recinto_id})")
                    except Exception as e:
                        print(f"   ❌ Error al crear trabajador: {str(e)}")
                        db.session.rollback()
                        # Buscar nuevamente por si se creó en otra transacción
                        trabajador = Trabajador.query.filter_by(nombrecorto=recurso).first() or \
                                   Trabajador.query.filter_by(email=email_esperado).first()
                        if trabajador:
                            print(f"   ✅ Trabajador encontrado tras error: ID {trabajador.id}")
                        else:
                            raise e
                else:
                    print(f"   ✅ Trabajador encontrado por NOMBRECORTO: ID {trabajador.id} (no se modifica nada)")
                
                # Verificar si ya existe un avance para esta combinación
                avance_existente = AvanceActividad.query.filter_by(
                    requerimiento_id=requerimiento_id,
                    actividad_id=actividad_id,
                    trabajador_id=trabajador.id
                ).first()
                
                if avance_existente:
                    print(f"   ⚠️ Ya existe avance para trabajador {trabajador.id} en actividad {actividad_id}")
                    continue
                
                # Crear registro de avance con campos correctos
                avance = AvanceActividad(
                    requerimiento_id=requerimiento_id,
                    actividad_id=actividad_id,
                    trabajador_id=trabajador.id,
                    porcentaje_asignacion=100.0,  # Por defecto 100%
                    progreso_actual=float(progreso_actual) if progreso_actual else 0.0,
                    progreso_anterior=0.0,
                    fecha_registro=datetime.now().date(),  # Obligatorio
                    observaciones=f'Recurso asignado automáticamente desde Excel: {recurso}'
                )
                db.session.add(avance)
                print(f"   ✅ Avance creado para trabajador '{trabajador.nombre}' (ID: {trabajador.id})")
                
            except Exception as e:
                print(f"   ❌ Error al crear avance para recurso '{recurso}': {str(e)}")
                import traceback
                traceback.print_exc()
                continue


# 🎯 BLUEPRINT DE PROYECTOS
proyectos_bp = Blueprint('proyectos', __name__)


# ==================================================================================
# 🎯 FUNCIONES AUXILIARES
# ==================================================================================

def verificar_permisos_proyecto(usuario=None):
    """
    Verifica los permisos del usuario para gestionar proyectos
    Usa la misma lógica que el controlador de requerimientos
    
    Returns:
        tuple: (is_superadmin, is_administrador, user_recinto_id)
    """
    if usuario is None:
        usuario = current_user
    
    # Verificar si es SUPERADMIN
    is_superadmin = usuario.is_superadmin()
    
    # Usar la misma lógica que requerimientos_controller para detectar administradores
    is_administrador = usuario.has_page_permission('/proyectos_aceptar') and not is_superadmin
    
    user_recinto_id = usuario.recinto_id if hasattr(usuario, 'recinto_id') else None
    
    return is_superadmin, is_administrador, user_recinto_id


def obtener_proyectos_por_permisos(is_superadmin, is_administrador, user_recinto_id):
    """
    Obtiene los proyectos filtrados según los permisos del usuario
    Solo retorna proyectos en estado "En Desarrollo - Ejecución" (id_estado = 3)
    
    Args:
        is_superadmin (bool): Si el usuario es superadmin
        is_administrador (bool): Si el usuario es administrador
        user_recinto_id (int): ID del recinto del usuario
        
    Returns:
        list: Lista de requerimientos/proyectos filtrados
    """
    base_query = Requerimiento.query.filter_by(id_estado=3).options(
        db.joinedload(Requerimiento.recinto),
        db.joinedload(Requerimiento.sector),
        db.joinedload(Requerimiento.estado),
        db.joinedload(Requerimiento.prioridad)
    )
    
    if is_superadmin:
        # SUPERADMIN ve todos los proyectos en ejecución
        return base_query.order_by(Requerimiento.fecha_aceptacion.desc()).all()
        
    elif is_administrador:
        # ADMINISTRADOR solo ve proyectos de sus recintos asignados
        recintos_asignados = AdministradorRecinto.obtener_recintos_administrador(current_user.id)
        print(f"🏢 Recintos asignados al administrador: {len(recintos_asignados) if recintos_asignados else 0}")
        
        if recintos_asignados:
            recinto_ids = [asignacion.recinto_id for asignacion in recintos_asignados]
            print(f"🏢 IDs de recintos asignados: {recinto_ids}")
            
            proyectos_filtrados = base_query.filter(
                Requerimiento.id_recinto.in_(recinto_ids)
            ).order_by(Requerimiento.fecha_aceptacion.desc()).all()
            
            print(f"📊 Proyectos encontrados para el administrador: {len(proyectos_filtrados)}")
            return proyectos_filtrados
        else:
            print("⚠️ Administrador sin recintos asignados")
            return []
    else:
        # Usuarios regulares solo ven proyectos de su recinto
        if user_recinto_id:
            return base_query.filter(
                Requerimiento.id_recinto == user_recinto_id
            ).order_by(Requerimiento.fecha_aceptacion.desc()).all()
        else:
            return []


def obtener_sectores_por_permisos(is_superadmin, is_administrador, user_recinto_id):
    """
    Obtiene los sectores disponibles según los permisos del usuario
    
    Returns:
        list: Lista de sectores filtrados
    """
    if is_superadmin:
        return Sector.query.filter_by(activo=True).all()
        
    elif is_administrador:
        recintos_asignados = AdministradorRecinto.obtener_recintos_administrador(current_user.id)
        if recintos_asignados:
            recinto_ids = [asignacion.recinto_id for asignacion in recintos_asignados]
            recintos = Recinto.query.filter(Recinto.id.in_(recinto_ids)).all()
            
            # Obtener sectores únicos de los recintos asignados
            sectores_ids = set()
            for recinto in recintos:
                if recinto.tiporecinto and recinto.tiporecinto.id_sector:
                    sectores_ids.add(recinto.tiporecinto.id_sector)
            
            if sectores_ids:
                return Sector.query.filter(
                    Sector.id.in_(sectores_ids), 
                    Sector.activo == True
                ).all()
            else:
                return []
        else:
            return []
    else:
        # Usuarios regulares solo ven sectores relacionados con su recinto
        if user_recinto_id and current_user.recinto:
            user_sector_id = (current_user.recinto.tiporecinto.id_sector 
                            if current_user.recinto.tiporecinto else None)
            if user_sector_id:
                return Sector.query.filter_by(id=user_sector_id, activo=True).all()
            else:
                return []
        else:
            return []


# ==================================================================================
# 🎯 RUTAS PRINCIPALES DE PROYECTOS
# ==================================================================================

@proyectos_bp.route('/proyectos_aceptar', endpoint='ruta_proyectos_aceptar')
@login_required
def proyectos_aceptar():
    """
    Vista principal para proyectos en estado "En Desarrollo - Ejecución"
    Permite gestionar proyectos que ya fueron aceptados y están en ejecución
    """
    try:
        start_time = time.time()
        print(f"🎯 CARGANDO PROYECTOS ACEPTAR - Usuario: {current_user.email}")
        
        # 1. Verificar permisos del usuario
        is_superadmin, is_administrador, user_recinto_id = verificar_permisos_proyecto()
        print(f"🔐 Permisos - Superadmin: {is_superadmin}, Administrador: {is_administrador}")
        print(f"👤 Usuario: {current_user.email}, Recinto ID: {user_recinto_id}")
        
        # Verificar qué permisos tiene el usuario
        tiene_permiso_proyectos = current_user.has_page_permission('/proyectos_aceptar')
        print(f"🔑 Permiso /proyectos_aceptar: {tiene_permiso_proyectos}")
        
        # 2. Obtener proyectos filtrados por permisos
        proyectos = obtener_proyectos_por_permisos(is_superadmin, is_administrador, user_recinto_id)
        print(f"📊 {len(proyectos)} proyectos en ejecución encontrados")
        
        # 3. Debug: Verificar cuántos requerimientos hay en estado 3 en total
        total_estado_3 = Requerimiento.query.filter_by(id_estado=3).count()
        print(f"🔍 Debug: Total de requerimientos en estado 3 (En Desarrollo): {total_estado_3}")
        
        # Debug: Ver en qué recintos están los requerimientos en estado 3
        reqs_estado_3 = Requerimiento.query.filter_by(id_estado=3).all()
        for req in reqs_estado_3:
            print(f"🔍 Requerimiento #{req.id} en estado 3, recinto_id: {req.id_recinto}")
        
        # 3. Obtener sectores disponibles según permisos
        sectores = obtener_sectores_por_permisos(is_superadmin, is_administrador, user_recinto_id)
        
        # 4. Renderizar template
        duration = time.time() - start_time
        print(f"✅ proyectos_aceptar cargado en {duration:.3f}s")
        print(f"📊 Enviando al template: {len(proyectos)} proyectos, {len(sectores)} sectores")
        
        # Debug: Mostrar información de los proyectos que se van a mostrar
        for proyecto in proyectos:
            print(f"🔍 Proyecto a mostrar: ID={proyecto.id}, Título='{proyecto.nombre}', Estado={proyecto.id_estado}")
        
        return render_template('projects/proyecto-aceptar.html',
                             requerimientos=proyectos,      # Para compatibilidad con otros templates
                             reqs_ejecucion=proyectos,      # Variable que espera el template
                             sectores=sectores,
                             total_proyectos=len(proyectos),
                             css_file='proyecto-aceptar.css')
        
    except Exception as e:
        print(f"❌ Error en proyectos_aceptar: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500


# ==================================================================================
# 🎯 ENDPOINTS DE GESTIÓN DE PROYECTOS
# ==================================================================================

@proyectos_bp.route('/update_proyecto_aceptar/<int:id>', methods=['POST'])
@login_required
def update_proyecto_aceptar(id):
    """
    Endpoint para finalizar un proyecto (cambiar estado a "Finalizado")
    Requiere observación obligatoria y registra en historial
    """
    try:
        # 1. Verificar permisos
        if not (current_user.is_superadmin() or current_user.has_page_permission('/proyectos_aceptar')):
            flash('No tiene permisos para finalizar proyectos', 'error')
            return redirect(url_for('proyectos.ruta_proyectos_aceptar'))
        
        # 2. Obtener proyecto y validar observación
        proyecto = Requerimiento.query.get_or_404(id)
        observacion_texto = request.form.get('observacion', '').strip()

        if not observacion_texto:
            flash('La observación es requerida para finalizar el proyecto', 'error')
            return redirect(url_for('proyectos.ruta_proyectos_aceptar'))

        # 3. Actualizar estado a "Finalizado"
        proyecto.id_estado = 4  # Estado: Finalizado
        proyecto.fecha_finalizacion = datetime.now()
        
        # 4. Actualizar observación
        if observacion_texto:
            proyecto.observacion = observacion_texto
        
        # 5. Registrar en historial de observaciones
        nueva_observacion = ObservacionRequerimiento(
            id_requerimiento=id,
            observacion=observacion_texto,
            fecha_registro=datetime.now(),
            id_usuario=current_user.id if current_user.is_authenticated else None,
            pagina_origen='proyectos_aceptar',
            tipo_evento='Finalizado'
        )
        db.session.add(nueva_observacion)
        
        db.session.commit()
        print(f"✅ Proyecto #{id} finalizado correctamente por {current_user.email}")
        flash('Proyecto finalizado correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al finalizar proyecto #{id}: {str(e)}")
        flash(f'Error al finalizar proyecto: {e}', 'error')
        
    return redirect(url_for('proyectos.ruta_proyectos_aceptar'))


@proyectos_bp.route('/update_proyecto_rechazar/<int:id>', methods=['POST'])
@login_required
def update_proyecto_rechazar(id):
    """
    Endpoint para rechazar un proyecto (cambiar estado a "Rechazado")
    Requiere observación obligatoria y registra en historial
    """
    try:
        # 1. Verificar permisos
        if not (current_user.is_superadmin() or current_user.has_page_permission('/proyectos_aceptar')):
            flash('No tiene permisos para rechazar proyectos', 'error')
            return redirect(url_for('proyectos.ruta_proyectos_aceptar'))
        
        # 2. Obtener proyecto y validar observación
        proyecto = Requerimiento.query.get_or_404(id)
        observacion_texto = request.form.get('observacion', '').strip()

        if not observacion_texto:
            flash('La observación es requerida para rechazar el proyecto', 'error')
            return redirect(url_for('proyectos.ruta_proyectos_aceptar'))

        # 3. Actualizar estado a "Rechazado"
        proyecto.id_estado = 9  # Estado: Rechazado
        proyecto.fecha_rechazo = datetime.now()
        
        # 4. Actualizar observación
        if observacion_texto:
            proyecto.observacion = observacion_texto
        
        # 5. Registrar en historial de observaciones
        nueva_observacion = ObservacionRequerimiento(
            id_requerimiento=id,
            observacion=observacion_texto,
            fecha_registro=datetime.now(),
            id_usuario=current_user.id if current_user.is_authenticated else None,
            pagina_origen='proyectos_aceptar',
            tipo_evento='Rechazado'
        )
        db.session.add(nueva_observacion)
        
        db.session.commit()
        print(f"✅ Proyecto #{id} rechazado correctamente por {current_user.email}")
        flash('Proyecto rechazado y actualizado correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al rechazar proyecto #{id}: {str(e)}")
        flash(f'Error al rechazar proyecto: {e}', 'error')
        
    return redirect(url_for('proyectos.ruta_proyectos_aceptar'))


# ==================================================================================
# 🎯 RUTAS FUTURAS (PARA EXPANSIÓN)
# ==================================================================================

# TODO: Implementar en futuras iteraciones
# - proyectos_completar(): Para completar información adicional
# - proyectos_etapas(): Para gestión de etapas de proyectos  
# - proyectos_seguimiento(): Para seguimiento de avances
# - proyectos_reportes(): Para generar reportes de proyectos

@proyectos_bp.route('/proyecto-llenar', endpoint='ruta_proyecto_llenar')
@login_required
def proyecto_llenar():
    """Página para subir archivos XLSX y asignar proyectos a requerimientos"""
    # Obtener requerimientos en estado = 4 (En Desarrollo Aceptado)
    requerimientos_disponibles = Requerimiento.query.filter_by(id_estado=4, activo=True).all()
    
    # Obtener requerimientos que ya tienen proyecto asignado  
    requerimientos_asignados = Requerimiento.query.filter(
        Requerimiento.id_estado == 4,
        Requerimiento.proyecto.isnot(None),
        Requerimiento.activo == True
    ).all()
    
    return render_template('projects/proyecto-llenar.html', 
                         requerimientos_disponibles=requerimientos_disponibles,
                         requerimientos_asignados=requerimientos_asignados)


@proyectos_bp.route('/procesar-proyecto-xlsx', methods=['POST'])
@login_required
def procesar_proyecto_xlsx():
    """Procesar archivo XLSX con información de proyecto"""
    print("🚨🚨🚨 FUNCIÓN PROCESAR_PROYECTO_XLSX INICIADA 🚨🚨🚨")
    print("🚨🚨🚨 VERSIÓN ACTUALIZADA CON DEBUGGING - CÓDIGO CORRECTO 🚨🚨🚨")
    try:
        # 🧹 LIMPIEZA DE ESTADO AL INICIO  
        user_id = current_user.id
        print(f"🚨🚨🚨 LIMPIANDO STORAGE PARA USUARIO {user_id} 🚨🚨🚨")
        clear_actividades_temp_storage(user_id)
        
        if 'archivo_xlsx' not in request.files:
            return jsonify({'success': False, 'message': 'No se seleccionó archivo'})
        
        archivo = request.files['archivo_xlsx']
        if archivo.filename == '':
            return jsonify({'success': False, 'message': 'No se seleccionó archivo'})
        
        if not archivo.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': 'El archivo debe ser Excel (.xlsx o .xls)'})
        
        # Leer el archivo Excel
        df = pd.read_excel(archivo)
        
        # Mostrar las columnas disponibles en el archivo para debugging
        columnas_disponibles = list(df.columns)
        print(f"Columnas disponibles en el archivo: {columnas_disponibles}")
        
        # Limpieza de datos: Eliminar tareas "msproj11" de nivel de esquema = 1
        filas_iniciales = len(df)
        
        # Identificar columnas para limpieza (búsqueda flexible)
        col_nivel_esquema = None
        col_nombre_tarea = None
        
        for col in columnas_disponibles:
            if 'nivel' in str(col).lower() and 'esquema' in str(col).lower():
                col_nivel_esquema = col
            elif 'nombre' in str(col).lower() and 'tarea' in str(col).lower():
                col_nombre_tarea = col
        
        # Validar columnas requeridas (más flexible con nombres) - NUEVO FORMATO SIN COLUMNA PROYECTO
        columnas_requeridas = ['Nivel de esquema', 'EDT', 'Nombre de tarea', 
                              'Duración', 'Comienzo', 'Fin', '% completado', 'Real Anterior', '% programado', '% Real', 'Decimales', 'Predecesoras', 'Nombres de los recursos', 'Días Corrido']
        
        # Crear mapeo de columnas más flexible
        mapeo_columnas = {}
        for col_req in columnas_requeridas:
            col_encontrada = None
            for col_disp in columnas_disponibles:
                # Comparación más flexible (sin distinguir mayúsculas/minúsculas y espacios)
                if col_req.lower().replace(' ', '') == str(col_disp).lower().replace(' ', ''):
                    col_encontrada = col_disp
                    break
                # Búsqueda por palabras clave
                elif col_req.lower() == 'id' and 'id' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'nivel' in col_req.lower() and 'nivel' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'edt' in col_req.lower() and 'edt' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'nombre' in col_req.lower() and 'tarea' in col_req.lower() and 'nombre' in str(col_disp).lower() and 'tarea' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'duración' in col_req.lower() and 'duraci' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'comienzo' in col_req.lower() and ('comienzo' in str(col_disp).lower() or 'inicio' in str(col_disp).lower()):
                    col_encontrada = col_disp
                    break
                elif col_req.lower() == 'fin' and ('fin' in str(col_disp).lower() or 'final' in str(col_disp).lower()):
                    col_encontrada = col_disp
                    break
                elif 'predecesora' in col_req.lower() and 'predecesora' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'recurso' in col_req.lower() and 'recurso' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                # Nota: Ya no necesitamos buscar columna 'Proyecto' en el nuevo formato
            
            if col_encontrada:
                mapeo_columnas[col_req] = col_encontrada
        
        columnas_faltantes = [col for col in columnas_requeridas if col not in mapeo_columnas]
        if columnas_faltantes:
            return jsonify({
                'success': False, 
                'message': f'El archivo debe contener las siguientes columnas requeridas:<br>' +
                          f'<strong>Columnas requeridas:</strong> {", ".join(columnas_requeridas)}<br>' +
                          f'<strong>Columnas encontradas:</strong> {", ".join(columnas_disponibles)}<br>' +
                          f'<strong>Columnas faltantes:</strong> {", ".join(columnas_faltantes)}<br><br>' +
                          f'<em>Nota: Las columnas pueden tener variaciones menores en mayúsculas/minúsculas y espacios.<br>' +
                          f'Ejemplo: "Nivel de Esquema", "nivel de esquema", "NivelDeEsquema" son válidos.</em>'
            })
        
        # Procesar datos
        proyectos_nuevos = []
        actividades_procesadas = 0
        
        # Obtener el nombre del archivo (sin extensión) para comparación
        nombre_archivo_sin_extension = archivo.filename.rsplit('.', 1)[0] if archivo.filename else ''
        print(f"Nombre del archivo (sin extensión): {nombre_archivo_sin_extension}")
        
        # IMPORTANTE: Ordenar DataFrame por EDT para procesar en orden jerárquico correcto
        def ordenar_por_edt(edt_str):
            """
            Función para ordenar correctamente los códigos EDT
            Convierte EDT como "1.2.3" en una tupla (1, 2, 3) para ordenamiento natural
            """
            try:
                # Convertir EDT a lista de números para ordenamiento natural
                partes = str(edt_str).split('.')
                return tuple(int(parte) for parte in partes)
            except (ValueError, AttributeError):
                # Si no se puede convertir, poner al final
                return (float('inf'),)
        
        # NUEVO FORMATO: Extraer proyectos desde filas con Nivel de esquema = 1
        print(f"📋 FASE 0: Analizando nuevo formato jerárquico...")
        
        # Crear mapeo de EDT de proyecto a nombre de proyecto
        proyectos_map = {}  # EDT_proyecto -> Nombre_proyecto
        
        edt_columna = mapeo_columnas['EDT']
        nivel_columna = mapeo_columnas['Nivel de esquema']
        nombre_columna = mapeo_columnas['Nombre de tarea']
        
        # Identificar proyectos (nivel 1)
        proyectos_nivel1 = df[df[nivel_columna] == 1]
        
        for _, proyecto_row in proyectos_nivel1.iterrows():
            edt_proyecto = str(proyecto_row[edt_columna])
            nombre_proyecto = str(proyecto_row[nombre_columna])
            proyectos_map[edt_proyecto] = nombre_proyecto
            print(f"   🎯 Proyecto detectado: EDT={edt_proyecto} → {nombre_proyecto}")
        
        if not proyectos_map:
            return jsonify({'success': False, 'message': 'No se encontraron proyectos (filas con Nivel de esquema = 1)'})
        
        # Función para asignar proyecto a cada actividad basado en su EDT
        def asignar_proyecto_por_edt(edt_actividad):
            """
            Asigna proyecto basado en el EDT de la actividad
            Ej: EDT="1.2.3" pertenece al proyecto con EDT="1"
            """
            try:
                edt_partes = str(edt_actividad).split('.')
                edt_proyecto = edt_partes[0]  # Primer número es el proyecto
                return proyectos_map.get(edt_proyecto, f"Proyecto {edt_proyecto}")
            except:
                return "Proyecto Desconocido"
        
        # Agregar columna de proyecto inferida al DataFrame
        df['_proyecto_inferido'] = df[edt_columna].apply(asignar_proyecto_por_edt)
        
        # Ordenar DataFrame por proyecto inferido y luego por EDT
        df_ordenado = df.copy()
        df_ordenado['_edt_sort'] = df_ordenado[edt_columna].apply(ordenar_por_edt)
        
        # ORDENAR PRIMERO POR PROYECTO INFERIDO, LUEGO POR EDT
        df_ordenado = df_ordenado.sort_values(['_proyecto_inferido', '_edt_sort'])
        df_ordenado = df_ordenado.drop('_edt_sort', axis=1)
        
        print(f"📋 FASE 1: Detectando proyectos disponibles para asignación...")
        print(f"   Ordenado por: Proyecto Inferido → EDT")
        print(f"   Proyectos encontrados: {list(proyectos_map.values())}")
        print(f"   Primeros 10 registros: {df_ordenado[['_proyecto_inferido', edt_columna]].head(10).values.tolist()}")
        
        # 🔑 INICIALIZAR STORAGE Y LISTA TEMPORAL
        user_id = current_user.id
        set_actividades_temp_storage(user_id, [])
        actividades_acumuladas = []  # Lista temporal para acumular actividades
        print(f"🔑 Storage inicializado para usuario {user_id}")
        print(f"🔄 DEBUG: Iniciando bucle de procesamiento de {len(df_ordenado)} filas...")
        
        # FASE 1: SOLO DETECTAR PROYECTOS Y GUARDAR ACTIVIDADES TEMPORALES
        total_filas = len(df_ordenado)
        print(f"📊 Procesando {total_filas} filas del DataFrame...")
        
        for index, row in df_ordenado.iterrows():
            print(f"🔄 DEBUG: Procesando fila {index + 1}/{total_filas} | Actividades acumuladas: {len(actividades_acumuladas)}")
            try:
                # Convertir fechas usando nuestro parser mejorado
                fecha_inicio_raw = row[mapeo_columnas['Comienzo']]
                fecha_fin_raw = row[mapeo_columnas['Fin']]
                
                fecha_inicio = parsear_fecha_espanol(fecha_inicio_raw)
                fecha_fin = parsear_fecha_espanol(fecha_fin_raw)
                
                if fecha_inicio is None:
                    fecha_inicio = datetime.now().date()
                if fecha_fin is None:
                    fecha_fin = datetime.now().date()
                
                # Procesar duración extrayendo solo números
                duracion_str = str(row[mapeo_columnas['Duración']]) if pd.notna(row[mapeo_columnas['Duración']]) else '0'
                duracion_match = re.search(r'\d+', duracion_str)
                duracion = int(duracion_match.group()) if duracion_match else 0
                
                # GUARDAR TODAS LAS ACTIVIDADES TEMPORALMENTE CON PROYECTO INFERIDO
                nueva_actividad = {
                    'edt': str(row[mapeo_columnas['EDT']]),
                    'nombre_tarea': str(row[mapeo_columnas['Nombre de tarea']]),
                    'nivel_esquema': int(row[mapeo_columnas['Nivel de esquema']]),
                    'proyecto': row['_proyecto_inferido'],  # USAR PROYECTO INFERIDO
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'duracion': duracion,
                    'predecesoras': str(row[mapeo_columnas['Predecesoras']]) if pd.notna(row[mapeo_columnas['Predecesoras']]) else '',
                    'recursos': str(row[mapeo_columnas['Nombres de los recursos']]) if pd.notna(row[mapeo_columnas['Nombres de los recursos']]) else ''
                }
                
                # Acumular actividad temporalmente (no guardar aún)
                actividades_acumuladas.append(nueva_actividad)
                
                # Log cada 20 actividades
                if len(actividades_acumuladas) % 20 == 0:
                    print(f"   📝 {len(actividades_acumuladas)} actividades acumuladas...")
                
                # IMPORTANTE: Detección de proyectos para asignación (SOLO nivel 1)
                if row[mapeo_columnas['Nivel de esquema']] == 1:
                    nombre_tarea = str(row[mapeo_columnas['Nombre de tarea']])
                    nombre_proyecto = row['_proyecto_inferido']  # USAR PROYECTO INFERIDO
                    edt = str(row[mapeo_columnas['EDT']])
                    
                    print(f"🔍 Analizando proyecto nivel 1:")
                    print(f"   - Nombre de tarea: '{nombre_tarea}'")
                    print(f"   - Proyecto: '{nombre_proyecto}'")
                    print(f"   - ¿Coincide con archivo?: {nombre_tarea.lower() == nombre_archivo_sin_extension.lower()}")
                    
                    # Verificar si el nombre de la tarea NO coincide con el nombre del archivo
                    if nombre_tarea.lower() != nombre_archivo_sin_extension.lower():
                        # CORREGIDO: Crear identificador único usando el EDT (que es único por proyecto)
                        proyecto_id = f"{edt}_{nombre_tarea.replace(' ', '_')}"
                        
                        # Verificar si este proyecto específico ya fue agregado EN ESTA SESIÓN
                        proyecto_existente = any(p.get('proyecto_id') == proyecto_id for p in proyectos_nuevos)
                        
                        # IMPORTANTE: Verificar si este proyecto específico ya está asignado EN LA BD
                        nombre_tarea_actual = str(row[mapeo_columnas['Nombre de tarea']])
                        print(f"   - Debug: Buscando en BD: '{nombre_tarea_actual}' (proyecto_id: {proyecto_id})")
                        
                        actividad_existente_nivel1 = ActividadProyecto.query.join(
                            Requerimiento, ActividadProyecto.requerimiento_id == Requerimiento.id
                        ).filter(
                            ActividadProyecto.nombre_tarea == nombre_tarea_actual,
                            ActividadProyecto.nivel_esquema == 1,
                            Requerimiento.id_estado == 4,
                            Requerimiento.activo == True
                        ).first()
                        
                        print(f"   - Verificando asignación: '{nombre_tarea_actual}' -> {'YA ASIGNADO' if actividad_existente_nivel1 else 'DISPONIBLE'}")
                        
                        # SOLO AGREGAR SI NO EXISTE EN SESIÓN Y NO ESTÁ YA ASIGNADO
                        if not proyecto_existente and not actividad_existente_nivel1:
                            proyectos_nuevos.append({
                                'edt': edt,
                                'nombre_tarea': nombre_tarea,
                                'proyecto': nombre_proyecto,  # Este es para mostrar agrupación
                                'proyecto_id': proyecto_id,
                                'duracion': duracion,
                                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                                'predecesoras': str(row[mapeo_columnas['Predecesoras']]) if pd.notna(row[mapeo_columnas['Predecesoras']]) else '',
                                'recursos': str(row[mapeo_columnas['Nombres de los recursos']]) if pd.notna(row[mapeo_columnas['Nombres de los recursos']]) else ''
                            })
                            print(f"✅ Proyecto agregado para asignación: '{nombre_tarea}' del proyecto '{nombre_proyecto}' (ID: {proyecto_id})")
                        elif proyecto_existente:
                            print(f"⚠️ Proyecto ya agregado en esta sesión: '{nombre_tarea}' del proyecto '{nombre_proyecto}' (ID: {proyecto_id})")
                        elif actividad_existente_nivel1:
                            req_asignado = actividad_existente_nivel1.requerimiento
                            print(f"⚠️ Proyecto ya asignado al requerimiento '{req_asignado.nombre}': '{nombre_tarea}'")
                    else:
                        print(f"⚠️ Proyecto excluido (coincide con archivo): {nombre_tarea}")
            except Exception as e:
                print(f"❌ Error en fila {index}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # � GUARDAR TODAS LAS ACTIVIDADES ACUMULADAS AL FINAL DEL LOOP
        print(f"💾 Guardando {len(actividades_acumuladas)} actividades en storage...")
        set_actividades_temp_storage(user_id, actividades_acumuladas)
        print(f"✅ Actividades guardadas exitosamente en storage para usuario {user_id}")
        
        # �📊 RESUMEN FINAL DEL PROCESAMIENTO
        storage = get_actividades_temp_storage()
        user_key = str(user_id)
        total_actividades_guardadas = len(storage.get(user_key, []))
        print(f"✅ BUCLE COMPLETADO: {total_actividades_guardadas} actividades guardadas en storage para usuario {user_id}")
        
        # Si hay proyectos nuevos para asignar, retornar JSON para el modal
        if proyectos_nuevos:
            # ⚠️ LIMPIEZA DE DUPLICADOS ROBUSTA ANTES DE ENVIAR AL MODAL
            print(f"🧹 Limpiando duplicados antes de enviar al modal...")
            print(f"   Proyectos antes de limpieza: {len(proyectos_nuevos)}")
            
            # Crear diccionario para eliminar duplicados por proyecto_id
            proyectos_unicos = {}
            for proyecto in proyectos_nuevos:
                proyecto_id = proyecto.get('proyecto_id')
                if proyecto_id not in proyectos_unicos:
                    proyectos_unicos[proyecto_id] = proyecto
                    print(f"   ✅ Mantenido: {proyecto['nombre_tarea']} (ID: {proyecto_id})")
                else:
                    print(f"   ❌ Duplicado eliminado: {proyecto['nombre_tarea']} (ID: {proyecto_id})")
            
            # Convertir de vuelta a lista
            proyectos_nuevos_limpios = list(proyectos_unicos.values())
            
            print(f"   Proyectos después de limpieza: {len(proyectos_nuevos_limpios)}")
            print(f"📊 Total proyectos ÚNICOS para asignación: {len(proyectos_nuevos_limpios)}")
            
            for i, proyecto in enumerate(proyectos_nuevos_limpios, 1):
                print(f"   {i}. '{proyecto['nombre_tarea']}' (Proyecto: {proyecto['proyecto']}, EDT: {proyecto['edt']})")
            
            # 🚨 CRÍTICO: GUARDAR ACTIVIDADES ANTES DEL RETURN
            print(f"💾 CRÍTICO: Guardando {len(actividades_acumuladas)} actividades antes de devolver modal...")
            set_actividades_temp_storage(user_id, actividades_acumuladas)
            
            # Verificación inmediata
            storage_check = get_actividades_temp_storage()
            actividades_check = storage_check.get(str(user_id), [])
            print(f"✅ CRÍTICO: Verificado - {len(actividades_check)} actividades guardadas en storage")
            print(f"🔍 CRÍTICO: Muestra de actividades guardadas: {actividades_check[:2] if actividades_check else 'ninguna'}")
            
            # Obtener requerimientos disponibles para asignación directa
            requerimientos_disponibles = Requerimiento.query.filter_by(
                id_estado=4, activo=True
            ).filter(Requerimiento.proyecto.is_(None)).all()
            
            # 🚀 FLUJO OPTIMIZADO: IR DIRECTO AL MODAL DE ASIGNACIONES
            # En lugar de mostrar modal de "seleccionar proyecto principal", 
            # vamos directo a asignar cada proyecto a su requerimiento
            return jsonify({
                'success': True,
                'message': f'Se detectaron {len(proyectos_nuevos_limpios)} proyectos. Asigna cada uno a su requerimiento.',
                'accion': 'mostrar_modal_asignaciones',  # Indicador para el frontend
                'proyectos_nuevos': proyectos_nuevos_limpios,  # CORREGIDO: cambiar a proyectos_nuevos
                'requerimientos_disponibles': [
                    {
                        'id': req.id, 
                        'titulo': f"REQ-{req.id}: {req.nombre}"  # CORREGIDO: usar req.nombre en lugar de req.titulo
                    }
                    for req in requerimientos_disponibles
                ]
            })
            
        # 🔍 DEBUG: Verificar storage antes de devolver respuesta
        debug_storage = get_actividades_temp_storage()
        debug_user_key = str(user_id)
        debug_actividades = debug_storage.get(debug_user_key, [])
        print(f"🔍 DEBUG PRE-RESPONSE: Usuario {user_id} tiene {len(debug_actividades)} actividades antes de response")
        print(f"🔍 DEBUG PRE-RESPONSE: Primeras 3 actividades: {debug_actividades[:3] if debug_actividades else 'ninguna'}")

        # 📊 SIN PROYECTOS NUEVOS - PROCESAMIENTO COMPLETADO
        print(f"📊 No se detectaron proyectos nuevos para asignación")
        storage = get_actividades_temp_storage()
        user_key = str(user_id)
        total_actividades = len(storage.get(user_key, []))
        print(f"💾 Total actividades procesadas: {total_actividades}")
        
        return jsonify({
            'success': True, 
            'message': f'Archivo Excel procesado correctamente. {total_actividades} actividades encontradas. No hay proyectos nuevos para asignar.',
            'proyectos_nuevos': [],  # CORREGIDO: usar proyectos_nuevos para consistencia con frontend
            'actividades_procesadas': total_actividades
        })
        
    except Exception as e:
        print(f"❌ Error procesando archivo Excel: {str(e)}")
        return jsonify({'success': False, 'message': f'Error procesando archivo: {str(e)}'})


@proyectos_bp.route('/guardar-asignaciones-proyecto', methods=['POST'])
@login_required
def guardar_asignaciones_proyecto():
    """Guardar las asignaciones de proyectos a requerimientos"""
    try:
        print(f"🚀 DEBUG INICIO: guardar_asignaciones_proyecto() iniciada")
        
        # 🔍 DEBUG: Verificar storage al inicio
        debug_user_id = current_user.id
        debug_storage = get_actividades_temp_storage()
        debug_user_key = str(debug_user_id)
        debug_actividades = debug_storage.get(debug_user_key, [])
        print(f"🔍 DEBUG INICIO: Usuario {debug_user_id} tiene {len(debug_actividades)} actividades al inicio")
        print(f"🔍 DEBUG INICIO: Primeras 3 actividades: {debug_actividades[:3] if debug_actividades else 'ninguna'}")
        
        # Verificar que sea una petición AJAX con datos JSON
        if not request.is_json:
            return jsonify({'success': False, 'message': 'Petición debe ser JSON'}), 400
        
        # Verificar autenticación específicamente
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Por favor, recarga la página e inicia sesión nuevamente'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Datos JSON requeridos'}), 400
            
        asignaciones = data.get('asignaciones', {})
        requerimiento_para_procesar = data.get('requerimiento_para_procesar', None)  # NUEVO: ID del requerimiento que procesará actividades
        
        if not asignaciones:
            return jsonify({'success': False, 'message': 'No hay asignaciones para guardar'})
        
        print(f"🎯 DEBUG: Asignaciones recibidas: {asignaciones}")
        print(f"🎯 DEBUG: Requerimiento para procesar actividades: {requerimiento_para_procesar}")
        
        # NUEVO: Crear mapeo de EDT a nombre de proyecto usando las actividades temporales
        user_id = current_user.id
        edt_to_proyecto = {}
        storage = get_actividades_temp_storage()
        user_key = str(user_id)
        actividades_temp = storage.get(user_key, [])
        
        print(f"🔍 DEBUG: Usuario {user_id} tiene {len(actividades_temp)} actividades temporales")
        
        if actividades_temp:
            for actividad in actividades_temp:
                if actividad.get('nivel_esquema') == 1:  # Solo proyectos nivel 1
                    edt = str(actividad.get('edt'))
                    proyecto = actividad.get('proyecto')
                    nombre_tarea = actividad.get('nombre_tarea')
                    # Crear clave compuesta: EDT|NombreTarea
                    clave_compuesta = f"{edt}|{nombre_tarea}"
                    if clave_compuesta not in edt_to_proyecto:
                        edt_to_proyecto[clave_compuesta] = proyecto
                        print(f"   🗺️ Mapeo creado: '{clave_compuesta}' → Proyecto '{proyecto}'")
        
        print(f"🗺️ DEBUG: Mapeo EDT|NombreTarea a Proyecto completo: {edt_to_proyecto}")
        print(f"🎯 DEBUG: Total actividades temporales disponibles: {len(actividades_temp)}")
        
        # Procesar cada asignación
        actividades_creadas = 0
        actividades_actualizadas = 0
        
        try:
            for edt_nombre_tarea, requerimiento_id in asignaciones.items():
                # Convertir clave compuesta a nombre de proyecto usando el mapeo
                nombre_proyecto_real = edt_to_proyecto.get(edt_nombre_tarea, None)
                
                if not nombre_proyecto_real:
                    print(f"   ⚠️ WARNING: No se encontró mapeo para '{edt_nombre_tarea}'")
                    # Fallback: extraer solo EDT y buscar primer proyecto con ese EDT
                    edt_solo = edt_nombre_tarea.split('|')[0] if '|' in edt_nombre_tarea else edt_nombre_tarea
                    for clave, proyecto in edt_to_proyecto.items():
                        if clave.startswith(f"{edt_solo}|"):
                            nombre_proyecto_real = proyecto
                            break
                    
                    if not nombre_proyecto_real:
                        print(f"   ❌ ERROR: No se pudo encontrar proyecto para '{edt_nombre_tarea}'")
                        continue
                
                print(f"   📋 Procesando asignación: '{edt_nombre_tarea}' → Proyecto '{nombre_proyecto_real}' → Requerimiento {requerimiento_id}")
                
                # Actualizar el requerimiento con el proyecto asignado
                requerimiento = Requerimiento.query.get(requerimiento_id)
                if requerimiento:
                    requerimiento.proyecto = nombre_proyecto_real  # Usar el nombre real del proyecto
                    
                    # NUEVO: Procesar actividades para TODOS los requerimientos asignados
                    procesar_actividades = True  # Simplificado: siempre procesar actividades
                    
                    print(f"   🔍 DEBUG: requerimiento_id={requerimiento_id}, ¿procesar?={procesar_actividades}")
                    
                    if procesar_actividades:
                        # ⚠️ NUEVO: Limpiar actividades existentes del requerimiento antes de procesar las nuevas
                        print(f"   🧹 Limpiando actividades existentes del requerimiento {requerimiento_id}...")
                        
                        # Primero eliminar registros relacionados (avance_actividad)
                        actividades_existentes = ActividadProyecto.query.filter_by(requerimiento_id=requerimiento_id).all()
                        actividades_eliminadas = len(actividades_existentes)
                        
                        for actividad_existente in actividades_existentes:
                            # Eliminar avances relacionados primero
                            avances = AvanceActividad.query.filter_by(actividad_id=actividad_existente.id).all()
                            for avance in avances:
                                db.session.delete(avance)
                            
                            # Luego eliminar la actividad
                            db.session.delete(actividad_existente)
                        
                        print(f"   🗑️ Eliminadas {actividades_eliminadas} actividades anteriores")
                        
                        # Guardar todas las actividades temporales de este proyecto
                        if actividades_temp:
                            for actividad_data in actividades_temp:
                                try:
                                    # Si la actividad pertenece a este proyecto (usando el nombre real del proyecto)
                                    if actividad_data.get('proyecto') == nombre_proyecto_real:
                                        print(f"      ✅ Creando actividad: EDT {actividad_data.get('edt')} - {actividad_data.get('nombre_tarea')}")
                                        
                                        # Convertir fechas desde formato string/GMT a date si es necesario
                                        fecha_inicio_date = actividad_data['fecha_inicio']
                                        fecha_fin_date = actividad_data['fecha_fin']
                                        
                                        # Si las fechas son strings (formato GMT), convertirlas
                                        if isinstance(fecha_inicio_date, str):
                                            try:
                                                from datetime import datetime
                                                # Parsear fecha GMT a datetime y extraer solo la fecha
                                                fecha_inicio_date = datetime.strptime(fecha_inicio_date.split(' GMT')[0], '%a, %d %b %Y %H:%M:%S').date()
                                            except:
                                                fecha_inicio_date = datetime.now().date()
                                                
                                        if isinstance(fecha_fin_date, str):
                                            try:
                                                from datetime import datetime
                                                # Parsear fecha GMT a datetime y extraer solo la fecha
                                                fecha_fin_date = datetime.strptime(fecha_fin_date.split(' GMT')[0], '%a, %d %b %Y %H:%M:%S').date()
                                            except:
                                                fecha_fin_date = datetime.now().date()
                                        
                                        # Crear nueva actividad (ya limpiamos las existentes)
                                        nueva_actividad = ActividadProyecto(
                                            requerimiento_id=requerimiento_id,
                                            edt=actividad_data['edt'],
                                            nombre_tarea=actividad_data['nombre_tarea'],
                                            nivel_esquema=actividad_data['nivel_esquema'],
                                            fecha_inicio=fecha_inicio_date,
                                            fecha_fin=fecha_fin_date,
                                            duracion=actividad_data['duracion'],
                                            predecesoras=actividad_data['predecesoras'],
                                            recursos=actividad_data['recursos']
                                        )
                                        db.session.add(nueva_actividad)
                                        db.session.flush()  # Para obtener el ID de la nueva actividad
                                        
                                        # Procesar y guardar recursos de la actividad
                                        recursos_procesados = procesar_recursos_actividad(actividad_data.get('recursos', ''))
                                        nueva_actividad.datos_adicionales = {
                                            'recursos_procesados': recursos_procesados
                                        }
                                        
                                        # Crear registros de avance_actividad para la nueva actividad
                                        progreso_actual = float(actividad_data.get('progreso', 0.0)) if actividad_data.get('progreso') else 0.0
                                        crear_avances_actividad(
                                            requerimiento_id=requerimiento_id,
                                            actividad_id=nueva_actividad.id,
                                            recursos_string=actividad_data.get('recursos', ''),
                                            progreso_actual=progreso_actual
                                        )
                                        
                                        actividades_creadas += 1
                                except Exception as e:
                                    logger.error(f"Error al procesar actividad {actividad_data.get('edt', 'desconocida')}: {str(e)}")
                                    continue

            # Confirmar cambios
            db.session.commit()
            
            # Limpiar trabajadores huérfanos después del procesamiento exitoso
            # TEMPORALMENTE DESHABILITADO POR ERROR
            # trabajadores_eliminados = limpiar_trabajadores_huerfanos()
            trabajadores_eliminados = 0
            
            logger.info(f"Procesamiento completado. Actividades creadas: {actividades_creadas}, Actividades actualizadas: {actividades_actualizadas}")
            
            # Limpiar actividades temporales del storage después de procesar
            clear_actividades_temp_storage(user_id)
            print(f"🧹 Actividades temporales limpiadas del storage para usuario {user_id}")
            
        except Exception as e:
            db.session.rollback()
            error_message = f"Error durante el procesamiento: {str(e)}"
            logger.error(error_message)
            return jsonify({'success': False, 'message': error_message})
        
        # Mensaje de éxito detallado - ÚNICO mensaje
        mensaje = 'Asignaciones guardadas exitosamente. '
        if actividades_creadas > 0:
            mensaje += f'Se crearon {actividades_creadas} actividades nuevas. '
        if actividades_actualizadas > 0:
            mensaje += f'Se actualizaron {actividades_actualizadas} actividades existentes.'
            
        return jsonify({'success': True, 'message': mensaje})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al guardar asignaciones: {str(e)}'})


@proyectos_bp.route('/ver-gantt-proyecto/<int:requerimiento_id>', endpoint='ver_gantt_proyecto')
@login_required
def ver_gantt_proyecto(requerimiento_id):
    """Ver el diagrama de Gantt de un proyecto"""
    requerimiento = Requerimiento.query.get_or_404(requerimiento_id)
    actividades_obj = ActividadProyecto.query.filter_by(
        requerimiento_id=requerimiento_id, activo=True
    ).order_by(ActividadProyecto.edt).all()
    
    # Convertir objetos SQLAlchemy a diccionarios para serialización JSON
    actividades = []
    for act in actividades_obj:
        actividades.append({
            'id': act.id,
            'edt': act.edt,
            'nombre_tarea': act.nombre_tarea,
            'nivel_esquema': act.nivel_esquema,
            'duracion': act.duracion,
            'fecha_inicio': act.fecha_inicio.strftime('%Y-%m-%d') if act.fecha_inicio else None,
            'fecha_inicio_display': act.fecha_inicio.strftime('%d/%m/%Y') if act.fecha_inicio else 'No definida',
            'fecha_fin': act.fecha_fin.strftime('%Y-%m-%d') if act.fecha_fin else None,
            'fecha_fin_display': act.fecha_fin.strftime('%d/%m/%Y') if act.fecha_fin else 'No definida',
            'progreso': float(act.progreso) if act.progreso else 0.0,
            'predecesoras': act.predecesoras or '',
            'recursos': act.recursos or '',
            'activo': act.activo
        })
    
    return render_template('gantt-proyecto.html', 
                         requerimiento=requerimiento,
                         actividades=actividades)

@proyectos_bp.route('/obtener-detalle-proyecto/<int:requerimiento_id>', endpoint='obtener_detalle_proyecto')
@login_required
def obtener_detalle_proyecto(requerimiento_id):
    """Obtener detalles de un proyecto vía AJAX"""
    try:
        actividades = ActividadProyecto.query.filter_by(
            requerimiento_id=requerimiento_id, activo=True
        ).order_by(ActividadProyecto.edt).all()
        
        actividades_data = []
        for act in actividades:
            actividades_data.append({
                'edt': act.edt,
                'nombre_tarea': act.nombre_tarea,
                'nivel_esquema': act.nivel_esquema,
                'duracion': act.duracion,
                'fecha_inicio': act.fecha_inicio.strftime('%d/%m/%Y') if act.fecha_inicio else 'No definida',
                'fecha_fin': act.fecha_fin.strftime('%d/%m/%Y') if act.fecha_fin else 'No definida',
                'progreso': float(act.progreso) if act.progreso else 0.0,
                'predecesoras': act.predecesoras or '',
                'recursos': act.recursos or ''
            })
        
        return jsonify({'success': True, 'actividades': actividades_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@proyectos_bp.route('/descargar-plantilla-gantt', methods=['GET'], endpoint='descargar_plantilla_gantt')
@login_required
def descargar_plantilla_gantt():
    """Descargar plantilla de ejemplo para archivos Gantt"""
    try:
        import tempfile
        import os
        from flask import send_file
        
        # Datos de ejemplo
        datos_ejemplo = {
            'Id': [1, 2, 3, 4, 5, 6, 7],
            'Nivel de esquema': [1, 2, 3, 3, 2, 3, 3],
            'EDT': ['1', '1.1', '1.1.1', '1.1.2', '1.2', '1.2.1', '1.2.2'],
            'Nombre de tarea': [
                'Proyecto Ejemplo',
                'Fase de Planificación',
                'Análisis de Requerimientos',
                'Diseño del Sistema',
                'Fase de Desarrollo',
                'Desarrollo Frontend',
                'Desarrollo Backend'
            ],
            'Duración': [100, 30, 10, 20, 70, 35, 35],
            'Comienzo': [
                '2025-01-01',
                '2025-01-01',
                '2025-01-01',
                '2025-01-11',
                '2025-01-31',
                '2025-01-31',
                '2025-02-15'
            ],
            'Fin': [
                '2025-04-30',
                '2025-01-30',
                '2025-01-10',
                '2025-01-30',
                '2025-04-30',
                '2025-02-14',
                '2025-04-30'
            ],
            'Predecesoras': ['', '', '', '3', '2', '4', '6'],
            'Nombres de los recursos': [
                'Equipo Completo',
                'Analista Senior',
                'Analista de Sistemas',
                'Arquitecto de Software',
                'Equipo Desarrollo',
                'Desarrollador Frontend',
                'Desarrollador Backend'
            ]
        }
        
        # Crear DataFrame
        df = pd.DataFrame(datos_ejemplo)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            
            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name='plantilla_proyecto_gantt_ejemplo.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    except Exception as e:
        flash(f'Error al generar plantilla: {str(e)}', 'error')
        return redirect(url_for('proyectos.ruta_proyecto_llenar'))

print("📘 Blueprint de proyectos cargado correctamente")