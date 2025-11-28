import pandas as pd
import os

# Crear un archivo Excel de prueba
data = {
    'Id': [1, 2, 3],
    'Nivel de esquema': [1, 2, 2],
    'EDT': ['1', '1.1', '1.2'],
    'Nombre de tarea': ['Proyecto Test', 'Fase 1', 'Fase 2'],
    'Duración': [30, 15, 15],
    'Comienzo': ['2024-01-01', '2024-01-01', '2024-01-16'],
    'Fin': ['2024-01-30', '2024-01-15', '2024-01-30'],
    'Predecesoras': ['', '', '2'],
    'Nombres de los recursos': ['Recurso1', 'Recurso1', 'Recurso2']
}

df = pd.DataFrame(data)
output_file = 'test_proyecto.xlsx'
df.to_excel(output_file, index=False)
print(f"Archivo de prueba creado: {output_file}")
print(f"Ruta completa: {os.path.abspath(output_file)}")