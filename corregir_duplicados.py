#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para eliminar el código duplicado que causa proyectos duplicados en el modal
"""

import re

def corregir_duplicados():
    """Eliminar el loop duplicado que causa proyectos duplicados"""
    
    archivo_path = r"c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\controllers.py"
    
    print("🔧 CORRIGIENDO DUPLICADOS EN controllers.py")
    print("=" * 50)
    
    # Leer archivo completo
    with open(archivo_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar el patrón de inicio de FASE 2 problemático
    patron_inicio = "        # FASE 2: PROCESAR ACTIVIDADES (solo si no hay proyectos para asignar)"
    patron_final = "@controllers_bp.route('/guardar-asignaciones-proyecto', methods=['POST'], endpoint='guardar_asignaciones_proyecto')"
    
    # Encontrar posiciones
    pos_inicio = contenido.find(patron_inicio)
    pos_final = contenido.find(patron_final)
    
    if pos_inicio == -1:
        print("❌ No se encontró el patrón de inicio de FASE 2")
        return False
        
    if pos_final == -1:
        print("❌ No se encontró el patrón final")
        return False
    
    print(f"📍 FASE 2 problemática encontrada:")
    print(f"   Inicio: posición {pos_inicio}")
    print(f"   Final: posición {pos_final}")
    print(f"   Tamaño a eliminar: {pos_final - pos_inicio} caracteres")
    
    # Nuevo contenido sin la FASE 2 problemática
    nuevo_contenido = (
        contenido[:pos_inicio] + 
        "        # 📊 SIN PROYECTOS NUEVOS - PROCESAMIENTO COMPLETADO  \n" +
        "        print(f\"📊 No se detectaron proyectos nuevos para asignación\")\n" +
        "        print(f\"💾 Total actividades procesadas: {actividades_procesadas}\")\n" +
        "        \n" +
        "        return jsonify({\n" +
        "            'success': True, \n" +
        "            'message': f'Archivo Excel procesado correctamente. {actividades_procesadas} actividades encontradas. No hay proyectos nuevos para asignar.',\n" +
        "            'proyectos_nuevos': [],\n" +
        "            'actividades_procesadas': actividades_procesadas\n" +
        "        })\n" +
        "        \n" +
        "    except Exception as e:\n" +
        "        print(f\"❌ Error procesando archivo Excel: {str(e)}\")\n" +
        "        return jsonify({'success': False, 'message': f'Error procesando archivo: {str(e)}'})\n\n\n" +
        contenido[pos_final:]
    )
    
    # Guardar archivo corregido
    with open(archivo_path, 'w', encoding='utf-8') as f:
        f.write(nuevo_contenido)
    
    # Calcular diferencia
    lineas_antes = contenido.count('\n')
    lineas_despues = nuevo_contenido.count('\n')
    lineas_eliminadas = lineas_antes - lineas_despues
    
    print(f"✅ CORRECCIÓN COMPLETADA:")
    print(f"   Líneas antes: {lineas_antes}")
    print(f"   Líneas después: {lineas_despues}")
    print(f"   Líneas eliminadas: {lineas_eliminadas}")
    print(f"   Archivo actualizado: {archivo_path}")
    
    return True

if __name__ == "__main__":
    corregir_duplicados()
