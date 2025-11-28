#!/usr/bin/env python3
"""
Diagnóstico de Conexión MySQL para Operaciones de Limpieza
==========================================================

Script para diagnosticar y preparar la base de datos para operaciones de limpieza.
"""

import pymysql
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_mysql_connection():
    """Diagnosticar configuración MySQL para operaciones largas"""
    print("🔍 === DIAGNÓSTICO DE CONEXIÓN MYSQL ===")
    
    try:
        from config import Config
        
        # Configuración de DB
        config = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'charset': 'utf8mb4',
            'connect_timeout': 60,
            'read_timeout': 1200,
            'write_timeout': 1200,
            'autocommit': False
        }
        
        print(f"📋 Configuración: {config['host']}:{config['port']}")
        
        # Test de conexión
        start_time = time.time()
        connection = pymysql.connect(**config)
        connect_time = time.time() - start_time
        print(f"✅ Conexión establecida en {connect_time:.2f}s")
        
        with connection.cursor() as cursor:
            # Verificar variables de timeout actuales
            print("\n🔧 Variables de timeout actuales:")
            timeout_vars = [
                'wait_timeout',
                'interactive_timeout',
                'net_read_timeout',
                'net_write_timeout',
                'max_allowed_packet'
            ]
            
            for var in timeout_vars:
                cursor.execute(f"SHOW VARIABLES LIKE '{var}'")
                result = cursor.fetchone()
                if result:
                    print(f"   {var}: {result[1]}")
            
            # Obtener lista de tablas y sus tamaños
            print("\n📊 Información de tablas:")
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            total_tables = len(tables)
            system_tables = ['alembic_version']
            tables_to_clean = [t for t in tables if t not in system_tables]
            
            print(f"   📋 Total de tablas: {total_tables}")
            print(f"   🧹 Tablas a limpiar: {len(tables_to_clean)}")
            print(f"   🔒 Tablas del sistema: {len(system_tables)}")
            
            # Verificar tamaño de las tablas principales
            print("\n📦 Tamaños de tablas (primeras 10):")
            cursor.execute("""
                SELECT 
                    table_name,
                    table_rows,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
                FROM information_schema.tables 
                WHERE table_schema = %s 
                ORDER BY (data_length + index_length) DESC 
                LIMIT 10
            """, (config['database'],))
            
            for row in cursor.fetchall():
                print(f"   📄 {row[0]}: {row[1] or 0} filas, {row[2]} MB")
        
        # Test de operaciones básicas
        print("\n🧪 Test de operaciones básicas:")
        
        with connection.cursor() as cursor:
            # Test de configuración de timeouts
            print("   🔧 Configurando timeouts...")
            test_timeouts = [
                "SET SESSION wait_timeout = 1200",
                "SET SESSION interactive_timeout = 1200",
                "SET SESSION net_read_timeout = 600",
                "SET SESSION net_write_timeout = 600",
                "SET FOREIGN_KEY_CHECKS = 0",
                "SET AUTOCOMMIT = 1"
            ]
            
            for cmd in test_timeouts:
                try:
                    cursor.execute(cmd)
                    print(f"   ✅ {cmd}")
                except Exception as e:
                    print(f"   ❌ {cmd}: {e}")
            
            # Test de operación TRUNCATE en tabla de prueba
            print("\n   🧪 Test de operación TRUNCATE:")
            try:
                cursor.execute("CREATE TEMPORARY TABLE test_truncate (id INT)")
                cursor.execute("INSERT INTO test_truncate VALUES (1), (2), (3)")
                cursor.execute("SELECT COUNT(*) FROM test_truncate")
                count_before = cursor.fetchone()[0]
                
                cursor.execute("TRUNCATE TABLE test_truncate")
                cursor.execute("SELECT COUNT(*) FROM test_truncate")
                count_after = cursor.fetchone()[0]
                
                print(f"   ✅ TRUNCATE test: {count_before} → {count_after} filas")
                cursor.execute("DROP TEMPORARY TABLE test_truncate")
                
            except Exception as e:
                print(f"   ❌ TRUNCATE test fallido: {e}")
            
            # Restaurar configuración
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            cursor.execute("SET AUTOCOMMIT = 0")
        
        connection.close()
        print("\n✅ Diagnóstico completado exitosamente")
        print("💡 Recomendación: La conexión está lista para operaciones de limpieza")
        
    except Exception as e:
        print(f"\n❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_table_by_table_cleanup():
    """Test de limpieza tabla por tabla"""
    print("\n🧹 === TEST DE LIMPIEZA TABLA POR TABLA ===")
    
    try:
        from config import Config
        
        config = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'charset': 'utf8mb4',
            'connect_timeout': 60,
            'read_timeout': 1200,
            'write_timeout': 1200,
        }
        
        connection = pymysql.connect(**config)
        
        with connection.cursor() as cursor:
            # Obtener tablas pequeñas para test
            cursor.execute("""
                SELECT table_name, table_rows
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name NOT IN ('alembic_version')
                ORDER BY table_rows ASC 
                LIMIT 5
            """, (config['database'],))
            
            small_tables = cursor.fetchall()
            print(f"📋 Testing limpieza en {len(small_tables)} tablas pequeñas:")
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("SET AUTOCOMMIT = 1")
            
            for table_name, row_count in small_tables:
                try:
                    start_time = time.time()
                    cursor.execute(f"TRUNCATE TABLE `{table_name}`")
                    elapsed = time.time() - start_time
                    print(f"   ✅ {table_name}: {row_count} filas → 0 filas ({elapsed:.2f}s)")
                except Exception as e:
                    print(f"   ❌ {table_name}: Error - {e}")
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            cursor.execute("SET AUTOCOMMIT = 0")
        
        connection.close()
        print("✅ Test de limpieza completado")
        
    except Exception as e:
        print(f"❌ Error en test de limpieza: {e}")

def main():
    """Función principal"""
    print("🚀 === DIAGNÓSTICO MYSQL PARA LIMPIEZA DE BD ===")
    print(f"⏰ Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar diagnóstico
    success = diagnose_mysql_connection()
    
    if success:
        test_table_by_table_cleanup()
    
    print("\n✅ === DIAGNÓSTICO COMPLETADO ===")

if __name__ == "__main__":
    main()