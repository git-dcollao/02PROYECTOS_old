#!/usr/bin/env python3
"""
Script para debuggar el problema de trabajadores no guardados
"""
import sys
import os

# Agregar la ruta del proyecto al sys.path
sys.path.insert(0, '/app')

from app import create_app
from app.models import *
from datetime import datetime, date

# Crear contexto de la aplicación
app = create_app()

with app.app_context():
    print("🔍 DIAGNÓSTICO: Trabajadores y recursos en la base de datos")
    print("=" * 60)
    
    # 1. Verificar trabajadores creados recientemente
    print("\n1. TRABAJADORES RECIENTES:")
    trabajadores_recientes = Trabajador.query.filter(
        Trabajador.created_at >= date(2025, 11, 17)
    ).all()
    print(f"   Total: {len(trabajadores_recientes)}")
    for t in trabajadores_recientes[:10]:
        print(f"   - {t.nombre} (ID: {t.id}, RUT: {t.rut})")
    
    # 2. Verificar registros de AvanceActividad
    print("\n2. REGISTROS DE AVANCE_ACTIVIDAD:")
    avances = AvanceActividad.query.all()
    print(f"   Total: {len(avances)}")
    for a in avances[:5]:
        print(f"   - Trabajador {a.trabajador_id} en Req {a.requerimiento_id}")
    
    # 3. Verificar actividades de proyecto 
    print("\n3. ACTIVIDADES DE PROYECTO:")
    actividades = ActividadProyecto.query.all()
    print(f"   Total: {len(actividades)}")
    for act in actividades[:5]:
        print(f"   - {act.edt}: {act.nombre_tarea}")
        print(f"     Recursos: {act.recursos}")
    
    # 4. Verificar requerimientos con proyecto asignado
    print("\n4. REQUERIMIENTOS CON PROYECTO:")
    reqs_con_proyecto = Requerimiento.query.filter(
        Requerimiento.proyecto.isnot(None)
    ).all()
    print(f"   Total: {len(reqs_con_proyecto)}")
    for req in reqs_con_proyecto[:3]:
        print(f"   - REQ-{req.id}: {req.proyecto}")
        actividades_req = ActividadProyecto.query.filter_by(requerimiento_id=req.id).all()
        print(f"     Actividades: {len(actividades_req)}")
        for act in actividades_req[:2]:
            print(f"       - {act.edt}: {act.recursos or 'Sin recursos'}")
    
    print("\n✅ Diagnóstico completado")