#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el procesamiento del nuevo formato Excel
donde los proyectos están definidos por Nivel de esquema = 1
"""

import pandas as pd

def test_nuevo_formato():
    """Simular el procesamiento del nuevo formato Excel"""
    
    # Simular datos del nuevo formato
    datos_ejemplo = [
        # Proyecto 1
        {'Nivel de esquema': 1, 'EDT': 1, 'Nombre de tarea': 'SISTEMA PROYECTO 01', 'Duración': '10 días', 'Comienzo': 'lun 01-01-24 8:00', 'Fin': 'vie 12-01-24 17:00', '% completado': 0, 'Predecesoras': '', 'Nombres de los recursos': ''},
        {'Nivel de esquema': 2, 'EDT': '1.1', 'Nombre de tarea': 'Análisis', 'Duración': '3 días', 'Comienzo': 'lun 01-01-24 8:00', 'Fin': 'mié 03-01-24 17:00', '% completado': 0, 'Predecesoras': '', 'Nombres de los recursos': 'Analista'},
        {'Nivel de esquema': 2, 'EDT': '1.2', 'Nombre de tarea': 'Diseño', 'Duración': '4 días', 'Comienzo': 'jue 04-01-24 8:00', 'Fin': 'mar 09-01-24 17:00', '% completado': 0, 'Predecesoras': '2', 'Nombres de los recursos': 'Diseñador'},
        {'Nivel de esquema': 2, 'EDT': '1.3', 'Nombre de tarea': 'Implementación', 'Duración': '3 días', 'Comienzo': 'mié 10-01-24 8:00', 'Fin': 'vie 12-01-24 17:00', '% completado': 0, 'Predecesoras': '3', 'Nombres de los recursos': 'Desarrollador'},
        
        # Proyecto 2  
        {'Nivel de esquema': 1, 'EDT': 2, 'Nombre de tarea': 'SISTEMA PROYECTO 02', 'Duración': '8 días', 'Comienzo': 'lun 15-01-24 8:00', 'Fin': 'mié 24-01-24 17:00', '% completado': 0, 'Predecesoras': '', 'Nombres de los recursos': ''},
        {'Nivel de esquema': 2, 'EDT': '2.1', 'Nombre de tarea': 'Requerimientos', 'Duración': '2 días', 'Comienzo': 'lun 15-01-24 8:00', 'Fin': 'mar 16-01-24 17:00', '% completado': 0, 'Predecesoras': '', 'Nombres de los recursos': 'Analista'},
        {'Nivel de esquema': 2, 'EDT': '2.2', 'Nombre de tarea': 'Desarrollo', 'Duración': '4 días', 'Comienzo': 'mié 17-01-24 8:00', 'Fin': 'lun 22-01-24 17:00', '% completado': 0, 'Predecesoras': '6', 'Nombres de los recursos': 'Desarrollador'},
        {'Nivel de esquema': 2, 'EDT': '2.3', 'Nombre de tarea': 'Pruebas', 'Duración': '2 días', 'Comienzo': 'mar 23-01-24 8:00', 'Fin': 'mié 24-01-24 17:00', '% completado': 0, 'Predecesoras': '7', 'Nombres de los recursos': 'Tester'},
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(datos_ejemplo)
    
    print("🔍 ANÁLISIS DEL NUEVO FORMATO")
    print("=" * 50)
    
    # Paso 1: Identificar proyectos (nivel 1)
    print("\n📋 PASO 1: Identificando proyectos (Nivel de esquema = 1)")
    proyectos_nivel1 = df[df['Nivel de esquema'] == 1]
    
    proyectos_map = {}  # EDT_proyecto -> Nombre_proyecto
    
    for _, proyecto_row in proyectos_nivel1.iterrows():
        edt_proyecto = str(proyecto_row['EDT'])
        nombre_proyecto = str(proyecto_row['Nombre de tarea'])
        proyectos_map[edt_proyecto] = nombre_proyecto
        print(f"   🎯 Proyecto detectado: EDT={edt_proyecto} → {nombre_proyecto}")
    
    # Paso 2: Asignar proyecto a cada actividad basado en su EDT
    def asignar_proyecto_por_edt(edt_actividad):
        """Asigna proyecto basado en el EDT de la actividad"""
        try:
            edt_partes = str(edt_actividad).split('.')
            edt_proyecto = edt_partes[0]  # Primer número es el proyecto
            return proyectos_map.get(edt_proyecto, f"Proyecto {edt_proyecto}")
        except:
            return "Proyecto Desconocido"
    
    print("\n📋 PASO 2: Asignando proyecto a cada actividad")
    df['_proyecto_inferido'] = df['EDT'].apply(asignar_proyecto_por_edt)
    
    # Mostrar resultado
    print("\n📊 RESULTADO FINAL:")
    for _, row in df.iterrows():
        nivel = "P" if row['Nivel de esquema'] == 1 else "A"
        print(f"   [{nivel}] EDT={row['EDT']:>4} | Proyecto: {row['_proyecto_inferido']:<20} | Tarea: {row['Nombre de tarea']}")
    
    # Paso 3: Verificar mapping correcto
    print("\n✅ VERIFICACIÓN DE MAPEO:")
    actividades_por_proyecto = df.groupby('_proyecto_inferido').size()
    for proyecto, cantidad in actividades_por_proyecto.items():
        print(f"   📁 {proyecto}: {cantidad} actividades")
    
    # Paso 4: Test específico para el problema reportado
    print("\n🎯 TEST ESPECÍFICO:")
    proyecto_b_row = df[df['Nombre de tarea'] == 'SISTEMA PROYECTO 02'].iloc[0]
    proyecto_b_actividades = df[df['_proyecto_inferido'] == 'SISTEMA PROYECTO 02']
    
    print(f"   • 'SISTEMA PROYECTO 02' tiene EDT: {proyecto_b_row['EDT']}")
    print(f"   • Actividades asignadas a 'SISTEMA PROYECTO 02': {len(proyecto_b_actividades)}")
    print(f"   • Lista de actividades:")
    for _, act in proyecto_b_actividades.iterrows():
        print(f"     - EDT={act['EDT']}: {act['Nombre de tarea']}")
    
    return True

if __name__ == "__main__":
    test_nuevo_formato()
