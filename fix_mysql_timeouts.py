#!/usr/bin/env python3
"""
Script para configurar MySQL con timeouts apropiados para operaciones de backup/restore
"""
import sys
import os
import pymysql
import time
from sqlalchemy import create_engine, text
from config import get_config

def configure_mysql_timeouts():
    """Configurar timeouts de MySQL para operaciones largas"""
    print("🔧 Configurando timeouts de MySQL para operaciones de backup/restore...")
    
    try:
        config = get_config()
        
        # Configuración de base de datos
        db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3308)),  # Puerto mapeado de Docker
            'user': os.getenv('MYSQL_USER', 'proyectos_admin'),
            'password': os.getenv('MYSQL_PASSWORD', '123456!#Td'),
            'database': os.getenv('MYSQL_DB', 'proyectosDB'),
        }
        
        print(f"📊 Conectando a MySQL en {db_config['host']}:{db_config['port']}")
        
        # Conectar con PyMySQL directo
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset='utf8mb4',
            connect_timeout=60,
            read_timeout=30,
            write_timeout=30
        )
        
        with connection.cursor() as cursor:
            # Verificar configuración actual
            print("\n📋 Configuración actual de timeouts:")
            timeouts_to_check = [
                'wait_timeout',
                'interactive_timeout',
                'net_read_timeout',
                'net_write_timeout',
                'connect_timeout',
                'max_execution_time',
                'innodb_lock_wait_timeout'
            ]
            
            for timeout_var in timeouts_to_check:
                cursor.execute(f"SHOW VARIABLES LIKE '{timeout_var}'")
                result = cursor.fetchone()
                if result:
                    print(f"   {result[0]}: {result[1]}")
            
            # Configurar timeouts globales para sesiones futuras
            print("\n🔧 Configurando timeouts globales:")
            timeout_configs = [
                ("SET GLOBAL wait_timeout = 1800", "wait_timeout = 30 minutos"),
                ("SET GLOBAL interactive_timeout = 1800", "interactive_timeout = 30 minutos"),
                ("SET GLOBAL net_read_timeout = 600", "net_read_timeout = 10 minutos"),
                ("SET GLOBAL net_write_timeout = 600", "net_write_timeout = 10 minutos"),
                ("SET GLOBAL max_execution_time = 1800000", "max_execution_time = 30 minutos (ms)"),
                ("SET GLOBAL innodb_lock_wait_timeout = 600", "innodb_lock_wait_timeout = 10 minutos")
            ]
            
            for sql, description in timeout_configs:
                try:
                    cursor.execute(sql)
                    print(f"   ✅ {description}")
                except Exception as e:
                    print(f"   ⚠️ {description} - Error: {e}")
            
            connection.commit()
            
            # Configurar timeouts para la sesión actual
            print("\n🔧 Configurando timeouts de sesión:")
            session_configs = [
                ("SET SESSION wait_timeout = 1800", "wait_timeout de sesión = 30 minutos"),
                ("SET SESSION interactive_timeout = 1800", "interactive_timeout de sesión = 30 minutos"),
                ("SET SESSION net_read_timeout = 600", "net_read_timeout de sesión = 10 minutos"),
                ("SET SESSION net_write_timeout = 600", "net_write_timeout de sesión = 10 minutos"),
                ("SET SESSION max_execution_time = 1800000", "max_execution_time de sesión = 30 minutos"),
                ("SET SESSION autocommit = 1", "autocommit habilitado para mejor rendimiento")
            ]
            
            for sql, description in session_configs:
                try:
                    cursor.execute(sql)
                    print(f"   ✅ {description}")
                except Exception as e:
                    print(f"   ⚠️ {description} - Error: {e}")
            
            # Verificar que los cambios se aplicaron
            print("\n📋 Verificando configuración actualizada:")
            for timeout_var in timeouts_to_check:
                cursor.execute(f"SHOW VARIABLES LIKE '{timeout_var}'")
                result = cursor.fetchone()
                if result:
                    print(f"   {result[0]}: {result[1]}")
        
        connection.close()
        print("\n✅ Configuración de timeouts completada exitosamente")
        
        # Ahora probar con SQLAlchemy
        print("\n🧪 Probando conexión con SQLAlchemy...")
        engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}",
            pool_size=5,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={
                'charset': 'utf8mb4',
                'connect_timeout': 120,
                'read_timeout': 1800,
                'write_timeout': 1800,
                'autocommit': False
            }
        )
        
        with engine.connect() as conn:
            # Probar una consulta simple
            result = conn.execute(text("SELECT COUNT(*) as total FROM trabajador"))
            row = result.fetchone()
            print(f"   ✅ Conexión SQLAlchemy OK - Total trabajadores: {row.total}")
            
            # Configurar timeouts de sesión en SQLAlchemy
            session_configs_sqlalchemy = [
                "SET SESSION wait_timeout = 1800",
                "SET SESSION interactive_timeout = 1800",
                "SET SESSION net_read_timeout = 600",
                "SET SESSION net_write_timeout = 600",
                "SET SESSION max_execution_time = 1800000"
            ]
            
            for config_sql in session_configs_sqlalchemy:
                conn.execute(text(config_sql))
            
            print("   ✅ Timeouts de sesión SQLAlchemy configurados")
        
        print("\n🎉 Todas las configuraciones aplicadas correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error configurando timeouts: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_connection():
    """Probar que la conexión puede mantenerse durante operaciones largas"""
    print("\n🧪 Probando estabilidad de conexión para operaciones largas...")
    
    try:
        config = get_config()
        
        # Configurar SQLAlchemy con timeouts largos
        engine = create_engine(
            config.SQLALCHEMY_DATABASE_URI,
            **config.SQLALCHEMY_ENGINE_OPTIONS
        )
        
        with engine.connect() as conn:
            # Simular una operación larga
            print("   🔄 Simulando operación de 60 segundos...")
            conn.execute(text("SELECT SLEEP(60)"))
            
            # Verificar que la conexión sigue activa
            result = conn.execute(text("SELECT 'Conexión activa' as status"))
            row = result.fetchone()
            print(f"   ✅ {row.status}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en prueba de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando configuración de timeouts MySQL para backups\n")
    
    # Esperar a que MySQL esté listo
    max_retries = 30
    for i in range(max_retries):
        try:
            # Probar conexión básica
            connection = pymysql.connect(
                host='localhost',
                port=3308,
                user='proyectos_admin',
                password='123456!#Td',
                database='proyectosDB',
                charset='utf8mb4',
                connect_timeout=5
            )
            connection.close()
            print("✅ MySQL está listo")
            break
        except Exception as e:
            print(f"⏳ Esperando MySQL ({i+1}/{max_retries})...")
            time.sleep(2)
            if i == max_retries - 1:
                print(f"❌ No se pudo conectar a MySQL: {e}")
                sys.exit(1)
    
    # Configurar timeouts
    success = configure_mysql_timeouts()
    
    if success:
        # Probar conexión larga
        test_backup_connection()
        print("\n🎉 Sistema listo para operaciones de backup/restore largas")
    else:
        print("\n❌ Falló la configuración, revise los logs")
        sys.exit(1)