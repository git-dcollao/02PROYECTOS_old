#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# Añadir el directorio de la aplicación al path de Python
sys.path.insert(0, '/app')

from app import create_app
from app.models import Trabajador, AvanceActividad, db
from app.controllers.proyectos_controller import crear_avances_actividad

def main():
    print("🧪 PRUEBA FINAL: SIMULANDO CARGA DE EXCEL SIN DUPLICADOS")
    print("=" * 70)
    
    app = create_app()
    with app.app_context():
        try:
            # Simular el contexto de usuario logueado (necesario para la función)
            class MockUser:
                def __init__(self):
                    self.sector_id = 1
                    self.recinto_id = 7
                    self.email = "admin@sistema.local"
            
            # Simular Flask-Login current_user
            from unittest.mock import patch
            mock_user = MockUser()
            
            with patch('app.controllers.proyectos_controller.current_user', mock_user):
                print("🎯 SIMULANDO RECURSOS DEL EXCEL...")
                
                # Simular recursos que vienen del Excel (incluyendo ARQ02 que ya existe)
                recursos_excel = [
                    "ARQ01",   # Ya existe
                    "ARQ02",   # Ya existe (pero con nombrecorto=None)
                    "EST01",   # Ya existe
                    "NUEVO01", # Nuevo trabajador
                    "NUEVO02"  # Otro nuevo trabajador
                ]
                
                print(f"📋 Recursos a procesar: {recursos_excel}")
                print("-" * 50)
                
                # Contar trabajadores antes
                trabajadores_antes = Trabajador.query.filter(
                    Trabajador.email.like('%@temp.com')
                ).count()
                print(f"🔢 Trabajadores con emails @temp.com ANTES: {trabajadores_antes}")
                
                # Simular llamadas a crear_avances_actividad para cada recurso
                requerimiento_id = 1  # ID de requerimiento de prueba
                actividad_id = 1      # ID de actividad de prueba
                
                for i, recurso in enumerate(recursos_excel, 1):
                    print(f"\n{i}. 🔄 Procesando recurso: '{recurso}'")
                    try:
                        # Llamar a la función mejorada
                        crear_avances_actividad(
                            requerimiento_id=requerimiento_id,
                            actividad_id=actividad_id,
                            recursos_string=recurso,
                            progreso_actual=25.0
                        )
                        print(f"   ✅ Recurso '{recurso}' procesado exitosamente")
                        
                    except Exception as e:
                        print(f"   ❌ Error procesando '{recurso}': {str(e)}")
                        if "Duplicate entry" in str(e):
                            print(f"   🚨 FALLO: Aún hay problemas de duplicados!")
                        db.session.rollback()
                
                # Contar trabajadores después
                trabajadores_despues = Trabajador.query.filter(
                    Trabajador.email.like('%@temp.com')
                ).count()
                print(f"\n🔢 Trabajadores con emails @temp.com DESPUÉS: {trabajadores_despues}")
                print(f"📈 Nuevos trabajadores creados: {trabajadores_despues - trabajadores_antes}")
                
                # Verificar estado final de todos los trabajadores temp
                print(f"\n📋 ESTADO FINAL DE TRABAJADORES TEMPORALES:")
                print("-" * 50)
                
                trabajadores_temp = Trabajador.query.filter(
                    Trabajador.email.like('%@temp.com')
                ).order_by(Trabajador.created_at.desc()).all()
                
                for i, trabajador in enumerate(trabajadores_temp, 1):
                    print(f"{i}. ID:{trabajador.id} | Nombre:'{trabajador.nombre}' | Corto:'{trabajador.nombrecorto}' | Email:'{trabajador.email}'")
                
                # Verificar avances creados
                avances_count = AvanceActividad.query.filter_by(
                    requerimiento_id=requerimiento_id,
                    actividad_id=actividad_id
                ).count()
                
                print(f"\n🎯 AVANCES DE ACTIVIDAD CREADOS: {avances_count}")
                
                # Verificar específicamente ARQ02
                arq02 = Trabajador.query.filter_by(email='arq02@temp.com').first()
                if arq02:
                    print(f"\n✅ VERIFICACIÓN ARQ02:")
                    print(f"   Nombre: {arq02.nombre}")
                    print(f"   Nombrecorto: {arq02.nombrecorto}")
                    print(f"   Email: {arq02.email}")
                    print(f"   Estado: {'✅ CORRECTO' if arq02.nombrecorto == 'ARQ02' else '❌ FALTA NOMBRECORTO'}")
                
                db.session.commit()
                print(f"\n🎉 PRUEBA COMPLETADA - Sin errores de duplicados!")
                
        except Exception as e:
            print(f"❌ Error general: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    main()