#!/usr/bin/env python3
"""
Script rápido para corregir permisos de usuario
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Trabajador, Sector, Recinto, UserRole

def fix_user_permissions():
    app = create_app()
    
    with app.app_context():
        print("=== DIAGNÓSTICO RÁPIDO ===")
        
        # Buscar todos los trabajadores con email (usuarios activos)
        usuarios = Trabajador.query.filter(Trabajador.email.isnot(None)).all()
        
        for usuario in usuarios:
            print(f"Usuario: {usuario.email}")
            print(f"  - Nombre: {usuario.nombre}")
            print(f"  - Rol: {usuario.rol}")
            print(f"  - Sector ID: {usuario.sector_id}")
            print(f"  - Recinto ID: {usuario.recinto_id}")
            
            # Si es SUPERADMIN, no necesita recinto
            if usuario.rol and usuario.rol.name == 'SUPERADMIN':
                print("  ✅ SUPERADMIN - No necesita recinto")
                continue
            
            # Si no tiene recinto, asignar uno
            if not usuario.recinto_id:
                print("  ❌ Sin recinto asignado")
                
                # Buscar primer recinto disponible
                primer_recinto = Recinto.query.first()
                if primer_recinto:
                    usuario.recinto_id = primer_recinto.id
                    if primer_recinto.tiporecinto:
                        usuario.sector_id = primer_recinto.tiporecinto.id_sector
                    
                    print(f"  ✅ Asignado a recinto: {primer_recinto.nombre}")
                    print(f"  ✅ Asignado a sector: {primer_recinto.tiporecinto.sector.nombre if primer_recinto.tiporecinto else 'N/A'}")
        
        # Guardar cambios
        db.session.commit()
        print("\n✅ Permisos actualizados exitosamente")
        
        print("\n=== USUARIOS FINALES ===")
        for usuario in usuarios:
            recinto_nombre = usuario.recinto.nombre if usuario.recinto else "Sin recinto"
            print(f"{usuario.email} -> {recinto_nombre}")

if __name__ == "__main__":
    fix_user_permissions()