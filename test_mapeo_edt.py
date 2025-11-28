#!/usr/bin/env python3
"""
Script para probar el mapeo EDT → Proyecto
"""

import os
import sys
import pandas as pd

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar la aplicación
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.models import ActividadProyecto, Requerimiento

def test_mapeo_edt_proyecto():
    """Probar el mapeo de EDT a nombre de proyecto"""
    
    app = create_app()
    
    with app.app_context():
        print("🗺️ PROBANDO MAPEO EDT → PROYECTO...")
        print()
        
        # PASO 1: Limpiar actividades anteriores
        print("🧹 PASO 1: Limpiando actividades anteriores...")
        actividades_antes = ActividadProyecto.query.count()
        ActividadProyecto.query.delete()
        db.session.commit()
        print(f"   - Actividades eliminadas: {actividades_antes}")
        print()
        
        # PASO 2: Simular el procesamiento del Excel para crear actividades_temp
        archivo_path = "DOCS/Tip/all.xlsx"
        
        if not os.path.exists(archivo_path):
            print(f"❌ Archivo no encontrado: {archivo_path}")
            return
            
        print("📊 PASO 2: Simulando procesamiento Excel...")
        df = pd.read_excel(archivo_path)
        
        from app.controllers import parsear_fecha_espanol, procesar_proyecto_xlsx
        
        def crear_clave_edt(edt_value):
            try:
                if pd.isna(edt_value):
                    return "99999"
                edt_str = str(edt_value)
                if '.' in edt_str:
                    partes = edt_str.split('.')
                    partes_padded = [parte.zfill(3) for parte in partes]
                    return '.'.join(partes_padded)
                else:
                    return edt_str.zfill(3)
            except:
                return "99999"
        
        df['_edt_sort'] = df['EDT'].apply(crear_clave_edt)
        df_ordenado = df.sort_values(['Proyecto', '_edt_sort'])
        
        # Crear actividades temporales simuladas
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
            fecha_inicio_raw = row[mapeo_columnas['Comienzo']]
            fecha_fin_raw = row[mapeo_columnas['Fin']]
            
            fecha_inicio = parsear_fecha_espanol(fecha_inicio_raw) if pd.notna(fecha_inicio_raw) else None
            fecha_fin = parsear_fecha_espanol(fecha_fin_raw) if pd.notna(fecha_fin_raw) else None
            
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
        
        # Simular que las actividades se guardaron en procesar_proyecto_xlsx
        procesar_proyecto_xlsx.actividades_temp = actividades_temp
        
        print(f"   - Total actividades temporales creadas: {len(actividades_temp)}")
        print()
        
        # PASO 3: Crear el mapeo EDT → Proyecto
        print("🗺️ PASO 3: Creando mapeo EDT → Proyecto...")
        
        edt_to_proyecto = {}
        for actividad in actividades_temp:
            if actividad.get('nivel_esquema') == 1:  # Solo proyectos nivel 1
                edt = str(actividad.get('edt'))
                proyecto = actividad.get('proyecto')
                if edt not in edt_to_proyecto:
                    edt_to_proyecto[edt] = proyecto
                    print(f"   🗺️ Mapeo: EDT '{edt}' → Proyecto '{proyecto}'")
        
        print(f"   - Total mapeos creados: {len(edt_to_proyecto)}")
        print()
        
        # PASO 4: Simular asignaciones que vendrían del frontend
        print("📋 PASO 4: Simulando asignaciones del frontend...")
        
        asignaciones_frontend = {'1': '3'}  # EDT '1' asignado a requerimiento 3
        requerimiento_para_procesar = '3'
        
        print(f"   - Asignaciones recibidas: {asignaciones_frontend}")
        print(f"   - Requerimiento para procesar: {requerimiento_para_procesar}")
        print()
        
        # PASO 5: Procesar con el nuevo mapeo
        print("💾 PASO 5: Procesando con mapeo correcto...")
        
        actividades_procesadas = 0
        
        for edt_proyecto, requerimiento_id in asignaciones_frontend.items():
            nombre_proyecto_real = edt_to_proyecto.get(edt_proyecto, edt_proyecto)
            print(f"   📋 EDT '{edt_proyecto}' → Proyecto '{nombre_proyecto_real}' → Requerimiento {requerimiento_id}")
            
            procesar_actividades = (requerimiento_para_procesar is not None and 
                                   int(requerimiento_id) == int(requerimiento_para_procesar))
            
            print(f"   🔍 ¿Procesar actividades? {procesar_actividades}")
            
            if procesar_actividades:
                print(f"   ✅ PROCESANDO actividades de '{nombre_proyecto_real}'...")
                
                for actividad_data in actividades_temp:
                    if actividad_data.get('proyecto') == nombre_proyecto_real:
                        print(f"      ✅ Encontrada: EDT {actividad_data.get('edt')} - {actividad_data.get('nombre_tarea')}")
                        
                        nueva_actividad = ActividadProyecto(
                            requerimiento_id=int(requerimiento_id),
                            edt=actividad_data['edt'],
                            nombre_tarea=actividad_data['nombre_tarea'],
                            nivel_esquema=actividad_data['nivel_esquema'],
                            fecha_inicio=actividad_data['fecha_inicio'],
                            fecha_fin=actividad_data['fecha_fin'],
                            duracion=actividad_data['duracion'],
                            predecesoras=actividad_data['predecesoras'],
                            recursos=actividad_data['recursos']
                        )
                        db.session.add(nueva_actividad)
                        actividades_procesadas += 1
            else:
                print(f"   ⏭️ SALTANDO proyecto '{nombre_proyecto_real}'")
        
        db.session.commit()
        
        # PASO 6: Verificar resultados
        print()
        print("📊 RESULTADOS:")
        total_actividades = ActividadProyecto.query.count()
        actividades_req_3 = ActividadProyecto.query.filter_by(requerimiento_id=3).count()
        
        print(f"   - Total actividades en BD: {total_actividades}")
        print(f"   - Actividades para requerimiento_id=3: {actividades_req_3}")
        print(f"   - Actividades procesadas: {actividades_procesadas}")
        print()
        
        if actividades_procesadas > 0 and total_actividades == actividades_procesadas:
            print("✅ ÉXITO: El mapeo EDT → Proyecto funciona correctamente")
        else:
            print("❌ ERROR: El mapeo no funcionó como esperado")

if __name__ == '__main__':
    test_mapeo_edt_proyecto()
