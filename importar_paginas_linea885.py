import pymysql

print("🔧 Extrayendo e importando páginas del BACKUP_FINAL_LIMPIO...\n")

# Leer solo la línea 885 del backup
backup_path = r"backups\BACKUP_FINAL_LIMPIO_20251103_111639.sql"

try:
    with open(backup_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # La línea 885 (índice 884) contiene el INSERT de páginas
    insert_line = lines[884].strip()
    
    # Verificar que sea la línea correcta
    if not insert_line.startswith("INSERT INTO `pages` VALUES"):
        print(f"❌ Error: La línea 885 no contiene el INSERT esperado")
        print(f"   Contenido: {insert_line[:100]}...")
        exit(1)
    
    # Contar páginas
    # El formato es: INSERT INTO `pages` VALUES (datos1),(datos2),...;
    # Extraer la parte entre VALUES y ;
    data_part = insert_line[len("INSERT INTO `pages` VALUES "):-1]  # Quitar INSERT y el punto y coma final
    pages_list = data_part.split('),(')
    pages_count = len(pages_list)
    
    print(f"✅ Encontradas {pages_count} páginas en la línea 885")
    
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
        # Deshabilitar comprobación de claves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        cursor.execute("SET NAMES utf8mb4")
        cursor.execute("SET CHARACTER SET utf8mb4")
        
        # Limpiar páginas existentes
        cursor.execute("TRUNCATE TABLE pages")
        print("   ✅ Tabla pages limpiada")
        
        # Insertar páginas - usar la línea completa
        cursor.execute(insert_line)
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
        
        # Mostrar algunas páginas de ejemplo
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

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
