"""
Script para diagnosticar exactamente qué está pasando con el procesamiento
de múltiples proyectos en el archivo all.xlsx
"""
import pandas as pd
import re

def ordenar_por_edt(edt_str):
    """
    Función para ordenar correctamente los códigos EDT
    Convierte EDT como "1.2.3" en una tupla (1, 2, 3) para ordenamiento natural
    """
    try:
        # Convertir EDT a lista de números para ordenamiento natural
        partes = str(edt_str).split('.')
        return tuple(int(parte) for parte in partes)
    except (ValueError, AttributeError):
        # Si no se puede convertir, poner al final
        return (float('inf'),)

def procesar_archivo_debug():
    archivo_path = "DOCS/Tip/all.xlsx"  # Ajusta la ruta si es necesario
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo_path)
        
        print("=== DIAGNÓSTICO COMPLETO ===")
        print(f"Total de filas: {len(df)}")
        print(f"Columnas disponibles: {list(df.columns)}")
        
        # Crear mapeo de columnas
        columnas_disponibles = list(df.columns)
        columnas_requeridas = ['Id', 'Nivel de esquema', 'EDT', 'Nombre de tarea', 
                              'Duración', 'Comienzo', 'Fin', 'Predecesoras', 'Nombres de los recursos', 'Proyecto']
        
        mapeo_columnas = {}
        for col_req in columnas_requeridas:
            col_encontrada = None
            for col_disp in columnas_disponibles:
                # Comparación más flexible (sin distinguir mayúsculas/minúsculas y espacios)
                if col_req.lower().replace(' ', '') == str(col_disp).lower().replace(' ', ''):
                    col_encontrada = col_disp
                    break
                # Búsqueda por palabras clave específicas
                elif col_req.lower() == 'id' and 'id' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'nivel' in col_req.lower() and 'nivel' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'edt' in col_req.lower() and 'edt' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'nombre' in col_req.lower() and 'tarea' in col_req.lower() and 'nombre' in str(col_disp).lower() and 'tarea' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'duración' in col_req.lower() and 'duraci' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'comienzo' in col_req.lower() and ('comienzo' in str(col_disp).lower() or 'inicio' in str(col_disp).lower()):
                    col_encontrada = col_disp
                    break
                elif col_req.lower() == 'fin' and ('fin' in str(col_disp).lower() or 'final' in str(col_disp).lower()):
                    col_encontrada = col_disp
                    break
                elif 'predecesora' in col_req.lower() and 'predecesora' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'recurso' in col_req.lower() and 'recurso' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
                elif 'proyecto' in col_req.lower() and 'proyecto' in str(col_disp).lower():
                    col_encontrada = col_disp
                    break
            
            if col_encontrada:
                mapeo_columnas[col_req] = col_encontrada
        
        print(f"\n=== MAPEO DE COLUMNAS ===")
        for req, disp in mapeo_columnas.items():
            print(f"'{req}' → '{disp}'")
        
        # Verificar si encontramos todas las columnas necesarias
        columnas_faltantes = [col for col in columnas_requeridas if col not in mapeo_columnas]
        if columnas_faltantes:
            print(f"\n❌ COLUMNAS FALTANTES: {columnas_faltantes}")
            return
        
        # Procesar proyectos (nivel_esquema = 1)
        print(f"\n=== ANÁLISIS DE PROYECTOS (Nivel de esquema = 1) ===")
        
        # Filtrar solo filas de nivel_esquema = 1
        nivel_col = mapeo_columnas['Nivel de esquema']
        nombre_col = mapeo_columnas['Nombre de tarea']
        edt_col = mapeo_columnas['EDT']
        proyecto_col = mapeo_columnas.get('Proyecto', None)
        
        proyectos_nivel_1 = df[df[nivel_col] == 1].copy()
        print(f"Total de filas con nivel de esquema = 1: {len(proyectos_nivel_1)}")
        
        # Simular el filtrado como lo hace el código
        nombre_archivo_sin_extension = "all"  # Como en los logs
        proyectos_nuevos = []
        
        print(f"\nAnalizando cada proyecto...")
        for index, row in proyectos_nivel_1.iterrows():
            nombre_tarea = str(row[nombre_col])
            edt = str(row[edt_col])
            nombre_proyecto = str(row[proyecto_col]) if proyecto_col and pd.notna(row[proyecto_col]) else 'Sin Proyecto'
            
            print(f"\n🔍 Proyecto {index}:")
            print(f"   - Nombre de tarea: '{nombre_tarea}'")
            print(f"   - EDT: '{edt}'")
            print(f"   - Proyecto: '{nombre_proyecto}'")
            print(f"   - ¿Coincide con archivo?: {nombre_tarea.lower() == nombre_archivo_sin_extension.lower()}")
            
            # Simular la lógica del código
            if nombre_tarea.lower() != nombre_archivo_sin_extension.lower():
                proyecto_id = f"{nombre_proyecto}_{edt}"
                
                # Verificar si este proyecto específico ya fue agregado
                proyecto_existente = any(p.get('proyecto_id') == proyecto_id for p in proyectos_nuevos)
                
                if not proyecto_existente:
                    proyectos_nuevos.append({
                        'edt': edt,
                        'nombre_tarea': nombre_tarea,
                        'proyecto': nombre_proyecto,
                        'proyecto_id': proyecto_id
                    })
                    print(f"   ✅ AGREGADO para asignación (proyecto_id: {proyecto_id})")
                else:
                    print(f"   ⚠️ DUPLICADO (ya existe proyecto_id: {proyecto_id})")
            else:
                print(f"   ❌ EXCLUIDO (nombre coincide con archivo)")
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"📊 Total proyectos que aparecerían para asignación: {len(proyectos_nuevos)}")
        
        if proyectos_nuevos:
            print(f"\n📋 Proyectos disponibles para asignación:")
            for i, proyecto in enumerate(proyectos_nuevos, 1):
                print(f"   {i}. '{proyecto['nombre_tarea']}' (Proyecto: {proyecto['proyecto']}, EDT: {proyecto['edt']})")
        else:
            print(f"\n❌ No hay proyectos disponibles para asignación")
            print("Posibles causas:")
            print("1. Todos los nombres de tareas coinciden con el nombre del archivo")
            print("2. Hay duplicados que están siendo filtrados")
            print("3. No hay filas con nivel de esquema = 1")
        
        # Análisis adicional de datos únicos
        print(f"\n=== ANÁLISIS ADICIONAL ===")
        if proyecto_col:
            valores_proyecto_unicos = df[proyecto_col].value_counts()
            print(f"Valores únicos en columna 'Proyecto':")
            for proyecto, count in valores_proyecto_unicos.items():
                print(f"   - '{proyecto}': {count} filas")
        
        valores_edt_nivel1 = proyectos_nivel_1[edt_col].value_counts()
        print(f"\nValores EDT únicos en nivel de esquema = 1:")
        for edt, count in valores_edt_nivel1.items():
            print(f"   - EDT '{edt}': {count} apariciones")
        
    except FileNotFoundError:
        print("❌ No se encontró el archivo 'DOCS/all.xlsx'")
        print("   Verifica que el archivo esté en la ubicación correcta")
    except Exception as e:
        print(f"❌ Error al procesar: {e}")

if __name__ == "__main__":
    procesar_archivo_debug()
