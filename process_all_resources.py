#!/usr/bin/env python3
"""
Script para procesar todos los recursos existentes y crear trabajadores/avances
"""
import sys
sys.path.insert(0, '/app')

from app import create_app
from app.models import *
from app.controllers.proyectos_controller import crear_avances_actividad

app = create_app()

with app.app_context():
    print("🚀 PROCESANDO TODOS LOS RECURSOS EXISTENTES")
    print("=" * 60)
    
    # 1. Buscar todas las actividades con recursos
    actividades_con_recursos = ActividadProyecto.query.filter(
        ActividadProyecto.recursos.isnot(None),
        ActividadProyecto.recursos != ''
    ).all()
    
    print(f"📋 Actividades con recursos encontradas: {len(actividades_con_recursos)}")
    
    if not actividades_con_recursos:
        print("❌ No hay actividades con recursos para procesar")
        exit(1)
    
    # 2. Mostrar todas las actividades que vamos a procesar
    for i, actividad in enumerate(actividades_con_recursos, 1):
        print(f"   {i}. EDT {actividad.edt}: {actividad.nombre_tarea}")
        print(f"      Recursos: '{actividad.recursos}'")
    
    # 3. Procesar cada actividad
    total_trabajadores_creados = 0
    total_avances_creados = 0
    
    for actividad in actividades_con_recursos:
        try:
            print(f"\n🔧 Procesando actividad {actividad.edt}: {actividad.nombre_tarea}")
            
            # Verificar avances existentes antes
            avances_antes = AvanceActividad.query.filter_by(
                actividad_id=actividad.id
            ).count()
            
            # Ejecutar función
            crear_avances_actividad(
                requerimiento_id=actividad.requerimiento_id,
                actividad_id=actividad.id,
                recursos_string=actividad.recursos,
                progreso_actual=0.0
            )
            
            # Verificar avances después
            avances_despues = AvanceActividad.query.filter_by(
                actividad_id=actividad.id
            ).count()
            
            avances_nuevos = avances_despues - avances_antes
            if avances_nuevos > 0:
                print(f"   ✅ {avances_nuevos} avances creados")
                total_avances_creados += avances_nuevos
            else:
                print(f"   ⚠️ No se crearon avances nuevos")
                
        except Exception as e:
            print(f"   ❌ Error procesando actividad {actividad.edt}: {str(e)}")
            continue
    
    # 4. Commit para guardar todos los cambios
    try:
        db.session.commit()
        print(f"\n💾 Cambios guardados exitosamente")
    except Exception as e:
        print(f"\n❌ Error guardando cambios: {str(e)}")
        db.session.rollback()
    
    # 5. Resumen final
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   - Actividades procesadas: {len(actividades_con_recursos)}")
    print(f"   - Avances creados: {total_avances_creados}")
    
    # Verificar trabajadores creados hoy
    from datetime import date
    trabajadores_hoy = Trabajador.query.filter(
        Trabajador.created_at >= date.today()
    ).all()
    print(f"   - Trabajadores creados hoy: {len(trabajadores_hoy)}")
    
    for t in trabajadores_hoy:
        print(f"     • {t.nombre} (ID: {t.id})")
    
    # Verificar total de avances
    total_avances = AvanceActividad.query.count()
    print(f"   - Total de avances en sistema: {total_avances}")
    
    print(f"\n✅ Procesamiento completado")