import gzip
import shutil
import os

# Rutas
gz_file = r'backups\BACKUP_MAESTRO_FINAL-V2_20251105_150126.sql.gz'
sql_file = r'backups\BACKUP_MAESTRO_FINAL-V2_20251105_150126.sql'

# Verificar si ya existe descomprimido
if os.path.exists(sql_file):
    print(f"✅ El archivo SQL ya existe descomprimido: {sql_file}")
    print(f"   Tamaño: {os.path.getsize(sql_file):,} bytes")
else:
    print(f"📦 Descomprimiendo {gz_file}...")
    with gzip.open(gz_file, 'rb') as f_in:
        with open(sql_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"✅ Descomprimido exitosamente")
    print(f"   Tamaño: {os.path.getsize(sql_file):,} bytes")
