#!/usr/bin/env python3
"""
Script simplificado para probar el procesamiento de Excel
"""

import os
import sys
import pandas as pd

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar la aplicación
os.environ['FLASK_ENV'] = 'development'

def analizar_archivo_excel():
    """Analizar el archivo all.xlsx directamente"""
    
    archivo_path = "DOCS/Tip/all.xlsx"
    
    if not os.path.exists(archivo_path):
        print(f"❌ Archivo no encontrado: {archivo_path}")
        return
        
    print("🔥 ANALIZANDO ARCHIVO EXCEL DIRECTAMENTE...")
    print(f"📄 Archivo: {archivo_path}")
    print()
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo_path)
        
        print(f"📊 Total de filas: {len(df)}")
        print(f"📊 Total de columnas: {len(df.columns)}")
        print()
        
        print("📋 COLUMNAS DISPONIBLES:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        print()
        
        # Buscar columna de proyecto
        proyecto_columna = None
        for col in df.columns:
            if 'proyecto' in str(col).lower():
                proyecto_columna = col
                break
                
        if proyecto_columna:
            print(f"✅ Columna de proyecto encontrada: '{proyecto_columna}'")
            proyectos_unicos = df[proyecto_columna].dropna().unique()
            print(f"📋 Proyectos únicos encontrados ({len(proyectos_unicos)}):")
            for i, proyecto in enumerate(proyectos_unicos, 1):
                count = len(df[df[proyecto_columna] == proyecto])
                print(f"  {i}. {proyecto} ({count} actividades)")
            print()
        else:
            print("❌ No se encontró columna de proyecto")
            print("📋 Buscando columnas similares...")
            for col in df.columns:
                if any(word in str(col).lower() for word in ['proy', 'name', 'nombre']):
                    sample_values = df[col].dropna().head(3).tolist()
                    print(f"  - {col}: {sample_values}")
            print()
            
        # Buscar columna EDT
        edt_columna = None
        for col in df.columns:
            if 'edt' in str(col).lower():
                edt_columna = col
                break
                
        if edt_columna:
            print(f"✅ Columna EDT encontrada: '{edt_columna}'")
            edts_sample = df[edt_columna].dropna().head(10).tolist()
            print(f"📋 Ejemplos de EDT: {edts_sample}")
        else:
            print("❌ No se encontró columna EDT")
            
        # Buscar columna de nombre de tarea
        nombre_tarea_columna = None
        for col in df.columns:
            if 'nombre' in str(col).lower() and 'tarea' in str(col).lower():
                nombre_tarea_columna = col
                break
                
        if nombre_tarea_columna:
            print(f"✅ Columna de nombre de tarea encontrada: '{nombre_tarea_columna}'")
            nombres_sample = df[nombre_tarea_columna].dropna().head(5).tolist()
            print(f"📋 Ejemplos de nombres: {nombres_sample}")
        else:
            print("❌ No se encontró columna de nombre de tarea")
            
        print()
        print("📋 PRIMERAS 10 FILAS DEL ARCHIVO:")
        print(df.head(10).to_string())
        
    except Exception as e:
        print(f"❌ Error al analizar archivo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analizar_archivo_excel()
