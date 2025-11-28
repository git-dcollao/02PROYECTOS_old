#!/usr/bin/env python3
"""
Script para diagnosticar requerimientos y permisos de administrador
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, Requerimiento, Sector, Recinto

def diagnosticar_requerimientos():
    app = create_app()
    
    with app.app_context():
        print("=== DIAGNÓSTICO DE REQUERIMIENTOS ===")
        
        # Usuario administrador
        admin = Trabajador.query.filter_by(email='administrador@sistema.local').first()
        if admin:
            print(f"👤 Usuario: {admin.nombre}")
            print(f"   Email: {admin.email}")
            print(f"   Sector ID: {admin.sector_id}")
            print(f"   Recinto ID: {admin.recinto_id}")
            if admin.sector:
                print(f"   Sector: {admin.sector.nombre}")
            if admin.recinto:
                print(f"   Recinto: {admin.recinto.nombre}")
            print()
        
        # Todos los requerimientos
        requerimientos = Requerimiento.query.all()
        print(f"📋 Total de requerimientos en sistema: {len(requerimientos)}")
        print()
        
        if requerimientos:
            print("=== DETALLE DE REQUERIMIENTOS ===")
            for req in requerimientos[:10]:  # Solo los primeros 10
                print(f"ID: {req.id}")
                print(f"   Nombre: {req.nombre[:50]}...")
                print(f"   Sector ID: {req.id_sector}")
                print(f"   Recinto ID: {req.id_recinto}")
                if req.sector:
                    print(f"   Sector: {req.sector.nombre}")
                if req.recinto:
                    print(f"   Recinto: {req.recinto.nombre}")
                print(f"   Solicitante ID: {req.solicitante_id if hasattr(req, 'solicitante_id') else 'N/A'}")
                print("---")
        
        print("\n=== SECTORES DISPONIBLES ===")
        sectores = Sector.query.all()
        for sector in sectores:
            print(f"ID: {sector.id} - {sector.nombre}")
            
        print("\n=== RECINTOS DISPONIBLES ===")
        recintos = Recinto.query.all()
        for recinto in recintos:
            sector_nombre = recinto.tiporecinto.sector.nombre if recinto.tiporecinto and recinto.tiporecinto.sector else "Sin sector"
            print(f"ID: {recinto.id} - {recinto.nombre} (Sector: {sector_nombre})")
        
        # Verificar qué requerimientos debería ver el administrador
        if admin:
            print(f"\n=== REQUERIMIENTOS QUE DEBERÍA VER EL ADMINISTRADOR ===")
            
            # Filtrar por sector del administrador
            reqs_por_sector = Requerimiento.query.filter_by(id_sector=admin.sector_id).all()
            print(f"Por sector ({admin.sector.nombre if admin.sector else admin.sector_id}): {len(reqs_por_sector)}")
            
            # Filtrar por recinto del administrador
            if admin.recinto_id:
                reqs_por_recinto = Requerimiento.query.filter_by(id_recinto=admin.recinto_id).all()
                print(f"Por recinto ({admin.recinto.nombre if admin.recinto else admin.recinto_id}): {len(reqs_por_recinto)}")

if __name__ == "__main__":
    diagnosticar_requerimientos()