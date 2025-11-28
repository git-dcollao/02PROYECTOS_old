import gzip
import shutil
import os
from datetime import datetime

# Archivos
sql_file = r'backups\BACKUP_MAESTRO_FINAL-V2_20251105_150126.sql'
gz_original = r'backups\BACKUP_MAESTRO_FINAL-V2_20251105_150126.sql.gz'
gz_backup = r'backups\BACKUP_MAESTRO_FINAL-V2_20251105_150126.sql.gz.OLD'
gz_new = r'backups\BACKUP_MAESTRO_FINAL-V2_20251105_150126_CORREGIDO.sql.gz'

print("🔄 Proceso de compresión del backup corregido...")
print()

# Hacer backup del archivo original .gz
if os.path.exists(gz_original):
    print(f"📦 Respaldando archivo original: {gz_original}")
    shutil.copy2(gz_original, gz_backup)
    print(f"✅ Backup guardado como: {gz_backup}")
    print()

# Comprimir el archivo SQL corregido
print(f"🗜️  Comprimiendo archivo corregido: {sql_file}")
with open(sql_file, 'rb') as f_in:
    with gzip.open(gz_new, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

print(f"✅ Archivo comprimido guardado como: {gz_new}")
print()

# Mostrar tamaños
print("📊 Comparación de tamaños:")
print(f"   Original .gz: {os.path.getsize(gz_original):,} bytes")
print(f"   Corregido .gz: {os.path.getsize(gz_new):,} bytes")
print(f"   SQL descomprimido: {os.path.getsize(sql_file):,} bytes")
print()
print("✅ ¡Proceso completado exitosamente!")
print()
print("📝 Archivos generados:")
print(f"   1. {gz_backup} (backup del original)")
print(f"   2. {gz_new} (versión corregida)")
