#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test para verificar que no se generen proyectos duplicados en el modal
"""

import pandas as pd

def test_deteccion_proyectos_unicos():
    """Simular la detección de proyectos para el modal sin duplicados"""
    
    # Simular datos del nuevo formato (igual que en el Excel creado)
    datos_excel = [
        # Proyecto 1 (nivel 1)
        {'Nivel de esquema': 1, 'EDT': 1, 'Nombre de tarea': 'SISTEMA PROYECTO 01', 'Duración': '10 días'},
        {'Nivel de esquema': 2, 'EDT': '1.1', 'Nombre de tarea': 'Análisis de Requerimientos', 'Duración': '3 días'},
        {'Nivel de esquema': 2, 'EDT': '1.2', 'Nombre de tarea': 'Diseño de Sistema', 'Duración': '4 días'},
        {'Nivel de esquema': 2, 'EDT': '1.3', 'Nombre de tarea': 'Implementación', 'Duración': '3 días'},
        
        # Proyecto 2 (nivel 1)
        {'Nivel de esquema': 1, 'EDT': 2, 'Nombre de tarea': 'SISTEMA PROYECTO 02', 'Duración': '8 días'},
        {'Nivel de esquema': 2, 'EDT': '2.1', 'Nombre de tarea': 'Levantamiento de Requerimientos', 'Duración': '2 días'},
        {'Nivel de esquema': 2, 'EDT': '2.2', 'Nombre de tarea': 'Desarrollo de Módulos', 'Duración': '4 días'},
        {'Nivel de esquema': 2, 'EDT': '2.3', 'Nombre de tarea': 'Pruebas Integración', 'Duración': '2 días'},
    ]
    
    df = pd.DataFrame(datos_excel)
    
    print("🔍 SIMULACIÓN DE DETECCIÓN DE PROYECTOS PARA MODAL")
    print("=" * 60)
    
    # PASO 1: Crear mapeo de proyectos (igual que en el código actualizado)
    proyectos_map = {}
    proyectos_nivel1 = df[df['Nivel de esquema'] == 1]
    
    for _, proyecto_row in proyectos_nivel1.iterrows():
        edt_proyecto = str(proyecto_row['EDT'])
        nombre_proyecto = str(proyecto_row['Nombre de tarea'])
        proyectos_map[edt_proyecto] = nombre_proyecto
    
    print(f"📋 Proyectos detectados en archivo:")
    for edt, nombre in proyectos_map.items():
        print(f"   • EDT={edt} → {nombre}")
    
    # PASO 2: Simular procesamiento para modal (SOLO nivel 1)
    proyectos_nuevos = []  # Esta es la lista que se envía al modal
    nombre_archivo_sin_extension = "proyecto_nuevo_formato_test"  # Simular nombre archivo
    
    print(f"\n🔍 PROCESAMIENTO PARA MODAL:")
    print(f"   Nombre archivo: {nombre_archivo_sin_extension}")
    
    for index, row in df.iterrows():
        # SOLO procesar filas de nivel 1 (proyectos)
        if row['Nivel de esquema'] == 1:
            nombre_tarea = str(row['Nombre de tarea'])
            edt = str(row['EDT'])
            
            print(f"\n   📝 Analizando: {nombre_tarea} (EDT={edt})")
            
            # Verificar si NO coincide con nombre de archivo
            coincide_archivo = nombre_tarea.lower() == nombre_archivo_sin_extension.lower()
            print(f"      ¿Coincide con archivo?: {coincide_archivo}")
            
            if not coincide_archivo:
                # NUEVA LÓGICA: usar EDT + nombre para ID único
                proyecto_id = f"{edt}_{nombre_tarea.replace(' ', '_')}"
                
                # Verificar duplicados EN LA SESIÓN
                proyecto_existente = any(p.get('proyecto_id') == proyecto_id for p in proyectos_nuevos)
                print(f"      ¿Ya existe en sesión?: {proyecto_existente}")
                
                # Simular verificación BD (asumimos que no están asignados)
                ya_asignado_bd = False  # En la aplicación real hace query a BD
                print(f"      ¿Ya asignado en BD?: {ya_asignado_bd}")
                
                # AGREGAR SOLO SI NO EXISTE
                if not proyecto_existente and not ya_asignado_bd:
                    proyecto_nuevo = {
                        'edt': edt,
                        'nombre_tarea': nombre_tarea,
                        'proyecto_id': proyecto_id,
                        'duracion': row['Duración']
                    }
                    proyectos_nuevos.append(proyecto_nuevo)
                    print(f"      ✅ AGREGADO al modal (ID: {proyecto_id})")
                else:
                    print(f"      ❌ NO agregado (duplicado o ya asignado)")
            else:
                print(f"      ⚠️ EXCLUIDO (coincide con archivo)")
    
    # RESULTADO FINAL
    print(f"\n📊 RESULTADO FINAL PARA MODAL:")
    print(f"   Total proyectos detectados: {len(proyectos_nuevos)}")
    
    if proyectos_nuevos:
        print(f"   Lista para mostrar en modal:")
        for i, proyecto in enumerate(proyectos_nuevos, 1):
            print(f"      {i}. {proyecto['nombre_tarea']} (EDT={proyecto['edt']}, ID={proyecto['proyecto_id']})")
    else:
        print(f"   ⚠️ No hay proyectos nuevos para asignar")
    
    # VERIFICACIÓN DE DUPLICADOS
    proyecto_ids = [p['proyecto_id'] for p in proyectos_nuevos]
    nombres_proyectos = [p['nombre_tarea'] for p in proyectos_nuevos]
    
    print(f"\n✅ VERIFICACIÓN DE DUPLICADOS:")
    print(f"   IDs únicos: {len(set(proyecto_ids))} de {len(proyecto_ids)}")
    print(f"   Nombres únicos: {len(set(nombres_proyectos))} de {len(nombres_proyectos)}")
    
    if len(set(proyecto_ids)) == len(proyecto_ids):
        print(f"   🎉 ¡SIN DUPLICADOS! El modal mostrará {len(proyectos_nuevos)} proyectos únicos")
    else:
        print(f"   ❌ ¡HAY DUPLICADOS! Revisar lógica")
        
    return proyectos_nuevos

if __name__ == "__main__":
    test_deteccion_proyectos_unicos()
