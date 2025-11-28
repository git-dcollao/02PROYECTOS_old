import pandas as pd
import os

def crear_plantilla_excel():
    """Crear archivo de plantilla Excel con el formato esperado"""
    
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
    
    # Ruta del archivo
    ruta_archivo = 'plantilla_proyecto_gantt.xlsx'
    
    # Guardar archivo Excel
    df.to_excel(ruta_archivo, index=False)
    
    print(f"Plantilla creada exitosamente: {ruta_archivo}")
    print("Estructura del archivo:")
    print(df.to_string(index=False))

if __name__ == "__main__":
    crear_plantilla_excel()
