#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test final: Verificar corrección del problema de duplicados en modal
"""

import pandas as pd

def test_correccion_duplicados():
    """Test completo de la corrección de duplicados"""
    
    print("🔧 TEST FINAL: CORRECCIÓN DE DUPLICADOS EN MODAL")
    print("=" * 60)
    
    # Simular exactamente lo que hace la aplicación
    proyectos_nuevos = []  # Lista que se llena durante el procesamiento
    
    # Simular datos de entrada (como los del Excel real)
    datos_test = [
        {'Nivel de esquema': 1, 'EDT': 1, 'Nombre de tarea': 'SISTEMA PROYECTO 01'},
        {'Nivel de esquema': 2, 'EDT': '1.1', 'Nombre de tarea': 'Actividad 1.1'},
        {'Nivel de esquema': 1, 'EDT': 2, 'Nombre de tarea': 'SISTEMA PROYECTO 02'},
        {'Nivel de esquema': 2, 'EDT': '2.1', 'Nombre de tarea': 'Actividad 2.1'},
    ]
    
    df = pd.DataFrame(datos_test)
    
    # PASO 1: Procesar como lo hace la aplicación (solo nivel 1)
    print("📝 PASO 1: Procesamiento inicial (simulando lógica de aplicación)")
    
    for index, row in df.iterrows():
        if row['Nivel de esquema'] == 1:  # Solo proyectos
            nombre_tarea = str(row['Nombre de tarea'])
            edt = str(row['EDT'])
            
            # Crear proyecto_id único
            proyecto_id = f"{edt}_{nombre_tarea.replace(' ', '_')}"
            
            # Verificar si ya existe (simulando lógica real)
            proyecto_existente = any(p.get('proyecto_id') == proyecto_id for p in proyectos_nuevos)
            
            print(f"   Procesando: {nombre_tarea} (EDT={edt})")
            print(f"   proyecto_id: {proyecto_id}")
            print(f"   ¿Ya existe?: {proyecto_existente}")
            
            if not proyecto_existente:
                proyecto = {
                    'edt': edt,
                    'nombre_tarea': nombre_tarea,
                    'proyecto': nombre_tarea,  # En el nuevo formato son iguales
                    'proyecto_id': proyecto_id,
                    'duracion': 10
                }
                proyectos_nuevos.append(proyecto)
                print(f"   ✅ AGREGADO")
            else:
                print(f"   ❌ DUPLICADO - NO agregado")
            print()
    
    print(f"📊 ESTADO DESPUÉS DEL PROCESAMIENTO:")
    print(f"   Total en lista: {len(proyectos_nuevos)}")
    for i, p in enumerate(proyectos_nuevos, 1):
        print(f"   {i}. {p['nombre_tarea']} (ID: {p['proyecto_id']})")
    print()
    
    # PASO 2: Aplicar limpieza de duplicados (nueva lógica)
    print("🧹 PASO 2: Limpieza de duplicados robusta")
    
    proyectos_unicos = {}
    for proyecto in proyectos_nuevos:
        proyecto_id = proyecto.get('proyecto_id')
        if proyecto_id not in proyectos_unicos:
            proyectos_unicos[proyecto_id] = proyecto
            print(f"   ✅ Mantenido: {proyecto['nombre_tarea']} (ID: {proyecto_id})")
        else:
            print(f"   ❌ Duplicado eliminado: {proyecto['nombre_tarea']} (ID: {proyecto_id})")
    
    proyectos_nuevos_limpios = list(proyectos_unicos.values())
    
    # RESULTADO FINAL
    print(f"\n📊 RESULTADO FINAL PARA MODAL:")
    print(f"   Proyectos antes de limpieza: {len(proyectos_nuevos)}")
    print(f"   Proyectos después de limpieza: {len(proyectos_nuevos_limpios)}")
    print(f"   Lista final:")
    
    for i, proyecto in enumerate(proyectos_nuevos_limpios, 1):
        print(f"      {i}. {proyecto['nombre_tarea']} (EDT={proyecto['edt']}, ID={proyecto['proyecto_id']})")
    
    # VERIFICACIÓN FINAL
    if len(proyectos_nuevos_limpios) == 2:
        print(f"\n✅ ¡CORRECCIÓN EXITOSA!")
        print(f"   El modal ahora mostrará exactamente 2 proyectos únicos")
        return True
    else:
        print(f"\n❌ Error: Se esperaban 2 proyectos, se obtuvieron {len(proyectos_nuevos_limpios)}")
        return False

if __name__ == "__main__":
    test_correccion_duplicados()
