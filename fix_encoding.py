#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para corregir caracteres específicos en el backup SQL
"""

import sys
from datetime import datetime

# Lista de correcciones específicas
CORRECTIONS = {
    'En Ejecuci├│n': 'En Ejecución',
    'Fin de Ejecuci├│n': 'Fin de Ejecución',
    'Administraci├│n': 'Administración',
    '├ürea de administraci├│n': 'Área de administración',
    '├ürea de gesti├│n': 'Área de gestión',
    'P├íginas del sistema': 'Páginas del sistema',
    'navegaci├│n': 'navegación',
    'Gesti├│n de requerimientos': 'Gestión de requerimientos',
    'Gesti├│n de usuarios': 'Gestión de usuarios',
    'Configuraci├│n de cat├ílogos': 'Configuración de catálogos',
    'par├ímetros': 'parámetros',
    'Administraci├│n avanzada': 'Administración avanzada',
    'Preinversi├│n': 'Preinversión',
    'Inversi├│n': 'Inversión',
    'Operaci├│n': 'Operación',
    'A├║n no se define': 'Aún no se define',
    'Subsecretar├¡a': 'Subsecretaría',
    'P├ígina principal': 'Página principal',
    'estad├¡sticas': 'estadísticas',
    'Gesti├│n de actividades': 'Gestión de actividades',
    'Visualizaci├│n de cronogramas': 'Visualización de cronogramas',
    'Gesti├│n de estados': 'Gestión de estados',
    'Gesti├│n de prioridades': 'Gestión de prioridades',
    'Gesti├│n de fases': 'Gestión de fases',
    'tipolog├¡as': 'tipologías',
    'Descripci├│n': 'Descripción',
}

def fix_file(input_file, output_file=None):
    """Corrige el archivo SQL"""
    
    print("="*80)
    print("🔧 CORRECCIÓN DE ENCODING EN BACKUP SQL")
    print("="*80)
    
    # Leer archivo
    print(f"\n📖 Leyendo: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Intentar con latin-1 si UTF-8 falla
        try:
            with open(input_file, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
            return False
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    # Aplicar correcciones
    original_content = content
    corrections_applied = {}
    
    for wrong, correct in CORRECTIONS.items():
        count = content.count(wrong)
        if count > 0:
            content = content.replace(wrong, correct)
            corrections_applied[wrong] = {
                'correct': correct,
                'count': count
            }
    
    # Mostrar correcciones
    total = sum(c['count'] for c in corrections_applied.values())
    print(f"\n📊 Total de correcciones: {total}")
    
    if corrections_applied:
        print("\n✅ Correcciones aplicadas:")
        for wrong, info in sorted(corrections_applied.items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"   '{wrong}' → '{info['correct']}' ({info['count']} veces)")
    
    # Determinar archivo de salida
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = input_file.replace('.sql', f'_FIXED_{timestamp}.sql')
    
    # Guardar archivo corregido
    print(f"\n💾 Guardando: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("✅ Archivo guardado exitosamente")
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")
        return False
    
    # Estadísticas
    import os
    size_original = os.path.getsize(input_file)
    size_fixed = os.path.getsize(output_file)
    
    print(f"\n📈 Estadísticas:")
    print(f"   Tamaño original: {size_original:,} bytes")
    print(f"   Tamaño corregido: {size_fixed:,} bytes")
    print(f"   Diferencia: {size_fixed - size_original:+,} bytes")
    
    print("\n"+"="*80)
    print("🎉 PROCESO COMPLETADO")
    print("="*80)
    print(f"\n📝 Para restaurar el backup corregido:")
    print(f"   docker-compose exec -T proyectos_db mysql -u root -p123456 proyectosDB < {output_file}")
    
    return True

if __name__ == '__main__':
    input_file = 'BACKUP_LIMPIO_UTF8_20251103_114447.sql'
    fix_file(input_file)
