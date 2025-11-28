#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import ActividadProyecto, Requerimiento
from app.controllers import procesar_proyecto_xlsx

app = create_app()

def diagnosticar_problema():
    with app.app_context():
        print("🔍 DIAGNÓSTICO DEL PROBLEMA DE ASIGNACIÓN")
        print("=" * 60)
        
        # 1. Ver qué actividades temporales existen
        print("\n📋 ACTIVIDADES TEMPORALES:")
        if hasattr(procesar_proyecto_xlsx, 'actividades_temp'):
            actividades_temp = procesar_proyecto_xlsx.actividades_temp
            proyectos_unicos = {}
            
            for i, act in enumerate(actividades_temp):
                if act.get('nivel_esquema') == 1:  # Solo proyectos
                    edt = str(act.get('edt'))
                    proyecto = act.get('proyecto')
                    proyectos_unicos[edt] = proyecto
                    print(f"   {i+1}. EDT: {edt} → Proyecto: '{proyecto}'")
            
            print(f"\n🗺️ MAPEO EDT → PROYECTO ÚNICO:")
            for edt, proyecto in proyectos_unicos.items():
                print(f"   EDT '{edt}' → '{proyecto}'")
        else:
            print("   ❌ No hay actividades temporales en memoria")
        
        # 2. Ver actividades en BD por requerimiento
        print("\n💾 ACTIVIDADES EN BASE DE DATOS:")
        for req_id in [1, 2, 3]:
            actividades = ActividadProyecto.query.filter_by(requerimiento_id=req_id).all()
            req = Requerimiento.query.get(req_id)
            proyecto_asignado = req.proyecto if req else "Sin asignar"
            
            print(f"   📋 Requerimiento {req_id} (Proyecto: {proyecto_asignado}):")
            if actividades:
                for act in actividades[:3]:  # Solo primeras 3 para ver
                    print(f"      - EDT {act.edt}: {act.nombre_tarea}")
                if len(actividades) > 3:
                    print(f"      ... y {len(actividades) - 3} más")
                print(f"      Total: {len(actividades)} actividades")
            else:
                print("      Sin actividades")
        
        # 3. Simular problema específico
        print("\n🎯 SIMULACIÓN DEL PROBLEMA:")
        print("Cuando asignas 'Proyecto B' al requerimiento ID=1...")
        
        # Ejemplo: Si tienes EDT '1' = Proyecto A, y EDT '2' = Proyecto B
        # pero el frontend envía {'1': '1'} o {'2': '1'}
        print("Frontend probablemente envía algo como:")
        print("   asignaciones = {'2': '1'}  # EDT '2' al requerimiento 1")
        print("   requerimiento_para_procesar = 1")
        
        print("Pero luego el backend busca actividades con:")
        print("   nombre_proyecto_real = edt_to_proyecto.get('2')  # = 'Proyecto B'")
        print("   if actividad_data.get('proyecto') == 'Proyecto B':")
        
        print("\n❓ PREGUNTA CLAVE:")
        print("¿Los nombres de proyecto en las actividades temporales coinciden exactamente")
        print("con lo que muestra el frontend?")

if __name__ == "__main__":
    diagnosticar_problema()
