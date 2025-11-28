#!/usr/bin/env python3
"""
Script para crear un requerimiento de prueba y verificar el sistema
"""
import os
import sys
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Requerimiento, Sector, TipoRecinto, Recinto, Estado

def crear_requerimiento_prueba():
    app = create_app()
    
    with app.app_context():
        print("=== CREACIÓN DE REQUERIMIENTO DE PRUEBA ===")
        
        # Verificar requerimientos existentes
        todos_req = Requerimiento.query.all()
        print(f"📋 Total de requerimientos en sistema: {len(todos_req)}")
        
        # Mostrar requerimientos por estado
        for estado_id in [1, 2, 3, 4]:
            count = Requerimiento.query.filter_by(id_estado=estado_id).count()
            estado = Estado.query.get(estado_id)
            estado_nombre = estado.nombre if estado else f"Estado {estado_id}"
            print(f"   Estado {estado_id} ({estado_nombre}): {count} requerimientos")
        
        # Verificar si hay requerimientos en preparación (estado 2)
        req_preparacion = Requerimiento.query.filter_by(id_estado=2).first()
        
        if req_preparacion:
            print(f"\n✅ Requerimiento en preparación encontrado: #{req_preparacion.id}")
        else:
            print("\n❌ No hay requerimientos en preparación. Creando uno de prueba...")
            
            # Obtener datos necesarios
            sector = Sector.query.first()
            tipo_recinto = TipoRecinto.query.first()
            recinto = Recinto.query.first()
            estado_preparacion = Estado.query.get(2)  # Estado "En Desarrollo - Preparación"
            
            if not all([sector, tipo_recinto, recinto, estado_preparacion]):
                print("❌ No se encontraron datos básicos necesarios")
                return
            
            # Crear requerimiento de prueba
            nuevo_req = Requerimiento(
                nombre="PROYECTO DE PRUEBA - COMPLETITUD",
                descripcion="Proyecto para probar el sistema de completitud con observaciones requeridas",
                fecha=datetime.utcnow(),
                fecha_aceptacion=datetime.utcnow(),
                id_sector=sector.id,
                id_tiporecinto=tipo_recinto.id,
                id_recinto=recinto.id,
                id_estado=2,  # En Desarrollo - Preparación
                activo=True
            )
            
            try:
                db.session.add(nuevo_req)
                db.session.commit()
                print(f"✅ Requerimiento de prueba creado: #{nuevo_req.id}")
                req_preparacion = nuevo_req
            except Exception as e:
                print(f"❌ Error al crear requerimiento: {e}")
                db.session.rollback()
                return
        
        # Ahora probar el requerimiento
        print(f"\n🧪 PROBANDO REQUERIMIENTO #{req_preparacion.id}:")
        print(f"   Nombre: {req_preparacion.nombre}")
        
        # Calcular completitud actual
        completitud = 0
        detalles = []
        
        # Verificar cada campo
        if req_preparacion.id_tipologia:
            completitud += 15
            detalles.append("✅ Tipología (15%)")
        else:
            detalles.append("❌ Tipología (0%)")
        
        if req_preparacion.id_financiamiento:
            completitud += 15
            detalles.append("✅ Financiamiento (15%)")
        else:
            detalles.append("❌ Financiamiento (0%)")
        
        if req_preparacion.id_tipoproyecto:
            completitud += 15
            detalles.append("✅ Tipo Proyecto (15%)")
        else:
            detalles.append("❌ Tipo Proyecto (0%)")
        
        if req_preparacion.id_prioridad:
            completitud += 15
            detalles.append("✅ Prioridad (15%)")
        else:
            detalles.append("❌ Prioridad (0%)")
        
        if req_preparacion.id_grupo:
            completitud += 15
            detalles.append("✅ Grupo (15%)")
        else:
            detalles.append("❌ Grupo (0%)")
        
        equipos_count = req_preparacion.equipos_trabajo.count()
        if equipos_count > 0:
            completitud += 15
            detalles.append(f"✅ Equipo ({equipos_count} miembros) (15%)")
        else:
            detalles.append("❌ Equipo (0 miembros) (0%)")
        
        if req_preparacion.observacion and req_preparacion.observacion.strip():
            completitud += 10
            detalles.append("✅ Observaciones (10%)")
        else:
            detalles.append("❌ Observaciones (0%)")
        
        print(f"\n📊 COMPLETITUD ACTUAL: {completitud}%")
        for detalle in detalles:
            print(f"   {detalle}")
        
        # Verificar si puede cambiar de estado
        puede_avanzar = all([
            req_preparacion.id_tipologia,
            req_preparacion.id_financiamiento,
            req_preparacion.id_tipoproyecto,  
            req_preparacion.id_prioridad,
            req_preparacion.id_grupo,
            equipos_count > 0,
            req_preparacion.observacion and req_preparacion.observacion.strip()
        ])
        
        if puede_avanzar:
            print(f"\n🚀 ESTADO: ✅ Puede avanzar (100% completo)")
        else:
            print(f"\n⏳ ESTADO: ❌ No puede avanzar (requiere 100%)")
        
        print(f"\n🌐 PRUEBA EN NAVEGADOR:")
        print(f"URL: http://127.0.0.1:5050/requerimientos_completar")
        print(f"Buscar requerimiento: #{req_preparacion.id}")

if __name__ == "__main__":
    crear_requerimiento_prueba()
