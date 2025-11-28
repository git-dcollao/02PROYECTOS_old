#!/usr/bin/env python3
"""
Script para verificar los timeouts configurados en MySQL
"""
import pymysql
import time
import sys

def test_mysql_timeouts():
    """Verificar que los timeouts están configurados correctamente"""
    print("🔍 Verificando configuración de timeouts en MySQL...")
    
    try:
        # Conectar a MySQL
        connection = pymysql.connect(
            host='localhost',
            port=3308,
            user='proyectos_admin',
            password='123456!#Td',
            database='proyectosDB',
            charset='utf8mb4',
            connect_timeout=60,
            read_timeout=30,
            write_timeout=30
        )
        
        with connection.cursor() as cursor:
            print("✅ Conexión establecida")
            
            # Verificar timeouts actuales
            timeouts_to_check = [
                'wait_timeout',
                'interactive_timeout', 
                'net_read_timeout',
                'net_write_timeout',
                'max_execution_time',
                'innodb_lock_wait_timeout'
            ]
            
            print("\n📊 Timeouts configurados:")
            for timeout_var in timeouts_to_check:
                cursor.execute(f"SHOW VARIABLES LIKE '{timeout_var}'")
                result = cursor.fetchone()
                if result:
                    value = result[1]
                    if timeout_var in ['wait_timeout', 'interactive_timeout']:
                        if int(value) >= 1800:
                            status = "✅"
                        else:
                            status = "⚠️"
                    elif timeout_var in ['net_read_timeout', 'net_write_timeout']:
                        if int(value) >= 600:
                            status = "✅"
                        else:
                            status = "⚠️"
                    elif timeout_var == 'max_execution_time':
                        if int(value) >= 1800000:
                            status = "✅"
                        else:
                            status = "⚠️"
                    else:
                        status = "ℹ️"
                    
                    print(f"   {status} {timeout_var}: {value}")
            
            # Probar operación que tome tiempo
            print("\n🧪 Probando operación larga (30 segundos)...")
            start_time = time.time()
            cursor.execute("SELECT SLEEP(30)")
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"   ✅ Operación completada en {duration:.2f} segundos")
            
            if duration >= 29:  # Debe haber durado al menos 29 segundos
                print("   ✅ Los timeouts están funcionando correctamente")
                return True
            else:
                print("   ❌ La operación se interrumpió prematuramente")
                return False
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Verificación de timeouts MySQL\n")
    
    success = test_mysql_timeouts()
    
    if success:
        print("\n🎉 Los timeouts están configurados correctamente")
        print("🔧 El sistema debería poder manejar operaciones de backup/restore largas")
    else:
        print("\n❌ Los timeouts no están funcionando correctamente")
        print("🔧 Es necesario revisar la configuración")
    
    sys.exit(0 if success else 1)