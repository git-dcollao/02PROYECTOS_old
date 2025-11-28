#!/usr/bin/env python3
"""
Script para test de restauración step by step
"""
import os
import subprocess
import pymysql
import time

def test_mysql_command():
    """Probar comando mysql directo"""
    print("🔧 Probando comando mysql...")
    
    backup_file = "/app/backups/uploaded_BD_V3_20251023_192653_20251023_211103.sql"
    
    # Comando mysql directo
    mysql_cmd = [
        'mysql',
        '-h', 'mysql_db',
        '-u', 'proyectos_admin',
        '-p123456!#Td',
        '-P', '3306',
        'proyectosDB'
    ]
    
    print(f"📁 Verificando archivo: {backup_file}")
    if not os.path.exists(backup_file):
        print(f"❌ Archivo no encontrado: {backup_file}")
        return
    
    print("📊 Comando mysql a ejecutar:")
    print(" ".join(mysql_cmd + [f"< {backup_file}"]))
    
    try:
        print("⏳ Ejecutando restauración con mysql...")
        with open(backup_file, 'r', encoding='utf-8') as f:
            process = subprocess.run(
                mysql_cmd,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300  # 5 minutos
            )
        
        if process.returncode == 0:
            print("✅ Restauración con mysql exitosa")
        else:
            print(f"❌ Error en mysql: {process.stderr.decode()}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout en comando mysql (5 minutos)")
    except Exception as e:
        print(f"❌ Error ejecutando mysql: {e}")

def test_pymysql_restore():
    """Probar restauración con PyMySQL"""
    print("\n🔧 Probando restauración con PyMySQL...")
    
    backup_file = "/app/backups/uploaded_BD_V3_20251023_192653_20251023_211103.sql"
    
    if not os.path.exists(backup_file):
        print(f"❌ Archivo no encontrado: {backup_file}")
        return
    
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(
            host='mysql_db',
            port=3306,
            user='proyectos_admin',
            password='123456!#Td',
            database='proyectosDB',
            charset='utf8mb4'
        )
        
        print("✅ Conexión PyMySQL establecida")
        
        with connection:
            cursor = connection.cursor()
            
            # Leer archivo
            print(f"📖 Leyendo archivo: {backup_file}")
            with open(backup_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            print(f"📊 Tamaño del archivo: {len(sql_content)} caracteres")
            
            # Separar statements (línea por línea para evitar problemas)
            statements = []
            current_statement = ""
            
            for line in sql_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('--'):
                    continue
                
                current_statement += " " + line
                
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
            
            print(f"📋 Encontrados {len(statements)} statements SQL")
            
            # Ejecutar statements con progreso
            executed = 0
            errors = 0
            
            for i, statement in enumerate(statements):
                if i % 100 == 0:  # Mostrar progreso cada 100 statements
                    print(f"⏳ Procesando statement {i+1}/{len(statements)}")
                
                try:
                    cursor.execute(statement)
                    executed += 1
                except pymysql.Error as e:
                    errors += 1
                    if errors <= 5:  # Solo mostrar los primeros 5 errores
                        print(f"⚠️ Error en statement {i+1}: {e}")
            
            connection.commit()
            print(f"✅ Restauración PyMySQL completada: {executed} éxitos, {errors} errores")
            
    except Exception as e:
        print(f"❌ Error con PyMySQL: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando test de restauración step by step...")
    test_mysql_command()
    test_pymysql_restore()
    print("🏁 Test completado")