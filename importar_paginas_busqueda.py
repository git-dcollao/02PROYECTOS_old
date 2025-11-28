import pymysql

print("🔧 Extrayendo e importando páginas del BACKUP_FINAL_LIMPIO...\n")

backup_path = r"backups\BACKUP_FINAL_LIMPIO_20251103_111639.sql"

try:
    with open(backup_path, 'r', encoding='latin-1') as f:
        for line_num, line in enumerate(f, 1):
            if "INSERT INTO" in line and "pages" in line and "VALUES" in line:
                insert_line = line.strip()
                
                # Contar páginas
                data_part = insert_line[len("INSERT INTO `pages` VALUES "):-1]
                pages_count = len(data_part.split('),('))
                
                print(f"✅ Encontradas {pages_count} páginas (línea {line_num})")
                
                # Conectar a la base de datos
                print("\n📥 Conectando a la base de datos...")
                
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
                    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                    cursor.execute("SET NAMES utf8mb4")
                    cursor.execute("SET CHARACTER SET utf8mb4")
                    
                    cursor.execute("TRUNCATE TABLE pages")
                    print("   ✅ Tabla pages limpiada")
                    
                    cursor.execute(insert_line)
                    print(f"   ✅ {pages_count} páginas insertadas")
                    
                    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                    conn.commit()
                    
                    cursor.execute("SELECT COUNT(*) as total FROM pages")
                    result = cursor.fetchone()
                    total = result[0]
                    
                    print(f"\n✅ ¡IMPORTACIÓN EXITOSA!")
                    print(f"📊 Total de páginas en la base de datos: {total}")
                    
                    cursor.execute("SELECT id, route, name FROM pages ORDER BY id LIMIT 10")
                    rows = cursor.fetchall()
                    print(f"\n📄 Primeras 10 páginas importadas:")
                    for row in rows:
                        print(f"   {row[0]:3d}. {row[1]:30s} → {row[2]}")
                    
                except Exception as e:
                    conn.rollback()
                    print(f"\n❌ Error durante la importación: {e}")
                    raise
                
                finally:
                    cursor.close()
                    conn.close()
                
                break
        else:
            print("❌ No se encontró la línea INSERT INTO `pages`")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
