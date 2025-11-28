#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test para verificar el manejo correcto de la estructura jerárquica:
- Nivel esquema = 1: EDT = número entero (1, 2, 3...) → Nombre del PROYECTO
- Nivel esquema = 2: EDT = decimal (1.1, 1.2, 2.1...) → Nombre de TAREA/ACTIVIDAD
- Puede haber más niveles (3, 4...) con EDT como 1.1.1, 1.1.2, etc.
"""

import pandas as pd

def test_estructura_jerarquica():
    """Test completo de estructura jerárquica según especificación del usuario"""
    
    print("🏗️ TEST: ESTRUCTURA JERÁRQUICA DE PROYECTOS Y ACTIVIDADES")
    print("=" * 70)
    
    # Datos de ejemplo siguiendo la estructura especificada
    datos_jerarquicos = [
        # PROYECTO 1 (Nivel esquema = 1, EDT = número entero)
        {'Nivel de esquema': 1, 'EDT': 1, 'Nombre de tarea': 'SISTEMA DE GESTIÓN FINANCIERA'},
        
        # TAREAS/ACTIVIDADES del PROYECTO 1 (Nivel esquema = 2, EDT = 1.x)
        {'Nivel de esquema': 2, 'EDT': '1.1', 'Nombre de tarea': 'Análisis y Diseño'},
        {'Nivel de esquema': 2, 'EDT': '1.2', 'Nombre de tarea': 'Desarrollo Backend'},
        {'Nivel de esquema': 2, 'EDT': '1.3', 'Nombre de tarea': 'Desarrollo Frontend'},
        {'Nivel de esquema': 2, 'EDT': '1.4', 'Nombre de tarea': 'Pruebas e Integración'},
        
        # SUB-TAREAS (Nivel esquema = 3, EDT = 1.x.y) - opcional
        {'Nivel de esquema': 3, 'EDT': '1.1.1', 'Nombre de tarea': 'Análisis de Requerimientos'},
        {'Nivel de esquema': 3, 'EDT': '1.1.2', 'Nombre de tarea': 'Diseño de Arquitectura'},
        
        # PROYECTO 2 (Nivel esquema = 1, EDT = número entero)
        {'Nivel de esquema': 1, 'EDT': 2, 'Nombre de tarea': 'SISTEMA DE RECURSOS HUMANOS'},
        
        # TAREAS/ACTIVIDADES del PROYECTO 2 (Nivel esquema = 2, EDT = 2.x)
        {'Nivel de esquema': 2, 'EDT': '2.1', 'Nombre de tarea': 'Módulo de Empleados'},
        {'Nivel de esquema': 2, 'EDT': '2.2', 'Nombre de tarea': 'Módulo de Nóminas'},
        {'Nivel de esquema': 2, 'EDT': '2.3', 'Nombre de tarea': 'Reportes y Analytics'},
    ]
    
    df = pd.DataFrame(datos_jerarquicos)
    
    print("📊 DATOS DE ENTRADA:")
    print(df[['Nivel de esquema', 'EDT', 'Nombre de tarea']].to_string(index=False))
    print()
    
    # PASO 1: Identificar PROYECTOS (Nivel esquema = 1)
    print("🎯 PASO 1: IDENTIFICACIÓN DE PROYECTOS")
    proyectos_nivel1 = df[df['Nivel de esquema'] == 1]
    proyectos_map = {}
    
    print("   Proyectos encontrados:")
    for _, proyecto_row in proyectos_nivel1.iterrows():
        edt_proyecto = str(proyecto_row['EDT'])
        nombre_proyecto = str(proyecto_row['Nombre de tarea'])
        proyectos_map[edt_proyecto] = nombre_proyecto
        print(f"   • EDT={edt_proyecto} (entero) → '{nombre_proyecto}'")
    print()
    
    # PASO 2: Asignar proyecto a cada actividad según su EDT
    print("🔗 PASO 2: ASIGNACIÓN DE ACTIVIDADES A PROYECTOS")
    def asignar_proyecto_por_edt(edt_actividad):
        """Asigna proyecto basado en el primer número del EDT"""
        try:
            edt_partes = str(edt_actividad).split('.')
            edt_proyecto = edt_partes[0]  # Primer número = proyecto
            return proyectos_map.get(edt_proyecto, f"Proyecto {edt_proyecto}")
        except:
            return "Proyecto Desconocido"
    
    df['_proyecto_asignado'] = df['EDT'].apply(asignar_proyecto_por_edt)
    
    print("   Resultado de asignación:")
    for _, row in df.iterrows():
        nivel = row['Nivel de esquema']
        edt = row['EDT']
        nombre = row['Nombre de tarea']
        proyecto = row['_proyecto_asignado']
        tipo = "PROYECTO" if nivel == 1 else f"ACTIVIDAD (N{nivel})"
        print(f"   • {tipo:15} | EDT={str(edt):6} → Proyecto: {proyecto}")
    print()
    
    # PASO 3: Análisis por proyecto
    print("📋 PASO 3: ANÁLISIS POR PROYECTO")
    for proyecto_nombre in proyectos_map.values():
        actividades_proyecto = df[df['_proyecto_asignado'] == proyecto_nombre]
        print(f"\n   📁 {proyecto_nombre}:")
        print(f"      Total elementos: {len(actividades_proyecto)}")
        
        for nivel in sorted(actividades_proyecto['Nivel de esquema'].unique()):
            elementos_nivel = actividades_proyecto[actividades_proyecto['Nivel de esquema'] == nivel]
            if nivel == 1:
                print(f"      - Proyecto principal: {len(elementos_nivel)} elemento(s)")
            else:
                print(f"      - Actividades nivel {nivel}: {len(elementos_nivel)} elemento(s)")
                for _, elem in elementos_nivel.iterrows():
                    print(f"        * EDT={elem['EDT']} → {elem['Nombre de tarea']}")
    
    # PASO 4: Verificación de consistencia
    print("\n✅ PASO 4: VERIFICACIÓN DE CONSISTENCIA")
    
    # Verificar que todos los EDT de nivel 2+ empiecen con número de proyecto válido
    actividades = df[df['Nivel de esquema'] > 1]
    inconsistencias = 0
    
    for _, actividad in actividades.iterrows():
        edt_partes = str(actividad['EDT']).split('.')
        if len(edt_partes) > 1:
            edt_proyecto = edt_partes[0]
            if edt_proyecto not in proyectos_map:
                print(f"   ❌ INCONSISTENCIA: EDT={actividad['EDT']} no corresponde a ningún proyecto")
                inconsistencias += 1
    
    if inconsistencias == 0:
        print("   🎉 Estructura jerárquica CORRECTA - Todas las actividades están bien asignadas")
    else:
        print(f"   ⚠️  Se encontraron {inconsistencias} inconsistencias")
    
    # PASO 5: Simulación para el modal (solo proyectos nivel 1)
    print("\n🖼️  PASO 5: PROYECTOS PARA MOSTRAR EN MODAL")
    proyectos_para_modal = []
    
    for _, proyecto_row in proyectos_nivel1.iterrows():
        edt_proyecto = str(proyecto_row['EDT'])
        nombre_proyecto = str(proyecto_row['Nombre de tarea'])
        proyecto_id = f"{edt_proyecto}_{nombre_proyecto.replace(' ', '_')}"
        
        proyectos_para_modal.append({
            'edt': edt_proyecto,
            'nombre_tarea': nombre_proyecto,
            'proyecto_id': proyecto_id
        })
    
    print(f"   Total proyectos para modal: {len(proyectos_para_modal)}")
    for i, proyecto in enumerate(proyectos_para_modal, 1):
        print(f"   {i}. {proyecto['nombre_tarea']} (EDT={proyecto['edt']}, ID={proyecto['proyecto_id']})")
    
    return len(proyectos_para_modal) == 2  # Debe ser exactamente 2

if __name__ == "__main__":
    exito = test_estructura_jerarquica()
    print(f"\n{'✅ TEST EXITOSO' if exito else '❌ TEST FALLIDO'}")
