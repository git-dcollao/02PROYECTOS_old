#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.controllers import procesar_proyecto_xlsx
from app.models import ActividadProyecto, Requerimiento, AvanceActividad, db

app = create_app()

def test_clave_compuesta():
    with app.app_context():
        print("🔧 PRUEBA: Clave compuesta EDT|NombreTarea")
        print("=" * 60)
        
        # 1. Limpiar BD
        print("🧹 Limpiando base de datos...")
        avances = AvanceActividad.query.all()
        for avance in avances:
            db.session.delete(avance)
        actividades = ActividadProyecto.query.all()
        for actividad in actividades:
            db.session.delete(actividad)
        db.session.commit()
        
        # 2. Crear actividades temporales simuladas
        print("📊 Creando actividades temporales...")
        actividades_temp = [
            # MASTER TAREAS (nivel 1)
            {'proyecto': 'MASTER TAREAS-all', 'edt': '1', 'nombre_tarea': 'msproj11', 'nivel_esquema': 1},
            {'proyecto': 'MASTER TAREAS-all', 'edt': '2', 'nombre_tarea': 'msproj11', 'nivel_esquema': 1},
            {'proyecto': 'MASTER TAREAS-all', 'edt': '3', 'nombre_tarea': 'msproj11', 'nivel_esquema': 1},
            
            # PROYECTO A (nivel 1)
            {'proyecto': 'SISTEMA PROYECTO 01', 'edt': '1', 'nombre_tarea': 'PROYECTO A', 'nivel_esquema': 1},
            {'proyecto': 'SISTEMA PROYECTO 01', 'edt': '1.1', 'nombre_tarea': 'TAREA A01', 'nivel_esquema': 2},
            {'proyecto': 'SISTEMA PROYECTO 01', 'edt': '1.2', 'nombre_tarea': 'TAREA A02', 'nivel_esquema': 2},
            
            # PROYECTO B (nivel 1)
            {'proyecto': 'SISTEMA PROYECTO 02', 'edt': '1', 'nombre_tarea': 'PROYECTO B', 'nivel_esquema': 1},
            {'proyecto': 'SISTEMA PROYECTO 02', 'edt': '1.1', 'nombre_tarea': 'TAREA B01', 'nivel_esquema': 2},
            {'proyecto': 'SISTEMA PROYECTO 02', 'edt': '1.2', 'nombre_tarea': 'TAREA B02', 'nivel_esquema': 2},
            
            # PROYECTO C (nivel 1)
            {'proyecto': 'SISTEMA PROYECTO 03', 'edt': '1', 'nombre_tarea': 'PROYECTO C', 'nivel_esquema': 1},
            {'proyecto': 'SISTEMA PROYECTO 03', 'edt': '1.1', 'nombre_tarea': 'TAREA C01', 'nivel_esquema': 2},
        ]
        
        procesar_proyecto_xlsx.actividades_temp = actividades_temp
        print(f"   ✅ {len(actividades_temp)} actividades temporales creadas")
        
        # 3. Simular mapeo como en el backend
        print("\n🗺️ Creando mapeo EDT|NombreTarea → Proyecto...")
        edt_to_proyecto = {}
        for actividad in actividades_temp:
            if actividad.get('nivel_esquema') == 1:  # Solo proyectos nivel 1
                edt = str(actividad.get('edt'))
                proyecto = actividad.get('proyecto')
                nombre_tarea = actividad.get('nombre_tarea')
                clave_compuesta = f"{edt}|{nombre_tarea}"
                if clave_compuesta not in edt_to_proyecto:
                    edt_to_proyecto[clave_compuesta] = proyecto
                    print(f"   📍 '{clave_compuesta}' → '{proyecto}'")
        
        # 4. Simular asignación del frontend: Proyecto B al requerimiento 1
        print("\n🎯 Simulando asignación Proyecto B → Requerimiento 1...")
        asignaciones = {'1|PROYECTO B': '1'}  # Nueva clave compuesta
        print(f"   📤 Asignaciones: {asignaciones}")
        
        # 5. Probar mapeo
        print("\n⚡ Probando mapeo...")
        for edt_nombre_tarea, requerimiento_id in asignaciones.items():
            nombre_proyecto_real = edt_to_proyecto.get(edt_nombre_tarea, None)
            print(f"   🔍 '{edt_nombre_tarea}' → '{nombre_proyecto_real}'")
            
            if nombre_proyecto_real:
                print(f"   ✅ ¡Mapeo correcto! Proyecto B se mapea a '{nombre_proyecto_real}'")
                
                # Verificar que las actividades coincidan
                actividades_proyecto_b = [a for a in actividades_temp if a['proyecto'] == nombre_proyecto_real]
                print(f"   📊 Actividades disponibles del proyecto: {len(actividades_proyecto_b)}")
                for act in actividades_proyecto_b:
                    print(f"      - EDT {act['edt']}: {act['nombre_tarea']}")
            else:
                print(f"   ❌ Error: No se encontró mapeo para '{edt_nombre_tarea}'")

if __name__ == "__main__":
    test_clave_compuesta()
