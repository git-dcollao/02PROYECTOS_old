#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar contenido del backup maestro
"""

import re

print("📦 VERIFICACIÓN DEL BACKUP MAESTRO")
print("=" * 60)

with open('backups/BACKUP_MAESTRO_COMPLETO_20251104_170110.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar todos los INSERT INTO
inserts = re.findall(r'INSERT INTO `(\w+)` VALUES (.*?);', content, re.DOTALL)

print(f"\n📊 Tablas encontradas: {len(inserts)}\n")

for table, values in inserts:
    # Contar registros (cada registro separado por '),(' )
    count = values.count('),(') + 1
    
    icon = "✅" if count > 0 else "⚠️"
    print(f"{icon} {table:25s}: {count:4d} registros")

print("\n" + "=" * 60)
print("✅ Verificación completada")
