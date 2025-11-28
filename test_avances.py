#!/usr/bin/env python3
"""
Script para probar la función crear_avances_actividad corregida
"""
import sys
sys.path.insert(0, '/app')

from app import create_app
from app.models import *
from app.controllers.proyectos_controller import crear_avances_actividad

app = create_app()

with app.app_context():
    print("🔧 PROBANDO FUNCIÓN CORREGIDA: crear_avances_actividad")
    print("=" * 60)
    
    # 1. Buscar una actividad con recursos para probar
    actividad = ActividadProyecto.query.filter(
        ActividadProyecto.recursos.isnot(None),
        ActividadProyecto.recursos != ''
    ).first()
    
    if not actividad:
        print("❌ No hay actividades con recursos para probar")
        exit(1)
    
    print(f"📋 Actividad de prueba:")
    print(f"   - EDT: {actividad.edt}")
    print(f"   - Nombre: {actividad.nombre_tarea}")
    print(f"   - Recursos: '{actividad.recursos}'")
    print(f"   - Requerimiento ID: {actividad.requerimiento_id}")
    print(f"   - Actividad ID: {actividad.id}")
    
    # 2. Verificar estado antes
    avances_antes = AvanceActividad.query.filter_by(
        actividad_id=actividad.id
    ).count()
    print(f"\n📊 Avances antes: {avances_antes}")
    
    # 3. Probar la función
    try:
        print(f"\n🔧 Ejecutando crear_avances_actividad...")
        print(f"   Parámetros:")
        print(f"   - requerimiento_id: {actividad.requerimiento_id}")
        print(f"   - actividad_id: {actividad.id}")
        print(f"   - recursos_string: '{actividad.recursos}'")
        print(f"   - progreso_actual: 0.0")
        
        crear_avances_actividad(
            requerimiento_id=actividad.requerimiento_id,
            actividad_id=actividad.id,
            recursos_string=actividad.recursos,
            progreso_actual=0.0
        )
        
        # Commit para guardar cambios
        db.session.commit()
        print(f"✅ Función ejecutada correctamente")
        
    except Exception as e:
        print(f"❌ Error al ejecutar función: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
    
    # 4. Verificar estado después
    avances_despues = AvanceActividad.query.filter_by(
        actividad_id=actividad.id
    ).count()
    print(f"\n📊 Avances después: {avances_despues}")
    
    if avances_despues > avances_antes:
        print(f"✅ ¡Éxito! Se crearon {avances_despues - avances_antes} nuevos avances")
        
        # Mostrar detalles de los avances creados
        avances = AvanceActividad.query.filter_by(
            actividad_id=actividad.id
        ).all()
        
        for i, avance in enumerate(avances, 1):
            print(f"   {i}. Trabajador: {avance.trabajador.nombre} (ID: {avance.trabajador.id})")
            print(f"      Progreso: {avance.progreso_actual}%")
            print(f"      Fecha: {avance.fecha_registro}")
    else:
        print(f"⚠️ No se crearon avances nuevos")
    
    # 5. Mostrar trabajadores relacionados con recursos
    if actividad.recursos:
        recursos_separados = actividad.recursos.replace(';', ',').split(',')
        print(f"\n👥 Trabajadores para recursos '{actividad.recursos}':")
        for recurso in recursos_separados:
            recurso = recurso.strip()
            if recurso:
                trabajador = Trabajador.query.filter_by(nombre=recurso).first()
                if trabajador:
                    print(f"   ✅ {recurso} → Trabajador ID {trabajador.id}")
                else:
                    print(f"   ❌ {recurso} → No encontrado")
    
    print(f"\n✅ Prueba completada")