#!/usr/bin/env python3
"""
Script para probar paso a paso el procesamiento completo
"""

import os
import sys
import pandas as pd
import json

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar la aplicación
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.models import ActividadProyecto, Requerimiento

def simular_proceso_completo():
    """Simular el proceso completo de carga y guardado"""
    
    app = create_app()
    
    with app.app_context():
        print("🔥 SIMULANDO PROCESO COMPLETO DE MULTI-PROYECTO...")
        print()
        
        # PASO 1: Leer y procesar archivo Excel
        archivo_path = "DOCS/Tip/all.xlsx"
        
        if not os.path.exists(archivo_path):
            print(f"❌ Archivo no encontrado: {archivo_path}")
            return
            
        print("📊 PASO 1: Leyendo archivo Excel...")
        df = pd.read_excel(archivo_path)
        print(f"   - Filas totales: {len(df)}")
        print(f"   - Columnas: {list(df.columns)}")
        print()
        
        # PASO 2: Detectar proyectos
        print("🔍 PASO 2: Detectando proyectos...")
        proyecto_columna = 'Proyecto'
        proyectos_unicos = df[proyecto_columna].dropna().unique()
        print(f"   - Proyectos encontrados: {list(proyectos_unicos)}")
        print(f"   - Total proyectos: {len(proyectos_unicos)}")
        print()
        
        # Filtrar solo los proyectos de "SISTEMA"
        proyectos_sistema = [p for p in proyectos_unicos if 'SISTEMA' in str(p)]
        print(f"   - Proyectos SISTEMA: {proyectos_sistema}")
        print()
        
        # PASO 3: Simular ordenamiento como lo hace la función
        print("📋 PASO 3: Procesando actividades temporales...")
        
        # Crear función de ordenamiento EDT simulada
        def crear_clave_edt(edt_value):
            try:
                if pd.isna(edt_value):
                    return "99999"
                edt_str = str(edt_value)
                if '.' in edt_str:
                    # Convertir a formato que se pueda ordenar como string
                    partes = edt_str.split('.')
                    # Padding con ceros para orden correcto
                    partes_padded = [parte.zfill(3) for parte in partes]
                    return '.'.join(partes_padded)
                else:
                    return edt_str.zfill(3)
            except:
                return "99999"
        
        # Agregar columna de ordenamiento
        df['_edt_sort'] = df['EDT'].apply(crear_clave_edt)
        
        # Ordenar por Proyecto + EDT
        print("   - Ordenando por: [Proyecto, EDT]")
        df_ordenado = df.sort_values([proyecto_columna, '_edt_sort'])
        
        print(f"   - Orden después de sorting:")
        for i, (idx, row) in enumerate(df_ordenado.head(15).iterrows()):
            proyecto = row[proyecto_columna]
            edt = row['EDT'] 
            nombre = row['Nombre de tarea']
            print(f"     {i+1:2d}. {proyecto} | {edt} | {nombre}")
        print()
        
        # PASO 4: Crear actividades temporales
        print("💾 PASO 4: Creando actividades temporales...")
        
        # Importar función de parseo de fechas
        from app.controllers import parsear_fecha_espanol
        
        actividades_temp = []
        
        mapeo_columnas = {
            'EDT': 'EDT',
            'Nombre de tarea': 'Nombre de tarea',
            'Nivel de esquema': 'Nivel de esquema',
            'Proyecto': 'Proyecto',
            'Comienzo': 'Comienzo',
            'Fin': 'Fin', 
            'Duración': 'Duración',
            'Predecesoras': 'Predecesoras',
            'Nombres de los recursos': 'Nombres de los recursos'
        }
        
        for idx, row in df_ordenado.iterrows():
            # Procesar fechas usando la función correcta
            fecha_inicio_raw = row[mapeo_columnas['Comienzo']]
            fecha_fin_raw = row[mapeo_columnas['Fin']]
            
            fecha_inicio = parsear_fecha_espanol(fecha_inicio_raw) if pd.notna(fecha_inicio_raw) else None
            fecha_fin = parsear_fecha_espanol(fecha_fin_raw) if pd.notna(fecha_fin_raw) else None
            
            # Procesar duración
            duracion_raw = row[mapeo_columnas['Duración']]
            try:
                if pd.notna(duracion_raw):
                    duracion_str = str(duracion_raw).replace(' días', '').replace(' día', '').strip()
                    duracion = int(float(duracion_str))
                else:
                    duracion = 0
            except:
                duracion = 0
            
            nueva_actividad = {
                'edt': str(row[mapeo_columnas['EDT']]),
                'nombre_tarea': str(row[mapeo_columnas['Nombre de tarea']]),
                'nivel_esquema': int(row[mapeo_columnas['Nivel de esquema']]),
                'proyecto': str(row[mapeo_columnas['Proyecto']]),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'duracion': duracion,
                'predecesoras': str(row[mapeo_columnas['Predecesoras']]) if pd.notna(row[mapeo_columnas['Predecesoras']]) else '',
                'recursos': str(row[mapeo_columnas['Nombres de los recursos']]) if pd.notna(row[mapeo_columnas['Nombres de los recursos']]) else ''
            }
            
            actividades_temp.append(nueva_actividad)
            
        print(f"   - Total actividades temporales creadas: {len(actividades_temp)}")
        print()
        
        # PASO 5: Simular asignaciones
        print("🎯 PASO 5: Simulando asignaciones de proyectos...")
        
        # Obtener requerimientos disponibles
        requerimientos = Requerimiento.query.filter_by(activo=True).limit(5).all()
        
        if len(requerimientos) < len(proyectos_sistema):
            print(f"❌ No hay suficientes requerimientos activos ({len(requerimientos)} disponibles, {len(proyectos_sistema)} proyectos)")
            return
            
        # Crear asignaciones simuladas
        asignaciones = {}
        for i, proyecto in enumerate(proyectos_sistema):
            if i < len(requerimientos):
                asignaciones[proyecto] = requerimientos[i].id
                print(f"   - {proyecto} → Requerimiento {requerimientos[i].id} ({requerimientos[i].nombre})")
        print()
        
        # PASO 6: Procesar y guardar actividades
        print("💾 PASO 6: Procesando y guardando actividades...")
        
        actividades_procesadas = 0
        actividades_creadas = 0
        
        for actividad_temp in actividades_temp:
            proyecto_actividad = actividad_temp['proyecto']
            requerimiento_id = asignaciones.get(proyecto_actividad)
            
            if requerimiento_id:
                print(f"   📋 Procesando: {actividad_temp['edt']} - {actividad_temp['nombre_tarea']} → Proyecto: {proyecto_actividad} → Req: {requerimiento_id}")
                
                # Verificar si ya existe
                actividad_existente = ActividadProyecto.query.filter_by(
                    requerimiento_id=requerimiento_id,
                    edt=actividad_temp['edt']
                ).first()
                
                if not actividad_existente:
                    # Crear nueva actividad
                    nueva_actividad = ActividadProyecto(
                        edt=actividad_temp['edt'],
                        nombre_tarea=actividad_temp['nombre_tarea'],
                        nivel_esquema=actividad_temp['nivel_esquema'],
                        fecha_inicio=actividad_temp['fecha_inicio'],
                        fecha_fin=actividad_temp['fecha_fin'],
                        duracion=actividad_temp['duracion'],
                        predecesoras=actividad_temp['predecesoras'],
                        recursos=actividad_temp['recursos'],
                        requerimiento_id=requerimiento_id
                    )
                    
                    db.session.add(nueva_actividad)
                    actividades_creadas += 1
                else:
                    print(f"     ⚠️ Ya existe actividad con EDT {actividad_temp['edt']} para requerimiento {requerimiento_id}")
                
                actividades_procesadas += 1
            else:
                print(f"   ⏭️ Saltando: {actividad_temp['proyecto']} (no asignado)")
        
        print()
        print(f"📊 RESUMEN:")
        print(f"   - Actividades procesadas: {actividades_procesadas}")
        print(f"   - Actividades creadas: {actividades_creadas}")
        
        # Confirmar cambios
        try:
            db.session.commit()
            print("   ✅ Cambios guardados en base de datos")
            
            # Verificar que se guardaron
            total_actividades = ActividadProyecto.query.count()
            print(f"   📋 Total actividades en DB después del guardado: {total_actividades}")
            
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Error al guardar: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    simular_proceso_completo()
