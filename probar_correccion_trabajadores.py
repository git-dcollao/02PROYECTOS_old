#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la corrección de asignación de trabajadores
"""

import sys
import os

# Añadir el directorio del proyecto al path
sys.path.append('.')

from app import create_app
from app.models import Trabajador, AvanceActividad, ActividadProyecto, db
from app.controllers import crear_avances_actividad

def probar_correccion_trabajadores():
    """Probar la corrección en la asignación de trabajadores"""
    
    app = create_app()
    
    with app.app_context():
        print('🧪 Probando corrección de asignación de trabajadores...')
        print()
        
        # Buscar la actividad problemática (1.1.1)
        actividad_111 = ActividadProyecto.query.filter_by(edt='1.1.1').first()
        
        if not actividad_111:
            print('❌ No se encontró actividad con EDT 1.1.1')
            return
        
        print(f'📋 Actividad encontrada: ID {actividad_111.id}, EDT: {actividad_111.edt}')
        print()
        
        # Ver estado ANTES de la corrección
        print('📊 Estado ANTES de la corrección:')
        avances_antes = AvanceActividad.query.filter_by(actividad_id=actividad_111.id).all()
        
        for avance in avances_antes:
            trabajador = db.session.get(Trabajador, avance.trabajador_id)
            print(f'   - ID {trabajador.id}: "{trabajador.nombre}" ({avance.porcentaje_asignacion}%)')
        
        print(f'   Total trabajadores asignados: {len(avances_antes)}')
        print()
        
        # Aplicar la corrección
        recursos_correctos = "RECURSO AA[50%];RECURSO AB[25%];RECURSO AC[25%]"
        print(f'🛠️ Aplicando corrección con recursos: "{recursos_correctos}"')
        print()
        
        try:
            # Llamar a la función corregida
            requerimiento_id = avances_antes[0].requerimiento_id if avances_antes else 1
            
            nuevos_avances = crear_avances_actividad(
                requerimiento_id=requerimiento_id,
                actividad_id=actividad_111.id,
                recursos_string=recursos_correctos,
                progreso_actual=0.0
            )
            
            # Confirmar cambios
            db.session.commit()
            
            print('✅ Corrección aplicada exitosamente')
            print()
            
        except Exception as e:
            print(f'❌ Error durante la corrección: {e}')
            db.session.rollback()
            return
        
        # Ver estado DESPUÉS de la corrección
        print('📊 Estado DESPUÉS de la corrección:')
        avances_despues = AvanceActividad.query.filter_by(actividad_id=actividad_111.id).all()
        
        trabajadores_correctos = []
        for avance in avances_despues:
            trabajador = db.session.get(Trabajador, avance.trabajador_id)
            trabajadores_correctos.append(trabajador.id)
            print(f'   - ID {trabajador.id}: "{trabajador.nombre}" ({avance.porcentaje_asignacion}%)')
        
        print(f'   Total trabajadores asignados: {len(avances_despues)}')
        print()
        
        # Verificar que la corrección es exitosa
        trabajadores_esperados = [6, 7, 8]  # RECURSO AA, AB, AC
        
        print('🎯 Verificación del resultado:')
        if set(trabajadores_correctos) == set(trabajadores_esperados):
            print('   ✅ ¡CORRECCIÓN EXITOSA! Solo están asignados los trabajadores correctos')
            print(f'   ✅ Trabajadores esperados: {trabajadores_esperados}')
            print(f'   ✅ Trabajadores actuales: {trabajadores_correctos}')
        else:
            print('   ❌ La corrección no fue exitosa')
            print(f'   ❌ Trabajadores esperados: {trabajadores_esperados}')
            print(f'   ❌ Trabajadores actuales: {trabajadores_correctos}')
        
        # Verificar porcentajes
        print()
        print('📋 Verificación de porcentajes:')
        porcentajes_esperados = {6: 50.0, 7: 25.0, 8: 25.0}
        
        for avance in avances_despues:
            trabajador_id = avance.trabajador_id
            porcentaje_actual = avance.porcentaje_asignacion
            porcentaje_esperado = porcentajes_esperados.get(trabajador_id, 0)
            
            if porcentaje_actual == porcentaje_esperado:
                print(f'   ✅ Trabajador ID {trabajador_id}: {porcentaje_actual}% ✓')
            else:
                print(f'   ❌ Trabajador ID {trabajador_id}: {porcentaje_actual}% (esperado: {porcentaje_esperado}%)')

if __name__ == "__main__":
    probar_correccion_trabajadores()
