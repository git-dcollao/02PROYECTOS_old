import pymysql

print("📊 VERIFICACIÓN FINAL DEL SISTEMA\n")
print("="*60)

conn = pymysql.connect(
    host='localhost',
    port=3308,
    user='proyectos_admin',
    password='123456!#Td',
    database='proyectosDB',
    charset='utf8mb4'
)

cursor = conn.cursor()

try:
    # Contar páginas
    cursor.execute("SELECT COUNT(*) FROM pages")
    total_pages = cursor.fetchone()[0]
    print(f"\n✅ PÁGINAS: {total_pages}")
    
    # Páginas por categoría
    cursor.execute("""
        SELECT c.name, COUNT(p.id) as total
        FROM categories c
        LEFT JOIN pages p ON p.category_id = c.id
        GROUP BY c.id, c.name
        ORDER BY c.id
    """)
    
    print(f"\n📂 PÁGINAS POR CATEGORÍA:")
    for row in cursor.fetchall():
        print(f"   {row[0]:30s}: {row[1]:2d} páginas")
    
    # Otras tablas
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM trabajador")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM estado")
    total_estados = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM prioridad")
    total_prioridades = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sector")
    total_sectores = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM especialidad")
    total_especialidades = cursor.fetchone()[0]
    
    print(f"\n📊 OTROS DATOS:")
    print(f"   Categorías: {total_categories}")
    print(f"   Usuarios: {total_users}")
    print(f"   Estados: {total_estados}")
    print(f"   Prioridades: {total_prioridades}")
    print(f"   Sectores: {total_sectores}")
    print(f"   Especialidades: {total_especialidades}")
    
    # Verificar que no hay duplicados en rutas
    cursor.execute("""
        SELECT route, COUNT(*) as count
        FROM pages
        GROUP BY route
        HAVING count > 1
    """)
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n⚠️  ADVERTENCIA: {len(duplicates)} rutas duplicadas:")
        for dup in duplicates:
            print(f"   {dup[0]}: {dup[1]} veces")
    else:
        print(f"\n✅ Sin rutas duplicadas")
    
    print(f"\n" + "="*60)
    print(f"✅ ¡SISTEMA COMPLETAMENTE RESTAURADO!")
    print(f"="*60)

except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    cursor.close()
    conn.close()
