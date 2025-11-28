#!/usr/bin/env python3
"""
Script para probar el filtrado por requerimiento_id=3
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

def test_filtro_proyecto():
    """Probar el filtrado para procesar solo el proyecto con requerimiento_id=3"""
    
    app = create_app()
    
    with app.app_context():
        print("🎯 PROBANDO FILTRO POR REQUERIMIENTO_ID=3...")
        print()
        
        # PASO 1: Limpiar actividades anteriores
        print("🧹 PASO 1: Limpiando actividades anteriores...")
        actividades_antes = ActividadProyecto.query.count()
        ActividadProyecto.query.delete()
        db.session.commit()
        print(f"   - Actividades eliminadas: {actividades_antes}")
        print()
        
        # PASO 2: Leer y procesar archivo Excel
        archivo_path = "DOCS/Tip/all.xlsx"
        
        if not os.path.exists(archivo_path):
            print(f"❌ Archivo no encontrado: {archivo_path}")
            return
            
        print("📊 PASO 2: Leyendo archivo Excel...")
        df = pd.read_excel(archivo_path)
        
        # PASO 3: Detectar proyectos
        print("🔍 PASO 3: Detectando proyectos...")
        proyecto_columna = 'Proyecto'
        proyectos_unicos = df[proyecto_columna].dropna().unique()
        proyectos_sistema = [p for p in proyectos_unicos if 'SISTEMA' in str(p)]
        print(f"   - Proyectos SISTEMA: {proyectos_sistema}")
        print()
        
        # PASO 4: Obtener requerimiento con ID=3
        print("🎯 PASO 4: Verificando requerimiento_id=3...")
        requerimiento_3 = Requerimiento.query.get(3)
        if not requerimiento_3:
            print("❌ No existe requerimiento con ID=3")
            return
        print(f"   - Requerimiento 3: {requerimiento_3.nombre}")
        print()
        
        # PASO 5: Simular asignaciones (solo requerimiento_id=3 debe procesar actividades)
        print("📋 PASO 5: Simulando asignaciones...")
        
        # Simular las asignaciones que se recibirían
        asignaciones_simuladas = {
            "SISTEMA PROYECTO 03": 1,  # NO debe procesar actividades
            "SISTEMA PROYECTO 02": 2,  # NO debe procesar actividades  
            "SISTEMA PROYECTO 01": 3   # SÍ debe procesar actividades
        }
        
        print("   Asignaciones simuladas:")
        for proyecto, req_id in asignaciones_simuladas.items():
            procesar = "✅ PROCESAR" if req_id == 3 else "⏭️ SALTAR"
            print(f"     - {proyecto} → Requerimiento {req_id} ({procesar})")
        print()
        
        # PASO 6: Simular el procesamiento con filtro
        print("💾 PASO 6: Procesando con filtro...")
        
        # Crear actividades temporales
        from app.controllers import parsear_fecha_espanol
        
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
        df_ordenado = df.sort_values([proyecto_columna, '_edt_sort'])
        
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
        
        # PASO 7: Aplicar el filtro y procesar
        print("🎯 PASO 7: Aplicando filtro y procesando...")
        
        actividades_procesadas = 0
        actividades_saltadas = 0
        
        for edt_proyecto, requerimiento_id in asignaciones_simuladas.items():
            requerimiento = Requerimiento.query.get(requerimiento_id)
            if requerimiento:
                requerimiento.proyecto = edt_proyecto
                
                # FILTRO: Solo procesar si requerimiento_id == 3
                if requerimiento_id == 3:
                    print(f"   ✅ PROCESANDO: {edt_proyecto} (requerimiento_id={requerimiento_id})")
                    
                    for actividad_data in actividades_temp:
                        if actividad_data.get('proyecto') == edt_proyecto:
                            nueva_actividad = ActividadProyecto(
                                requerimiento_id=requerimiento_id,
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
                    print(f"   ⏭️ SALTANDO: {edt_proyecto} (requerimiento_id={requerimiento_id})")
                    # Contar actividades que se saltaron
                    for actividad_data in actividades_temp:
                        if actividad_data.get('proyecto') == edt_proyecto:
                            actividades_saltadas += 1
        
        db.session.commit()
        
        # PASO 8: Verificar resultados
        print()
        print("📊 RESULTADOS:")
        total_actividades = ActividadProyecto.query.count()
        actividades_req_3 = ActividadProyecto.query.filter_by(requerimiento_id=3).count()
        
        print(f"   - Total actividades en BD: {total_actividades}")
        print(f"   - Actividades para requerimiento_id=3: {actividades_req_3}")
        print(f"   - Actividades procesadas: {actividades_procesadas}")
        print(f"   - Actividades saltadas: {actividades_saltadas}")
        print()
        
        # Verificar que solo hay actividades del proyecto correcto
        actividades_proyecto_3 = ActividadProyecto.query.filter_by(requerimiento_id=3).all()
        if actividades_proyecto_3:
            print("🔍 MUESTRA DE ACTIVIDADES GUARDADAS (requerimiento_id=3):")
            for i, act in enumerate(actividades_proyecto_3[:5]):
                req = Requerimiento.query.get(act.requerimiento_id)
                print(f"     {i+1}. EDT: {act.edt} | {act.nombre_tarea} | Proyecto: {req.proyecto if req else 'N/A'}")
        
        print()
        if total_actividades == actividades_procesadas and actividades_req_3 == total_actividades:
            print("✅ ÉXITO: Solo se procesaron las actividades del proyecto correcto")
        else:
            print("❌ ERROR: Se procesaron actividades incorrectas")

if __name__ == '__main__':
    test_filtro_proyecto()
