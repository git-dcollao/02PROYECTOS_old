"""
Script para simular exactamente la lógica de procesar_proyecto_xlsx
y entender por qué no se detectan múltiples proyectos
"""
import pandas as pd
import re
from datetime import datetime
import os
import sys

# Agregar el directorio raíz al path para importar módulos
sys.path.append('/mnt/c/Users/Daniel Collao/Documents/Repositories/02PROYECTOS')
sys.path.append('c:\\Users\\Daniel Collao\\Documents\\Repositories\\02PROYECTOS')

def parsear_fecha_espanol(fecha_str):
    """Parsear fecha en formato español como 'vie 29-01-10 9:00'"""
    if pd.isna(fecha_str) or not fecha_str:
        return None
    
    try:
        # Limpiar la cadena
        fecha_str = str(fecha_str).strip()
        
        # Patrón para fechas españolas: "vie 29-01-10 9:00"
        patron = r'^\w{3}\s+(\d{1,2})-(\d{1,2})-(\d{2})\s+\d{1,2}:\d{2}$'
        match = re.match(patron, fecha_str)
        
        if match:
            dia, mes, año_corto = match.groups()
            
            # Convertir año de 2 dígitos a 4 dígitos
            año_corto = int(año_corto)
            if año_corto >= 50:  # Años 50-99 son 1950-1999
                año = 1900 + año_corto
            else:  # Años 00-49 son 2000-2049
                año = 2000 + año_corto
            
            return datetime(año, int(mes), int(dia)).date()
        else:
            # Si no coincide con el patrón, intentar parsear directamente
            fecha_obj = pd.to_datetime(fecha_str, errors='coerce')
            if pd.notna(fecha_obj):
                return fecha_obj.date()
    except Exception as e:
        print(f"Error parseando fecha '{fecha_str}': {e}")
    
    return None

def simular_procesamiento():
    """Simular el procesamiento completo del archivo"""
    archivo_path = "DOCS/Tip/all.xlsx"
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo_path)
        
        print("=== SIMULACIÓN COMPLETA DE PROCESAMIENTO ===")
        print(f"Total de filas iniciales: {len(df)}")
        columnas_disponibles = list(df.columns)
        print(f"Columnas disponibles en el archivo: {columnas_disponibles}")
        
        # PASO 1: LIMPIEZA DE DATOS (eliminar msproj11)
        filas_iniciales = len(df)
        
        # Identificar columnas para limpieza
        col_nivel_esquema = None
        col_nombre_tarea = None
        
        for col in columnas_disponibles:
            if 'nivel' in str(col).lower() and 'esquema' in str(col).lower():
                col_nivel_esquema = col
            elif 'nombre' in str(col).lower() and 'tarea' in str(col).lower():
                col_nombre_tarea = col
        
        # Aplicar filtro de limpieza
        if col_nivel_esquema and col_nombre_tarea:
            msproj11_nivel1 = df[
                (df[col_nivel_esquema] == 1) & 
                (df[col_nombre_tarea].astype(str).str.lower() == 'msproj11')
            ]
            
            if len(msproj11_nivel1) > 0:
                print(f"🧹 Limpiando {len(msproj11_nivel1)} tareas 'msproj11' de nivel de esquema = 1")
                
                # Eliminar las filas problemáticas
                df = df[~(
                    (df[col_nivel_esquema] == 1) & 
                    (df[col_nombre_tarea].astype(str).str.lower() == 'msproj11')
                )]
                
                filas_despues = len(df)
                print(f"✅ Limpieza completada: {filas_iniciales} → {filas_despues} filas (eliminadas: {filas_iniciales - filas_despues})")
        
        # PASO 2: MAPEO DE COLUMNAS
        columnas_requeridas = ['Id', 'Nivel de esquema', 'EDT', 'Nombre de tarea', 
                              'Duración', 'Comienzo', 'Fin', 'Predecesoras', 'Nombres de los recursos', 'Proyecto']
        
        mapeo_columnas = {}
        for col_req in columnas_requeridas:
            col_encontrada = None
            for col_disp in columnas_disponibles:
                # Comparación más flexible
                if col_req.lower().replace(' ', '') == str(col_disp).lower().replace(' ', ''):
                    col_encontrada = col_disp
                    break
                # Búsquedas específicas...
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
        
        print(f"\n📋 Mapeo de columnas:")
        for req, disp in mapeo_columnas.items():
            print(f"   '{req}' → '{disp}'")
        
        # Verificar columnas faltantes
        columnas_faltantes = [col for col in columnas_requeridas if col not in mapeo_columnas]
        if columnas_faltantes:
            print(f"\n❌ COLUMNAS FALTANTES: {columnas_faltantes}")
            return
        
        # PASO 3: PROCESAMIENTO DE PROYECTOS
        proyectos_nuevos = []
        actividades_procesadas = 0
        nombre_archivo_sin_extension = "all"
        
        print(f"\nNombre del archivo (sin extensión): {nombre_archivo_sin_extension}")
        
        # Ordenar por EDT
        def ordenar_por_edt(edt_str):
            try:
                partes = str(edt_str).split('.')
                return tuple(int(parte) for parte in partes)
            except (ValueError, AttributeError):
                return (float('inf'),)
        
        df_ordenado = df.copy()
        df_ordenado['_edt_sort'] = df_ordenado[mapeo_columnas['EDT']].apply(ordenar_por_edt)
        df_ordenado = df_ordenado.sort_values('_edt_sort')
        df_ordenado = df_ordenado.drop('_edt_sort', axis=1)
        
        print(f"📋 Procesando actividades en orden EDT correcto...")
        print(f"   Primeros 10 EDTs: {df_ordenado[mapeo_columnas['EDT']].head(10).tolist()}")
        
        for index, row in df_ordenado.iterrows():
            try:
                # Convertir fechas
                fecha_inicio_raw = row[mapeo_columnas['Comienzo']]
                fecha_fin_raw = row[mapeo_columnas['Fin']]
                
                fecha_inicio = parsear_fecha_espanol(fecha_inicio_raw)
                fecha_fin = parsear_fecha_espanol(fecha_fin_raw)
                
                if fecha_inicio is None:
                    fecha_inicio = datetime.now().date()
                if fecha_fin is None:
                    fecha_fin = datetime.now().date()
                
                # Procesar duración
                duracion_str = str(row[mapeo_columnas['Duración']]) if pd.notna(row[mapeo_columnas['Duración']]) else '0'
                duracion_match = re.search(r'\d+', duracion_str)
                duracion = int(duracion_match.group()) if duracion_match else 0
                
                # Si es nivel_esquema = 1, es un proyecto principal
                if row[mapeo_columnas['Nivel de esquema']] == 1:
                    nombre_tarea = str(row[mapeo_columnas['Nombre de tarea']])
                    nombre_proyecto = str(row[mapeo_columnas.get('Proyecto', '')]) if 'Proyecto' in mapeo_columnas else 'Sin Proyecto'
                    
                    print(f"\n🔍 Analizando proyecto nivel 1:")
                    print(f"   - Nombre de tarea: '{nombre_tarea}'")
                    print(f"   - Proyecto: '{nombre_proyecto}'")
                    print(f"   - ¿Coincide con archivo?: {nombre_tarea.lower() == nombre_archivo_sin_extension.lower()}")
                    
                    # Verificar si NO coincide con el nombre del archivo
                    if nombre_tarea.lower() != nombre_archivo_sin_extension.lower():
                        # Crear identificador único
                        proyecto_id = f"{nombre_proyecto}_{str(row[mapeo_columnas['EDT']])}"
                        
                        # Verificar si ya fue agregado
                        proyecto_existente = any(p.get('proyecto_id') == proyecto_id for p in proyectos_nuevos)
                        
                        if not proyecto_existente:
                            proyectos_nuevos.append({
                                'edt': str(row[mapeo_columnas['EDT']]),
                                'nombre_tarea': nombre_tarea,
                                'proyecto': nombre_proyecto,
                                'proyecto_id': proyecto_id,
                                'duracion': duracion,
                                'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                                'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                                'predecesoras': str(row[mapeo_columnas['Predecesoras']]) if pd.notna(row[mapeo_columnas['Predecesoras']]) else '',
                                'recursos': str(row[mapeo_columnas['Nombres de los recursos']]) if pd.notna(row[mapeo_columnas['Nombres de los recursos']]) else ''
                            })
                            print(f"✅ Proyecto agregado para asignación: '{nombre_tarea}' del proyecto '{nombre_proyecto}' (ID: {proyecto_id})")
                        else:
                            print(f"⚠️ Proyecto ya agregado: '{nombre_tarea}' del proyecto '{nombre_proyecto}' (ID: {proyecto_id})")
                    else:
                        print(f"⚠️ Proyecto excluido (coincide con archivo): {nombre_tarea}")
                
                actividades_procesadas += 1
                
            except Exception as e:
                print(f"Error procesando fila {index}: {e}")
                continue
        
        # PASO 4: RESULTADOS FINALES
        print(f"\n=== RESULTADOS FINALES ===")
        print(f"📊 Total proyectos detectados para asignación: {len(proyectos_nuevos)}")
        
        if proyectos_nuevos:
            print(f"\n📋 Proyectos disponibles para asignación:")
            for i, proyecto in enumerate(proyectos_nuevos, 1):
                print(f"   {i}. '{proyecto['nombre_tarea']}' (Proyecto: {proyecto['proyecto']}, EDT: {proyecto['edt']})")
            
            print(f"\n🎯 CONCLUSIÓN: El sistema DEBERÍA mostrar {len(proyectos_nuevos)} proyectos para asignación")
        else:
            print(f"\n❌ No se detectaron proyectos para asignación")
            
        print(f"📈 Actividades procesadas en total: {actividades_procesadas}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simular_procesamiento()
