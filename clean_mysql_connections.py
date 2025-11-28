#!/usr/bin/env python3
"""
Script para limpiar conexiones MySQL antes de restauración
"""
import pymysql
import os

def clean_mysql_connections():
    """Limpia las conexiones MySQL activas"""
    print("🧹 Limpiando conexiones MySQL...")
    
    try:
        # Conectarse como admin
        connection = pymysql.connect(
            host='mysql_db',
            port=3306,
            user='proyectos_admin',
            password='123456!#Td',
            database='proyectosDB',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Ver procesos activos
            cursor.execute("SHOW PROCESSLIST")
            processes = cursor.fetchall()
            
            print(f"📊 Procesos activos encontrados: {len(processes)}")
            
            # Matar conexiones de la aplicación
            for process in processes:
                process_id, user, host, db, command, time_sec, state, info = process
                
                # No matar nuestra propia conexión ni conexiones del sistema
                if user == 'proyectos_admin' and process_id != connection.thread_id():
                    try:
                        cursor.execute(f"KILL {process_id}")
                        print(f"🔪 Proceso eliminado: {process_id} ({user}@{host})")
                    except Exception as e:
                        print(f"⚠️  No se pudo eliminar proceso {process_id}: {e}")
            
            # Limpiar tablas temporales
            cursor.execute("FLUSH TABLES")
            cursor.execute("RESET QUERY CACHE") 
            
            connection.commit()
            print("✅ Limpieza completada")
            
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    clean_mysql_connections()