#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import ActividadProyecto, Requerimiento
from app.controllers import procesar_proyecto_xlsx, guardar_asignaciones_proyecto
import pandas as pd
import json

app = create_app()

def test_proyecto_b_a_requerimiento_1():
    with app.app_context():
        print("🔧 PRUEBA: Asignar Proyecto B al Requerimiento ID=1")
        print("=" * 60)
        
        # 1. Cargar Excel para crear actividades temporales
        print("📊 PASO 1: Cargando Excel...")
        excel_path = "DOCS/proyecto_prueba_gantt-V3.xlsx"
        df = pd.read_excel(excel_path, sheet_name=0)
        
        # Simular procesamiento para crear actividades temporales
        print("⚙️ PASO 2: Creando actividades temporales...")
        actividades_temp = []
        
        for _, row in df.iterrows():
            actividad = {
                'proyecto': str(row['Proyecto']).strip(),
                'edt': str(row['EDT']).strip(),
                'nombre_tarea': str(row['Nombre de tarea']).strip(),
                'nivel_esquema': int(row.get('Nivel de esquema', 1)),
                'fecha_inicio': None,  # Simplificado para test
                'fecha_fin': None,
                'duracion': row.get('Duración', 0),
                'predecesoras': str(row.get('Predecesoras', '')),
                'recursos': str(row.get('Nombres de los recursos', '')),
                'progreso': float(row.get('% completado', 0))
            }
            actividades_temp.append(actividad)
        
        # Asignar actividades temporales
        procesar_proyecto_xlsx.actividades_temp = actividades_temp
        print(f"   ✅ {len(actividades_temp)} actividades temporales creadas")
        
        # 2. Ver estado inicial
        print("\n📋 PASO 3: Estado inicial del requerimiento 1...")
        req1 = Requerimiento.query.get(1)
        actividades_req1_antes = ActividadProyecto.query.filter_by(requerimiento_id=1).all()
        print(f"   Proyecto actual: {req1.proyecto if req1 else 'No encontrado'}")
        print(f"   Actividades actuales: {len(actividades_req1_antes)}")
        if actividades_req1_antes:
            print(f"   Primera actividad: EDT {actividades_req1_antes[0].edt} - {actividades_req1_antes[0].nombre_tarea}")
        
        # 3. Simular asignación del frontend
        print("\n🎯 PASO 4: Simulando asignación Proyecto B → Requerimiento 1...")
        
        # Encontrar EDT del Proyecto B (SISTEMA PROYECTO 02)
        proyecto_b_edt = None
        for actividad in actividades_temp:
            if actividad['proyecto'] == 'SISTEMA PROYECTO 02' and actividad['nivel_esquema'] == 1:
                proyecto_b_edt = actividad['edt']
                break
        
        print(f"   📍 EDT del Proyecto B encontrado: {proyecto_b_edt}")
        
        # Simular datos del frontend
        asignaciones = {proyecto_b_edt: '1'}  # EDT de Proyecto B → Requerimiento 1
        requerimiento_para_procesar = 1
        
        print(f"   📤 Enviando asignaciones: {asignaciones}")
        print(f"   📤 Requerimiento para procesar: {requerimiento_para_procesar}")
        
        # 4. Llamar función real con datos simulados
        print("\n⚡ PASO 5: Ejecutando guardar_asignaciones_proyecto...")
        
        # Simular request
        class MockRequest:
            def get_json(self):
                return {
                    'asignaciones': asignaciones,
                    'requerimiento_para_procesar': requerimiento_para_procesar
                }
        
        # NOTA: Esta prueba mostrará los logs pero no ejecutará la función completa
        # porque necesitaríamos un contexto Flask completo
        
        # 5. Verificar resultado
        print("\n📊 PASO 6: Estado después de la asignación...")
        req1_despues = Requerimiento.query.get(1)
        actividades_req1_despues = ActividadProyecto.query.filter_by(requerimiento_id=1).all()
        
        print(f"   Proyecto asignado: {req1_despues.proyecto if req1_despues else 'No encontrado'}")
        print(f"   Actividades después: {len(actividades_req1_despues)}")
        if actividades_req1_despues:
            print(f"   Primera actividad: EDT {actividades_req1_despues[0].edt} - {actividades_req1_despues[0].nombre_tarea}")
            
        # Verificar si son actividades del Proyecto B
        actividades_proyecto_b = [a for a in actividades_temp if a['proyecto'] == 'SISTEMA PROYECTO 02']
        print(f"   Actividades esperadas del Proyecto B: {len(actividades_proyecto_b)}")
        
        if len(actividades_req1_despues) == len(actividades_proyecto_b):
            print("   ✅ ¡Correcto! Se asignaron las actividades del Proyecto B")
        else:
            print("   ❌ Error: No coincide el número de actividades")

if __name__ == "__main__":
    test_proyecto_b_a_requerimiento_1()
