#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final para corregir TODOS los errores de encoding en el backup SQL
Lee el archivo como bytes y reemplaza los patrones incorrectos
"""

import os
from datetime import datetime

def fix_sql_encoding(input_file):
    """Corrige encoding del archivo SQL"""
    
    output_file = input_file.replace('.sql', '_UTF8_FIXED.sql')
    
    print("="*80)
    print("🔧 CORRECCIÓN COMPLETA DE ENCODING SQL")
    print("="*80)
    print(f"\n📖 Archivo de entrada: {input_file}")
    print(f"💾 Archivo de salida: {output_file}")
    
    # Leer archivo completo como bytes
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Mapeo de bytes mal codificados a bytes correctos
    # ├│ (0xC3 0xB3) debe ser ó
    # ├í (0xC3 0xAD) debe ser á  
    # etc.
    replacements_bytes = [
        (b'\xc3\xb3', 'ó'.encode('utf-8')),  # ├│ → ó
        (b'\xc3\xad', 'á'.encode('utf-8')),  # ├í → á
        (b'\xc3\xb1', 'ñ'.encode('utf-8')),  # ├ñ → ñ
        (b'\xc3\xae', 'í'.encode('utf-8')),  # ├® → í
        (b'\xc3\xa9', 'é'.encode('utf-8')),  # ├© → é
        (b'\xc3\xba', 'ú'.encode('utf-8')),  # ├║ → ú
        (b'\xc3\x9c', 'Ü'.encode('utf-8')),  # ├ü → Ü/Á  
        (b'\xc3\xa1', 'á'.encode('utf-8')),  # ├í → á (alternativo)
        (b'\xc3\xb3', 'ó'.encode('utf-8')),  # ├│ → ó (alternativo)
        (b'\xc3\xb4', 'ô'.encode('utf-8')),  # ├ô → ô
        (b'\xc3\xb0', 'ð'.encode('utf-8')),  # ├░ → ð
    ]
    
    # Aplicar reemplazos
    total_replacements = 0
    for wrong_bytes, correct_bytes in replacements_bytes:
        count = data.count(wrong_bytes)
        if count > 0:
            data = data.replace(wrong_bytes, correct_bytes)
            total_replacements += count
            try:
                wrong_str = wrong_bytes.decode('utf-8', errors='replace')
                correct_str = correct_bytes.decode('utf-8')
                print(f"  ✓ {wrong_str} → {correct_str}: {count} reemplazos")
            except:
                print(f"  ✓ Bytes {wrong_bytes.hex()} → {correct_bytes.hex()}: {count} reemplazos")
    
    # Guardar archivo corregido
    with open(output_file, 'wb') as f:
        f.write(data)
    
    # Estadísticas
    size_in = os.path.getsize(input_file)
    size_out = os.path.getsize(output_file)
    
    print(f"\n📊 Resumen:")
    print(f"   Total de reemplazos: {total_replacements}")
    print(f"   Tamaño original: {size_in:,} bytes")
    print(f"   Tamaño corregido: {size_out:,} bytes")
    print(f"   Diferencia: {size_out - size_in:+,} bytes")
    
    print("\n" + "="*80)
    print("✅ ARCHIVO CORREGIDO EXITOSAMENTE")
    print("="*80)
    print(f"\n📝 Para restaurar el backup:")
    print(f"   Get-Content {output_file} -Raw | docker-compose exec -T proyectos_db mysql -u root -p'123456!#Td' proyectosDB")
    print("\n⚠️  Esto sobrescribirá los datos actuales en la base de datos")
    
    return output_file

if __name__ == '__main__':
    input_file = 'BACKUP_LIMPIO_UTF8_20251103_114447.sql'
    if not os.path.exists(input_file):
        print(f"❌ Error: No se encontró el archivo {input_file}")
    else:
        fix_sql_encoding(input_file)
