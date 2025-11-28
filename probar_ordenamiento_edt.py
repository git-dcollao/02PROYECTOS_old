#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el ordenamiento por EDT en el archivo all.xlsx
"""

import pandas as pd
import os

def probar_ordenamiento_edt():
    """Probar el ordenamiento de actividades por EDT"""
    print('🧪 Probando ordenamiento por EDT...')
    file_path = r'DOCS\Tip\all.xlsx'
    
    if not os.path.exists(file_path):
        print('❌ Archivo all.xlsx no encontrado')
        return
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        print(f'📊 Archivo: {len(df)} filas')
        
        # Identificar columna EDT
        edt_col = None
        for col in df.columns:
            if 'edt' in str(col).lower():
                edt_col = col
                break
        
        if not edt_col:
            print('❌ No se encontró columna EDT')
            return
        
        print(f'🔍 Columna EDT encontrada: "{edt_col}"')
        print()
        
        # Mostrar orden original
        print('📋 Orden ORIGINAL de EDTs:')
        for i, edt in enumerate(df[edt_col].head(15)):
            print(f'   {i+1:2d}. {edt}')
        print()
        
        # Función de ordenamiento (igual que la implementada)
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
        
        # Aplicar ordenamiento
        df_ordenado = df.copy()
        df_ordenado['_edt_sort'] = df_ordenado[edt_col].apply(ordenar_por_edt)
        df_ordenado = df_ordenado.sort_values('_edt_sort')
        df_ordenado = df_ordenado.drop('_edt_sort', axis=1)
        
        # Mostrar orden corregido
        print('📋 Orden CORREGIDO de EDTs:')
        for i, edt in enumerate(df_ordenado[edt_col].head(15)):
            print(f'   {i+1:2d}. {edt}')
        print()
        
        # Verificar que el ordenamiento es correcto
        edts_ordenados = df_ordenado[edt_col].tolist()
        
        # Validar que está en orden jerárquico
        print('✅ Verificando orden jerárquico:')
        orden_correcto = True
        for i in range(len(edts_ordenados) - 1):
            edt_actual = str(edts_ordenados[i])
            edt_siguiente = str(edts_ordenados[i + 1])
            
            # Convertir a tuplas para comparar
            tupla_actual = ordenar_por_edt(edt_actual)
            tupla_siguiente = ordenar_por_edt(edt_siguiente)
            
            if tupla_actual > tupla_siguiente:
                print(f'   ❌ Error: {edt_actual} debería ir después de {edt_siguiente}')
                orden_correcto = False
                break
        
        if orden_correcto:
            print('   🎉 ¡Ordenamiento jerárquico correcto!')
        
        # Mostrar estructura jerárquica
        print()
        print('🌳 Estructura jerárquica (primeros 20):')
        for edt in df_ordenado[edt_col].head(20):
            nivel = str(edt).count('.')
            indent = '  ' * nivel
            print(f'{indent}{edt}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    probar_ordenamiento_edt()
