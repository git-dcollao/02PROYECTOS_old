#!/usr/bin/env python3
"""
Script para crear archivo Excel de prueba con múltiples proyectos
para validar la nueva arquitectura de eventos refactorizada
"""

import pandas as pd
from datetime import datetime, timedelta
import os

def crear_excel_multiple_proyectos():
    """Crea un Excel con múltiples proyectos para testing"""
    
    # Datos para el archivo Excel con MÚLTIPLES PROYECTOS
    actividades_data = [
        # PROYECTO 01 - Actividades
        {
            'EDT': '1',
            'Nombre de la tarea': 'PROYECTO 01',
            'Duración': '30 days',
            'Comienzo': '2025-01-15',
            'Fin': '2025-02-15',
            'Predecesores': '',
            'Nombres de los recursos': 'Equipo A'
        },
        {
            'EDT': '1.1',
            'Nombre de la tarea': 'Fase Inicial Proyecto 01',
            'Duración': '10 days',
            'Comienzo': '2025-01-15',
            'Fin': '2025-01-25',
            'Predecesores': '',
            'Nombres de los recursos': 'Juan'
        },
        {
            'EDT': '1.2',
            'Nombre de la tarea': 'Desarrollo Proyecto 01',
            'Duración': '15 days',
            'Comienzo': '2025-01-26',
            'Fin': '2025-02-10',
            'Predecesores': '1.1',
            'Nombres de los recursos': 'María'
        },
        {
            'EDT': '1.3',
            'Nombre de la tarea': 'Cierre Proyecto 01',
            'Duración': '5 days',
            'Comienzo': '2025-02-11',
            'Fin': '2025-02-15',
            'Predecesores': '1.2',
            'Nombres de los recursos': 'Carlos'
        },
        
        # PROYECTO 02 - Actividades
        {
            'EDT': '2',
            'Nombre de la tarea': 'PROYECTO 02',
            'Duración': '25 days',
            'Comienzo': '2025-02-01',
            'Fin': '2025-02-28',
            'Predecesores': '',
            'Nombres de los recursos': 'Equipo B'
        },
        {
            'EDT': '2.1',
            'Nombre de la tarea': 'Análisis Proyecto 02',
            'Duración': '8 days',
            'Comienzo': '2025-02-01',
            'Fin': '2025-02-08',
            'Predecesores': '',
            'Nombres de los recursos': 'Ana'
        },
        {
            'EDT': '2.2',
            'Nombre de la tarea': 'Implementación Proyecto 02',
            'Duración': '12 days',
            'Comienzo': '2025-02-09',
            'Fin': '2025-02-20',
            'Predecesores': '2.1',
            'Nombres de los recursos': 'Luis'
        },
        {
            'EDT': '2.3',
            'Nombre de la tarea': 'Testing Proyecto 02',
            'Duración': '5 days',
            'Comienzo': '2025-02-21',
            'Fin': '2025-02-28',
            'Predecesores': '2.2',
            'Nombres de los recursos': 'Pedro'
        }
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(actividades_data)
    
    # Nombre del archivo
    filename = 'test_multiple_projects.xlsx'
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    # Guardar como Excel
    df.to_excel(filepath, index=False, sheet_name='Actividades')
    
    print(f"✅ Archivo Excel creado: {filepath}")
    print(f"📊 Total actividades: {len(actividades_data)}")
    print(f"📋 Proyectos detectados esperados:")
    print(f"   • PROYECTO 01 (4 actividades)")
    print(f"   • PROYECTO 02 (4 actividades)")
    print(f"\n🎯 Use este archivo para probar la nueva arquitectura sin eventos submit")
    
    return filepath

if __name__ == "__main__":
    crear_excel_multiple_proyectos()