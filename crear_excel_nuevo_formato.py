#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Creador de archivo Excel en el NUEVO formato para pruebas
"""

import pandas as pd
from datetime import datetime

def crear_excel_nuevo_formato():
    """Crear archivo Excel con el nuevo formato jerárquico"""
    
    # Datos en el NUEVO formato (sin columna Proyecto)
    datos = [
        # Proyecto 1
        {
            'Nivel de esquema': 1, 
            'EDT': 1, 
            'Nombre de tarea': 'SISTEMA PROYECTO 01', 
            'Duración': '10 días', 
            'Comienzo': 'lun 01-01-24 8:00', 
            'Fin': 'vie 12-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '', 
            'Nombres de los recursos': '',
            'Días Corrido': 10
        },
        {
            'Nivel de esquema': 2, 
            'EDT': '1.1', 
            'Nombre de tarea': 'Análisis de Requerimientos', 
            'Duración': '3 días', 
            'Comienzo': 'lun 01-01-24 8:00', 
            'Fin': 'mié 03-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '', 
            'Nombres de los recursos': 'Analista Senior',
            'Días Corrido': 3
        },
        {
            'Nivel de esquema': 2, 
            'EDT': '1.2', 
            'Nombre de tarea': 'Diseño de Sistema', 
            'Duración': '4 días', 
            'Comienzo': 'jue 04-01-24 8:00', 
            'Fin': 'mar 09-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '2', 
            'Nombres de los recursos': 'Arquitecto de Software',
            'Días Corrido': 4
        },
        {
            'Nivel de esquema': 2, 
            'EDT': '1.3', 
            'Nombre de tarea': 'Implementación', 
            'Duración': '3 días', 
            'Comienzo': 'mié 10-01-24 8:00', 
            'Fin': 'vie 12-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '3', 
            'Nombres de los recursos': 'Desarrollador Full Stack',
            'Días Corrido': 3
        },
        
        # Proyecto 2  
        {
            'Nivel de esquema': 1, 
            'EDT': 2, 
            'Nombre de tarea': 'SISTEMA PROYECTO 02', 
            'Duración': '8 días', 
            'Comienzo': 'lun 15-01-24 8:00', 
            'Fin': 'mié 24-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '', 
            'Nombres de los recursos': '',
            'Días Corrido': 8
        },
        {
            'Nivel de esquema': 2, 
            'EDT': '2.1', 
            'Nombre de tarea': 'Levantamiento de Requerimientos', 
            'Duración': '2 días', 
            'Comienzo': 'lun 15-01-24 8:00', 
            'Fin': 'mar 16-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '', 
            'Nombres de los recursos': 'Analista de Negocio',
            'Días Corrido': 2
        },
        {
            'Nivel de esquema': 2, 
            'EDT': '2.2', 
            'Nombre de tarea': 'Desarrollo de Módulos', 
            'Duración': '4 días', 
            'Comienzo': 'mié 17-01-24 8:00', 
            'Fin': 'lun 22-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '6', 
            'Nombres de los recursos': 'Equipo Desarrollo',
            'Días Corrido': 4
        },
        {
            'Nivel de esquema': 2, 
            'EDT': '2.3', 
            'Nombre de tarea': 'Pruebas Integración', 
            'Duración': '2 días', 
            'Comienzo': 'mar 23-01-24 8:00', 
            'Fin': 'mié 24-01-24 17:00', 
            '% completado': 0, 
            'Real Anterior': '', 
            '% programado': 0, 
            '% Real': 0, 
            'Decimales': 2, 
            'Predecesoras': '7', 
            'Nombres de los recursos': 'QA Tester',
            'Días Corrido': 2
        },
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Guardar archivo Excel
    nombre_archivo = f"proyecto_nuevo_formato_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(nombre_archivo, index=False, engine='openpyxl')
    
    print(f"✅ Archivo Excel creado: {nombre_archivo}")
    print(f"📊 Estructura del archivo:")
    print(f"   • Columnas: {list(df.columns)}")
    print(f"   • Total filas: {len(df)}")
    print(f"   • Proyectos (nivel 1): {len(df[df['Nivel de esquema'] == 1])}")
    print(f"   • Actividades (nivel 2): {len(df[df['Nivel de esquema'] == 2])}")
    
    # Mostrar primeras filas
    print(f"\n📋 Primeras filas del archivo:")
    print(df[['Nivel de esquema', 'EDT', 'Nombre de tarea']].head(10))
    
    return nombre_archivo

if __name__ == "__main__":
    crear_excel_nuevo_formato()
