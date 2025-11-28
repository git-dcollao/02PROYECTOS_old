#!/usr/bin/env python3
"""
Script para asignar grupos a proyectos existentes
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Requerimiento, Grupo
import logging

def asignar_grupos_proyectos():
    """Asignar grupos a proyectos existentes para pruebas"""
    app = create_app()
    
    with app.app_context():
        try:
            # Obtener proyectos en estado 4 sin grupo
            proyectos_sin_grupo = Requerimiento.query.filter(
                Requerimiento.id_estado == 4,
                Requerimiento.id_grupo.is_(None),
                Requerimiento.activo == True
            ).all()
            
            print(f"🔍 Encontrados {len(proyectos_sin_grupo)} proyectos sin grupo")
            
            # Obtener el primer grupo disponible
            grupo = Grupo.query.filter_by(activo=True).first()
            
            if not grupo:
                print("❌ No se encontraron grupos activos")
                return False
                
            print(f"📋 Asignando grupo '{grupo.nombre}' (ID: {grupo.id})")
            
            # Asignar el grupo a todos los proyectos
            proyectos_actualizados = 0
            for proyecto in proyectos_sin_grupo:
                proyecto.id_grupo = grupo.id
                proyectos_actualizados += 1
                print(f"   ✅ Proyecto '{proyecto.nombre}' asignado al grupo '{grupo.nombre}'")
            
            # Guardar cambios
            db.session.commit()
            
            print(f"🎉 {proyectos_actualizados} proyectos actualizados exitosamente")
            return True
                
        except Exception as e:
            print(f"❌ Error al asignar grupos: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if asignar_grupos_proyectos():
        print("🎉 Asignación de grupos completada exitosamente")
    else:
        print("💥 Asignación de grupos fallida")
        sys.exit(1)
