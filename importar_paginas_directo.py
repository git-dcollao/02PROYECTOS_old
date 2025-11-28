import re

print("🔧 Extrayendo e importando páginas del BACKUP_FINAL_LIMPIO...\n")

# Leer el backup
backup_path = r"backups\BACKUP_FINAL_LIMPIO_20251103_111639.sql"

try:
    with open(backup_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("✅ Archivo leído correctamente")
    
    # Buscar la línea completa del INSERT de páginas (está toda en una línea)
    # Buscar el inicio y final del INSERT
    start_marker = "INSERT INTO `pages` VALUES ("
    end_marker = ");\n/*!40000 ALTER TABLE `pages` ENABLE KEYS */"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx != -1 and end_idx != -1:
        # Extraer los datos entre paréntesis
        pages_data = content[start_idx + len(start_marker):end_idx]
        pages_list = pages_data.split('),(')
        pages_count = len(pages_list)
        
        print(f"✅ Encontradas {pages_count} páginas")
        
        # Crear archivo SQL para importar
        output_file = "backups/IMPORTAR_PAGINAS.sql"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Importación de {} páginas\n".format(pages_count))
            f.write("-- Extraído de BACKUP_FINAL_LIMPIO\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n")
            f.write("SET NAMES utf8mb4;\n")
            f.write("SET CHARACTER SET utf8mb4;\n\n")
            f.write("-- Limpiar páginas existentes\n")
            f.write("TRUNCATE TABLE pages;\n\n")
            f.write("-- Insertar páginas\n")
            f.write(f"INSERT INTO `pages` VALUES ({pages_data});\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=1;\n")
        
        print(f"\n✅ Archivo SQL creado: {output_file}")
        print(f"📊 Contiene {pages_count} páginas listas para importar")
        
        # Ahora importar directamente usando Python
        print("\n📥 Importando a la base de datos...")
        
        import pymysql
        
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='proyectos_admin',
            password='123456!#Td',
            database='proyectosDB',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        try:
            # Deshabilitar comprobación de claves foráneas
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            cursor.execute("SET NAMES utf8mb4")
            cursor.execute("SET CHARACTER SET utf8mb4")
            
            # Limpiar páginas existentes
            cursor.execute("TRUNCATE TABLE pages")
            print("   ✅ Tabla pages limpiada")
            
            # Insertar páginas
            insert_sql = f"INSERT INTO `pages` VALUES ({pages_data})"
            cursor.execute(insert_sql)
            print(f"   ✅ {pages_count} páginas insertadas")
            
            # Habilitar comprobación de claves foráneas
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            
            conn.commit()
            
            # Verificar
            cursor.execute("SELECT COUNT(*) as total FROM pages")
            result = cursor.fetchone()
            total = result[0]
            
            print(f"\n✅ ¡IMPORTACIÓN EXITOSA!")
            print(f"📊 Total de páginas en la base de datos: {total}")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error durante la importación: {e}")
            raise
        
        finally:
            cursor.close()
            conn.close()
        
    else:
        print("❌ No se encontró el INSERT de páginas en el backup")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
