#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar el problema de asignación incorrecta de trabajadores
"""

import sys
import os

# Añadir el directorio del proyecto al path
sys.path.append('.')

from app import create_app
from app.models import Trabajador, AvanceActividad, ActividadProyecto, db
from sqlalchemy import text
import re

def diagnosticar_problema_trabajadores():
    """Diagnosticar por qué se están asignando trabajadores incorrectos"""
    
    app = create_app()
    
    with app.app_context():
        print('🔍 Diagnosticando problema de trabajadores...')
        print()
        
        # 1. Ver todos los trabajadores en la base de datos
        print('👥 Trabajadores en la base de datos:')
        trabajadores = Trabajador.query.all()
        for t in trabajadores:
            print(f'   ID {t.id}: "{t.nombre}" (corto: "{t.nombrecorto}")')
        print()
        
        # 2. Buscar la actividad problemática (1.1.1)
        print('📋 Buscando actividad 1.1.1...')
        actividad_111 = ActividadProyecto.query.filter_by(edt='1.1.1').first()
        
        if not actividad_111:
            print('❌ No se encontró actividad con EDT 1.1.1')
            return
        
        print(f'✅ Actividad encontrada: ID {actividad_111.id}, Nombre: "{actividad_111.nombre_tarea}"')
        print()
        
        # 3. Ver qué trabajadores están asignados a esta actividad
        print('🔗 Trabajadores asignados a la actividad 1.1.1:')
        avances = AvanceActividad.query.filter_by(actividad_id=actividad_111.id).all()
        
        trabajadores_asignados_ids = []
        for avance in avances:
            trabajador = Trabajador.query.get(avance.trabajador_id)
            trabajadores_asignados_ids.append(trabajador.id)
            print(f'   Trabajador ID {trabajador.id}: "{trabajador.nombre}" (asignación: {avance.porcentaje_asignacion}%)')
        
        print(f'   Total trabajadores asignados: {len(trabajadores_asignados_ids)}')
        print(f'   IDs asignados: {trabajadores_asignados_ids}')
        print()
        
        # 4. Simular el procesamiento de recursos
        recursos_string = "RECURSO AA[50%];RECURSO AB[25%];RECURSO AC[25%]"
        print(f'🧪 Simulando procesamiento de recursos: "{recursos_string}"')
        print()
        
        # Dividir recursos como lo hace la función
        recursos_lista = re.split(r'[,;]+', recursos_string)
        
        for i, recurso_item in enumerate(recursos_lista, 1):
            recurso_item = recurso_item.strip()
            print(f'   Recurso {i}: "{recurso_item}"')
            
            # Limpiar nombre como lo hace la función
            nombre_limpio = re.sub(r'\[.*?\]', '', recurso_item).strip()
            print(f'   Nombre limpio: "{nombre_limpio}"')
            
            # Buscar trabajadores como lo hace la función
            print('   Búsqueda en base de datos:')
            trabajadores_encontrados = Trabajador.query.filter(
                (Trabajador.nombre.ilike(f'%{nombre_limpio}%')) |
                (Trabajador.nombrecorto.ilike(f'%{nombre_limpio}%'))
            ).all()
            
            if trabajadores_encontrados:
                for t in trabajadores_encontrados:
                    print(f'     ✓ ID {t.id}: "{t.nombre}" (corto: "{t.nombrecorto}")')
            else:
                print(f'     ✗ Ningún trabajador encontrado para "{nombre_limpio}"')
            print()
        
        # 5. Verificar si hay trabajadores con nombres similares que puedan causar coincidencias falsas
        print('⚠️ Verificando posibles coincidencias falsas:')
        nombres_recursos = ["RECURSO AA", "RECURSO AB", "RECURSO AC"]
        
        for nombre in nombres_recursos:
            print(f'   Buscando coincidencias para "{nombre}":')
            
            # Simular las búsquedas que hace la función
            coincidencias_nombre = Trabajador.query.filter(Trabajador.nombre.ilike(f'%{nombre}%')).all()
            coincidencias_corto = Trabajador.query.filter(Trabajador.nombrecorto.ilike(f'%{nombre}%')).all()
            
            todas_coincidencias = list(set(coincidencias_nombre + coincidencias_corto))
            
            if todas_coincidencias:
                print(f'     Encontradas {len(todas_coincidencias)} coincidencias:')
                for t in todas_coincidencias:
                    print(f'       - ID {t.id}: "{t.nombre}" (corto: "{t.nombrecorto}")')
            else:
                print(f'     No se encontraron coincidencias')
        print()
        
        # 6. Recomendaciones
        print('💡 Análisis y recomendaciones:')
        
        # Verificar si los trabajadores 3,4,5 tienen nombres que podrían coincidir
        trabajadores_problema = [3, 4, 5]
        for id_trabajador in trabajadores_problema:
            t = Trabajador.query.get(id_trabajador)
            if t:
                print(f'   Trabajador ID {id_trabajador}: "{t.nombre}" (corto: "{t.nombrecorto}")')
                # Verificar si el nombre o nombre corto contiene alguna de las palabras clave
                for recurso in ["RECURSO AA", "RECURSO AB", "RECURSO AC"]:
                    if (recurso.lower() in t.nombre.lower() or 
                        recurso.lower() in t.nombrecorto.lower() or
                        t.nombre.lower() in recurso.lower() or
                        t.nombrecorto.lower() in recurso.lower()):
                        print(f'     ⚠️ POSIBLE COINCIDENCIA FALSA con "{recurso}"')

if __name__ == "__main__":
    diagnosticar_problema_trabajadores()
