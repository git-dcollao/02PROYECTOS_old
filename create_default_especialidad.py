#!/usr/bin/env python3
"""
Script para crear una especialidad por defecto si no existe
"""

from app import create_app
from app.models import db, Especialidad

def crear_especialidad_defecto():
    app = create_app()
    
    with app.app_context():
        # Verificar si existe especialidad "General" o "Responsable General"
        especialidad_general = Especialidad.query.filter_by(nombre='General').first()
        especialidad_responsable = Especialidad.query.filter_by(nombre='Responsable General').first()
        
        if not especialidad_general and not especialidad_responsable:
            # Crear especialidad por defecto
            nueva_especialidad = Especialidad(nombre='Responsable General')
            db.session.add(nueva_especialidad)
            db.session.commit()
            print("✅ Especialidad 'Responsable General' creada exitosamente")
        else:
            print("ℹ️ Ya existe una especialidad por defecto")
            if especialidad_general:
                print(f"   - General (ID: {especialidad_general.id})")
            if especialidad_responsable:
                print(f"   - Responsable General (ID: {especialidad_responsable.id})")

if __name__ == '__main__':
    crear_especialidad_defecto()
