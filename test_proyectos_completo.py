#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os

def crear_excel_prueba():
    """Crear archivo Excel de prueba para validar el flujo completo después de la migración"""
    
    # Datos de prueba para proyectos
    datos_proyectos = [
        {
            'PROYECTO': 'PROYECTO 01',
            'ETAPA N1': 'PLANIFICACION',
            'ETAPA N2': 'DISEÑO INICIAL',
            'ETAPA N3': 'ANALISIS REQUERIMIENTOS',
            'ETAPA N4': 'DOCUMENTACION TECNICA',
            'ACTIVIDAD': 'Revisión de especificaciones técnicas',
            'DURACION': '5 días',
            'PRECEDENCIA': '',
            'RECURSOS': 'Analista Senior, Documentador',
            'OBSERVACIONES': 'Primera actividad del proyecto - validación post-migración'
        },
        {
            'PROYECTO': 'PROYECTO 01',
            'ETAPA N1': 'PLANIFICACION',
            'ETAPA N2': 'DISEÑO INICIAL', 
            'ETAPA N3': 'ANALISIS REQUERIMIENTOS',
            'ETAPA N4': 'VALIDACION FUNCIONAL',
            'ACTIVIDAD': 'Validación de casos de uso',
            'DURACION': '3 días',
            'PRECEDENCIA': 'Revisión de especificaciones técnicas',
            'RECURSOS': 'Analista Funcional, Tester',
            'OBSERVACIONES': 'Depende de la actividad anterior'
        },
        {
            'PROYECTO': 'PROYECTO 02',
            'ETAPA N1': 'DESARROLLO',
            'ETAPA N2': 'IMPLEMENTACION BACKEND',
            'ETAPA N3': 'MIGRACION CONTROLADORES',
            'ETAPA N4': 'OPTIMIZACION ARQUITECTURA',
            'ACTIVIDAD': 'Migración de funciones duplicadas',
            'DURACION': '2 días',
            'PRECEDENCIA': '',
            'RECURSOS': 'Developer Senior, DevOps',
            'OBSERVACIONES': 'Proyecto de mejora arquitectónica - test post-migración'
        },
        {
            'PROYECTO': 'PROYECTO 02',
            'ETAPA N1': 'DESARROLLO',
            'ETAPA N2': 'IMPLEMENTACION BACKEND',
            'ETAPA N3': 'TESTING INTEGRACION',
            'ETAPA N4': 'VALIDACION FUNCIONAL',
            'ACTIVIDAD': 'Testing de flujo completo después de migración',
            'DURACION': '1 día',
            'PRECEDENCIA': 'Migración de funciones duplicadas',
            'RECURSOS': 'QA Engineer, Developer',
            'OBSERVACIONES': 'Validar que botón guardar funciona correctamente'
        }
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(datos_proyectos)
    
    # Nombre del archivo
    archivo = 'test_proyectos_post_migracion.xlsx'
    ruta_completa = os.path.join(os.getcwd(), archivo)
    
    # Crear archivo Excel
    with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Proyectos', index=False)
        
        # Obtener workbook y worksheet para formatear
        workbook = writer.book
        worksheet = writer.sheets['Proyectos']
        
        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print("✅ Archivo Excel creado exitosamente")
    print(f"📁 Ubicación: {ruta_completa}")
    print(f"📊 Total de actividades: {len(datos_proyectos)}")
    print(f"🎯 Proyectos incluidos: PROYECTO 01, PROYECTO 02")
    print("\n📋 Estructura del archivo:")
    print(df[['PROYECTO', 'ETAPA N1', 'ETAPA N2', 'ACTIVIDAD', 'DURACION']].to_string(index=False))
    
    return archivo

if __name__ == "__main__":
    try:
        archivo_creado = crear_excel_prueba()
        print(f"\n🚀 Listo para testing! Usar archivo: {archivo_creado}")
        print("🔍 Este archivo validará:")
        print("  - Carga correcta de proyectos")
        print("  - Funcionamiento del modal de asignaciones")
        print("  - Botón 'Guardar Asignaciones' post-migración")
        print("  - Persistencia de datos en Flask session")
        
    except Exception as e:
        print(f"❌ Error creando archivo de prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)