#!/usr/bin/env python3
"""
Script para verificar que el administrador puede ver los requerimientos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, AdministradorRecinto, Recinto, Requerimiento

def verificar_permisos_administrador():
    app = create_app()
    
    with app.app_context():
        # Buscar el administrador
        admin = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if not admin:
            print("❌ No se encontró el administrador")
            return
            
        print("=== VERIFICACIÓN DE PERMISOS ADMINISTRADOR ===")
        print(f"👤 Usuario: {admin.nombre}")
        print(f"   Email: {admin.email}")
        print(f"   Es SUPERADMIN: {admin.is_superadmin()}")
        print(f"   Tiene permisos página /requerimientos: {admin.has_page_permission('/requerimientos')}")
        print()
        
        # Verificar asignaciones AdministradorRecinto
        asignaciones = AdministradorRecinto.query.filter_by(
            administrador_id=admin.id,
            activo=True
        ).all()
        
        print(f"📋 Asignaciones AdministradorRecinto: {len(asignaciones)}")
        recintos_admin = []
        for asig in asignaciones:
            print(f"   - Recinto ID {asig.recinto_id}: {asig.recinto.nombre}")
            recintos_admin.append(asig.recinto_id)
        print()
        
        # Buscar requerimientos que debería ver
        print("🔍 REQUERIMIENTOS QUE DEBERÍA VER:")
        print("Opción 1: Por asignaciones específicas (AdministradorRecinto)")
        
        # Simulamos la lógica del controlador
        if admin.is_superadmin():
            reqs_admin = Requerimiento.query.all()
            print("   Como SUPERADMIN vería: TODOS")
        elif admin.has_page_permission('/requerimientos'):
            if recintos_admin:
                reqs_admin = Requerimiento.query.filter(
                    Requerimiento.id_recinto.in_(recintos_admin)
                ).all()
                print(f"   Por recintos asignados ({len(recintos_admin)}): {len(reqs_admin)} requerimientos")
            else:
                reqs_admin = []
                print("   Sin asignaciones: 0 requerimientos")
        else:
            reqs_admin = []
            print("   Sin permisos: 0 requerimientos")
            
        print()
        print("📊 DETALLE DE REQUERIMIENTOS VISIBLES:")
        for req in reqs_admin:
            print(f"   ID {req.id}: {req.nombre}")
            print(f"      - Recinto: {req.recinto.nombre if req.recinto else 'No asignado'}")
            print(f"      - Sector: {req.sector.nombre if req.sector else 'No asignado'}")
        
        print()
        print("🎯 RESULTADO:")
        print(f"   El administrador DEBERÍA ver {len(reqs_admin)} requerimiento(s)")
        if len(reqs_admin) > 0:
            print("   ✅ Permisos configurados correctamente")
        else:
            print("   ❌ Problema de configuración")

if __name__ == "__main__":
    verificar_permisos_administrador()