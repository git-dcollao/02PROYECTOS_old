#!/usr/bin/env python3
"""
Script para probar el procesamiento de Excel con multi-proyecto
"""

import os
import sys
import pandas as pd
from werkzeug.datastructures import FileStorage
import io
from unittest.mock import MagicMock

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar la aplicación
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.controllers import procesar_proyecto_xlsx

def simular_carga_archivo():
    """Simular la carga del archivo all.xlsx"""
    
    app = create_app()
    
    with app.app_context():
        # Leer el archivo Excel existente
        archivo_path = "DOCS/Tip/all.xlsx"
        
        if not os.path.exists(archivo_path):
            print(f"❌ Archivo no encontrado: {archivo_path}")
            return
            
        # Leer contenido del archivo
        with open(archivo_path, 'rb') as f:
            contenido_archivo = f.read()
        
        # Crear un objeto FileStorage simulado
        archivo_simulado = FileStorage(
            stream=io.BytesIO(contenido_archivo),
            filename='all.xlsx',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        print("🔥 INICIANDO SIMULACIÓN DE CARGA DE ARCHIVO...")
        print(f"📄 Archivo: all.xlsx")
        print(f"📊 Tamaño: {len(contenido_archivo)} bytes")
        print()
        
        try:
            # Simular Flask request
            from flask import Flask
            from werkzeug.test import Client
            from werkzeug.wrappers import BaseResponse
            
            # Crear un contexto de request simulado
            with app.test_request_context('/', method='POST'):
                from flask import g, request
                
                # Almacenar el archivo en request.files simulado
                class MockRequest:
                    files = {'archivo_xlsx': archivo_simulado}
                    form = {'requerimiento_id': '1'}
                
                # Reemplazar request temporalmente
                import app.controllers
                original_request = app.controllers.request
                app.controllers.request = MockRequest()
                
                # Procesar el archivo usando la función original
                resultado = procesar_proyecto_xlsx()
                
                # Restaurar request original
                app.controllers.request = original_request
            
            print("✅ Procesamiento completado")
            print(f"📋 Resultado: {type(resultado)}")
            
            # Verificar si hay actividades temporales
            if hasattr(procesar_proyecto_xlsx, 'actividades_temp'):
                actividades_temp = procesar_proyecto_xlsx.actividades_temp
                print(f"📊 Actividades temporales encontradas: {len(actividades_temp)}")
                
                if actividades_temp:
                    print("\n📋 PRIMERAS 5 ACTIVIDADES TEMPORALES:")
                    for i, actividad in enumerate(actividades_temp[:5]):
                        proyecto = actividad.get('proyecto', 'NO_DEFINIDO')
                        edt = actividad.get('edt', 'NO_EDT')
                        nombre = actividad.get('nombre_tarea', 'NO_NOMBRE')
                        print(f"  {i+1}. {proyecto} | {edt} | {nombre}")
            else:
                print("❌ No se encontraron actividades temporales")
                
        except Exception as e:
            print(f"❌ Error durante el procesamiento: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    simular_carga_archivo()
