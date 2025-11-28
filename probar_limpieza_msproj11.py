#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la limpieza de tareas msproj11 en el archivo all.xlsx
"""

import pandas as pd
import os
import sys

def probar_limpieza_msproj11():
    """Simular la limpieza que se haría en el controlador"""
    print('🧪 Probando limpieza de tareas "msproj11"...')
    file_path = r'DOCS\Tip\all.xlsx'
    
    if not os.path.exists(file_path):
        print('❌ Archivo all.xlsx no encontrado')
        return
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        print(f'📊 Archivo original: {len(df)} filas')
        print(f'📋 Columnas: {list(df.columns)}')
        print()
        
        # Identificar columnas
        col_nivel_esquema = None
        col_nombre_tarea = None
        col_proyecto = None
        
        columnas_disponibles = list(df.columns)
        for col in columnas_disponibles:
            if 'nivel' in str(col).lower() and 'esquema' in str(col).lower():
                col_nivel_esquema = col
            elif 'nombre' in str(col).lower() and 'tarea' in str(col).lower():
                col_nombre_tarea = col
            elif 'proyecto' in str(col).lower():
                col_proyecto = col
        
        print(f'🔍 Columnas identificadas:')
        print(f'   - Nivel de esquema: "{col_nivel_esquema}"')
        print(f'   - Nombre de tarea: "{col_nombre_tarea}"')
        print(f'   - Proyecto: "{col_proyecto}"')
        print()
        
        # Análisis antes de limpieza
        if col_nivel_esquema and col_nombre_tarea:
            print('📈 Estado ANTES de la limpieza:')
            print(f'   Nivel de esquema = 1: {len(df[df[col_nivel_esquema] == 1])} filas')
            msproj11_total = df[df[col_nombre_tarea].astype(str).str.lower() == 'msproj11']
            print(f'   Tareas "msproj11" (todos niveles): {len(msproj11_total)} filas')
            
            msproj11_nivel1 = df[
                (df[col_nivel_esquema] == 1) & 
                (df[col_nombre_tarea].astype(str).str.lower() == 'msproj11')
            ]
            print(f'   Tareas "msproj11" nivel 1: {len(msproj11_nivel1)} filas')
            
            if len(msproj11_nivel1) > 0:
                print(f'   📋 Detalles de tareas msproj11 nivel 1:')
                for idx, row in msproj11_nivel1.iterrows():
                    proyecto = row[col_proyecto] if col_proyecto else 'N/A'
                    print(f'      - Fila {idx}: Proyecto="{proyecto}", Nombre="{row[col_nombre_tarea]}", Nivel={row[col_nivel_esquema]}')
            print()
            
            # Aplicar limpieza
            filas_iniciales = len(df)
            
            if len(msproj11_nivel1) > 0:
                print(f'🧹 Aplicando limpieza...')
                
                # Eliminar las filas problemáticas
                df_limpio = df[~(
                    (df[col_nivel_esquema] == 1) & 
                    (df[col_nombre_tarea].astype(str).str.lower() == 'msproj11')
                )]
                
                filas_despues = len(df_limpio)
                print(f'✅ Limpieza completada: {filas_iniciales} → {filas_despues} filas')
                print(f'   Eliminadas: {filas_iniciales - filas_despues} filas')
                print()
                
                # Análisis después de limpieza
                print('📈 Estado DESPUÉS de la limpieza:')
                print(f'   Nivel de esquema = 1: {len(df_limpio[df_limpio[col_nivel_esquema] == 1])} filas')
                msproj11_despues = df_limpio[df_limpio[col_nombre_tarea].astype(str).str.lower() == 'msproj11']
                print(f'   Tareas "msproj11" (todos niveles): {len(msproj11_despues)} filas')
                
                msproj11_nivel1_despues = df_limpio[
                    (df_limpio[col_nivel_esquema] == 1) & 
                    (df_limpio[col_nombre_tarea].astype(str).str.lower() == 'msproj11')
                ]
                print(f'   Tareas "msproj11" nivel 1: {len(msproj11_nivel1_despues)} filas')
                
                if len(msproj11_nivel1_despues) == 0:
                    print('   🎉 ¡Limpieza exitosa! No quedan tareas msproj11 de nivel 1')
                else:
                    print('   ⚠️ Aún quedan tareas msproj11 de nivel 1')
                
                # Mostrar proyectos que aparecerían para asignación
                print()
                print('📦 Proyectos que aparecerían para asignación:')
                proyectos_nivel1 = df_limpio[df_limpio[col_nivel_esquema] == 1]
                if col_proyecto:
                    proyectos_unicos = proyectos_nivel1[col_proyecto].unique()
                    for i, proyecto in enumerate(proyectos_unicos, 1):
                        print(f'   {i}. "{proyecto}"')
                else:
                    print('   ⚠️ No se puede mostrar proyectos (columna Proyecto no encontrada)')
                    
            else:
                print('ℹ️ No se encontraron tareas "msproj11" de nivel 1 para limpiar')
                
        else:
            print('❌ No se pudieron identificar las columnas necesarias')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    probar_limpieza_msproj11()
