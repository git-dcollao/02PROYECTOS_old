#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas con la asignación de proyectos a requerimientos
"""

import sys
import os

# Añadir el directorio del proyecto al path
sys.path.append('.')

from app import create_app
from app.models import ActividadProyecto, Requerimiento, db

def diagnosticar_asignacion_proyectos():
    """Diagnosticar el estado de las asignaciones de proyectos"""
    
    app = create_app()
    
    with app.app_context():
        print('🔍 Diagnosticando asignación de proyectos del archivo all.xlsx...')
        print()
        
        # 1. Verificar actividades temporales que se procesaron
        print('📋 Actividades del archivo all.xlsx procesadas:')
        actividades_all = ActividadProyecto.query.filter(
            ActividadProyecto.edt.like('1%') | 
            ActividadProyecto.edt.like('2%') | 
            ActividadProyecto.edt.like('3%')
        ).all()
        
        if actividades_all:
            print(f'   Total actividades encontradas: {len(actividades_all)}')
            
            # Agrupar por proyecto principal
            proyectos = {}
            for actividad in actividades_all:
                proyecto_principal = actividad.edt.split('.')[0]
                if proyecto_principal not in proyectos:
                    proyectos[proyecto_principal] = []
                proyectos[proyecto_principal].append(actividad)
            
            for proyecto, actividades in proyectos.items():
                print(f'   📦 Proyecto {proyecto}: {len(actividades)} actividades')
                requerimiento_id = actividades[0].requerimiento_id if actividades else None
                if requerimiento_id:
                    requerimiento = db.session.get(Requerimiento, requerimiento_id)
                    if requerimiento:
                        print(f'       → Asignado a requerimiento ID {requerimiento_id}: "{requerimiento.nombre}"')
                    else:
                        print(f'       → Asignado a requerimiento ID {requerimiento_id} (no encontrado)')
                else:
                    print(f'       → ⚠️ Sin asignar a requerimiento')
        else:
            print('   ❌ No se encontraron actividades del archivo all.xlsx')
        print()
        
        # 2. Verificar requerimientos disponibles
        print('📋 Requerimientos disponibles para asignación:')
        requerimientos = Requerimiento.query.filter_by(activo=True).all()
        
        if requerimientos:
            for req in requerimientos:
                actividades_asignadas = ActividadProyecto.query.filter_by(requerimiento_id=req.id).count()
                print(f'   ID {req.id}: "{req.nombre}" ({actividades_asignadas} actividades asignadas)')
        else:
            print('   ❌ No se encontraron requerimientos activos')
        print()
        
        # 3. Verificar si hay proyectos sin asignar
        print('🔍 Verificando proyectos procesados pero sin asignar:')
        
        # Los proyectos del all.xlsx deberían ser: SISTEMA PROYECTO 01, 02, 03
        proyectos_esperados = ['1', '2', '3']  # EDTs principales
        
        for proyecto_edt in proyectos_esperados:
            actividades_proyecto = ActividadProyecto.query.filter(
                ActividadProyecto.edt.like(f'{proyecto_edt}%')
            ).all()
            
            if actividades_proyecto:
                requerimiento_asignado = actividades_proyecto[0].requerimiento_id
                print(f'   Proyecto EDT {proyecto_edt}: {len(actividades_proyecto)} actividades')
                
                if requerimiento_asignado:
                    requerimiento = db.session.get(Requerimiento, requerimiento_asignado)
                    print(f'     ✅ Asignado a: "{requerimiento.nombre if requerimiento else "Requerimiento no encontrado"}"')
                else:
                    print(f'     ⚠️ NO ASIGNADO - Necesita asignación manual')
            else:
                print(f'   Proyecto EDT {proyecto_edt}: ❌ No se encontraron actividades')
        print()
        
        # 4. Verificar si hay problemas de estructura
        print('🔧 Verificando posibles problemas:')
        
        # Actividades huérfanas (sin requerimiento)
        actividades_huerfanas = ActividadProyecto.query.filter_by(requerimiento_id=None).count()
        if actividades_huerfanas > 0:
            print(f'   ⚠️ {actividades_huerfanas} actividades sin requerimiento asignado')
        
        # Requerimientos sin proyecto asignado
        requerimientos_sin_proyecto = Requerimiento.query.filter(
            (Requerimiento.proyecto == None) | (Requerimiento.proyecto == '')
        ).count()
        if requerimientos_sin_proyecto > 0:
            print(f'   ⚠️ {requerimientos_sin_proyecto} requerimientos sin proyecto asignado')
        
        if actividades_huerfanas == 0 and requerimientos_sin_proyecto == 0:
            print('   ✅ No se detectaron problemas estructurales')

if __name__ == "__main__":
    diagnosticar_asignacion_proyectos()
