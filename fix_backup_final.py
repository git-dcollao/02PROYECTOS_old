#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrector final de encoding para archivo SQL
"""

def fix_backup():
    input_file = "BACKUP_LIMPIO_UTF8_20251103_114447.sql"
    output_file = "BACKUP_CORREGIDO_FINAL.sql"
    
    print("🔧 Corrigiendo encoding del backup SQL...")
    
    # Leer archivo como bytes
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Decodificar con latin-1 para preservar todos los bytes
    text = data.decode('latin-1')
    
    # Aplicar correcciones
    replacements = [
        ('├│', 'ó'),
        ('├í', 'á'),
        ('├ñ', 'ñ'),
        ('├®', 'í'),
        ('├©', 'é'),
        ('├║', 'ú'),
        ('├ü', 'Á'),
        ('├¡', 'í'),
        ('├ì', 'Í'),
        ('├ô', 'Ó'),
        ('├ë', 'Ñ'),
    ]
    
    total_changes = 0
    for wrong, correct in replacements:
        count = text.count(wrong)
        if count > 0:
            print(f"  ✓ Reemplazando '{wrong}' → '{correct}': {count} veces")
            text = text.replace(wrong, correct)
            total_changes += count
    
    # Guardar archivo corregido
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    
    print(f"\n✅ Total de correcciones: {total_changes}")
    print(f"💾 Archivo guardado: {output_file}")
    print(f"\n📝 Para restaurar:")
    print(f"   Get-Content {output_file} -Raw | docker-compose exec -T proyectos_db mysql -u root -p'123456!#Td' proyectosDB")

if __name__ == '__main__':
    fix_backup()
