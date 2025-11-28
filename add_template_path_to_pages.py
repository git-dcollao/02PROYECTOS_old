#!/usr/bin/env python3
"""
Script para agregar la columna template_path a la tabla pages
"""

import mysql.connector
import sys
import os

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,  # Puerto mapeado del contenedor Docker
    'user': 'proyectos_admin',
    'password': '123456!#Td',
    'database': 'proyectosDB'
}

def main():
    """Agregar columna template_path a la tabla pages"""
    
    connection = None
    try:
        print("🔧 Conectando a la base de datos...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Verificar si la columna ya existe
        print("🔍 Verificando si la columna template_path ya existe...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'proyectosDB' 
            AND TABLE_NAME = 'pages' 
            AND COLUMN_NAME = 'template_path'
        """)
        
        column_exists = cursor.fetchone()[0] > 0
        
        if column_exists:
            print("✅ La columna template_path ya existe en la tabla pages")
            return
        
        # Agregar la nueva columna
        print("📝 Agregando columna template_path a la tabla pages...")
        cursor.execute("""
            ALTER TABLE pages 
            ADD COLUMN template_path VARCHAR(300) NULL 
            COMMENT 'Ruta al archivo de template HTML para páginas dinámicas'
        """)
        
        connection.commit()
        print("✅ Columna template_path agregada exitosamente!")
        
        # Verificar la estructura actualizada de la tabla
        print("\n📋 Estructura actualizada de la tabla pages:")
        cursor.execute("DESCRIBE pages")
        columns = cursor.fetchall()
        
        for column in columns:
            field_name = column[0]
            field_type = column[1]
            is_null = column[2]
            key_info = column[3]
            default_val = column[4]
            extra = column[5] if len(column) > 5 else ''
            
            print(f"  - {field_name}: {field_type} {'NULL' if is_null == 'YES' else 'NOT NULL'} {key_info} {extra}")
        
        print("\n🎉 Migración completada exitosamente!")
        
    except mysql.connector.Error as e:
        print(f"💥 Error de MySQL: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
        
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MIGRACION: Agregar template_path a tabla pages")
    print("=" * 60)
    main()
