#!/usr/bin/env python3
"""
Script para limpiar backups antiguos (OPCIONAL)
"""

import sys
import os
import glob

def main():
    """Limpiar backups antiguos"""
    backup_dir = r"C:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\backups"
    
    print("🗑️ Limpieza de backups antiguos (OPCIONAL)")
    print(f"📂 Directorio: {backup_dir}")
    
    # Buscar todos los archivos de backup
    backup_files = []
    for ext in ['*.sql', '*.sql.gz', '*.meta']:
        backup_files.extend(glob.glob(os.path.join(backup_dir, ext)))
    
    print(f"\n📋 Archivos encontrados: {len(backup_files)}")
    for file in sorted(backup_files):
        print(f"  - {os.path.basename(file)}")
    
    if backup_files:
        print(f"\n⚠️ Si quieres eliminar TODOS estos archivos:")
        print(f"💻 Ejecuta: rmdir /s \"{backup_dir}\"")
        print(f"💻 Luego: mkdir \"{backup_dir}\"")
        print(f"\n🔒 Mantenerlos es RECOMENDADO para seguridad")
    else:
        print("\n✅ No hay archivos de backup para limpiar")

if __name__ == "__main__":
    main()