import pandas as pd
import os

# Crear un DataFrame de prueba con el formato correcto
data = {
    'Nivel de esquema': [1, 2, 3, 3, 1, 2, 3],
    'EDT': ['1', '1.1', '1.1.1', '1.1.2', '2', '2.1', '2.1.1'],
    'Nombre de tarea': ['PROYECTO 01', 'Fase 1', 'Actividad 1.1', 'Actividad 1.2', 'PROYECTO 02', 'Fase 2', 'Actividad 2.1'],
    'Duración': ['10 días', '5 días', '2 días', '3 días', '8 días', '4 días', '2 días'],
    'Comienzo': ['01/12/2024', '01/12/2024', '01/12/2024', '03/12/2024', '15/12/2024', '15/12/2024', '15/12/2024'],
    'Fin': ['15/12/2024', '05/12/2024', '02/12/2024', '05/12/2024', '25/12/2024', '18/12/2024', '16/12/2024'],
    '% completado': [0, 0, 0, 0, 0, 0, 0],
    'Real Anterior': [0, 0, 0, 0, 0, 0, 0],
    '% programado': [0, 0, 0, 0, 0, 0, 0],
    '% Real': [0, 0, 0, 0, 0, 0, 0],
    'Decimales': [2, 2, 2, 2, 2, 2, 2],
    'Predecesoras': ['', '', '', '3', '', '', ''],
    'Nombres de los recursos': ['', 'Juan Pérez', 'María García', 'Carlos López', '', 'Ana Martín', 'Luis Rodríguez'],
    'Días Corrido': [10, 5, 2, 3, 8, 4, 2]
}

df = pd.DataFrame(data)

# Guardar como Excel
output_path = 'test_gantt.xlsx'
df.to_excel(output_path, index=False)

print(f"✅ Archivo de prueba creado: {output_path}")
print("📋 Estructura del archivo:")
print(df.to_string(index=False))