#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para investigar por qué solo se procesa 1 proyecto de los 3 en all.xlsx
"""

import pandas as pd
import os

def investigar_proyectos_all_xlsx():
    """Investigar por qué solo se detecta 1 proyecto en lugar de 3"""
    
    print('🔍 Investigando proyectos en all.xlsx...')
    file_path = r'DOCS\Tip\all.xlsx'
    
    if not os.path.exists(file_path):
        print('❌ Archivo all.xlsx no encontrado')
        return
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        print(f'📊 Archivo original: {len(df)} filas')
        
        # Aplicar la misma limpieza que hace el sistema
        print('\n🧹 Aplicando limpieza de msproj11...')
        df_limpio = df[~(
            (df['Nivel de esquema'] == 1) & 
            (df['Nombre de tarea'].astype(str).str.lower() == 'msproj11')
        )]
        print(f'✅ Después de limpieza: {len(df_limpio)} filas')
        
        # Analizar proyectos de nivel 1 (proyectos principales)
        print('\n📋 Analizando proyectos de nivel de esquema = 1:')
        nivel_1 = df_limpio[df_limpio['Nivel de esquema'] == 1]
        
        if len(nivel_1) > 0:
            proyectos_unicos = nivel_1['Proyecto'].unique()
            print(f'📦 Proyectos únicos encontrados: {len(proyectos_unicos)}')
            
            for i, proyecto in enumerate(proyectos_unicos, 1):
                actividades_proyecto = nivel_1[nivel_1['Proyecto'] == proyecto]
                print(f'\n   {i}. Proyecto: "{proyecto}"')
                print(f'      Actividades nivel 1: {len(actividades_proyecto)}')
                
                # Mostrar detalles de las actividades de nivel 1
                for idx, row in actividades_proyecto.iterrows():
                    print(f'      - EDT: {row["EDT"]}, Nombre: "{row["Nombre de tarea"]}"')
                
                # Verificar filtro por nombre de archivo
                filename_without_ext = "all"  # Como hace el sistema
                nombre_tarea = str(actividades_proyecto.iloc[0]['Nombre de tarea'])
                
                if nombre_tarea.lower() != filename_without_ext.lower():
                    print(f'      ✅ Este proyecto SÍ aparecería para asignación')
                else:
                    print(f'      ❌ Este proyecto sería EXCLUIDO (coincide con archivo)')
        
        # Simular el filtro completo que aplica el sistema
        print('\n🎯 Simulando el filtro completo del sistema:')
        filename_without_ext = "all"
        
        proyectos_para_asignacion = []
        for index, row in df_limpio.iterrows():
            if row['Nivel de esquema'] == 1:
                nombre_tarea = str(row['Nombre de tarea'])
                
                # El filtro que aplica el sistema
                if nombre_tarea.lower() != filename_without_ext.lower():
                    # Crear proyecto_id único combinando nombre del proyecto y EDT
                    proyecto_id = f"{row['Proyecto']}_{str(row['EDT'])}"
                    proyecto_info = {
                        'proyecto_id': proyecto_id,
                        'edt': str(row['EDT']),
                        'nombre_tarea': nombre_tarea,
                        'proyecto': row['Proyecto']
                    }
                    # Evitar duplicados basado en proyecto_id
                    if not any(p['proyecto_id'] == proyecto_info['proyecto_id'] for p in proyectos_para_asignacion):
                        proyectos_para_asignacion.append(proyecto_info)
                    print(f'   ✅ Incluido: EDT {row["EDT"]}, "{nombre_tarea}" del proyecto "{row["Proyecto"]}"')
                else:
                    print(f'   ❌ Excluido: EDT {row["EDT"]}, "{nombre_tarea}" (coincide con archivo)')
        
        print(f'\n📊 Total proyectos que aparecerían para asignación: {len(proyectos_para_asignacion)}')
        
        if len(proyectos_para_asignacion) == 0:
            print('\n⚠️ PROBLEMA IDENTIFICADO: No hay proyectos disponibles para asignación')
            print('   Posibles causas:')
            print('   1. Todos los proyectos tienen nombres que coinciden con "all"')
            print('   2. Todos los proyectos ya están asignados a requerimientos')
            print('   3. El filtro está siendo demasiado restrictivo')
        elif len(proyectos_para_asignacion) < 3:
            print(f'\n⚠️ PROBLEMA PARCIAL: Solo {len(proyectos_para_asignacion)} proyectos disponibles de 3 esperados')
        else:
            print('\n✅ Los 3 proyectos deberían estar disponibles para asignación')
            
        # Mostrar todos los datos de nivel 1 para debug
        print('\n🔍 DEBUG - Todos los registros de nivel 1:')
        for idx, row in nivel_1.iterrows():
            print(f'   Fila {idx}: Proyecto="{row["Proyecto"]}", EDT={row["EDT"]}, Nombre="{row["Nombre de tarea"]}"')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    investigar_proyectos_all_xlsx()
