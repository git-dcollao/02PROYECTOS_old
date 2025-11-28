#!/usr/bin/env python3
"""
Script para asignar recintos al administrador via tabla AdministradorRecinto
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, AdministradorRecinto, Recinto, TipoRecinto

def asignar_recintos_administrador():
    app = create_app()
    
    with app.app_context():
        print("=== ASIGNAR RECINTOS A ADMINISTRADOR ===")
        
        # Usuario administrador
        admin = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if not admin:
            print("❌ No se encontró el administrador")
            return
        
        print(f"👤 Usuario: {admin.nombre}")
        print(f"   Email: {admin.email}")
        print(f"   Sector: {admin.sector.nombre if admin.sector else 'Sin sector'}")
        print(f"   Recinto: {admin.recinto.nombre if admin.recinto else 'Sin recinto'}")
        print()
        
        # Verificar asignaciones existentes
        asignaciones_actuales = AdministradorRecinto.query.filter_by(administrador_id=admin.id, activo=True).all()
        print(f"📋 Asignaciones actuales: {len(asignaciones_actuales)}")
        for asig in asignaciones_actuales:
            print(f"   - Recinto ID {asig.recinto_id}: {asig.recinto.nombre}")
        print()
        
        # Opción 1: Asignar TODOS los recintos del sector MUNICIPAL
        recintos_municipales = Recinto.query.join(
            TipoRecinto
        ).filter(
            TipoRecinto.id_sector == 1  # MUNICIPAL
        ).all()
        
        print(f"🏢 Recintos MUNICIPALES disponibles: {len(recintos_municipales)}")
        for recinto in recintos_municipales:
            print(f"   ID {recinto.id}: {recinto.nombre}")
            
            # Verificar si ya existe asignación
            existe = AdministradorRecinto.query.filter_by(
                administrador_id=admin.id,
                recinto_id=recinto.id
            ).first()
            
            if not existe:
                nueva_asignacion = AdministradorRecinto(
                    administrador_id=admin.id,
                    recinto_id=recinto.id,
                    activo=True
                )
                db.session.add(nueva_asignacion)
                print(f"   ✅ Nueva asignación creada")
            else:
                if not existe.activo:
                    existe.activo = True
                    print(f"   ✅ Asignación reactivada")
                else:
                    print(f"   ⚪ Ya asignado")
        
        # Guardar cambios
        db.session.commit()
        print(f"\n✅ Asignaciones actualizadas")
        
        # Verificar resultado final
        asignaciones_finales = AdministradorRecinto.query.filter_by(administrador_id=admin.id, activo=True).all()
        print(f"\n📊 RESULTADO FINAL:")
        print(f"Total asignaciones activas: {len(asignaciones_finales)}")
        for asig in asignaciones_finales:
            print(f"   - {asig.recinto.nombre}")

if __name__ == "__main__":
    asignar_recintos_administrador()