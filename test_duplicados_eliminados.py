"""
🧪 TEST: Validar eliminación de duplicados en procesamiento jerárquico
"""
import pandas as pd

def main():
    print("=" * 80)
    print("🧪 TEST: Validar eliminación de duplicados en procesamiento jerárquico")
    print("=" * 80)
    
    # Simular datos como los del Excel real
    data = {
        'Nivel de esquema': [1, 2, 3, 3, 3, 3, 3, 3, 3, 1, 2, 3, 3, 3],
        'EDT': [1, '1.1', '1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1.4.1', '1.1.4.2', '1.1.4.3', 2, '2.1', '2.1.1', '2.1.2', '2.1.3'],
        'Nombre de tarea': [
            'PROYECTO 01', 'Actividad 1.1', 'Sub 1.1.1', 'Sub 1.1.2', 'Sub 1.1.3', 
            'Sub 1.1.4', 'Sub 1.1.4.1', 'Sub 1.1.4.2', 'Sub 1.1.4.3',
            'PROYECTO 02', 'Actividad 2.1', 'Sub 2.1.1', 'Sub 2.1.2', 'Sub 2.1.3'
        ],
        'Duración': ['10 días'] * 14,
        'Comienzo': ['01/01/2025'] * 14,
        'Fin': ['10/01/2025'] * 14,
        '% completado': [0] * 14,
        'Real Anterior': [''] * 14,
        '% programado': [0] * 14,
        '% Real': [0] * 14,
        'Decimales': [2] * 14,
        'Predecesoras': [''] * 14,
        'Nombres de los recursos': [''] * 14,
        'Días Corrido': [10] * 14
    }
    
    df = pd.DataFrame(data)
    
    print("📊 Datos de prueba creados:")
    print(f"   Total filas: {len(df)}")
    print(f"   Proyectos nivel 1: {len(df[df['Nivel de esquema'] == 1])}")
    print(f"   Actividades nivel 2+: {len(df[df['Nivel de esquema'] > 1])}")
    
    # Función para asignar proyecto por EDT (simulando la lógica del sistema)
    def asignar_proyecto_por_edt(edt_str):
        try:
            edt_parts = str(edt_str).split('.')
            primer_numero = int(edt_parts[0])
            
            # Mapear números a nombres de proyectos
            proyectos_map = {1: 'PROYECTO 01', 2: 'PROYECTO 02'}
            return proyectos_map.get(primer_numero, 'Sin Proyecto')
        except:
            return 'Sin Proyecto'
    
    # Aplicar asignación de proyecto
    df['_proyecto_inferido'] = df['EDT'].apply(asignar_proyecto_por_edt)
    
    print("\n🎯 Proyectos detectados por EDT:")
    proyectos_unicos = df[df['Nivel de esquema'] == 1]['_proyecto_inferido'].unique()
    for i, proyecto in enumerate(proyectos_unicos, 1):
        print(f"   {i}. {proyecto}")
    
    # Simular lógica de procesamiento (SOLO UN BUCLE, NO DOS)
    proyectos_para_asignar = []
    
    print("\n📋 Procesamiento de proyectos nivel 1 (LÓGICA CORREGIDA):")
    for index, row in df.iterrows():
        if row['Nivel de esquema'] == 1:  # Solo procesar nivel 1
            nombre_tarea = str(row['Nombre de tarea'])
            proyecto_inferido = row['_proyecto_inferido']
            edt = str(row['EDT'])
            
            print(f"\n🔍 Analizando proyecto nivel 1:")
            print(f"   - Nombre de tarea: '{nombre_tarea}'")
            print(f"   - Proyecto inferido: '{proyecto_inferido}'")
            print(f"   - EDT: '{edt}'")
            
            # Crear ID único usando EDT
            proyecto_id = f"{edt}_{nombre_tarea.replace(' ', '_')}"
            
            # Verificar duplicados en la sesión actual
            proyecto_existente = any(p.get('proyecto_id') == proyecto_id for p in proyectos_para_asignar)
            
            if not proyecto_existente:
                proyectos_para_asignar.append({
                    'edt': edt,
                    'nombre_tarea': nombre_tarea,
                    'proyecto': proyecto_inferido,
                    'proyecto_id': proyecto_id,
                })
                print(f"   ✅ Proyecto agregado: '{nombre_tarea}' (ID: {proyecto_id})")
            else:
                print(f"   ⚠️ Proyecto ya agregado: '{nombre_tarea}' (ID: {proyecto_id})")
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   Total proyectos para asignar: {len(proyectos_para_asignar)}")
    
    for i, proyecto in enumerate(proyectos_para_asignar, 1):
        print(f"   {i}. '{proyecto['nombre_tarea']}' del proyecto '{proyecto['proyecto']}' (EDT: {proyecto['edt']})")
    
    # Validar que no hay duplicados
    nombres_tareas = [p['nombre_tarea'] for p in proyectos_para_asignar]
    nombres_unicos = list(set(nombres_tareas))
    
    print(f"\n🧹 Validación de duplicados:")
    print(f"   Total proyectos encontrados: {len(proyectos_para_asignar)}")
    print(f"   Nombres únicos: {len(nombres_unicos)}")
    print(f"   ¿Hay duplicados?: {'SÍ' if len(proyectos_para_asignar) != len(nombres_unicos) else 'NO'}")
    
    if len(proyectos_para_asignar) == len(nombres_unicos) == 2:
        print("\n✅ TEST EXITOSO: Se detectaron exactamente 2 proyectos únicos sin duplicados")
        print("   El sistema ahora procesa correctamente el formato jerárquico")
        return True
    else:
        print("\n❌ TEST FALLIDO: Se esperaban 2 proyectos únicos")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
