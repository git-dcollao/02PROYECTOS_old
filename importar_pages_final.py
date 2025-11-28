import pymysql

print("🔧 Importando páginas desde archivo extraído...\n")

# Leer el archivo SQL extraído
sql_file = "backups/insert_pages_extracted.sql"

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        insert_line = f.read().strip()
    
    # Verificar que sea un INSERT válido
    if not insert_line.startswith("INSERT INTO"):
        print(f"❌ El archivo no contiene un INSERT válido")
        exit(1)
    
    # Contar páginas
    pages_count = insert_line.count('),(') + 1
    print(f"✅ Archivo leído: {pages_count} páginas")
    
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
        
        cursor.execute("SELECT id, route, name FROM pages ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print(f"\n📄 Últimas 5 páginas importadas:")
        for row in rows:
            print(f"   {row[0]:3d}. {row[1]:40s} → {row[2]}")
        
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
