#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas de charset en el menú
"""

import pymysql

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'port': 3308,
    'user': 'proyectos_admin',
    'password': '123456!#Td',
    'database': 'proyectosDB',
    'charset': 'utf8mb4'
}

print("=" * 80)
print("DIAGNÓSTICO DE CHARSET DEL MENÚ")
print("=" * 80)

try:
    # Conectar a la base de datos
    connection = pymysql.connect(**db_config)
    
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        # Verificar categorías
        print("\n📋 CATEGORÍAS:")
        print("-" * 80)
        cursor.execute("""
            SELECT id, name, icon, 
                   HEX(name) as hex_name,
                   CHAR_LENGTH(name) as char_length,
                   LENGTH(name) as byte_length
            FROM categories 
            ORDER BY display_order
        """)
        
        categories = cursor.fetchall()
        for cat in categories:
            print(f"\nID: {cat['id']}")
            print(f"  Nombre: {cat['name']}")
            print(f"  Icon: {cat['icon']}")
            print(f"  HEX: {cat['hex_name']}")
            print(f"  Caracteres: {cat['char_length']}, Bytes: {cat['byte_length']}")
            
            # Verificar si hay bytes sospechosos
            name_bytes = bytes.fromhex(cat['hex_name'])
            try:
                decoded_utf8 = name_bytes.decode('utf-8')
                print(f"  ✅ Decodificación UTF-8: {decoded_utf8}")
            except:
                print(f"  ❌ ERROR al decodificar como UTF-8")
        
        # Verificar páginas con caracteres especiales
        print("\n\n📄 PÁGINAS CON CARACTERES ESPECIALES:")
        print("-" * 80)
        cursor.execute("""
            SELECT id, name, route,
                   HEX(name) as hex_name,
                   CHAR_LENGTH(name) as char_length,
                   LENGTH(name) as byte_length
            FROM pages 
            WHERE LENGTH(name) > CHAR_LENGTH(name)
            ORDER BY name
            LIMIT 15
        """)
        
        pages = cursor.fetchall()
        for page in pages:
            print(f"\nID: {page['id']}")
            print(f"  Nombre: {page['name']}")
            print(f"  Ruta: {page['route']}")
            print(f"  HEX: {page['hex_name']}")
            print(f"  Caracteres: {page['char_length']}, Bytes: {page['byte_length']}")
            
            # Verificar decodificación
            name_bytes = bytes.fromhex(page['hex_name'])
            try:
                decoded_utf8 = name_bytes.decode('utf-8')
                print(f"  ✅ Decodificación UTF-8: {decoded_utf8}")
            except:
                print(f"  ❌ ERROR al decodificar como UTF-8")
        
        # Verificar configuración de la base de datos
        print("\n\n⚙️ CONFIGURACIÓN DE BASE DE DATOS:")
        print("-" * 80)
        cursor.execute("SHOW VARIABLES LIKE 'character_set%'")
        for row in cursor.fetchall():
            print(f"{row['Variable_name']}: {row['Value']}")
        
        print("\n")
        cursor.execute("SHOW VARIABLES LIKE 'collation%'")
        for row in cursor.fetchall():
            print(f"{row['Variable_name']}: {row['Value']}")
    
    connection.close()
    
    print("\n" + "=" * 80)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
