#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer SOLO los INSERTs de page_permissions del backup
"""

import re

print("Leyendo backup...")

# Detectar encoding
import codecs
with open('backups/BACKUP_FINAL_LIMPIO_20251103_111639.sql', 'rb') as f:
    raw = f.read(4)
    
if raw[:2] == b'\xff\xfe':
    encoding = 'utf-16-le'
    print("  Detectado: UTF-16 LE")
elif raw[:2] == b'\xfe\xff':
    encoding = 'utf-16-be'
    print("  Detectado: UTF-16 BE")
else:
    encoding = 'utf-8'
    print("  Detectado: UTF-8")

with open('backups/BACKUP_FINAL_LIMPIO_20251103_111639.sql', 'r', encoding=encoding) as f:
    content = f.read()
    
print(f"  Leídos {len(content)} caracteres")

print("Buscando INSERT de page_permissions...")

# Buscar el INSERT de page_permissions
pattern = r"INSERT INTO `page_permissions` VALUES (.*?);"
match = re.search(pattern, content, re.DOTALL)

if match:
    insert_statement = f"INSERT INTO `page_permissions` VALUES {match.group(1)};"
    
    # Guardar
    with open('restore_page_permissions_only.sql', 'w', encoding='utf-8') as f:
        f.write(insert_statement)
    
    # Contar registros
    values_count = insert_statement.count('),(') + 1
    print(f"✅ Extraído INSERT con {values_count} registros")
    print(f"✅ Guardado en: restore_page_permissions_only.sql")
    print(f"   Tamaño: {len(insert_statement)} caracteres")
else:
    print("❌ No se encontró INSERT de page_permissions")
