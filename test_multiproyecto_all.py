#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para validar que los 3 proyectos del archivo all.xlsx
se detectan correctamente para asignación a requerimientos.
"""

import requests
import json

def test_upload_all_xlsx():
    """
    Test que sube el archivo all.xlsx y verifica que los 3 proyectos 
    sean detectados correctamente para asignación.
    """
    print("🧪 INICIANDO TEST - Multi-proyecto all.xlsx")
    print("=" * 60)
    
    url = 'http://127.0.0.1:5050/procesar-proyecto-xlsx'
    
    # Abrir el archivo all.xlsx
    try:
        with open('all.xlsx', 'rb') as file:
            files = {'archivo': ('all.xlsx', file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print("📤 Subiendo archivo all.xlsx al servidor...")
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Archivo procesado correctamente")
                print(f"📊 Status: {data['status']}")
                print(f"📝 Mensaje: {data['message']}")
                
                # Verificar que hay proyectos disponibles
                if 'proyectos_para_asignar' in data:
                    proyectos = data['proyectos_para_asignar']
                    print(f"\n🎯 RESULTADO PRINCIPAL: {len(proyectos)} proyectos detectados")
                    
                    if len(proyectos) == 3:
                        print("✅ ÉXITO: Se detectaron los 3 proyectos esperados")
                        
                        for i, proyecto in enumerate(proyectos, 1):
                            print(f"\n   📦 Proyecto {i}:")
                            print(f"      - EDT: {proyecto.get('edt', 'N/A')}")
                            print(f"      - Nombre: {proyecto.get('nombre_tarea', 'N/A')}")
                            print(f"      - Archivo: {proyecto.get('archivo', 'N/A')}")
                            if 'proyecto_origen' in proyecto:
                                print(f"      - Origen: {proyecto['proyecto_origen']}")
                        
                        print("\n🎉 TEST SUPERADO: Los 3 proyectos están disponibles para asignación")
                        return True
                        
                    else:
                        print(f"❌ ERROR: Se esperaban 3 proyectos, pero se encontraron {len(proyectos)}")
                        
                        if proyectos:
                            print("\n📋 Proyectos encontrados:")
                            for i, proyecto in enumerate(proyectos, 1):
                                print(f"   {i}. EDT: {proyecto.get('edt', 'N/A')} - {proyecto.get('nombre_tarea', 'N/A')}")
                        
                        return False
                else:
                    print("❌ ERROR: No se encontraron proyectos en la respuesta")
                    return False
                    
            else:
                print(f"❌ ERROR HTTP: {response.status_code}")
                print(f"📄 Respuesta: {response.text}")
                return False
                
    except FileNotFoundError:
        print("❌ ERROR: Archivo all.xlsx no encontrado en el directorio actual")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor. ¿Está ejecutándose Flask?")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {str(e)}")
        return False

def verificar_servidor():
    """Verifica que el servidor Flask esté funcionando"""
    try:
        response = requests.get('http://127.0.0.1:5050')
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Verificando que el servidor Flask esté funcionando...")
    
    if not verificar_servidor():
        print("❌ El servidor Flask no está funcionando en http://127.0.0.1:5050")
        print("   Por favor, ejecuta: python app.py")
        exit(1)
    
    print("✅ Servidor Flask funcionando correctamente")
    print()
    
    # Ejecutar test
    resultado = test_upload_all_xlsx()
    
    print("\n" + "=" * 60)
    if resultado:
        print("🎉 TEST COMPLETADO EXITOSAMENTE")
        print("   Los 3 proyectos del archivo all.xlsx se detectan correctamente")
    else:
        print("💥 TEST FALLÓ")
        print("   Hay problemas con la detección multi-proyecto")
    
    print("=" * 60)
