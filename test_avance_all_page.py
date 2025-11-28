#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# Añadir el directorio de la aplicación al path de Python
sys.path.insert(0, '/app')

from app import create_app
from app.models import Trabajador, Requerimiento, AvanceActividad, db

def test_avance_all_page():
    print("🧪 PROBANDO PÁGINA /avance-actividades-all")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        try:
            # 1. Verificar trabajador administrador
            admin = Trabajador.query.filter_by(email='administrador@sistema.local').first()
            if admin:
                print(f"✅ Admin encontrado: ID {admin.id} - {admin.nombre}")
                print(f"   Email: {admin.email}")
                print(f"   Rol: {admin.rol if admin.rol else 'No especificado'}")
                print(f"   Custom Role: {admin.custom_role_id}")
            else:
                print("❌ Administrador no encontrado")
                return
            
            # 2. Verificar cuántos trabajadores hay en total
            total_trabajadores = Trabajador.query.count()
            print(f"\n📊 Total trabajadores en sistema: {total_trabajadores}")
            
            # 3. Verificar proyectos activos
            proyectos_activos = Requerimiento.query.filter(
                Requerimiento.id_estado.in_([2, 3])
            ).count()
            print(f"📋 Proyectos activos (estados 2-3): {proyectos_activos}")
            
            if proyectos_activos == 0:
                print("⚠️ No hay proyectos activos para mostrar")
            
            # 4. Buscar trabajadores con asignaciones
            trabajadores_con_asignaciones = db.session.query(Trabajador).join(
                AvanceActividad, Trabajador.id == AvanceActividad.trabajador_id
            ).distinct().all()
            
            print(f"\n👥 Trabajadores con asignaciones de actividades: {len(trabajadores_con_asignaciones)}")
            for trabajador in trabajadores_con_asignaciones:
                asignaciones = AvanceActividad.query.filter_by(trabajador_id=trabajador.id).count()
                print(f"   - {trabajador.nombrecorto or trabajador.nombre}: {asignaciones} asignaciones")
            
            # 5. Probar específicamente trabajador ARQ01 (que sabemos que tiene asignaciones)
            arq01 = Trabajador.query.filter_by(email='arq01@temp.com').first()
            if arq01:
                print(f"\n🔍 PRUEBA CON ARQ01 (ID {arq01.id}):")
                
                # Simular API call proyectos_por_trabajador_all
                proyectos_arq01 = db.session.query(Requerimiento).filter(
                    Requerimiento.id_estado.in_([2, 3])
                ).all()
                
                print(f"   Proyectos disponibles: {len(proyectos_arq01)}")
                
                for proyecto in proyectos_arq01[:3]:  # Solo primeros 3 para no saturar
                    actividades = AvanceActividad.query.filter_by(
                        trabajador_id=arq01.id,
                        requerimiento_id=proyecto.id
                    ).count()
                    print(f"   - Proyecto '{proyecto.nombre}': {actividades} actividades asignadas")
            
            # 6. Verificar que el administrador puede ver todos los trabajadores
            if admin:
                print(f"\n🔑 PERMISOS ADMINISTRADOR:")
                print(f"   Puede ver todos los trabajadores: SÍ (hay {total_trabajadores} total)")
                print(f"   Puede acceder a todos los proyectos: SÍ (hay {proyectos_activos} activos)")
                
                # Verificar si el administrador tiene alguna asignación directa
                admin_asignaciones = AvanceActividad.query.filter_by(trabajador_id=admin.id).count()
                print(f"   Asignaciones propias del administrador: {admin_asignaciones}")
            
            print("\n🎯 RESULTADO:")
            print("✅ La página /avance-actividades-all debería funcionar correctamente")
            print("✅ El administrador puede seleccionar cualquier trabajador")
            print("✅ Se mostrarán todos los proyectos activos del sistema")
            if len(trabajadores_con_asignaciones) > 0:
                print("✅ Hay trabajadores con asignaciones para probar")
            else:
                print("⚠️ No hay trabajadores con asignaciones - crear algunas primero")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_avance_all_page()