import gzip
import re

print("🔧 Extrayendo páginas del BACKUP_FINAL_LIMPIO...\n")

# Leer el backup
backup_path = r"backups\BACKUP_FINAL_LIMPIO_20251103_111639.sql"

try:
    with open(backup_path, 'r', encoding='latin-1', errors='ignore') as f:
        content = f.read()
    
    print("✅ Archivo descomprimido correctamente")
    
    # Buscar el INSERT de páginas
    match = re.search(r'INSERT INTO `?pages`? VALUES(.+?);', content, re.DOTALL)
    
    if match:
        pages_data = match.group(0)
        pages_count = len(match.group(1).split('),('))
        
        print(f"✅ Encontradas {pages_count} páginas")
        
        # Guardar solo el INSERT de páginas en un archivo limpio
        output_file = "backups/SOLO_PAGINAS_LIMPIO.sql"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Escribir encabezados necesarios
            f.write("-- Páginas extraídas de BACKUP_FINAL_LIMPIO\n")
            f.write("-- Total: {} páginas\n\n".format(pages_count))
            f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
            f.write("TRUNCATE TABLE pages;\n\n")
            f.write(pages_data)
            f.write("\n\nSET FOREIGN_KEY_CHECKS=1;\n")
        
        print(f"\n✅ Archivo creado: {output_file}")
        print(f"📊 Contiene {pages_count} páginas")
        print(f"\n💡 Ahora puedes importar este archivo en la base de datos con:")
        print(f"   docker exec -i mysql_db mysql -u proyectos_admin -p123456!'#'Td proyectosDB < {output_file}")
        
    else:
        print("❌ No se encontró el INSERT de páginas en el backup")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
